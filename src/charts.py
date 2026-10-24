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
