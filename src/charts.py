"""SVG charts, generated from content/numbers.yaml. Edit numbers there; edit the look here."""
from __future__ import annotations
import math


def network_svg(n: dict, labels: dict, connected: bool, hub_title: str, hub_sub: str) -> str:
    """Stakeholder network: real organisations, grouped by scope. connected=False shows them isolated."""
    pal = n["palette"]; net = n["network"]
    nodes = net["nodes"]; hub = net["hub"]; k = net.get("neighbours", 2)
    g = []
    for sc in net.get("scopes", []):
        g.append(f'<text x="{sc["x"]}" y="18" text-anchor="middle" font-size="12" font-weight="700" '
                 f'letter-spacing="2" fill="#93002d" opacity=".55">{sc["label"]}</text>')
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
                 f'<title>{p["label"]} ({p["scope"]})</title></circle>')
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


def tools_matrix_html(tools_cfg: dict) -> str:
    """Table: one row per tool, one column per layer. Empty cells show '?' (not confirmed)."""
    cols = tools_cfg["columns"]
    keys = list(cols.keys())
    head = "<tr><th>Tool</th>" + "".join(f"<th>{_esc(cols[k])}</th>" for k in keys) + "<th>Source</th></tr>"
    rows = []
    for i, t in enumerate(tools_cfg["tools"]):
        col = TOOL_COLOURS[i % len(TOOL_COLOURS)]
        cells = []
        for k in keys:
            v = t.get(k)
            cells.append(f'<td>{_esc(v)}</td>' if v else '<td class="unk">?</td>')
        src = f'<a href="{t["source"]}">link</a>' if t.get("source") else ""
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
        comp = _num(c["rent"]["values"][k]) + _num(c["labour_total"]["values"][k]) \
            + _num(c["students"]["values"][k]) + _num(c["travel"]["values"][k])
        tot = _num(c["total_costs"]["values"][k])
        if abs(comp - tot) > 2:
            w.append(f"{y}: total costs {tot:,} but rent + total labour + students + travel = {comp:,} (difference {tot-comp:,})")
        lab = _num(c["ra_unit"]["values"][k]) * _num(c["ra_number"]["values"][k]) + _num(c["pm_unit"]["values"][k])
        if abs(lab - _num(c["labour_total"]["values"][k])) > 2 and y != ys[0]:
            w.append(f"{y}: total labour {c['labour_total']['values'][k]:,} but RA x number + PM = {lab:,}")
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
    team_last = _num(c["ra_number"]["values"][-1]) + _num(c["pm_number"]["values"][-1])
    return {"total": total, "first": _num(c["total_costs"]["values"][0]), "years": f'{b["years"][0]} to {b["years"][-1]}',
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


def budget_team_svg(b: dict, unit: str) -> str:
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
        pm = _num(c["pm_number"]["values"][k]); ra = _num(c["ra_number"]["values"][k])
        g.append(f'<rect x="{x:.1f}" y="{Y(pm):.1f}" width="{bw:.1f}" height="{Y(0)-Y(pm):.1f}" fill="#93002d"><title>Project manager: {pm}</title></rect>')
        if ra:
            g.append(f'<rect x="{x:.1f}" y="{Y(pm+ra):.1f}" width="{bw:.1f}" height="{Y(pm)-Y(pm+ra):.1f}" fill="#1598d6"><title>Research assistants: {ra}</title></rect>')
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


def budget_table_html(b: dict) -> str:
    ys = b["years"]
    head = "<tr><th>EUR</th>" + "".join(f"<th>{y}</th>" for y in ys) + "<th>Total</th></tr>"
    def row(d, cls=""):
        tot = "" if d.get("count") else f"{sum(_num(v) for v in d['values']):,.0f}"
        return f'<tr class="{cls}"><td>{_esc(d["label"])}</td>' + "".join(f"<td>{_fmt(v)}</td>" for v in d["values"]) + f"<td>{tot}</td></tr>"
    out = [head, '<tr class="sec"><td colspan="%d">Costs</td></tr>' % (len(ys) + 2)]
    for k, d in b["costs"].items():
        out.append(row(d, "tot" if d.get("total") else ("cnt" if d.get("count") else "")))
    out.append('<tr class="sec"><td colspan="%d">Incomes</td></tr>' % (len(ys) + 2))
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
            nm = t["name"].split(" (")[0].split(" / ")[0]
            if t["id"] == "commercial":
                nm = "Commercial platforms (Italy)"
            if t["id"] == "inventories":
                nm = "Tool inventories (openmod, quarree100)"
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


def irec_first_years_svg(b: dict) -> str:
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
        g.append(f'<text x="{W-18}" y="{top+bh+14}" text-anchor="end" font-size="11" fill="#5f5a5b">total costs {tot[r]:,} EUR</text>')
    return f'<svg viewBox="0 0 900 150" width="100%" role="img" aria-label="Who covers the costs in the first two years">' + "".join(g) + "</svg>"
