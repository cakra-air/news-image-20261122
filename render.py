"""Draw the Sunday 22 November 2026 front page.

Single source of truth: the layout specification in the brief.  Everything is
Pillow primitives; the only external asset is world110.geojson.
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

from stories import STORIES, DATE_CHECK, SOURCES_LINE, REGIONS, REGION_COLORS

W = H = 1024

PAPER = "#F7F2E7"
INK = "#181818"
RED = "#9E1F1F"
LINE = "#CBBB9C"
MUTED = "#6C6459"
CARD = "#FDFBF4"
PANEL = "#FFFDF7"
BUTTON = "#F6F0E2"
OCEAN = "#D8E8F1"
LAND = "#EADCB9"
COAST = "#B8A175"
GRAT = "#C6DEEA"

FONT_DIR = r"C:\Windows\Fonts"

# Vertical rhythm: a compact masthead buys room for the index lists.
BAR_H = 20
TITLE_Y = 52
DECK_Y = 92
RULE_Y = 104
STAT_LINE_TOP, STAT_LINE_BOT = 109, 150
STAT_BIG_Y, STAT_SMALL_Y = 124, 142
REG_Y0, REG_Y1 = 155, 173
MAIN_Y, MAIN_H = 182, 188
SMALL_Y0, SMALL_H, SMALL_STEP = 374, 140, 143
PANEL_Y0, PANEL_Y1 = 661, 970
PANEL_RULE_Y = 683
MAP_FRAME = (316, 689, 708, 962)
PLOT = (324, 697, 700, 940)
LEGEND_Y = 952

# Filled during map_panel() so audit.py can check the invariants exactly.
MAP_PLACEMENTS = []   # (n, dot_x, dot_y, badge_x, badge_y)
MAP_BRIEF_DOTS = []   # (n, dot_x, dot_y, colour)


def font(px, bold=False, serif=False):
    if serif:
        name = "georgiab.ttf" if bold else "georgia.ttf"
    else:
        name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), px)


def rgb(value):
    h = value.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def put(d, xy, text, fnt, fill=INK, anchor=None):
    d.text(xy, text, font=fnt, fill=rgb(fill) if isinstance(fill, str) else fill,
           anchor=anchor)


def wrap(text, fnt, maxw, d):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def number_badge(d, cx, cy, n, colour, r=6, fsize=8, width=2):
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=rgb(colour), outline=(255, 255, 255), width=width)
    put(d, (cx, cy), str(n), font(fsize, True), "#FFFFFF", anchor="mm")


def square_badge(d, x0, y0, x1, y1, n, colour, fsize=9):
    """Rounded-square number badge at the LEFT end of a strip (frame.md)."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=3,
                        fill=rgb(colour), outline=(255, 255, 255), width=1)
    put(d, ((x0 + x1) / 2, (y0 + y1) / 2), str(n),
        font(fsize, True), "#FFFFFF", anchor="mm")


def chip(d, x, y, text, fill="#E7DFCC", fsize=8):
    f = font(fsize, True)
    w = d.textlength(text, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=3,
                        fill=rgb(fill), outline=rgb(LINE), width=1)
    put(d, (x + 5, y + 6.5), text, f, INK, anchor="lm")


# ---------------------------------------------------------------------------
# illustrations: every scene carries a place tag and a time/event tag
# ---------------------------------------------------------------------------
DARK_SCENES = {"cop", "hormuz", "dymer", "shipdrone", "benghazi", "f1"}


PAGE = None
GEO = None


def real_map(box, lat0, lat1, lon0, lon1, graticule=2):
    """Paste a correctly projected crop of world110.geojson into box."""
    global GEO, PAGE
    x0, y0, x1, y1 = box
    w, h = max(2, int(x1 - x0)), max(2, int(y1 - y0))
    if GEO is None:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "world110.geojson"), encoding="utf-8") as fh:
            GEO = json.load(fh)
    tile = Image.new("RGB", (w, h), rgb(OCEAN))
    dd = ImageDraw.Draw(tile)

    def px(lon): return (lon - lon0) / (lon1 - lon0) * w
    def py(lat): return (lat1 - lat) / (lat1 - lat0) * h

    g = math.ceil(lon0 / graticule) * graticule
    while g <= lon1:
        dd.line([px(g), 0, px(g), h], fill=rgb(GRAT), width=1)
        g += graticule
    g = math.ceil(lat0 / graticule) * graticule
    while g <= lat1:
        dd.line([0, py(g), w, py(g)], fill=rgb(GRAT), width=1)
        g += graticule
    for feat in GEO["features"]:
        geo = feat.get("geometry") or {}
        polys = geo.get("coordinates") or []
        if geo.get("type") == "Polygon":
            polys = [polys]
        for poly in polys:
            for ring in poly:
                pts = [(px(c[0]), py(c[1])) for c in ring if len(c) >= 2]
                if len(pts) < 3:
                    continue
                if (max(p[0] for p in pts) < 0 or min(p[0] for p in pts) > w or
                        max(p[1] for p in pts) < 0 or min(p[1] for p in pts) > h):
                    continue
                dd.polygon(pts, fill=rgb(LAND))
                dd.line(pts + [pts[0]], fill=rgb(COAST), width=1)
    PAGE.paste(tile, (int(x0), int(y0)))

    def proj(latv, lonv):
        return (x0 + px(lonv), y0 + py(latv))
    return proj


def mix(a, b, t):
    if isinstance(a, str):
        a = rgb(a)
    if isinstance(b, str):
        b = rgb(b)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def detail_figure(d, x, y, h, coat, skin="#C99564", helmet=None):
    w = h * 0.42
    d.ellipse([x - w / 2, y - h, x + w / 2, y - h + w], fill=rgb(skin))
    if helmet:
        d.ellipse([x - w * 0.6, y - h - w * 0.2, x + w * 0.6, y - h + w * 0.45],
                  fill=rgb(helmet))
    d.rectangle([x - w * 0.42, y - h + w, x + w * 0.42, y - h * 0.28], fill=rgb(coat))
    d.line([x - w * 0.42, y - h * 0.8, x - w * 0.7, y - h * 0.35],
           fill=rgb(coat), width=max(2, int(h * 0.12)))
    d.line([x + w * 0.42, y - h * 0.8, x + w * 0.7, y - h * 0.35],
           fill=rgb(coat), width=max(2, int(h * 0.12)))
    d.line([x - w * 0.16, y - h * 0.28, x - w * 0.22, y], fill="#27313E",
           width=max(2, int(h * 0.1)))
    d.line([x + w * 0.16, y - h * 0.28, x + w * 0.22, y], fill="#27313E",
           width=max(2, int(h * 0.1)))


def ship_icon(d, x, y, sc, color="#AAB7C1"):
    d.polygon([(x - 1.7 * sc, y), (x + 1.7 * sc, y),
               (x + 1.3 * sc, y + 0.65 * sc), (x - 1.3 * sc, y + 0.65 * sc)],
              fill=rgb(color), outline="#4A5864")
    d.rectangle([x - 0.9 * sc, y - 0.55 * sc, x + 0.6 * sc, y],
                fill="#D5DEE5", outline="#6C7A86")
    d.rectangle([x - 0.2 * sc, y - 0.95 * sc, x + 0.12 * sc, y - 0.55 * sc],
                fill="#93A2AD")


def burst(d, x, y, r, color="#E26B1D"):
    for a in range(8):
        ang = 2 * math.pi * a / 8
        d.line([x, y, x + r * math.cos(ang), y + r * math.sin(ang)],
               fill=rgb(color), width=2)
    d.ellipse([x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35],
              fill="#F2C14E")


def tag(d, x, y, text, fill="#181818", fsize=8):
    """One compact location badge per illustration, top-left."""
    f = font(fsize, True)
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x - 4, y - 2, x + w + 4, y + fsize + 5],
                        radius=2, fill=rgb(fill))
    put(d, (x, y), text, f, "#FFFFFF")


def scene(d, box, s):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    col = rgb(REGION_COLORS[s["region"]])
    k = s["scene"]

    def P(fx, fy):
        return (x0 + fx * bw, y0 + fy * bh)

    def ln(a, b, fill, width=2):
        d.line([P(*a), P(*b)], fill=fill, width=width)

    def bx(a, b, fill=None, outline=None, width=1):
        d.rectangle([P(*a), P(*b)], fill=fill, outline=outline, width=width)

    def el(a, b, fill=None, outline=None, width=1):
        d.ellipse([P(*a), P(*b)], fill=fill, outline=outline, width=width)

    def poly(points, fill, outline=None):
        d.polygon([P(*p) for p in points], fill=fill)
        if outline:
            d.line([P(*p) for p in points + [points[0]]], fill=outline, width=1)

    def grad(top, bottom, steps=9):
        for i in range(steps):
            bx((0, i / steps), (1, (i + 1) / steps),
               fill=mix(top, bottom, i / (steps - 1)))

    if k == "cop":
        grad("#22334A", "#43536B")
        bx((0.05, 0.60), (0.95, 0.74), fill="#7A6146")
        coats = ["#3E5A7A", "#7A4A4A", "#4C6B57", "#6A5A3E", "#3E5A7A", "#7A4A4A"]
        for i, fx in enumerate((0.10, 0.22, 0.34, 0.46, 0.58, 0.70)):
            el((fx, 0.34), (fx + 0.06, 0.42), fill="#C99564")
            poly([(fx + 0.01, 0.42), (fx + 0.05, 0.42), (fx + 0.08, 0.60),
                  (fx - 0.02, 0.60)], fill=coats[i])
        bx((0.76, 0.12), (0.96, 0.56), fill="#FFFDF5", outline=rgb(LINE))
        for j in range(4):
            ln((0.79, 0.20 + j * 0.07), (0.93, 0.20 + j * 0.07), "#9B9B9B", 1)
        bx((0.76, 0.42), (0.96, 0.56), fill=rgb(RED))
        put(d, P(0.86, 0.45), "NO DEAL", font(7, True), "#FFFFFF", anchor="mm")

    elif k == "hormuz":
        grad("#1E3046", "#5C7185")
        for yy in (0.42, 0.56, 0.70):
            ln((0.02, yy), (0.98, yy), "#3E5E78", 1)
        for fx in (0.18, 0.46, 0.70):
            px, py = P(fx, 0.50)
            ship_icon(d, px, py, 10)
            ax, ay = P(fx + 0.04, 0.40)
            burst(d, ax, ay, 4)
        poly([(0, 0), (0.14, 0), (0.09, 0.30), (0, 0.40)], fill="#C9B98F")
        poly([(0.88, 0.70), (1, 0.58), (1, 1), (0.82, 1)], fill="#C9B98F")

    elif k == "dymer":
        grad("#44566B", "#A6ADAD")
        ln((0, 0.84), (1, 0.84), "#6D6759", 2)
        bx((0.10, 0.28), (0.52, 0.84), fill="#5E6876", outline="#343C48")
        for yy in (0.38, 0.52, 0.66):
            ln((0.10, yy), (0.52, yy), "#4A5361", 1)
            for xx in (0.14, 0.26, 0.38):
                bx((xx, yy + 0.02), (xx + 0.05, yy + 0.06), fill="#E4D49A")
        poly([(0.52, 0.48), (0.70, 0.60), (0.60, 0.84), (0.48, 0.84)], fill="#817B70")
        poly([(0, 0.84), (0.30, 0.70), (0.62, 0.84)], fill="#8B8579")
        for fx in (0.62, 0.78):
            px, py = P(fx, 0.84)
            detail_figure(d, px, py, 38, "#D9A23B", helmet="#F2C14E")

    elif k == "shipdrone":
        grad("#1B2C42", "#3D5A72")
        for yy in (0.52, 0.64, 0.76, 0.88):
            ln((0.02, yy), (0.98, yy), "#4E6E88", 1)
        px, py = P(0.38, 0.68)
        ship_icon(d, px, py, 15)
        ax, ay = P(0.46, 0.44)
        burst(d, ax, ay, 5)
        cx, cy = P(0.80, 0.28)
        for ox, oy in ((-9, -5), (9, -5), (-9, 5), (9, 5)):
            el((cx + ox - 3, cy + oy - 2), (cx + ox + 3, cy + oy + 2), fill="#D5DEE5")
        d.line([cx - 9, cy - 5, cx + 9, cy + 5], fill="#D5DEE5", width=1)
        d.line([cx + 9, cy - 5, cx - 9, cy + 5], fill="#D5DEE5", width=1)

    elif k == "poland":
        grad("#DCE7EC", "#F2ECDD")
        pts = [(0.24, 0.28), (0.38, 0.20), (0.54, 0.18), (0.68, 0.24),
               (0.76, 0.36), (0.72, 0.52), (0.60, 0.62), (0.50, 0.76),
               (0.38, 0.68), (0.28, 0.56), (0.20, 0.42)]
        poly(pts, fill=rgb(LAND), outline=rgb(COAST))
        for fx, fy in ((0.44, 0.40), (0.62, 0.52)):
            ax, ay = P(fx, fy)
            burst(d, ax, ay, 5)

    elif k == "westbank":
        grad("#33455A", "#7B7C72")
        poly([(0, 0.76), (0.30, 0.62), (0.62, 0.72), (1, 0.60), (1, 1), (0, 1)],
             fill="#6F7455")
        for i, fx in enumerate((0.30, 0.46, 0.62, 0.78)):
            bx((fx, 0.50), (fx + 0.11, 0.74), fill="#E4D8BC", outline="#8A7550")
            poly([(fx - 0.01, 0.50), (fx + 0.055, 0.40), (fx + 0.12, 0.50)], fill="#A66B3F")
            if i in (1, 3):
                poly([(fx + 0.03, 0.42), (fx + 0.055, 0.30), (fx + 0.09, 0.42)],
                     fill="#E26B1D")

    elif k == "benghazi":
        grad("#2B3A4C", "#8A8A82")
        ln((0, 0.74), (1, 0.74), "#7C7568", 2)
        px, py = P(0.42, 0.70)
        ship_icon(d, px, py, 3.2)
        ax, ay = P(0.50, 0.46)
        burst(d, ax, ay, 7)
        bx((0.80, 0.24), (0.84, 0.64), fill="#8A95A0")
        ln((0.82, 0.26), (0.64, 0.26), "#8A95A0", 2)

    elif k == "ice":
        grad("#DCE5EC", "#F3EFE3")
        d.rounded_rectangle([P(0.62, 0.24), P(1.02, 0.78)], radius=9,
                            fill="#D2DCE4", outline="#8493A0")
        bx((0.12, 0.38), (0.70, 0.60), fill="#BCC9C0", outline="#6F7F75")
        for fx in (0.30, 0.44):
            px, py = P(fx, 0.84)
            detail_figure(d, px, py, 45, "#E8B84B")
        px, py = P(0.78, 0.86)
        detail_figure(d, px, py, 50, "#2E3A46")

    elif k == "tariff":
        grad("#DCE5EC", "#F3EFE3")
        for i in range(4):
            fx = 0.10 + i * 0.16
            bx((fx, 0.48), (fx + 0.12, 0.78), fill="#6E7E8C", outline="#4C5A66")
        bx((0.62, 0.22), (0.96, 0.60), fill="#FFFDF5", outline=rgb(LINE))
        bx((0.68, 0.42), (0.78, 0.54), fill="#8A9AA6")
        bx((0.82, 0.32), (0.92, 0.54), fill="#B9C6CE")
        d.line([P(0.68, 0.34), P(0.92, 0.46)], fill=rgb(RED), width=3)

    elif k == "f1":
        grad("#121A2A", "#3A2C4E")
        for i in range(12):
            bx((i / 12, 0.36 + (i % 3) * 0.06), ((i + 0.7) / 12, 0.66), fill="#1C2940")
        poly([(0.10, 0.62), (0.20, 0.50), (0.36, 0.48), (0.50, 0.42),
              (0.68, 0.44), (0.80, 0.54), (0.88, 0.56), (0.88, 0.62),
              (0.68, 0.66), (0.24, 0.66)], fill=rgb(RED), outline="#5E1A1A")
        for fx in (0.26, 0.68):
            el((fx, 0.60), (fx + 0.10, 0.72), fill="#171717", outline="#3A3A3A")
        bx((0.78, 0.10), (0.96, 0.34), fill="#FFFFFF", outline="#9B9B9B")
        for ry in range(3):
            for rx in range(3):
                if (rx + ry) % 2 == 0:
                    bx((0.78 + rx * 0.06, 0.10 + ry * 0.08),
                       (0.84 + rx * 0.06, 0.18 + ry * 0.08), fill="#202020")

    elif k == "flags_jp_in":
        grad("#DFE8EF", "#F3EFE3")
        bx((0.06, 0.20), (0.38, 0.54), fill="#FFFFFF", outline="#9B9B9B")
        el((0.18, 0.30), (0.26, 0.38), fill=rgb(RED))
        bx((0.60, 0.20), (0.92, 0.54), fill="#FFFFFF", outline="#9B9B9B")
        bx((0.60, 0.20), (0.92, 0.31), fill="#FF9933")
        bx((0.60, 0.43), (0.92, 0.54), fill="#138808")
        el((0.72, 0.33), (0.80, 0.41), outline="#000088", width=1)
        for i, fx in enumerate((0.34, 0.64)):
            px, py = P(fx, 0.88)
            detail_figure(d, px, py, 45,
                          "#2E3A46" if i == 0 else "#4A5A6E")

    else:
        el((0.34, 0.30), (0.66, 0.62), outline=col, width=2)

    tag(d, x0 + 5, y0 + 4, s["place"], "#181818", 7)



def map_panel(d):
    MAP_PLACEMENTS.clear()
    MAP_BRIEF_DOTS.clear()

    mx0, my0, mx1, my1 = PLOT
    d.rectangle([mx0, my0, mx1, my1], fill=rgb(OCEAN))

    LAT_TOP, LAT_BOT = 83.0, -58.0

    def px(lon):
        return mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)

    def py(lat):
        return my0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (my1 - my0)

    for lon in range(-180, 181, 30):
        d.line([px(lon), my0, px(lon), my1], fill=rgb(GRAT), width=1)
    for lat in range(-60, 90, 30):
        d.line([mx0, py(lat), mx1, py(lat)], fill=rgb(GRAT), width=1)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world110.geojson")
    with open(path, encoding="utf-8") as fh:
        geo = json.load(fh)
    for feat in geo["features"]:
        g = feat.get("geometry") or {}
        polys = g.get("coordinates") or []
        if g.get("type") == "Polygon":
            polys = [polys]
        for poly in polys:
            for ring in poly:
                pts = [(px(c[0]), py(c[1])) for c in ring if len(c) >= 2]
                if len(pts) < 3:
                    continue
                if sum(p[1] for p in pts) / len(pts) > my1 - 4:
                    continue
                d.polygon(pts, fill=rgb(LAND))
                d.line(pts + [pts[0]], fill=rgb(COAST), width=1, joint="curve")

    for s in STORIES:
        dx, dy = px(s["lon"]), py(s["lat"])
        col = REGION_COLORS[s["region"]]
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3],
                  fill=rgb(col), outline=(255, 255, 255), width=1)
        if s["size"] == "brief":
            MAP_BRIEF_DOTS.append((s["n"], dx, dy, col))

    placed = []
    for s in STORIES:
        if s["size"] == "brief":
            continue
        dx, dy = px(s["lon"]), py(s["lat"])
        col = REGION_COLORS[s["region"]]
        got = None
        for r in (0, 14, 24, 34, 42):
            for k in range(16):
                ang = 2 * math.pi * k / 16
                bx, by = dx + r * math.cos(ang), dy + r * math.sin(ang)
                if not (mx0 + 8 < bx < mx1 - 8 and my0 + 8 < by < my1 - 8):
                    continue
                if all(math.hypot(bx - qx, by - qy) >= 2 * 6 + 3 for qx, qy in placed):
                    got = (bx, by)
                    break
            if got:
                break
        if got is None:
            got = (dx, dy)
        bx, by = got
        if math.hypot(bx - dx, by - dy) > 4:
            d.line([dx, dy, bx, by], fill=rgb(col), width=1)
            ang = math.atan2(by - dy, bx - dx)
            ax, ay = bx - 7 * math.cos(ang), by - 7 * math.sin(ang)
            d.line([ax, ay, bx, by], fill=rgb(col), width=2)
            d.polygon([(bx, by),
                       (ax + 3 * math.sin(ang), ay - 3 * math.cos(ang)),
                       (ax - 3 * math.sin(ang), ay + 3 * math.cos(ang))], fill=rgb(col))
        placed.append((bx, by))
        MAP_PLACEMENTS.append((s["n"], dx, dy, bx, by))
        number_badge(d, bx, by, s["n"], col, r=6, fsize=9, width=2)

    ly = LEGEND_Y
    f = font(6.5)
    labels = [f"{reg} {sum(1 for s in STORIES if s['region'] == reg)}"
              for reg in REGIONS]
    widths = [d.textlength(label, font=f) for label in labels]
    lx = mx0 + (mx1 - mx0 - sum(17 + w for w in widths)) / 2
    for reg, label, w in zip(REGIONS, labels, widths):
        d.ellipse([lx, ly, lx + 7, ly + 7], fill=rgb(REGION_COLORS[reg]))
        put(d, (lx + 10, ly + 3.5), label, f, INK, anchor="lm")
        lx += 17 + w


def redraw_map_marks(d):
    """Repaint dots and numbered badges above the index connector lines."""
    by_n = {s["n"]: s for s in STORIES}
    for n, dx, dy, col in MAP_BRIEF_DOTS:
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3],
                  fill=rgb(col), outline=(255, 255, 255), width=1)
    for n, dx, dy, bx, by in MAP_PLACEMENTS:
        col = REGION_COLORS[by_n[n]["region"]]
        number_badge(d, bx, by, n, col, r=6, fsize=9, width=2)


def list_panel(d, box, items):
    x0, y0, x1, y1 = box
    top = y0 + 31
    step = (y1 - top - 6) // len(items)

    def row_y(i):
        return top + i * step

    badge_x = x0 + 20
    text_x = x0 + 40
    edge = (x1 - 6) if x1 < 512 else (x0 + 6)
    dot_by_n = {n: (dx, dy, col) for n, dx, dy, col in MAP_BRIEF_DOTS}
    f = font(8)

    for i, s in enumerate(items):
        dot = dot_by_n.get(s["n"])
        if not dot:
            continue
        dx, dy, col = dot
        r, g, b = rgb(col)
        faint = (int(r + (255 - r) * 0.62),
                 int(g + (255 - g) * 0.62),
                 int(b + (255 - b) * 0.62))
        d.line([dx, dy, edge, row_y(i) + 7], fill=faint, width=1)

    for i, _s in enumerate(items):
        cy = row_y(i)
        d.rounded_rectangle([x0 + 6, cy - 3, x1 - 6, cy + step - 4], radius=3,
                            fill=rgb(BUTTON), outline=rgb(LINE), width=1)

    for i, s in enumerate(items):
        cy = row_y(i)
        col = REGION_COLORS[s["region"]]
        d.rounded_rectangle([badge_x - 10, cy - 2, badge_x + 10, cy + 16], radius=3,
                            fill=rgb(col), outline=(255, 255, 255), width=1)
        put(d, (badge_x, cy + 7), str(s["n"]), font(9, True), "#FFFFFF", anchor="mm")
        for j, line in enumerate(wrap(s["brief"], f, (x1 - 10) - text_x - 76, d)[:2]):
            put(d, (text_x, cy - 3 + j * 9), line, f, INK)
        put(d, (x1 - 10, cy + 7), s["source"], font(6.5), MUTED, anchor="rm")


# ---------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------
def build(out="entry.png"):
    global PAGE
    im = Image.new("RGB", (W, H), rgb(PAPER))
    PAGE = im
    d = ImageDraw.Draw(im)

    d.rectangle([0, 0, 1024, BAR_H], fill=rgb(RED))
    put(d, (12, BAR_H / 2), "THE WORLD IN ONE DAY",
        font(9, True), "#FFFFFF", anchor="lm")
    put(d, (512, BAR_H / 2), "SUNDAY 22 NOV 2026 · WEEK 47 · Q4 · UTC",
        font(9, True), "#FFFFFF", anchor="mm")
    put(d, (1012, BAR_H / 2), f"{len(STORIES)} STORIES · {len(REGIONS)} REGIONS",
        font(9, True), "#FFFFFF", anchor="rm")
    put(d, (512, TITLE_Y), "Sunday 22 November 2026",
        font(52, True, True), INK, anchor="mm")
    put(d, (512, DECK_Y),
        "COP31 ends in collapse · Iran strikes tankers · Russian drone hits flats near Kyiv",
        font(13, False, True), MUTED, anchor="mm")
    d.line([12, RULE_Y, 1012, RULE_Y], fill=rgb(LINE), width=1)

    stats = [("44H", "COP31 overtime, then collapse"),
             ("3", "tankers hit near Hormuz"),
             ("14", "missing in Dymer, Ukraine"),
             ("4", "West Bank villages attacked"),
             ("186", "drones launched at Ukraine"),
             ("720/9", "India's first-Test total"),
             ("3rd", "Vegas win for Verstappen")]
    sw = 142
    for i, (big, small) in enumerate(stats):
        sx = 12 + i * sw
        d.line([sx, STAT_LINE_TOP, sx, STAT_LINE_BOT], fill=rgb(LINE), width=1)
        put(d, (sx + 71, STAT_BIG_Y), big, font(26, True, True), RED, anchor="mm")
        put(d, (sx + 71, STAT_SMALL_Y), small, font(7), INK, anchor="mm")

    counts = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGIONS}
    for i, r in enumerate(REGIONS):
        bx = 12 + i * 142
        d.rectangle([bx, REG_Y0, bx + 140, REG_Y1], fill=rgb(REGION_COLORS[r]))
        put(d, (bx + 6, (REG_Y0 + REG_Y1) / 2), f"{r} · {counts[r]}",
            font(9, True), "#FFFFFF", anchor="lm")

    for i, s in enumerate([x for x in STORIES if x["size"] == "main"][:3]):
        x, y = 12 + i * 336, MAIN_Y
        d.rectangle([x, y, x + 326, y + MAIN_H], fill=rgb(CARD), outline=rgb(LINE))
        scene(d, (x + 3, y + 3, x + 323, y + 68), s)
        d.rectangle([x + 3, y + 70, x + 323, y + 84],
                    fill=rgb(REGION_COLORS[s["region"]]))
        square_badge(d, x + 7, y + 70, x + 21, y + 84, s["n"],
                     REGION_COLORS[s["region"]])
        put(d, (x + 26, y + 79), s["kicker"], font(9, True), "#FFFFFF", anchor="lm")
        put(d, (x + 315, y + 79), s["source"], font(7), "#FFFFFF", anchor="rm")
        head = font(15, True, True)
        for j, line in enumerate(wrap(s["headline"], head, 326 - 14, d)[:2]):
            put(d, (x + 7, y + 88 + j * 17), line, head, INK)
        for j, line in enumerate(wrap(s["body"], font(9), 300, d)[:7]):
            put(d, (x + 7, y + 122 + j * 9), line, font(9), INK)

    for i, s in enumerate([x for x in STORIES if x["size"] == "small"][:8]):
        row, col = divmod(i, 4)
        x, y = 12 + col * 252, SMALL_Y0 + row * SMALL_STEP
        d.rectangle([x, y, x + 244, y + SMALL_H], fill=rgb(CARD), outline=rgb(LINE))
        scene(d, (x + 3, y + 4, x + 241, y + 54), s)
        d.rectangle([x + 3, y + 56, x + 241, y + 70],
                    fill=rgb(REGION_COLORS[s["region"]]))
        square_badge(d, x + 7, y + 56, x + 21, y + 70, s["n"],
                     REGION_COLORS[s["region"]])
        put(d, (x + 26, y + 63), s["kicker"], font(8, True), "#FFFFFF", anchor="lm")
        put(d, (x + 235, y + 63), s["source"], font(7), "#FFFFFF", anchor="rm")
        head = font(10, True, True)
        for j, line in enumerate(wrap(s["headline"], head, 244 - 12, d)[:2]):
            put(d, (x + 6, y + 74 + j * 10), line, head, INK)
        for j, line in enumerate(wrap(s["body"], font(7.5), 232, d)[:5]):
            put(d, (x + 6, y + 94 + j * 9), line, font(7.5), INK)

    d.rounded_rectangle([12, PANEL_Y0, 1012, PANEL_Y1], radius=4,
                        fill=rgb(PANEL), outline=rgb(LINE), width=1)
    d.rectangle([20, PANEL_Y0 + 4, 94, PANEL_Y0 + 18], fill=rgb(RED))
    put(d, (57, PANEL_Y0 + 11), "INDEX", font(8, True), "#FFFFFF", anchor="mm")
    put(d, (102, PANEL_Y0 + 11),
        "WHERE IT HAPPENED · ALSO ON SUNDAY 22 NOVEMBER 2026 — 20 STORIES LINKED BY NUMBER",
        font(9, True), INK, anchor="lm")
    d.line([12, PANEL_RULE_Y, 1012, PANEL_RULE_Y], fill=rgb(LINE), width=1)
    d.rounded_rectangle(MAP_FRAME, radius=6, outline=rgb(LINE), width=1)

    map_panel(d)
    briefs = [s for s in STORIES if s["size"] == "brief"]
    left = [s for s in briefs if s["region"] in {"Europe", "Africa", "Americas"}]
    right = [s for s in briefs if s["region"] in {"Middle East", "Asia", "Oceania"}]
    list_panel(d, (12, PANEL_Y0, 312, PANEL_Y1), left)
    list_panel(d, (712, PANEL_Y0, 1012, PANEL_Y1), right)
    redraw_map_marks(d)

    d.rectangle([12, 974, 1012, 1002], fill="#FBF6EE", outline=rgb(RED), width=1)
    d.rectangle([18, 977, 68, 999], fill=rgb(RED))
    put(d, (43, 984), "DATE", font(7, True), "#FFFFFF", anchor="mm")
    put(d, (43, 994), "CHECK", font(7, True), "#FFFFFF", anchor="mm")
    put(d, (76, 978),
        "Every story happened, or was first reported, on Sunday 22 November 2026.",
        font(7.5), INK)
    put(d, (76, 990), DATE_CHECK, font(7.5), INK)
    put(d, (1012, 1011), SOURCES_LINE, font(8), INK, anchor="rm")

    im.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    build()
