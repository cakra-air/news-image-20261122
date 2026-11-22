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
    """Paste a correctly projected crop of world110.geojson into box.
    Returns (lat, lon) -> page-space (x, y)."""
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


def detail_figure(d, x, y, h, coat, skin="#C99564", helmet=None, bag=None):
    """A small but anatomical figure: head, hair, face, coat, belt, limbs."""
    w = h * 0.42
    d.ellipse([x - w / 2, y - h, x + w / 2, y - h + w], fill=rgb(skin),
              outline="#7A5538", width=1)
    d.pieslice([x - w / 2, y - h - w * 0.1, x + w / 2, y - h + w * 0.6],
               180, 360, fill="#3A2A1E")
    if helmet:
        d.ellipse([x - w * 0.6, y - h - w * 0.2, x + w * 0.6, y - h + w * 0.45],
                  fill=rgb(helmet), outline="#5A4A20", width=1)
    ex = w * 0.16
    d.ellipse([x - w * 0.30, y - h + w * 0.42, x - w * 0.30 + 1.4,
               y - h + w * 0.42 + 1.4], fill="#1A1A1A")
    d.ellipse([x + w * 0.16, y - h + w * 0.42, x + w * 0.16 + 1.4,
               y - h + w * 0.42 + 1.4], fill="#1A1A1A")
    d.arc([x - w * 0.2, y - h + w * 0.45, x + w * 0.2, y - h + w * 0.85],
          15, 165, fill="#8A5A3A", width=1)
    d.polygon([(x - w * 0.22, y - h + w * 0.95), (x, y - h + w * 1.3),
               (x + w * 0.22, y - h + w * 0.95)], fill=mix(coat, "#FFFFFF", 0.35))
    d.rectangle([x - w * 0.45, y - h + w * 1.25, x + w * 0.45, y - h * 0.30],
                fill=rgb(coat), outline="#2E2E2E", width=1)
    d.rectangle([x - w * 0.45, y - h * 0.42, x + w * 0.45, y - h * 0.34], fill="#4A3A28")
    d.rectangle([x - w * 0.08, y - h + w * 1.3, x + w * 0.08, y - h * 0.36],
                fill=mix(coat, "#FFFFFF", 0.25))
    d.line([x - w * 0.45, y - h * 0.88, x - w * 0.72, y - h * 0.38],
           fill=rgb(coat), width=max(2, int(h * 0.13)))
    d.line([x + w * 0.45, y - h * 0.88, x + w * 0.72, y - h * 0.38],
           fill=rgb(coat), width=max(2, int(h * 0.13)))
    d.ellipse([x - w * 0.80, y - h * 0.42, x - w * 0.60, y - h * 0.28],
              fill=rgb(skin))
    d.ellipse([x + w * 0.60, y - h * 0.42, x + w * 0.80, y - h * 0.28],
              fill=rgb(skin))
    d.line([x - w * 0.16, y - h * 0.30, x - w * 0.24, y], fill="#27313E",
           width=max(2, int(h * 0.10)))
    d.line([x + w * 0.16, y - h * 0.30, x + w * 0.24, y], fill="#27313E",
           width=max(2, int(h * 0.10)))
    d.rectangle([x - w * 0.34, y - 2, x - w * 0.14, y], fill="#1A1A1A")
    d.rectangle([x + w * 0.14, y - 2, x + w * 0.34, y], fill="#1A1A1A")
    if bag:
        d.rectangle([x - w * 0.85, y - h * 0.72, x - w * 0.40, y - h * 0.28],
                    fill=rgb(bag), outline="#3A3020", width=1)


def ship_icon(d, x, y, sc, color="#AAB7C1"):
    d.polygon([(x - 1.7 * sc, y), (x + 1.7 * sc, y),
               (x + 1.3 * sc, y + 0.65 * sc), (x - 1.3 * sc, y + 0.65 * sc)],
              fill=rgb(color), outline="#4A5864")
    d.rectangle([x - 0.9 * sc, y - 0.55 * sc, x + 0.6 * sc, y],
                fill="#D5DEE5", outline="#6C7A86")
    d.rectangle([x - 0.2 * sc, y - 0.95 * sc, x + 0.12 * sc, y - 0.55 * sc],
                fill="#93A2AD")
    for i in range(3):
        d.rectangle([x - 1.1 * sc + i * 0.62 * sc, y + 0.06 * sc,
                     x - 0.70 * sc + i * 0.62 * sc, y + 0.38 * sc], fill="#A8703C")
    d.line([x - 1.7 * sc, y + 0.75 * sc, x + 1.7 * sc, y + 0.75 * sc],
           fill="#9FB8C8", width=1)


def burst(d, x, y, r, color="#E26B1D"):
    for a in range(10):
        ang = 2 * math.pi * a / 10
        d.line([x, y, x + r * math.cos(ang), y + r * math.sin(ang)],
               fill=rgb(color), width=2)
    d.ellipse([x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35],
              fill="#F2C14E")


def tag(d, x, y, text, fill="#181818", fsize=8, anchor="la"):
    """A solid red/black badge block with white text for illustration labels."""
    f = font(fsize, True)
    w = d.textlength(text, font=f)
    h = fsize + 6
    if anchor == "mm":
        x -= w / 2
        y -= h / 2
    elif anchor == "rm":
        x -= w
    d.rounded_rectangle([x - 4, y - 2, x + w + 4, y + h - 2],
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

    def puff(fx, fy, r, fill):
        for ox, oy, sc in ((-0.8, 0.15, 0.6), (-0.35, -0.25, 0.85),
                           (0.2, -0.1, 0.9), (0.7, 0.2, 0.65)):
            el((fx + ox * r - sc * r, fy + oy * r - sc * r),
               (fx + ox * r + sc * r, fy + oy * r + sc * r), fill=fill)

    if k == "cop":
        grad("#26354A", "#3E5069")
        tag(d, x0 + 5, y0 + 5, "ANTALYA, TÜRKIYE", "#181818", 7)
        dx0, dy0, dx1, dy1 = x0 + 34, y0 + 24, x1 - 34, y1 - 8
        d.rectangle([dx0, dy0, dx1, dy1], fill="#FFFDF5",
                    outline=rgb(LINE), width=1)
        put(d, ((dx0 + dx1) / 2, dy0 + 8), "COP31",
            font(12, True, True), INK, anchor="mm")
        put(d, ((dx0 + dx1) / 2, dy0 + 28), "DRAFT 3",
            font(16, True, True), INK, anchor="mm")
        d.rectangle([dx0 + 8, dy0 + 44, dx1 - 8, dy0 + 66], fill=rgb(RED))
        put(d, ((dx0 + dx1) / 2, dy0 + 49), "REJECTED",
            font(13, True), "#FFFFFF", anchor="mm")

    elif k == "hormuz":
        pj = real_map(box, 23, 29.5, 49, 61, 1)
        for latv, lonv in ((25.8, 55.0), (26.5, 56.2), (27.1, 57.4)):
            sx, sy = pj(latv, lonv)
            ship_icon(d, sx, sy, 2.2)
            burst(d, sx + 4, sy - 9, 4.5)
        tag(d, x0 + 5, y0 + 5, "STRAIT OF HORMUZ", "#181818", 7)
        tag(d, *P(0.36, 0.03), "IRAN STRIKES 3 TANKERS", "#181818", 7)
        tag(d, *P(0.74, 0.03), "RPT 22 NOV", "#181818", 7)
        tag(d, *P(0.68, 0.72), "US BLOCKADE: ACT OF WAR", RED, 7)

    elif k == "dymer":
        grad("#46566A", "#A6ADAD")
        puff(0.80, 0.20, 0.20, "#B6BCBC")
        ln((0, 0.83), (1, 0.83), "#6D6759", 2)
        bx((0.06, 0.20), (0.46, 0.83), fill="#5E6876", outline="#343C48")
        for fx in (0.09, 0.18, 0.27, 0.36):
            ln((fx, 0.20), (fx, 0.83), "#4A5361", 1)
        for yy in (0.29, 0.42, 0.55, 0.68):
            ln((0.06, yy), (0.46, yy), "#4A5361", 1)
            for xx in (0.10, 0.20, 0.30, 0.39):
                bx((xx, yy + 0.02), (xx + 0.055, yy + 0.075), fill="#E4D49A")
        poly([(0.46, 0.44), (0.66, 0.58), (0.56, 0.83), (0.42, 0.83)], fill="#817B70")
        for i in range(9):
            fx = 0.40 + (i % 5) * 0.07
            fy = 0.70 + (i // 5) * 0.06
            bx((fx, fy), (fx + 0.05, fy + 0.045), fill="#8E887E", outline="#625D55")
        poly([(0, 0.83), (0.24, 0.69), (0.62, 0.83)], fill="#8B8579")
        puff(0.52, 0.54, 0.10, "#BCBAB4")
        for fx in (0.51, 0.71, 0.83):
            detail_figure(d, P(fx, 0.83)[0], P(fx, 0.83)[1], 0.46,
                          "#D9A23B", helmet="#F2C14E", bag="#8B5E34")
        bx((0.88, 0.68), (1.0, 0.82), fill="#7C3030", outline="#3E2020")
        el((0.91, 0.66), (0.95, 0.70), fill="#F2C14E")
        tag(d, *P(0.03, 0.03), "03:00 LOCAL", "#181818", 8)
        tag(d, *P(0.03, 0.22), "RUSSIAN DRONE", RED, 7)
        bx((0.66, 0.03), (0.99, 0.18), fill=rgb(RED))
        put(d, P(0.825, 0.105), "14 MISSING", font(8, True), "#FFFFFF", anchor="mm")

    elif k == "shipdrone":
        pj = real_map(box, 58, 62, 21, 31, 1)
        sx, sy = pj(59.8, 26.5)
        ship_icon(d, sx, sy, 1.7)
        burst(d, sx + 3, sy - 6, 4.5)
        tag(d, x0 + 5, y0 + 5, "07:26 GMT", "#181818", 8)
        tag(d, x0 + 70, y0 + 5, "SHIP DAMAGED", RED, 7)
        tag(d, sx - 4, sy - 26, "DRONE HITS RUSSIAN SHIP", RED, 7)
        cx, cy = pj(60.3, 28.5)
        for ox, oy in ((-5, -3), (5, -3), (-5, 3), (5, 3)):
            d.ellipse([cx + ox - 2, cy + oy - 1.5, cx + ox + 2, cy + oy + 1.5],
                      fill="#4A5864")
        d.line([cx - 5, cy - 3, cx + 5, cy + 3], fill="#4A5864", width=1)
        d.line([cx + 5, cy - 3, cx - 5, cy + 3], fill="#4A5864", width=1)
        d.line([cx, cy + 3, sx, sy], fill=rgb(RED), width=1)

    elif k == "poland":
        pj = real_map(box, 48, 56, 10, 28, 2)
        for latv, lonv in ((52.23, 21.01), (51.70, 22.80)):
            sx, sy = pj(latv, lonv)
            burst(d, sx, sy, 5)
        gx, gy = pj(52.0, 14.5)
        put(d, (gx, gy), "GERMANY", font(6, True), MUTED)
        ux, uy = pj(50.5, 25.0)
        put(d, (ux, uy), "UKRAINE", font(6, True), MUTED)
        bx0, by0 = pj(53.5, 25.0)
        put(d, (bx0, by0), "BELARUS", font(6, True), MUTED)
        tag(d, x0 + 5, y0 + 4, "NATO", "#181818", 8)
        tag(d, x0 + 48, y0 + 4, "22 NOV", "#181818", 8)
        tag(d, x0 + 5, y0 + 20, "POLAND", "#181818", 7)
        tag(d, x1 - 110, y0 + 4, "RUSSIAN MISSILE + DRONE", RED, 7)

    elif k == "westbank":
        pj = real_map(box, 30, 34, 30, 39, 1)
        fx, fy = x0 + 4, y0 + 4
        d.rectangle([fx, fy, fx + 18, fy + 12], fill="#FFFFFF", outline="#9B9B9B")
        d.rectangle([fx, fy, fx + 18, fy + 4], fill="#111111")
        d.rectangle([fx, fy + 8, fx + 18, fy + 12], fill="#007A3D")
        d.polygon([(fx, fy), (fx + 8, fy + 6), (fx, fy + 12)], fill="#CE1126")
        for latv, lonv in ((32.10, 35.20), (32.00, 35.32), (31.90, 35.15), (32.20, 35.40)):
            vx, vy = pj(latv, lonv)
            d.ellipse([vx - 2, vy - 2, vx + 2, vy + 2], fill=rgb(RED),
                      outline="#FFFFFF", width=1)
            burst(d, vx + 3, vy - 4, 3)
        tag(d, *P(0.02, 0.03), "OVERNIGHT", "#181818", 7)
        tag(d, *P(0.30, 0.10), "SETTLERS ATTACK 4 VILLAGES", "#181818", 7)

    elif k == "benghazi":
        pj = real_map(box, 30, 34, 15, 25, 2)
        sx, sy = pj(32.12, 20.07)
        ship_icon(d, sx, sy, 1.9)
        burst(d, sx + 3, sy - 8, 6)
        d.line([sx, sy + 5, sx + 22, sy + 5], fill="#6D6759", width=2)
        d.line([sx + 19, sy - 14, sx + 19, sy + 5], fill="#8A95A0", width=2)
        d.line([sx + 19, sy - 14, sx + 6, sy - 14], fill="#8A95A0", width=2)
        tag(d, x0 + 5, y0 + 4, "15:50 GMT", "#181818", 8)
        tag(d, x0 + 66, y0 + 4, "DRONE BLAST", RED, 7)
        tag(d, x0 + 5, y0 + 30, "BENGHAZI, LIBYA", "#181818", 7)
        tag(d, x0 + 5, y0 + 16, "RUSSIAN SHIP HIT", RED, 7)

    elif k == "ice":
        grad("#DCE5EC", "#F3EFE3")
        d.rounded_rectangle([P(0.60, 0.22), P(1.02, 0.78)], radius=9,
                            fill="#D2DCE4", outline="#8493A0")
        for wx in (0.68, 0.76, 0.84, 0.92):
            bx((wx, 0.30), (wx + 0.035, 0.35), fill="#9AA9B5")
        bx((0.12, 0.36), (0.70, 0.58), fill="#BCC9C0", outline="#6F7F75")
        bx((0.14, 0.58), (0.68, 0.62), fill="#8E9E94")
        el((0.24, 0.62), (0.30, 0.67), fill="#3B424C")
        el((0.56, 0.62), (0.62, 0.67), fill="#3B424C")
        for fx in (0.32, 0.45):
            detail_figure(d, P(fx, 0.74)[0], P(fx, 0.74)[1], 0.34, "#E8B84B")
        d.line([P(0.50, 0.63), P(0.54, 0.63)], fill=rgb(RED), width=2)
        detail_figure(d, P(0.76, 0.74)[0], P(0.76, 0.74)[1], 0.44, "#2E3A46",
                      skin="#8A6A4E")
        tag(d, *P(0.03, 0.03), "SEA-TAC", "#181818", 8)
        tag(d, *P(0.24, 0.03), "08:00", "#181818", 8)
        tag(d, *P(0.03, 0.20), "ICE ARREST", RED, 7)
        tag(d, *P(0.52, 0.20), "2 DETAINED", RED, 7)

    elif k == "tariff":
        grad("#DCE5EC", "#F3EFE3")
        for i in range(4):
            fx = 0.02 + i * 0.13
            bx((fx, 0.50), (fx + 0.10, 0.78), fill="#6E7E8C", outline="#4C5A66")
            bx((fx + 0.02, 0.44), (fx + 0.08, 0.50), fill="#8494A1")
        bx((0.60, 0.22), (0.98, 0.60), fill="#FFFDF5", outline=rgb(LINE))
        for i, (h, c) in enumerate(((0.26, "#8A9AA6"), (0.18, "#B9C6CE"))):
            bx((0.65 + i * 0.15, 0.54 - h), (0.75 + i * 0.15, 0.54), fill=c)
        d.line([P(0.65, 0.26), P(0.92, 0.44)], fill=rgb(RED), width=3)
        d.polygon([P(0.92, 0.44), P(0.87, 0.39), P(0.90, 0.35)], fill=rgb(RED))
        detail_figure(d, P(0.54, 0.82)[0], P(0.54, 0.82)[1], 0.36, "#A8703C")
        tag(d, *P(0.03, 0.03), "22 NOV", "#181818", 8)
        tag(d, *P(0.24, 0.03), "US EASES", "#181818", 8)
        tag(d, *P(0.48, 0.03), "CANADA", "#181818", 8)
        tag(d, *P(0.66, 0.13), "TARIFF CUT", RED, 8)

    elif k == "f1":
        grad("#121A2A", "#3A2C4E")
        for i in range(16):
            bx((i / 16, 0.34 + (i % 4) * 0.05), ((i + 0.7) / 16, 0.68), fill="#1C2940")
            for wy in (0.40, 0.48, 0.56):
                bx(((i + 0.2) / 16, wy), ((i + 0.45) / 16, wy + 0.025), fill="#E8C25A")
        poly([(0.08, 0.62), (0.18, 0.50), (0.34, 0.48), (0.48, 0.42),
              (0.68, 0.44), (0.78, 0.54), (0.86, 0.56), (0.86, 0.62),
              (0.66, 0.66), (0.22, 0.66)], fill=rgb(RED), outline="#5E1A1A")
        poly([(0.30, 0.48), (0.44, 0.40), (0.54, 0.40), (0.48, 0.48)], fill="#E86A4A")
        d.ellipse([P(0.45, 0.385), P(0.515, 0.455)], fill="#E8C25A", outline="#2A2A2A")
        d.ellipse([P(0.465, 0.40), P(0.50, 0.435)], fill="#1A1A1A")
        bx((0.06, 0.56), (0.16, 0.60), fill="#B52323")
        bx((0.80, 0.52), (0.90, 0.56), fill="#B52323")
        d.line([P(0.22, 0.50), P(0.28, 0.47)], fill="#C9CBD0", width=1)
        for fx in (0.24, 0.68):
            el((fx, 0.60), (fx + 0.11, 0.73), fill="#171717", outline="#3A3A3A")
            el((fx + 0.04, 0.64), (fx + 0.07, 0.69), fill="#9AA3A8")
        bx((0.78, 0.08), (0.98, 0.36), fill="#FFFFFF", outline="#9B9B9B")
        for ry in range(4):
            for rx in range(4):
                if (rx + ry) % 2 == 0:
                    bx((0.78 + rx * 0.05, 0.08 + ry * 0.07),
                       (0.83 + rx * 0.05, 0.15 + ry * 0.07), fill="#202020")
        tag(d, *P(0.04, 0.03), "SAT NIGHT", "#181818", 8)
        put(d, P(0.05, 0.15), "P1", font(19, True), "#FFFFFF")
        tag(d, *P(0.22, 0.05), "VERSTAPPEN WINS", RED, 7)

    elif k == "flags_jp_in":
        grad("#DFE8EF", "#F3EFE3")
        bx((0.04, 0.16), (0.40, 0.54), fill="#FFFFFF", outline="#9B9B9B")
        el((0.18, 0.28), (0.26, 0.36), fill=rgb(RED))
        bx((0.58, 0.16), (0.94, 0.54), fill="#FFFFFF", outline="#9B9B9B")
        bx((0.58, 0.16), (0.94, 0.28), fill="#FF9933")
        bx((0.58, 0.42), (0.94, 0.54), fill="#138808")
        el((0.71, 0.30), (0.81, 0.40), outline="#000088", width=1)
        detail_figure(d, P(0.36, 0.92)[0], P(0.36, 0.92)[1], 0.44, "#2E3A46",
                      skin="#C99564")
        detail_figure(d, P(0.64, 0.92)[0], P(0.64, 0.92)[1], 0.44, "#4A5A6E",
                      skin="#8A6A4E")
        d.line([P(0.40, 0.72), P(0.60, 0.72)], fill="#C99564", width=4)
        tag(d, *P(0.04, 0.04), "JAPAN + INDIA", "#181818", 7)
        tag(d, *P(0.28, 0.62), "DEFENCE PACT", "#181818", 7)
        tag(d, *P(0.70, 0.62), "22 NOV", "#181818", 7)

    else:
        el((0.34, 0.30), (0.66, 0.62), outline=col, width=2)
        put(d, P(0.50, 0.46), s["place"].split(",")[0][:10], font(8, True), INK,
            anchor="mm")

    if k not in {"cop", "hormuz", "poland", "benghazi"}:
        tag(d, x0 + 5, y1 - 12, s["place"], "#181818", 8)



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
        scene(d, (x + 3, y + 3, x + 323, y + 113), s)
        d.rectangle([x + 3, y + 115, x + 323, y + 129],
                    fill=rgb(REGION_COLORS[s["region"]]))
        square_badge(d, x + 7, y + 115, x + 21, y + 129, s["n"],
                     REGION_COLORS[s["region"]])
        put(d, (x + 26, y + 124), s["kicker"], font(9, True), "#FFFFFF", anchor="lm")
        put(d, (x + 315, y + 124), s["source"], font(7), "#FFFFFF", anchor="rm")
        head = font(15, True, True)
        for j, line in enumerate(wrap(s["headline"], head, 326 - 14, d)[:2]):
            put(d, (x + 7, y + 133 + j * 17), line, head, INK)
        for line in wrap(s["body"], font(9), 235, d)[:1]:
            put(d, (x + 7, y + 169), line, font(9), INK)
        chip(d, x + 250, y + 170, s["status"])

    for i, s in enumerate([x for x in STORIES if x["size"] == "small"][:8]):
        row, col = divmod(i, 4)
        x, y = 12 + col * 252, SMALL_Y0 + row * SMALL_STEP
        d.rectangle([x, y, x + 244, y + SMALL_H], fill=rgb(CARD), outline=rgb(LINE))
        scene(d, (x + 3, y + 4, x + 241, y + 89), s)
        d.rectangle([x + 3, y + 91, x + 241, y + 105],
                    fill=rgb(REGION_COLORS[s["region"]]))
        square_badge(d, x + 7, y + 91, x + 21, y + 105, s["n"],
                     REGION_COLORS[s["region"]])
        put(d, (x + 26, y + 98), s["kicker"], font(8, True), "#FFFFFF", anchor="lm")
        put(d, (x + 235, y + 98), s["source"], font(7), "#FFFFFF", anchor="rm")
        head = font(10, True, True)
        for j, line in enumerate(wrap(s["headline"], head, 244 - 12, d)[:2]):
            put(d, (x + 6, y + 109 + j * 10), line, head, INK)
        chip(d, x + 174, y + 126, s["status"], fill="#E9E2D2", fsize=7)

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
