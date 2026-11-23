#!/usr/bin/env python3
"""Generates the profile README's SVG assets (no dependencies).

    python3 assets/src/build_assets.py

Writes assets/banner-light.svg, assets/banner-dark.svg and assets/icon-*.svg.
Edit the palette or geometry here and re-run; do not hand-edit the outputs.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# Colours follow GitHub's light and dark canvases so the banner sits flush.
THEMES = {
    "light": dict(bg="#ffffff", border="#d0d7de", text="#1f2328", muted="#59636e",
                  wall="#e6eaef", dot="#c8d1da", accent="#bf8700", label="#9a6700", edge="#afb8c1"),
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", muted="#9198a1",
                 wall="#1c2129", dot="#30363d", accent="#d29922", label="#d29922", edge="#3d444d"),
}

# ---------------------------------------------------------------- banner
W, H = 1280, 320
GX, GY, PITCH, COLS, ROWS = 652, 46, 22, 18, 10

# Shortest path through the grid (col, row), leaving on the right edge.
PATH = [(0, 8)]
for dc, dr, n in [(1, 0, 4), (0, -1, 5), (1, 0, 5), (0, 1, 3), (1, 0, 5), (0, -1, 4), (1, 0, 3)]:
    for _ in range(n):
        c, r = PATH[-1]
        PATH.append((c + dc, r + dr))
ON_PATH = set(PATH)

# Network graph the path continues into.
NODES = {"a": (1104, 107), "b": (1166, 64), "c": (1158, 178), "d": (1232, 118),
         "e": (1104, 246), "f": (1214, 252)}
EDGES = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("c", "e"), ("e", "f"), ("d", "f"), ("c", "f")]
ROUTE = [("a", "b"), ("b", "d")]
FAILED = ("a", "c")  # a down link, drawn dashed


def walls():
    """Deterministic ~24% wall pattern that never touches the path."""
    x, out = 2027, set()
    for r in range(ROWS):
        for c in range(COLS):
            x = (x * 1103515245 + 12345) % (1 << 31)
            if (c, r) not in ON_PATH and x % 100 < 24:
                out.add((c, r))
    return out


def centre(c, r):
    return GX + c * PITCH + PITCH / 2, GY + r * PITCH + PITCH / 2


def banner(t):
    wl = walls()
    explored = {(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in wl and (c, r) not in ON_PATH
                and min(abs(c - pc) + abs(r - pr) for pc, pr in PATH) <= 2}
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'role="img" aria-labelledby="t d">')
    a('<title id="t">Nitin Upadhyay</title>')
    a('<desc id="d">Systems, backend and infrastructure engineering. A shortest path crosses a search '
      'grid and continues as a route through a small network graph.</desc>')
    a(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    # text block
    a(f'<text x="64" y="104" font-family="{MONO}" font-size="18" letter-spacing="2.5" fill="{t["label"]}">'
      'SYSTEMS · BACKEND · INFRASTRUCTURE</text>')
    a(f'<text x="62" y="172" font-family="{SANS}" font-size="60" font-weight="700" fill="{t["text"]}">'
      'Nitin Upadhyay</text>')
    a(f'<text font-family="{SANS}" font-size="23" fill="{t["muted"]}">'
      '<tspan x="64" y="218">C++ and Python on Linux.</tspan>'
      '<tspan x="64" y="250">Performance, correctness, practical engineering.</tspan></text>')
    a(f'<text x="64" y="286" font-family="{MONO}" font-size="19" fill="{t["muted"]}">CS student · class of 2027</text>')
    # grid
    a('<g>')
    for r in range(ROWS):
        for c in range(COLS):
            x, y = GX + c * PITCH, GY + r * PITCH
            if (c, r) in wl:
                a(f'<rect x="{x+3}" y="{y+3}" width="16" height="16" rx="3" fill="{t["wall"]}"/>')
            elif (c, r) in explored:
                a(f'<rect x="{x+5}" y="{y+5}" width="12" height="12" rx="2.5" fill="{t["accent"]}" fill-opacity=".13"/>')
            elif (c, r) not in ON_PATH:
                cx, cy = centre(c, r)
                a(f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="{t["dot"]}"/>')
    a('</g>')
    # graph edges
    for u, v in EDGES:
        (x1, y1), (x2, y2) = NODES[u], NODES[v]
        if (u, v) in ROUTE:
            continue
        dash = ' stroke-dasharray="5 6"' if (u, v) == FAILED else ""
        a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["edge"]}" stroke-width="2"{dash}/>')
    # route: grid path, exit, then graph hops
    pts = [centre(c, r) for c, r in PATH] + [NODES["a"], NODES["b"], NODES["d"]]
    a(f'<polyline points="{" ".join(f"{x:g},{y:g}" for x, y in pts)}" fill="none" stroke="{t["accent"]}" '
      'stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>')
    sx, sy = centre(*PATH[0])
    a(f'<circle cx="{sx:g}" cy="{sy:g}" r="6" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="3"/>')
    for k, (x, y) in NODES.items():
        on = k in ("a", "b", "d")
        fill = t["accent"] if k == "d" else t["bg"]
        a(f'<circle cx="{x}" cy="{y}" r="8" fill="{fill}" stroke="{t["accent"] if on else t["edge"]}" stroke-width="2.5"/>')
    a('</svg>')
    return "".join(p)


# ---------------------------------------------------------------- icons
# Mid-tone colours readable on both GitHub canvases, so one file per icon.
G, A = "#8c959f", "#d29922"


def icon(title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img">'
            f'<title>{title}</title>{body}</svg>')


ICONS = {
    "pathfinding": icon("Grid search", "".join(
        f'<rect x="{6+c*13}" y="{6+r*13}" width="10" height="10" rx="2" fill="{G}" fill-opacity="{.55 if (c, r) in {(1, 0), (1, 1)} else .18}"/>'
        for r in range(3) for c in range(3))
        + f'<polyline points="11,37 11,24 24,24 24,24 37,24 37,11" fill="none" stroke="{A}" stroke-width="3" '
          'stroke-linejoin="round" stroke-linecap="round" transform="translate(0,0)"/>'
        + f'<circle cx="11" cy="37" r="3.5" fill="{A}"/><circle cx="37" cy="11" r="3.5" fill="{A}"/>'),
    "orderbridge": icon("Message to reviewed order", (
        f'<rect x="4" y="9" width="17" height="14" rx="3" fill="none" stroke="{G}" stroke-width="2.2"/>'
        f'<path d="M8 23v5l5-5" fill="none" stroke="{G}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<path d="M8 14h9M8 18h6" stroke="{G}" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M23 21h6" stroke="{A}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<path d="M27 17l4 4-4 4" fill="none" stroke="{A}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="31" y="11" width="14" height="27" rx="3" fill="none" stroke="{G}" stroke-width="2.2"/>'
        f'<path d="M34.5 25l2.8 2.8 4.7-5.6" fill="none" stroke="{A}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')),
    "routesage": icon("Network graph with a failed link", (
        f'<line x1="9" y1="24" x2="24" y2="9" stroke="{A}" stroke-width="2.5"/>'
        f'<line x1="24" y1="9" x2="39" y2="24" stroke="{A}" stroke-width="2.5"/>'
        f'<line x1="9" y1="24" x2="24" y2="39" stroke="{G}" stroke-width="2.2" stroke-dasharray="3 3.5"/>'
        f'<line x1="24" y1="39" x2="39" y2="24" stroke="{G}" stroke-width="2.2"/>'
        f'<line x1="24" y1="9" x2="24" y2="39" stroke="{G}" stroke-width="2.2"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="{A if (x, y) != (24, 39) else G}" stroke-width="2.5"/>'
                  for x, y in [(9, 24), (24, 9), (39, 24), (24, 39)]))),
    "chainsense": icon("Merkle tree with an inclusion proof", (
        f'<path d="M24 11L13 24M24 11L35 24M13 24L7 37M13 24L19 37M35 24L29 37M35 24L41 37" stroke="{G}" stroke-width="2"/>'
        f'<path d="M24 11L13 24L19 37" fill="none" stroke="{A}" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<rect x="19" y="6" width="10" height="10" rx="2" fill="{A}"/>'
        + "".join(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" rx="1.8" fill="{A if (x, y) in {(13, 24), (19, 37)} else "none"}" '
                  f'stroke="{A if (x, y) in {(13, 24), (19, 37)} else G}" stroke-width="2"/>'
                  for x, y in [(13, 24), (35, 24), (7, 37), (19, 37), (29, 37), (41, 37)]))),
}


def main():
    for name, theme in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(banner(theme) + "\n", encoding="utf-8")
    for name, svg in ICONS.items():
        (OUT / f"icon-{name}.svg").write_text(svg + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
