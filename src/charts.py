"""SVG charts, generated from content/numbers.yaml. Edit numbers there; edit the look here."""
from __future__ import annotations
import math


def network_svg(n: dict, labels: dict, connected: bool, hub_title: str, hub_sub: str) -> str:
    pal = n["palette"]
    nodes = n["network"]["nodes"]
    hub = n["network"]["hub"]
    dist = n["network"]["link_distance"]
    g = []
    if connected:
        for p in nodes:
            g.append(f'<line x1="{p["x"]}" y1="{p["y"]}" x2="{hub["x"]}" y2="{hub["y"]}" '
                     f'stroke="{pal["teal"]}" stroke-opacity=".28" stroke-width="1.5"/>')
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < dist:
                    g.append(f'<line x1="{a["x"]}" y1="{a["y"]}" x2="{b["x"]}" y2="{b["y"]}" '
                             f'stroke="{pal["teal"]}" stroke-opacity=".22"/>')
        g.append(f'<circle cx="{hub["x"]}" cy="{hub["y"]}" r="{hub["radius"]}" fill="#f8e9ed" '
                 f'stroke="{pal["teal"]}" stroke-width="2"/>'
                 f'<text x="{hub["x"]}" y="{hub["y"]-4}" text-anchor="middle" font-size="13" font-weight="700" '
                 f'fill="{pal["teal"]}">{hub_title}</text>'
                 f'<text x="{hub["x"]}" y="{hub["y"]+13}" text-anchor="middle" font-size="11" fill="#1f1a1b">{hub_sub}</text>')
    for p in nodes:
        g.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="12" fill="{pal[p["type"]]}" stroke="#fff" stroke-width="2"/>')
    return ('<svg viewBox="0 0 900 300" width="100%" role="img" '
            'aria-label="Illustration of isolated organisations and a connected network">' + "".join(g) + "</svg>")


def network_legend_html(n: dict, labels: dict) -> str:
    pal = n["palette"]
    types = []
    for p in n["network"]["nodes"]:
        if p["type"] not in types:
            types.append(p["type"])
    return "".join(
        f'<span class="tab" style="cursor:default"><span style="display:inline-block;width:10px;height:10px;'
        f'border-radius:50%;background:{pal[t]};margin-right:6px"></span>{labels.get(t, t)}</span>'
        for t in types)


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
        g.append(f'<text x="{X(h)}" y="{H-14}" text-anchor="middle" font-size="11" fill="#5d6b6e">{h}h</text>')
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
