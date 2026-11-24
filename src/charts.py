"""SVG charts, generated from content/numbers.yaml. Edit numbers there; edit the look here."""
from __future__ import annotations
import math


def network_svg(n: dict, labels: dict, connected: bool, hub_title: str, hub_sub: str, scope_labels: dict | None = None) -> str:
    """Stakeholder network: real organisations, grouped by scope. connected=False shows them isolated."""
    pal = n["palette"]; net = n["network"]
    nodes = net["nodes"]; hub = net["hub"]; k = net.get("neighbours", 2)
    g = []
    scope_labels = scope_labels or {}
    for sc in net.get("scopes", []):
        lab = scope_labels.get(sc["label"], sc["label"])
        g.append(f'<text x="{sc["x"]}" y="18" text-anchor="middle" font-size="12" font-weight="700" '
                 f'letter-spacing="2" fill="#93002d" opacity=".55">{lab}</text>')
    if connected:
        for p in nodes:
            g.append(f'<line x1="{p["x"]}" y1="{p["y"]}" x2="{hub["x"]}" y2="{hub["y"]}" '
                     f'stroke="{pal["teal"]}" stroke-opacity=".18" stroke-width="1.2"/>')
        seen = set()
        for i, a in enumerate(nodes):
            near = sorted((m for m in range(len(nodes)) if m != i),
                          key=lambda m: math.hypot(a["x"] - nodes[m]["x"], a["y"] - nodes[m]["y"]))[:k]
            for m in near:
                key = tuple(sorted((i, m)))
                if key in seen:
                    continue
                seen.add(key); b = nodes[m]
                g.append(f'<line x1="{a["x"]}" y1="{a["y"]}" x2="{b["x"]}" y2="{b["y"]}" '
                         f'stroke="{pal["teal"]}" stroke-opacity=".35" stroke-width="1.5"/>')
        g.append(f'<circle cx="{hub["x"]}" cy="{hub["y"]}" r="{hub["radius"]}" fill="#f8e9ed" '
                 f'stroke="{pal["teal"]}" stroke-width="2"/>'
                 f'<text x="{hub["x"]}" y="{hub["y"]-3}" text-anchor="middle" font-size="13" font-weight="700" '
                 f'fill="{pal["teal"]}">{hub_title}</text>'
                 f'<text x="{hub["x"]}" y="{hub["y"]+12}" text-anchor="middle" font-size="9.5" fill="#1f1a1b">{hub_sub}</text>')
    for p in nodes:
        if p.get("engaged"):
            g.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="17" fill="none" stroke="{pal["engaged"]}" stroke-width="2.5"/>')
        g.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="11" fill="{pal[p["type"]]}" stroke="#fff" stroke-width="2">'
                 f'<title>{p["label"]} ({scope_labels.get(p["scope"].upper(), p["scope"])}{"; " + p["note"] if p.get("note") else ""})</title></circle>')
        g.append(f'<text x="{p["x"]}" y="{p["y"]+(30 if p.get("engaged") else 26)}" text-anchor="middle" font-size="12.5" '
                 f'font-weight="{700 if p.get("engaged") else 400}" fill="#1f1a1b">{p["label"]}</text>')
    return ('<svg viewBox="0 0 1000 480" width="100%" role="img" '
            'aria-label="Real organisations in community and local energy, isolated or connected through the Alliance">'
            + "".join(g) + "</svg>")


def network_legend_html(n: dict, labels: dict, engaged_label: str = "Already engaged") -> str:
    pal = n["palette"]
    types = []
    for p in n["network"]["nodes"]:
        if p["type"] not in types:
            types.append(p["type"])
    dots = "".join(
        f'<span class="tab" style="cursor:default"><span style="display:inline-block;width:10px;height:10px;'
        f'border-radius:50%;background:{pal[t]};margin-right:6px"></span>{labels.get(t, t)}</span>' for t in types)
    ring = (f'<span class="tab" style="cursor:default"><span style="display:inline-block;width:10px;height:10px;'
            f'border-radius:50%;border:2.5px solid {pal["engaged"]};margin-right:6px"></span>{engaged_label}</span>')
    return dots + ring


def feeder_profile(n: dict, scenario: str) -> list[float]:
    f = n["feeder"]
    prof = list(f["base_profile_kw"])
    if len(prof) != 24:
        raise ValueError("feeder.base_profile_kw must have 24 values")
    if scenario != "base":
        for ch in f[scenario]:
            a, b = ch["hours"]
            for h in range(a, b + 1):
                prof[h] += ch["delta"]
    return prof


def feeder_svg(n: dict, scenario: str, labels: dict) -> str:
    f = n["feeder"]; pal = n["palette"]
    prof = feeder_profile(n, scenario)
    W, H, L, B, T = 900, 300, 44, 36, 14
    ymax, lim = f["y_max"], f["limit_kw"]
    X = lambda h: L + h * (W - L - 14) / 23
    Y = lambda v: H - B - (v / ymax) * (H - B - T)
    g = []
    step = 40
    for v in range(0, int(ymax) + 1, step):
        g.append(f'<line x1="{L}" x2="{W-14}" y1="{Y(v)}" y2="{Y(v)}" stroke="#ddd5c4"/>'
                 f'<text x="{L-6}" y="{Y(v)+4}" text-anchor="end" font-size="11" fill="#5d6b6e">{v}</text>')
    for h in range(0, 24, 3):
        g.append(f'<text x="{X(h)}" y="{H-14}" text-anchor="middle" font-size="12.5" fill="#5d6b6e">{h}h</text>')
    for h, v in enumerate(prof):
        col = pal["alert"] if v > lim else pal["ok"]
        g.append(f'<rect x="{X(h)-14}" y="{Y(v)}" width="28" height="{Y(0)-Y(v)}" fill="{col}" opacity=".85" rx="2"/>')
    g.append(f'<line x1="{L}" x2="{W-14}" y1="{Y(lim)}" y2="{Y(lim)}" stroke="#1f1a1b" stroke-width="2" stroke-dasharray="6 4"/>'
             f'<text x="{W-16}" y="{Y(lim)-6}" text-anchor="end" font-size="12" font-weight="700" fill="#1f1a1b">'
             f'{labels["limit"]} ({lim} {labels["unit"]})</text>'
             f'<text x="12" y="12" font-size="11" fill="#5d6b6e">{labels["unit"]}</text>')
    return ('<svg viewBox="0 0 900 300" width="100%" role="img" aria-label="Daily load against the feeder limit">'
            + "".join(g) + "</svg>")


def feeder_stats(n: dict, scenario: str) -> dict:
    prof = feeder_profile(n, scenario)
    lim = n["feeder"]["limit_kw"]
    return {"peak": round(max(prof)), "hours_over": sum(1 for v in prof if v > lim)}


# ------------------------------------------------------------------ tool landscape
TOOL_COLOURS = ["#1598d6", "#e83f21", "#e90065", "#e08a00", "#93002d", "#00776f", "#7a4fa0", "#5f5a5b"]


def _esc(x):
    return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def tools_matrix_html(tools_cfg: dict, ui: dict) -> str:
    """Table: one row per tool, one column per layer. Empty cells show '?' (not confirmed)."""
    cols = tools_cfg["columns"]
    keys = list(cols.keys())
    head = f"<tr><th>{_esc(ui['tool'])}</th>" + "".join(f"<th>{_esc(cols[k])}</th>" for k in keys) + f"<th>{_esc(ui['source'])}</th></tr>"
    rows = []
    for i, t in enumerate(tools_cfg["tools"]):
        col = TOOL_COLOURS[i % len(TOOL_COLOURS)]
        cells = []
        for k in keys:
            v = t.get(k)
            cells.append(f'<td>{_esc(v)}</td>' if v else '<td class="unk">?</td>')
        src = f'<a href="{t["source"]}">{_esc(ui["link"])}</a>' if t.get("source") else ""
        rows.append(f'<tr><td class="tn" style="border-left:5px solid {col}"><b>{_esc(t["name"])}</b>'
                    f'<br><span>{_esc(t["owner"])}</span></td>' + "".join(cells) + f"<td>{src}</td></tr>")
    return f'<div class="tscroll"><table class="tm">{head}{"".join(rows)}</table></div>'


def stack_diagram_html(tools_cfg: dict, labels: dict, core_view: bool) -> str:
    """Columns = tools. Today: each tool has its own data model, capture and KPIs.
    Core view: those three rows become shared bars; front ends and back ends stay different."""
    tools = [(i, t) for i, t in enumerate(tools_cfg["tools"]) if t.get("diagram")]
    n = len(tools)
    short = lambda t: t["name"].split(" (")[0].split(" / ")[0]
    trunc = lambda v, m=58: (v if len(v) <= m else v[: m - 1].rsplit(" ", 1)[0] + "…") if v else "?"
    g = [f'<div class="stk" style="--n:{n}">']
    g.append('<div class="rl"></div>' + "".join(
        f'<div class="th" style="background:{TOOL_COLOURS[i % 8]}">{_esc(short(t))}</div>' for i, t in tools))
    def row(label, key, own=True):
        out = f'<div class="rl">{_esc(label)}</div>'
        for i, t in tools:
            c = TOOL_COLOURS[i % 8]
            v = t.get(key)
            cls = "cell" + ("" if v else " unk")
            out += f'<div class="{cls}" style="border-color:{c};background:{c}14">{_esc(trunc(v))}</div>'
        return out
    g.append(row(labels["row_frontend"], "frontend"))
    if core_view:
        for key in ("row_model", "row_capture", "row_kpis"):
            g.append(f'<div class="rl core">{_esc(labels[key])}</div><div class="corebar" style="grid-column:span {n}">{_esc(labels[key + "_core"])}</div>')
    else:
        g.append(row(labels["row_model"], "data_model"))
        g.append(row(labels["row_capture"], "capture"))
        g.append(row(labels["row_kpis"], "kpis"))
    g.append(row(labels["row_backend"], "backend"))
    g.append("</div>")
    return "".join(g)


def core_layers_html(tools_cfg: dict) -> str:
    return '<div class="grid g3">' + "".join(
        f'<div class="card layer"><b>{i + 1}. {_esc(l["title"])}</b><p>{_esc(l["text"])}</p></div>'
        for i, l in enumerate(tools_cfg["core_layers"])) + "</div>"


# ------------------------------------------------------------------ budget
def _num(v):
    return v or 0


def _fmt(v):
    return "-" if v in (None, 0) else f"{v:,.0f}"


def budget_checks(b: dict) -> list[str]:
    """Return warnings when the budget numbers do not add up. Printed by build.py."""
    w = []
    ys = b["years"]; c = b["costs"]; i = b["incomes"]
    for k, y in enumerate(ys):
        comp = sum(_num(v["values"][k]) for key, v in c.items() if not v.get("total") and not v.get("count"))
        tot = _num(c["total_costs"]["values"][k])
        if abs(comp - tot) > 2:
            w.append(f"{y}: total costs {tot:,} but the cost lines add up to {comp:,} (difference {tot-comp:,})")
        inc = sum(_num(v["values"][k]) for key, v in i.items() if not v.get("total"))
        if abs(inc - _num(i["total_incomes"]["values"][k])) > 2:
            w.append(f"{y}: total incomes {i['total_incomes']['values'][k]:,} but the lines add up to {inc:,}")
        if abs(inc - tot) > 2:
            w.append(f"{y}: incomes {inc:,} and costs {tot:,} are not balanced")
    return w


def budget_stats(b: dict) -> dict:
    c = b["costs"]; i = b["incomes"]
    total = sum(_num(v) for v in c["total_costs"]["values"])
    src = {k: sum(_num(x) for x in v["values"]) for k, v in i.items() if not v.get("total")}
    team_last = _num(b["team"]["ra"][-1]) + _num(b["team"]["pm"][-1])
    return {"total": total, "first": _num(c["total_costs"]["values"][0]), "y0": b["years"][0], "y1": b["years"][-1],
            "partners_pct": round(100 * src["partners"] / total), "projects_pct": round(100 * (src["bilateral"] + src["horizon"] + src["multilateral"]) / total),
            "team_last": team_last, "src": src}


def budget_income_svg(b: dict) -> str:
    ys = b["years"]; inc = {k: v for k, v in b["incomes"].items() if not v.get("total")}
    tot = b["costs"]["total_costs"]["values"]
    W, H, L, B, T = 900, 340, 60, 40, 24
    mx = 450000
    X0 = lambda k: L + k * (W - L - 10) / len(ys); bw = (W - L - 10) / len(ys) * 0.62
    Y = lambda v: H - B - v / mx * (H - B - T)
    g = []
    for v in range(0, mx + 1, 100000):
        g.append(f'<line x1="{L}" x2="{W-10}" y1="{Y(v)}" y2="{Y(v)}" stroke="#e2d9d6"/><text x="{L-8}" y="{Y(v)+4}" text-anchor="end" font-size="11" fill="#5f5a5b">{v//1000}k</text>')
    for k, y in enumerate(ys):
        x = X0(k) + ((W - L - 10) / len(ys) - bw) / 2; base = 0
        for key, d in inc.items():
            v = _num(d["values"][k])
            if v:
                g.append(f'<rect x="{x:.1f}" y="{Y(base+v):.1f}" width="{bw:.1f}" height="{Y(base)-Y(base+v):.1f}" fill="{d["colour"]}"><title>{d["label"]}: {v:,} EUR</title></rect>')
                base += v
        g.append(f'<text x="{x+bw/2:.1f}" y="{Y(base)-6:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#1f1a1b">{tot[k]/1000:.0f}k</text>')
        g.append(f'<text x="{x+bw/2:.1f}" y="{H-14}" text-anchor="middle" font-size="12" fill="#1f1a1b">{y}</text>')
    g.append(f'<text x="8" y="14" font-size="11" fill="#5f5a5b">EUR</text>')
    return ('<svg viewBox="0 0 900 340" width="100%" role="img" aria-label="Costs per year covered by income sources">' + "".join(g) + "</svg>")


def budget_legend_html(b: dict) -> str:
    return "".join(f'<span class="tab" style="cursor:default"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{d["colour"]};margin-right:6px"></span>{_esc(d["label"])}</span>'
                   for k, d in b["incomes"].items() if not d.get("total"))


def budget_team_svg(b: dict, unit: str, pm_word: str = "Project manager", ra_word: str = "Research assistants") -> str:
    ys = b["years"]; c = b["costs"]
    W, H, L, B, T = 440, 240, 30, 36, 20
    mx = 5
    bw = (W - L - 10) / len(ys) * 0.6
    Y = lambda v: H - B - v / mx * (H - B - T)
    g = [f'<line x1="{L}" x2="{W-10}" y1="{Y(0)}" y2="{Y(0)}" stroke="#e2d9d6"/>']
    for v in range(1, mx + 1):
        g.append(f'<line x1="{L}" x2="{W-10}" y1="{Y(v)}" y2="{Y(v)}" stroke="#f0e8e5"/><text x="{L-6}" y="{Y(v)+4}" text-anchor="end" font-size="10" fill="#5f5a5b">{v}</text>')
    for k, y in enumerate(ys):
        x = L + k * (W - L - 10) / len(ys) + ((W - L - 10) / len(ys) - bw) / 2
        pm = _num(b["team"]["pm"][k]); ra = _num(b["team"]["ra"][k])
        g.append(f'<rect x="{x:.1f}" y="{Y(pm):.1f}" width="{bw:.1f}" height="{Y(0)-Y(pm):.1f}" fill="#93002d"><title>{pm_word}: {pm}</title></rect>')
        if ra:
            g.append(f'<rect x="{x:.1f}" y="{Y(pm+ra):.1f}" width="{bw:.1f}" height="{Y(pm)-Y(pm+ra):.1f}" fill="#1598d6"><title>{ra_word}: {ra}</title></rect>')
        g.append(f'<text x="{x+bw/2:.1f}" y="{Y(pm+ra)-5:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#1f1a1b">{pm+ra}</text>')
        g.append(f'<text x="{x+bw/2:.1f}" y="{H-14}" text-anchor="middle" font-size="10.5" fill="#1f1a1b">{y}</text>')
    return (f'<svg viewBox="0 0 440 240" width="100%" role="img" aria-label="Team size per year">' + "".join(g) + "</svg>")


def budget_mix_svg(b: dict) -> str:
    st = budget_stats(b); inc = {k: v for k, v in b["incomes"].items() if not v.get("total")}
    tot = st["total"]; W, rowh = 440, 34
    g = []
    for r, (key, d) in enumerate(sorted(inc.items(), key=lambda kv: -st["src"][kv[0]])):
        v = st["src"][key]; pct = 100 * v / tot; y = 12 + r * rowh
        g.append(f'<text x="0" y="{y+13}" font-size="11.5" fill="#1f1a1b">{_esc(d["label"])}</text>')
        g.append(f'<rect x="235" y="{y}" width="{max(pct,0.5)*1.9:.1f}" height="18" fill="{d["colour"]}" rx="3"><title>{v:,} EUR</title></rect>')
        g.append(f'<text x="{235+max(pct,0.5)*1.9+6:.1f}" y="{y+13}" font-size="11.5" font-weight="700" fill="#1f1a1b">{pct:.0f}%</text>')
    return (f'<svg viewBox="0 0 440 {12+len(inc)*rowh}" width="100%" role="img" aria-label="Share of each income source over the whole period">' + "".join(g) + "</svg>")


def budget_table_html(b: dict, ui: dict) -> str:
    ys = b["years"]
    head = f"<tr><th>{ui['eur']}</th>" + "".join(f"<th>{y}</th>" for y in ys) + f"<th>{ui['total']}</th></tr>"
    def row(d, cls=""):
        tot = "" if d.get("count") else f"{sum(_num(v) for v in d['values']):,.0f}"
        return f'<tr class="{cls}"><td>{_esc(d["label"])}</td>' + "".join(f"<td>{_fmt(v)}</td>" for v in d["values"]) + f"<td>{tot}</td></tr>"
    out = [head, '<tr class="sec"><td colspan="%d">%s</td></tr>' % (len(ys) + 2, ui["costs"])]
    for k, d in b["costs"].items():
        out.append(row(d, "tot" if d.get("total") else ("cnt" if d.get("count") else "")))
    out.append('<tr class="sec"><td colspan="%d">%s</td></tr>' % (len(ys) + 2, ui["incomes"]))
    for k, d in b["incomes"].items():
        out.append(row(d, "tot" if d.get("total") else ""))
    return '<div class="tscroll"><table class="bt">' + "".join(out) + "</table></div>"


# ------------------------------------------------------------------ tool map (topic x scale, coloured by owner or origin)
def tools_map_html(tools_cfg: dict) -> str:
    m = tools_cfg["map"]; topics = m["topics"]; scales = m["scales"]; who = m["who"]; geo = m["geo"]
    used = {t["topic"] for t in tools_cfg["tools"]}
    out = ['<div class="tmap">', '<div class="tm-head"><div></div>' + "".join(
        f'<div class="tm-col">{_esc(v)}</div>' for k, v in scales.items()) + "</div>"]
    for tk, tl in topics.items():
        if tk not in used:
            continue
        chips = []
        for t in tools_cfg["tools"]:
            if t["topic"] != tk:
                continue
            a, b = t["scale"]
            nm = t.get("short") or t["name"].split(" (")[0].split(" / ")[0]
            link = t.get("source", "")
            chips.append(
                f'<a class="tchip" href="{link}" style="grid-column:{a} / span {b - a + 1};--who:{who[t["who"]]["colour"]};--geo:{geo[t["geo"]]["colour"]}" '
                f'title="{_esc(t["name"])} · {_esc(t["owner"])}"><b>{_esc(nm)}</b><span>{_esc(t["owner"])}</span></a>')
        out.append(f'<div class="tm-row"><div class="tm-lab">{_esc(tl)}</div><div class="tm-grid">{"".join(chips)}</div></div>')
    out.append("</div>")
    return "".join(out)


def tools_map_legend_html(tools_cfg: dict) -> str:
    m = tools_cfg["map"]
    def leg(d):
        return "".join(f'<span class="tab" style="cursor:default"><span style="display:inline-block;width:10px;height:10px;border-radius:3px;background:{v["colour"]};margin-right:6px"></span>{_esc(v["label"])}</span>' for v in d.values())
    return f'<div class="chips leg-who">{leg(m["who"])}</div><div class="chips leg-geo" style="display:none">{leg(m["geo"])}</div>'


# ------------------------------------------------------------------ IREC chapter (numbers come from budget.yaml)
def irec_budget(b: dict) -> dict:
    i = b["incomes"]; ys = b["years"]; tot = b["costs"]["total_costs"]["values"]
    st = budget_stats(b)
    g = lambda key, k: _num(i[key]["values"][k])
    return {
        "concordia_27": g("concordia", 0), "concordia_28": g("concordia", 1),
        "irec_27": g("irec", 0), "irec_28": g("irec", 1),
        "irec_pct_27": round(100 * g("irec", 0) / tot[0]), "irec_pct_28": round(100 * g("irec", 1) / tot[1]),
        "concordia_pct_27": round(100 * g("concordia", 0) / tot[0]), "concordia_pct_28": round(100 * g("concordia", 1) / tot[1]),
        "partners_28": g("partners", 1), "rent_later": _num(b["costs"]["rent"]["values"][2]),
        "bilateral": st["src"]["bilateral"], "horizon": st["src"]["horizon"], "multilateral": st["src"]["multilateral"],
        "year0": ys[0], "year1": ys[1],
    }


def irec_first_years_svg(b: dict, ui: dict) -> str:
    inc = {k: v for k, v in b["incomes"].items() if not v.get("total")}
    ys = b["years"][:2]; tot = b["costs"]["total_costs"]["values"]
    W, L, bh = 900, 70, 34
    g = []
    for r, y in enumerate(ys):
        top = 16 + r * 66; x = L; scale = (W - L - 20) / tot[r]
        g.append(f'<text x="0" y="{top+22}" font-size="13" font-weight="700" fill="#1f1a1b">{y}</text>')
        for key, d in inc.items():
            v = _num(d["values"][r])
            if not v:
                continue
            w = v * scale
            g.append(f'<rect x="{x:.1f}" y="{top}" width="{w:.1f}" height="{bh}" fill="{d["colour"]}"><title>{d["label"]}: {v:,} EUR</title></rect>')
            if w > 70:
                g.append(f'<text x="{x+w/2:.1f}" y="{top+22}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fff">{100*v/tot[r]:.0f}%</text>')
            x += w
        g.append(f'<text x="{W-18}" y="{top+bh+14}" text-anchor="end" font-size="11" fill="#5f5a5b">{ui["total_costs_word"]} {tot[r]:,} {ui["eur"]}</text>')
    return f'<svg viewBox="0 0 900 150" width="100%" role="img" aria-label="Who covers the costs in the first two years">' + "".join(g) + "</svg>"


# ------------------------------------------------------------------ cover: four intersecting circles
def venn_svg(cv: dict) -> str:
    import textwrap
    cols = ["#00776F", "#E08A00", "#E90065", "#1598D6"]
    cx, cy, d, r = 320, 300, 100, 165
    centres = [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]
    widths = [20, 15, 20, 15]
    labpos = [(cx, cy - d - r + 62), (cx + d + r - 72, cy), (cx, cy + d + r - 62), (cx - d - r + 72, cy)]
    g = []
    for i, ((x, y), col) in enumerate(zip(centres, cols)):
        p = cv["pillars"][i]
        g.append(f'<circle class="vc" cx="{x}" cy="{y}" r="{r}" fill="{col}" fill-opacity=".42" stroke="{col}" stroke-width="2"><title>{_esc(p["title"])}: {_esc(p["text"])}</title></circle>')
    for i, (lx, ly) in enumerate(labpos):
        lines = textwrap.wrap(cv["pillars"][i]["title"], widths[i])
        y0 = ly - (len(lines) - 1) * 10
        tsp = "".join(f'<tspan x="{lx}" y="{y0 + k * 20}">{_esc(t)}</tspan>' for k, t in enumerate(lines))
        g.append(f'<text text-anchor="middle" dominant-baseline="middle" font-size="16.5" font-weight="700" fill="#1f1a1b">{tsp}</text>')
    words = textwrap.wrap(cv["centre"], 11)
    y0 = cy - (len(words) - 1) * 10
    tsp = "".join(f'<tspan x="{cx}" y="{y0 + k * 20}">{_esc(w)}</tspan>' for k, w in enumerate(words))
    g.append(f'<circle cx="{cx}" cy="{cy}" r="62" fill="#93002D" stroke="#fff" stroke-width="3"/>'
             f'<text text-anchor="middle" dominant-baseline="middle" font-size="15" font-weight="700" fill="#fff">{tsp}</text>')
    return ('<svg viewBox="0 0 640 600" width="100%" role="img" aria-label="' + _esc(cv["roof"]) + '">' + "".join(g) + "</svg>")


# ------------------------------------------------------------------ vision: world map of communities with example fact sheets
def world_map(markers: list, dots: dict, v: dict, lang: str) -> dict:
    """Dot map of the world with example communities. Fact sheets use HYPOTHETICAL data, generated deterministically."""
    import random
    W, H, x0, y0 = 720, 300, 0, 0
    sx = W / 360.0; top = 82.0
    X = lambda lon: (lon + 180) * sx
    Y = lambda lat: (top - lat) * sx
    cols = {"ec": "#E90065", "dh": "#E08A00", "mg": "#00776F"}
    g = ['<path d="' + "".join(f"M{X(a):.0f} {Y(b):.0f}h0" for a, b in dots["dots"]) + '" stroke="#d9cfd2" stroke-width="3.4" stroke-linecap="round" fill="none"/>']
    fmt = (lambda x, d=0: (f"{x:,.{d}f}").replace(",", "§").replace(".", ",").replace("§", ".")) if lang == "ca" else (lambda x, d=0: f"{x:,.{d}f}")
    cards = {}
    mk = []
    for m in markers:
        rnd = random.Random(1000 + m["id"]); ty = m["type"]
        place = m["place_" + lang]
        if ty == "ec":
            cust = rnd.randint(60, 1800); kw = rnd.randint(40, 1500); prod = kw * rnd.uniform(1.15, 1.45); share = rnd.randint(32, 78)
            capex = rnd.randint(900, 1400); price = rnd.uniform(0.12, 0.22)
        elif ty == "dh":
            cust = rnd.randint(90, 3200); kw = rnd.randint(2500, 24000); prod = kw * rnd.uniform(1.8, 2.6); share = rnd.randint(45, 92)
            capex = rnd.randint(700, 1500); price = rnd.uniform(0.07, 0.14)
        else:
            cust = rnd.randint(150, 2600); kw = rnd.randint(25, 420); prod = kw * rnd.uniform(1.3, 1.7); share = rnd.randint(70, 98)
            capex = rnd.randint(1800, 3200); price = rnd.uniform(0.25, 0.45)
        cons = prod * 100 / share
        imp = rnd.randint(8, 32); co2 = rnd.randint(10, 45); pov = rnd.randint(4, 28); jobs = rnd.randint(2, 40)
        bm = v["card"]["models"][ty][rnd.randrange(len(v["card"]["models"][ty]))]
        gov = v["card"]["gov"][rnd.randrange(len(v["card"]["gov"]))]
        qual = v["card"]["quality"][rnd.randrange(len(v["card"]["quality"]))]
        # monthly bars (production vs consumption), seasonal shapes
        pm = []; cm = []
        for k in range(12):
            s = math.cos((k - 5.5) / 12 * 2 * math.pi)       # 1 in summer, -1 in winter
            if ty == "dh":
                pm.append(1 + 0.15 * s + rnd.uniform(-.05, .05)); cm.append(1 - 0.55 * s + rnd.uniform(-.05, .05))
            else:
                pm.append(1 + 0.6 * s + rnd.uniform(-.06, .06)); cm.append(1 - 0.15 * s + rnd.uniform(-.06, .06))
        mx = max(pm + cm); bars = []
        for k in range(12):
            bx = 8 + k * 24
            hp = 56 * pm[k] / mx; hc = 56 * cm[k] / mx
            bars.append(f'<rect x="{bx}" y="{62 - hp:.1f}" width="10" height="{hp:.1f}" fill="#E90065"/><rect x="{bx + 11}" y="{62 - hc:.1f}" width="10" height="{hc:.1f}" fill="#1598D6"/>')
        chart = (f'<svg viewBox="0 0 300 70" width="100%" role="img" aria-label="{_esc(v["card"]["chart"])}">' + "".join(bars) + "</svg>")
        rows = [
            (v["card"]["f_type"], v["types"][ty]),
            (v["card"]["f_customers"][ty], fmt(cust)),
            (v["card"]["f_capacity"][ty], f"{fmt(kw)} kW"),
            (v["card"]["f_prod"], f"{fmt(prod)} MWh"),
            (v["card"]["f_cons"], f"{fmt(cons)} MWh"),
            (v["card"]["f_share"], f"{share} %"),
            (v["card"]["f_ref"], v["card"]["ref_text"].format(imp=imp, co2=co2)),
            (v["card"]["f_cost"], v["card"]["cost_text"].format(capex=fmt(capex), price=fmt(price, 2))),
            (v["card"]["f_model"], bm),
            (v["card"]["f_gov"], gov),
            (v["card"]["f_social"], v["card"]["social_text"].format(pov=pov, jobs=jobs)),
            (v["card"]["f_quality"], qual),
            (v["card"]["f_update"], v["card"]["update_text"].format(d=rnd.randint(1, 28))),
        ]
        tr = "".join(f"<tr><th>{_esc(a)}</th><td>{_esc(b)}</td></tr>" for a, b in rows)
        cards[str(m["id"])] = (f'<div class="fs-head"><b>{_esc(v["card"]["name"])} {m["id"]}</b><span>{_esc(place)}</span></div>'
                               f'<table class="fs">{tr}</table><div class="fs-chart"><small>{_esc(v["card"]["chart"])}: <span style="color:#E90065">■</span> {_esc(v["card"]["prod_word"])} <span style="color:#1598D6">■</span> {_esc(v["card"]["cons_word"])}</small>{chart}</div>'
                               f'<p class="note">{_esc(v["card"]["hypothetical"])}</p>')
        mk.append(f'<g class="wm" data-id="{m["id"]}" tabindex="0" role="button" aria-label="{_esc(place)}"><circle cx="{X(m["lon"]):.1f}" cy="{Y(m["lat"]):.1f}" r="9" fill="transparent"/>'
                  f'<circle class="wd" cx="{X(m["lon"]):.1f}" cy="{Y(m["lat"]):.1f}" r="4.6" fill="{cols[m["type"]]}" stroke="#fff" stroke-width="1.4"><title>{_esc(place)}</title></circle></g>')
    svg = f'<svg id="wsvg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{_esc(v["map_title"])}">' + "".join(g) + "".join(mk) + "</svg>"
    legend = "".join(f'<span class="tab" style="cursor:default"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{cols[k]};margin-right:6px"></span>{_esc(v["types"][k])}</span>' for k in ("ec", "dh", "mg"))
    return {"svg": svg, "legend": legend, "cards": cards, "first": str(markers[14]["id"])}


# ------------------------------------------------------------------ impact scenario
def impact_calc(imp: dict, budget: dict, lang: str = "en") -> dict:
    """Illustrative impact model: low / central / high scenarios from content/impact.yaml."""
    ny = imp["cost_years"]
    cost = sum(_num(v) for v in budget["costs"]["total_costs"]["values"][:ny])
    sep = "." if lang == "ca" else ","
    dec = "," if lang == "ca" else "."

    def n0(v):
        return f"{round(v):,}".replace(",", sep)

    def n1(v):
        return f"{v:,.1f}".replace(",", "\0").replace(".", dec).replace("\0", sep)

    res = {}
    for key, s in imp["scenarios"].items():
        members = s["supported"] * s["members"]
        saving = members * s["saving_eur_member"]
        prod = s["supported"] * s["kw"] * s["yield_kwh_kw"]            # kWh
        co2 = prod * s["ef_kg_kwh"] / 1000                            # t
        mo = s["months_earlier"]
        cost_comm = cost / s["supported"]
        saving_comm = s["members"] * s["saving_eur_member"]
        res[key] = {
            "s": s, "members": members, "saving": saving, "prod": prod, "co2": co2,
            "saving_attr": saving * mo / 12, "co2_attr": co2 * mo / 12,
            "saving_comm": saving_comm, "co2_comm": s["kw"] * s["yield_kwh_kw"] * s["ef_kg_kwh"] / 1000,
            "cost_comm": cost_comm, "payback": 12 * cost_comm / saving_comm,
            "ratio": saving / cost, "ratio_attr": saving * mo / 12 / cost,
        }
    f = {"cost": n0(cost), "cost_years": ny, "city_n": imp["cities_example"]}
    for key, p in (("low", "l_"), ("central", "c_"), ("high", "h_")):
        r = res[key]; s = r["s"]
        f.update({
            p + "supported": n0(s["supported"]), p + "members_comm": n0(s["members"]), p + "kw": n0(s["kw"]),
            p + "saving_member": n0(s["saving_eur_member"]), p + "ef": f"{s['ef_kg_kwh']:.2f}".replace(".", dec),
            p + "months": n0(s["months_earlier"]), p + "members": n0(r["members"]),
            p + "saving": n1(r["saving"] / 1e6), p + "saving_k": n0(r["saving"] / 1e3),
            p + "prod": n1(r["prod"] / 1e6), p + "co2": n0(r["co2"]),
            p + "saving_attr": n1(r["saving_attr"] / 1e6), p + "co2_attr": n0(r["co2_attr"]),
            p + "saving_comm": n0(r["saving_comm"]), p + "co2_comm": n0(r["co2_comm"]),
            p + "prod_comm": n0(s["kw"] * s["yield_kwh_kw"] / 1e3),
            p + "payback": n0(r["payback"]), p + "ratio": n1(r["ratio"]), p + "ratio_attr": n1(r["ratio_attr"]),
            p + "cost_comm": n0(r["cost_comm"]),
            p + "city_co2": n0(r["co2_comm"] * imp["cities_example"]),
        })
    fmt = {"members": lambda r: n0(r["members"]), "saving": lambda r: n0(r["saving"]),
           "prod_gwh": lambda r: n1(r["prod"] / 1e6), "co2": lambda r: n0(r["co2"]),
           "saving_attr": lambda r: n0(r["saving_attr"]), "co2_attr": lambda r: n0(r["co2_attr"]),
           "payback_months": lambda r: n0(r["payback"]), "ratio": lambda r: n1(r["ratio"]),
           "ratio_attr": lambda r: n1(r["ratio_attr"])}
    rows = [(k, *[fn(res[sc]) for sc in ("low", "central", "high")]) for k, fn in fmt.items()]
    afmt = {"supported": n0, "members": n0, "kw": n0, "yield_kwh_kw": n0, "saving_eur_member": n0,
            "ef_kg_kwh": lambda v: f"{v:.2f}".replace(".", dec), "months_earlier": n0}
    assump = [(k, *[fn(imp["scenarios"][sc][k]) for sc in ("low", "central", "high")]) for k, fn in afmt.items()]
    return {"f": f, "rows": rows, "assump": assump, "res": res, "cost": cost}
