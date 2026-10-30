"""Generates the SVG logo files. Run from the repo root:  python3 scripts/make_logo.py

Writes static/images/logo.svg, static/images/logo-mark.svg and static/favicon.svg.
The text is converted to paths with the self-hosted Lato. Needs: pip install fonttools brotli

PNG icons and the social image, rendered from the SVGs with ImageMagick:
  convert -background none -density 300 static/favicon.svg -resize 32x32 -strip static/favicon-32.png
  convert -background white -density 600 static/images/logo-mark.svg -resize 150x150 \\
    -gravity center -extent 180x180 -strip static/apple-touch-icon.png
  convert -background white -density 400 static/images/logo.svg -resize x500 \\
    -gravity center -extent 1200x630 -strip -quality 88 static/images/og-image.jpg
"""
import math

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = "static/fonts"
DARK, GREEN, CHIP, LIGHT, INK = "#10412a", "#1d5c3a", "#2b7049", "#86b783", "#5e8063"


def r(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- mark
def mark(pins=5, detailed=True):
    """Chip with traces on 4 sides, in a 100x100 box. Returns SVG elements."""
    c0, c1 = 34, 66                       # chip body
    sw = 2.2 if detailed else 4.2         # trace width
    dot = 2.4 if detailed else 4.2
    gap = (c1 - c0 - 8) / (pins - 1)
    xs = [c0 + 4 + i * gap for i in range(pins)]
    lengths = [16, 22, 26, 22, 16] if pins == 5 else [18, 24, 18]
    side = []
    for i, x in enumerate(xs):
        off = x - 50
        y0 = c0
        y1 = y0 - 6                       # straight out of the pin
        L = lengths[i]
        dx = math.copysign(min(abs(off) * 0.9, 9), off) if off else 0
        y2 = y1 - abs(dx)                 # 45° bend
        x2 = x + dx
        y3 = max(y0 - L - abs(dx), 5)     # straight to the end
        col = LIGHT if (detailed and i % 2 == 1) else GREEN
        side.append(
            f'<path d="M{r(x)} {r(y0)}V{r(y1)}L{r(x2)} {r(y2)}V{r(y3 + dot)}" '
            f'fill="none" stroke="{GREEN}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{r(x2)}" cy="{r(y3)}" r="{dot}" fill="none" stroke="{col}" stroke-width="{sw}"/>'
        )
    side = "".join(side)
    els = [f'<g transform="rotate({a} 50 50)">{side}</g>' for a in (0, 90, 180, 270)]
    els.append(f'<rect x="{c0}" y="{c0}" width="{c1 - c0}" height="{c1 - c0}" rx="3" fill="{DARK}"/>')
    if detailed:
        els.append(f'<rect x="41" y="41" width="18" height="18" rx="1.5" fill="{CHIP}"/>')
        els.append(f'<circle cx="38.5" cy="38.5" r="1.4" fill="{LIGHT}"/>')
    else:
        els.append(f'<rect x="42" y="42" width="16" height="16" rx="1.5" fill="{CHIP}"/>')
    return "".join(els)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r(w)} {r(h)}" role="img">'
            f'<title>{title}</title>{body}</svg>\n')


# ---------------------------------------------------------------- text as paths
def text_path(text, weight, size, x, y, tracking=0, anchor="middle", fill=DARK):
    font = TTFont(f"{FONTS}/lato-{weight}-latin.woff2")
    upm = font["head"].unitsPerEm
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    s = size / upm
    names = [cmap[ord(ch)] for ch in text]
    adv = [hmtx[n][0] * s + tracking for n in names]
    width = sum(adv) - tracking
    cx = x - width / 2 if anchor == "middle" else x
    pen = SVGPathPen(gs, ntos=lambda v: r(v))
    for n, a in zip(names, adv):
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += a
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>', width


# full logo: mark above, three lines of text
W = 300
gps, _ = text_path("GPS", 900, 64, W / 2, 178, tracking=1)
elec, _ = text_path("ELECTRONICS", 700, 31, W / 2, 216, tracking=1.5, fill=GREEN)
tag, _ = text_path("DEVELOPMENT & INNOVATION", 400, 13.5, W / 2, 240, tracking=1.6, fill=INK)
full = f'<g transform="translate({r(W / 2 - 55)} 0) scale(1.1)">{mark()}</g>{gps}{elec}{tag}'

files = {
    "images/logo-mark.svg": svg(100, 100, mark(), "GPS Electronics"),
    "images/logo.svg": svg(W, 252, full, "GPS Electronics"),
    "favicon.svg": svg(100, 100, mark(pins=3, detailed=False), "GPS Electronics"),
}
for name, data in files.items():
    open(f"static/{name}", "w").write(data)
    print(name, len(data), "bytes")
