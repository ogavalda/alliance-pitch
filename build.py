#!/usr/bin/env python3
"""Build the pitch page.

    python build.py            # writes docs/index.html
    python build.py --serve    # build, then serve at http://localhost:8000 and rebuild on every change
"""
from __future__ import annotations
import argparse, base64, http.server, json, mimetypes, socketserver, sys, threading, time
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import charts  # noqa: E402

WATCH = [ROOT / "content", ROOT / "src", ROOT / "assets"]


def load_logos(items: list) -> list:
    """Embed each logo file as a data URI so the output stays a single file."""
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


def load(name: str) -> dict:
    with open(ROOT / "content" / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build() -> Path:
    t, n, layout = load("text.yaml"), load("numbers.yaml"), load("layout.yaml")
    sections = [s["id"] for s in layout["sections"] if s.get("enabled", True)]
    for s in sections:
        if s not in t:
            raise SystemExit(f"layout.yaml lists section '{s}' but text.yaml has no '{s}' block")
    hero, demo = t["hero"], t["demo"]
    tools_cfg = load("tools.yaml")
    budget = load("budget.yaml")
    for w in charts.budget_checks(budget):
        print("BUDGET WARNING:", w)
    bst = charts.budget_stats(budget)
    figs = {
        "net_off": charts.network_svg(n, hero["actor_labels"], False, hero["net_hub_title"], hero["net_hub_sub"]),
        "net_on": charts.network_svg(n, hero["actor_labels"], True, hero["net_hub_title"], hero["net_hub_sub"]),
        "budget": {"stats": bst, "income_svg": charts.budget_income_svg(budget), "legend": charts.budget_legend_html(budget),
                   "team_svg": charts.budget_team_svg(budget, t["budget"]["team_unit"]), "mix_svg": charts.budget_mix_svg(budget),
                   "table": charts.budget_table_html(budget)},
        "irec": {**charts.irec_budget(budget), "svg": charts.irec_first_years_svg(budget), "legend": charts.budget_legend_html(budget)},
        "tools_map": charts.tools_map_html(tools_cfg),
        "tools_map_legend": charts.tools_map_legend_html(tools_cfg),
        "tools_matrix": charts.tools_matrix_html(tools_cfg),
        "stack_today": charts.stack_diagram_html(tools_cfg, t["landscape"]["rows"], False),
        "stack_core": charts.stack_diagram_html(tools_cfg, t["landscape"]["rows"], True),
        "core_layers": charts.core_layers_html(tools_cfg),
        "net_legend": charts.network_legend_html(n, hero["actor_labels"], hero.get("engaged_label", "Already engaged")),
        "feeder": {s: {"svg": charts.feeder_svg(n, s, demo["labels"]), **charts.feeder_stats(n, s)}
                   for s in ("base", "uncoordinated", "coordinated")},
    }
    js_data = {
        "jobs": t["alliance"]["jobs"],
        "roles": t["members"]["roles"],
        "bring_label": t["members"]["bring_label"], "get_label": t["members"]["get_label"],
        "form": t["form"],
        "asks": t["ask"]["roles"], "next_step_label": t["ask"]["next_step_label"],
        "questions": t["ask"]["questions"],
        "copied": t["ask"]["copied"], "copy_failed": t["ask"]["copy_failed"],
        "demo": {"verdicts": demo["verdicts"], "feeder": figs["feeder"], "unit": demo["labels"]["unit"]},
    }
    env = Environment(loader=FileSystemLoader(ROOT / "src" / "templates"),
                      undefined=StrictUndefined, autoescape=False)
    html = env.get_template("index.html.j2").render(
        t=t, n=n, sections=sections, numbered=list(enumerate(sections, 1)), figs=figs, logos=load_logos(t.get("logos", [])),
        css=(ROOT / "src/static/style.css").read_text(encoding="utf-8"),
        js=(ROOT / "src/static/app.js").read_text(encoding="utf-8"),
        data_json=json.dumps(js_data, ensure_ascii=False).replace("</", "<\\/"))
    out = ROOT / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def snapshot() -> dict:
    return {str(p): p.stat().st_mtime for d in WATCH for p in d.rglob("*") if p.is_file()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="serve docs/ and rebuild on changes")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    out = build()
    print(f"Built {out}")
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
                    build(); print("Rebuilt")
                except Exception as e:  # keep serving while you fix a typo
                    print("Build error:", e)
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
