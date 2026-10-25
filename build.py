#!/usr/bin/env python3
"""Build the pitch documents (see content/editions.yaml).

    python build.py                  # builds every edition into docs/
    python build.py --only irec_ca   # builds one edition
    python build.py --serve          # build, serve docs/ at http://localhost:8000 and rebuild on every change
"""
from __future__ import annotations
import argparse, base64, copy, http.server, json, mimetypes, socketserver, sys, threading, time
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import charts  # noqa: E402

WATCH = [ROOT / "content", ROOT / "src", ROOT / "assets"]


def load(name: str):
    with open(ROOT / "content" / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def deep_merge(a, b):
    """Merge b into a copy of a. Dicts merge key by key; anything else is replaced."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = deep_merge(a[k], v) if k in a else copy.deepcopy(v)
        return out
    return copy.deepcopy(b)


def load_logos(items: list) -> list:
    out = []
    for it in items:
        f = ROOT / "assets" / "logos" / it["file"]
        d = dict(it, src=None)
        if f.exists():
            mime = mimetypes.guess_type(f.name)[0] or "image/png"
            d["src"] = f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()
        else:
            print(f"Note: logo file missing: assets/logos/{it['file']}  (placeholder shown)")
        out.append(d)
    return out


def load_tools(lang: str) -> dict:
    cfg = load("tools.yaml")
    ov = ROOT / "content" / f"tools.{lang}.yaml"
    if lang != "en" and ov.exists():
        o = yaml.safe_load(ov.read_text(encoding="utf-8"))
        by_id = {t["id"]: t for t in o.get("tools", [])}
        cfg["tools"] = [deep_merge(t, by_id.get(t["id"], {})) for t in cfg["tools"]]
        for k in ("columns", "map", "core_layers"):
            if k in o:
                cfg[k] = deep_merge(cfg[k], o[k]) if k != "core_layers" else o[k]
    return cfg


def load_budget(lang: str) -> dict:
    b = load("budget.yaml")
    ov = ROOT / "content" / f"budget.{lang}.yaml"
    if lang != "en" and ov.exists():
        b = deep_merge(b, yaml.safe_load(ov.read_text(encoding="utf-8")))
    return b


def build_edition(ed: dict) -> Path:
    t = load("text.yaml")
    for o in ed.get("overlays", []):
        t = deep_merge(t, load(o))
    lang = ed["lang"]
    n, tools_cfg, budget = load("numbers.yaml"), load_tools(lang), load_budget(lang)
    for w in charts.budget_checks(budget):
        print("BUDGET WARNING:", w)
    main, annex = ed["main"], ed["annex"]
    for s in main + annex:
        key = {"landscape_summary": "landscape_summary", "members_summary": "members_summary", "budget_summary": "budget_summary", "irec_ask": "irec_ask"}.get(s, s)
        if key not in t:
            raise SystemExit(f"edition '{ed['id']}' lists section '{s}' but text has no '{key}' block")
    ui, hero, demo = t["ui"], t["hero"], t["demo"]
    bst = charts.budget_stats(budget)
    unknown_model = sum(1 for x in tools_cfg["tools"] if not x.get("data_model"))
    unknown_kpis = sum(1 for x in tools_cfg["tools"] if not x.get("kpis"))
    tstats = {"n": len(tools_cfg["tools"]), "m": unknown_model, "k": unknown_kpis}
    figs = {
        "net_off": charts.network_svg(n, hero["actor_labels"], False, hero["net_hub_title"], hero["net_hub_sub"], hero.get("scope_labels")),
        "net_on": charts.network_svg(n, hero["actor_labels"], True, hero["net_hub_title"], hero["net_hub_sub"], hero.get("scope_labels")),
        "net_legend": charts.network_legend_html(n, hero["actor_labels"], hero.get("engaged_label", "Already engaged")),
        "budget": {"stats": bst, "income_svg": charts.budget_income_svg(budget), "legend": charts.budget_legend_html(budget),
                   "mix_svg": charts.budget_mix_svg(budget),
                   "table": charts.budget_table_html(budget, ui)},
        "irec": {**charts.irec_budget(budget), "svg": charts.irec_first_years_svg(budget, ui), "legend": charts.budget_legend_html(budget)},
        "tools_map": charts.tools_map_html(tools_cfg),
        "tools_map_legend": charts.tools_map_legend_html(tools_cfg),
        "tools_matrix": charts.tools_matrix_html(tools_cfg, ui),
        "stack_today": charts.stack_diagram_html(tools_cfg, t["landscape"]["rows"], False),
        "stack_core": charts.stack_diagram_html(tools_cfg, t["landscape"]["rows"], True),
        "core_layers": charts.core_layers_html(tools_cfg),
        "tstats": tstats,
        "feeder": {s: {"svg": charts.feeder_svg(n, s, demo["labels"]), **charts.feeder_stats(n, s)}
                   for s in ("base", "uncoordinated", "coordinated")},
    }
    questions = t["irec_ask"]["questions"] if "irec_ask" in main else t["ask"]["questions"]
    js_data = {
        "jobs": t["alliance"]["jobs"],
        "roles": t["members"]["roles"],
        "bring_label": t["members"]["bring_label"], "get_label": t["members"]["get_label"],
        "form": t["form"],
        "asks": t["ask"]["roles"], "next_step_label": t["ask"]["next_step_label"],
        "questions": questions,
        "copied": t["ask"]["copied"], "copy_failed": t["ask"]["copy_failed"],
        "demo": {"verdicts": demo["verdicts"], "feeder": figs["feeder"], "unit": demo["labels"]["unit"]},
    }
    letters = "ABCDEFGHIJ"
    numbered = [(f"{i:02d}", s) for i, s in enumerate(main, 1)]
    annexed = [(f"{t['annex']['label']} {letters[i]}", s) for i, s in enumerate(annex)]
    env = Environment(loader=FileSystemLoader(ROOT / "src" / "templates"), undefined=StrictUndefined, autoescape=False)
    html = env.get_template("index.html.j2").render(
        t=t, n=n, main=main, annex=annex, numbered=numbered, annexed=annexed, figs=figs, lang=lang,
        logos=load_logos(t.get("logos", [])),
        css=(ROOT / "src/static/style.css").read_text(encoding="utf-8"),
        js=(ROOT / "src/static/app.js").read_text(encoding="utf-8"),
        data_json=json.dumps(js_data, ensure_ascii=False).replace("</", "<\\/"))
    out = ROOT / "docs" / ed["output"]
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def build_all(only: str | None = None) -> list[Path]:
    eds = [e for e in load("editions.yaml")["editions"] if e.get("enabled", True) and (only is None or e["id"] == only)]
    return [build_edition(e) for e in eds]


def snapshot() -> dict:
    return {str(p): p.stat().st_mtime for d in WATCH for p in d.rglob("*") if p.is_file()}


def main_cli() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="edition id to build (see content/editions.yaml)")
    ap.add_argument("--serve", action="store_true", help="serve docs/ and rebuild on changes")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    for o in build_all(a.only):
        print(f"Built {o}")
    if not a.serve:
        return
    handler = lambda *x, **k: http.server.SimpleHTTPRequestHandler(*x, directory=str(ROOT / "docs"), **k)
    srv = socketserver.TCPServer(("", a.port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"Serving http://localhost:{a.port}  (Ctrl+C to stop)")
    last = snapshot()
    try:
        while True:
            time.sleep(1)
            cur = snapshot()
            if cur != last:
                last = cur
                try:
                    build_all(a.only); print("Rebuilt")
                except Exception as e:
                    print("Build error:", e)
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main_cli()
