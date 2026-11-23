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
    px = max(10, px)  # global minimum: every text stays readable
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


def ship_icon(d, x, y, sc, color="#AAB7C1", kind="cargo"):
    # long low hull with a pointed bow to the right
    d.polygon([(x - 1.9 * sc, y), (x + 2.0 * sc, y - 0.12 * sc),
               (x + 1.6 * sc, y + 0.5 * sc), (x - 1.5 * sc, y + 0.5 * sc)],
              fill=rgb(color), outline="#4A5864")
    d.line([x - 1.9 * sc, y + 0.28 * sc, x + 1.7 * sc, y + 0.28 * sc],
           fill="#8A99A4", width=1)
    # white bridge superstructure at the stern (left)
    d.rectangle([x - 1.5 * sc, y - 0.9 * sc, x - 0.8 * sc, y],
                fill="#E8EEF1", outline="#6C7A86")
    d.rectangle([x - 1.4 * sc, y - 0.8 * sc, x - 1.25 * sc, y - 0.65 * sc],
                fill="#5B7488")
    d.rectangle([x - 1.15 * sc, y - 0.8 * sc, x - 1.0 * sc, y - 0.65 * sc],
                fill="#5B7488")
    if kind == "cargo":
        # two tiers of stacked, differently coloured containers
        cols = ("#B5342E", "#2E6FA3", "#C48A2E", "#3E7A52", "#8A5A9E")
        for tier in range(2):
            for i in range(5):
                cx = x - 0.7 * sc + i * 0.42 * sc
                cy = y - (0.55 + tier * 0.55) * sc
                c = cols[(i + tier * 2) % len(cols)]
                d.rectangle([cx, cy, cx + 0.36 * sc, cy + 0.48 * sc],
                            fill=c, outline="#3A3A3A")
    else:
        # flat tanker deck: piping, hatches and a small crane
        d.line([x - 0.7 * sc, y - 0.18 * sc, x + 1.5 * sc, y - 0.18 * sc],
               fill="#5E6E7A", width=2)
        for i in range(4):
            cx = x - 0.6 * sc + i * 0.55 * sc
            d.ellipse([cx, y - 0.34 * sc, cx + 0.28 * sc, y - 0.16 * sc],
                      fill="#93A2AD", outline="#4A5864")
        d.line([x + 0.6 * sc, y - 0.2 * sc, x + 1.0 * sc, y - 1.0 * sc],
               fill="#C9D2D8", width=2)


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

    def puff(fx, fy, r, fill):
        for ox, oy, sc in ((-0.8, 0.15, 0.6), (-0.35, -0.25, 0.85),
                           (0.2, -0.1, 0.9), (0.7, 0.2, 0.65)):
            el((fx + ox * r - sc * r, fy + oy * r - sc * r),
               (fx + ox * r + sc * r, fy + oy * r + sc * r), fill=fill)

    if k == "cop":
        grad("#26354A", "#43536B")
        bx((0.05, 0.62), (0.74, 0.76), fill="#7A6146", outline="#4A3A28")
        coats = ["#3E5A7A", "#7A4A4A", "#4C6B57", "#6A5A3E", "#3E5A7A", "#7A4A4A"]
        for i, fx in enumerate((0.09, 0.20, 0.31, 0.42, 0.53, 0.64)):
            # head, hair and shoulders above the table
            el((fx, 0.36), (fx + 0.055, 0.47), fill="#C99564", outline="#7A5538")
            el((fx - 0.005, 0.35), (fx + 0.06, 0.41), fill="#3A2A1E")
            el((fx - 0.025, 0.46), (fx + 0.08, 0.68), fill=coats[i],
               outline="#2E2E2E")
        # rejected draft at the right
        bx((0.76, 0.12), (0.97, 0.68), fill="#FFFDF5", outline=rgb(LINE))
        for j in range(4):
            ln((0.79, 0.20 + j * 0.06), (0.94, 0.20 + j * 0.06), "#9B9B9B", 1)
        bx((0.76, 0.50), (0.97, 0.66), fill=rgb(RED))
        put(d, P(0.865, 0.54), "NO DEAL", font(7, True), "#FFFFFF", anchor="mm")

    elif k == "hormuz":
        grad("#1E3046", "#5C7185")
        for yy in (0.42, 0.56, 0.70):
            ln((0.02, yy), (0.98, yy), "#3E5E78", 1)
        for fx in (0.18, 0.46, 0.70):
            px, py = P(fx, 0.50)
            ship_icon(d, px, py, 10, kind="tanker")
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
        poly([(0, 0.20), (0.06, 0.18), (0.10, 0.32), (0.05, 0.48), (0, 0.50)],
             fill="#C9B98F")
        for yy in (0.54, 0.66, 0.78, 0.90):
            ln((0.02, yy), (0.98, yy), "#4E6E88", 1)
        px, py = P(0.38, 0.72)
        ship_icon(d, px, py, 13, kind="cargo")
        ax, ay = P(0.46, 0.46)
        burst(d, ax, ay, 5)
        # quadcopter drone in the air with a strike line
        cx, cy = P(0.80, 0.26)
        for ox, oy in ((-10, -5), (10, -5), (-10, 5), (10, 5)):
            d.ellipse([cx + ox - 4, cy + oy - 3, cx + ox + 4, cy + oy + 3],
                      fill="#D5DEE5")
        d.line([cx - 10, cy - 5, cx + 10, cy + 5], fill="#BCC7D0", width=1)
        d.line([cx + 10, cy - 5, cx - 10, cy + 5], fill="#BCC7D0", width=1)
        d.line([cx, cy + 5, ax, ay], fill=rgb(RED), width=2)

    elif k == "poland":
        # real map: Poland with its neighbours, Russia to the east
        pj = real_map(box, 47, 58, 8, 36, 4)
        for sx0, sy0, tx, ty in ((54.0, 31.0, 52.23, 21.01),
                                 (53.0, 30.0, 51.70, 22.80)):
            ax, ay = pj(sx0, sy0)
            ex, ey = pj(tx, ty)
            d.line([ax, ay, ex, ey], fill=rgb(RED), width=2)
            d.polygon([(ex, ey), (ex - 5, ey - 2), (ex - 4, ey + 3)], fill=rgb(RED))
            burst(d, ex, ey, 5)
            # small drone at the eastern origin
            d.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill="#2E3A46")

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
        # naval ship, not a container ship
        poly([(0.34, 0.60), (0.74, 0.60), (0.70, 0.74), (0.38, 0.74)],
             fill="#5E6E7A", outline="#3A4A56")
        bx((0.44, 0.42), (0.60, 0.60), fill="#C2CDD5", outline="#6C7A86")
        bx((0.52, 0.34), (0.56, 0.42), fill="#8A99A4")
        bx((0.78, 0.24), (0.82, 0.64), fill="#8A95A0")
        ln((0.80, 0.26), (0.62, 0.26), "#8A95A0", 2)
        ax, ay = P(0.55, 0.46)
        burst(d, ax, ay, 7)
        # sea drone approaching with a wake
        sx, sy = P(0.14, 0.84)
        # low unmanned surface vessel: flat hull, sensor mast, wake
        d.polygon([(sx - 14, sy - 2), (sx + 12, sy - 3),
                   (sx + 9, sy + 4), (sx - 11, sy + 4)],
                  fill="#3E4A52", outline="#20282E")
        d.rectangle([sx - 2, sy - 9, sx + 3, sy - 2], fill="#20282E")
        d.ellipse([sx - 1, sy - 12, sx + 2, sy - 9], fill="#C2CDD5")
        d.line([sx - 24, sy + 5, sx - 14, sy + 3], fill="#AFC3D0", width=1)
        d.line([sx - 24, sy + 9, sx - 14, sy + 5], fill="#AFC3D0", width=1)
        d.line([sx + 12, sy, ax, ay], fill=rgb(RED), width=2)

    elif k == "ice":
        grad("#DCE5EC", "#F3EFE3")
        # open aircraft door at the right
        d.rounded_rectangle([P(0.66, 0.26), P(1.02, 0.80)], radius=9,
                            fill="#D2DCE4", outline="#8493A0")
        bx((0.70, 0.32), (0.76, 0.56), fill="#9AA9B5", outline="#5E6E7A")
        bx((0.80, 0.34), (0.95, 0.40), fill="#9AA9B5")
        # jetway tube leading to the door
        bx((0.08, 0.42), (0.70, 0.60), fill="#BCC9C0", outline="#6F7F75")
        bx((0.10, 0.60), (0.68, 0.64), fill="#8E9E94")
        # two detainees, wrists cuffed behind their backs
        for fx in (0.26, 0.38):
            px, py = P(fx, 0.90)
            detail_figure(d, px, py, 27, "#E8B84B")
        d.line([P(0.29, 0.73), P(0.35, 0.73)], fill=rgb(RED), width=3)
        for fx in (0.29, 0.35):
            ax, ay = P(fx, 0.73)
            d.ellipse([ax - 2, ay - 2, ax + 2, ay + 2],
                      outline=rgb(RED), width=1)
        # uniformed agent with ICE lettering
        px, py = P(0.58, 0.92)
        detail_figure(d, px, py, 31, "#2E3A46")
        put(d, (px - 6, py - 20), "ICE", font(6, True), "#FFFFFF")

    elif k == "tariff":
        grad("#1C3048", "#3E5069")
        # designed for the wide, short box: high tariff bar -> low tariff bar
        put(d, (x0 + 8, y0 + 16), "TARIFF", font(9, True), "#F2C14E")
        d.rectangle([x0 + 40, y0 + 20, x0 + 80, y0 + 44],
                    fill="#7E8E9A", outline="#4A5864")
        put(d, (x0 + 48, y0 + 25), "HIGH", font(7, True), "#FFFFFF")
        d.rectangle([x0 + 150, y0 + 34, x0 + 190, y0 + 44],
                    fill="#9FB0BC", outline="#4A5864")
        put(d, (x0 + 157, y0 + 36), "LOW", font(6, True), "#1C3048")
        d.line([x0 + 82, y0 + 23, x0 + 148, y0 + 37],
               fill=rgb(RED), width=4)
        d.polygon([(x0 + 152, y0 + 38), (x0 + 142, y0 + 32), (x0 + 145, y0 + 43)],
                  fill=rgb(RED))

    elif k == "f1":
        grad("#121A2A", "#3A2C4E")
        # simple banner instead of a forced detailed car drawing
        d.rectangle([x0 + 6, y0 + 12, x1 - 6, y0 + 34], fill=rgb(RED))
        put(d, (x0 + 12, y0 + 16), "F1 · VERSTAPPEN WINS VEGAS",
            font(10, True), "#FFFFFF")
        # chequered flag: mandatory victory symbol
        ln((0.86, 0.90), (0.86, 0.36), "#D6DCE2", 2)
        bx((0.87, 0.38), (0.99, 0.72), fill="#FFFFFF", outline="#6B6B6B")
        for ry in range(3):
            for rx in range(2):
                if (rx + ry) % 2 == 0:
                    bx((0.87 + rx * 0.06, 0.38 + ry * 0.11),
                       (0.93 + rx * 0.06, 0.49 + ry * 0.11), fill="#202020")

    elif k == "flags_jp_in":
        grad("#DFE8EF", "#F3EFE3")
        # Japan: white field with a large centred red disc
        bx((0.03, 0.40), (0.33, 0.96), fill="#FFFFFF", outline="#6B6B6B", width=2)
        el((0.147, 0.51), (0.214, 0.83), fill=rgb(RED))
        # India: saffron / white / green with blue chakra
        bx((0.67, 0.40), (0.97, 0.96), fill="#FFFFFF", outline="#6B6B6B", width=2)
        bx((0.67, 0.40), (0.97, 0.59), fill="#FF9933")
        bx((0.67, 0.77), (0.97, 0.96), fill="#138808")
        el((0.775, 0.59), (0.825, 0.83), outline="#000088", width=2)
        # delegates stand between the two flags, never over them
        for i, fx in enumerate((0.45, 0.55)):
            px, py = P(fx, 0.98)
            detail_figure(d, px, py, 30,
                          "#2E3A46" if i == 0 else "#4A5A6E")

    elif k == "drones":
        grad("#101A2E", "#2E3E58")
        # city skyline with lit windows
        for i in range(12):
            fx = i / 12
            bx((fx, 0.58 + (i % 3) * 0.05), (fx + 0.075, 0.96), fill="#1C2940")
            for wy in (0.66, 0.78, 0.90):
                bx((fx + 0.02, wy), (fx + 0.045, wy + 0.03), fill="#E8C25A")
        # swarm of incoming drones with light trails
        for i in range(18):
            fx = 0.04 + (i % 9) * 0.105
            fy = 0.10 + (i // 9) * 0.13
            ax, ay = P(fx, fy)
            d.ellipse([ax - 1.5, ay - 1.5, ax + 1.5, ay + 1.5], fill="#F2C14E")
            d.line([ax - 7, ay + 4, ax, ay], fill="#7E8FA6", width=1)
        for fx, fy in ((0.28, 0.62), (0.58, 0.70), (0.82, 0.56)):
            ax, ay = P(fx, fy)
            burst(d, ax, ay, 5)
        put(d, P(0.90, 0.44), "186", font(14, True), "#FFFFFF")

    elif k == "radar":
        grad("#1C3048", "#4A6276")
        # the illustration itself states the disputed object and both sides
        put(d, ((x0 + x1) / 2 - d.textlength("US RADARS", font=font(8, True)) / 2,
                y0 + 15), "US RADARS", font(8, True), "#FFFFFF")
        # proper parabolic radar dishes: dish, feed horn, mast and base
        for fx, struck in ((0.28, True), (0.74, False)):
            lx, ly = P(fx - 0.10, 0.40)
            rx, ry = P(fx + 0.10, 0.72)
            d.pieslice([lx, ly, rx, ry], 200, 340,
                       fill="#D5DEE5", outline="#8493A0")
            # feed horn in front of the dish
            hx, hy = P(fx, 0.44)
            d.line([P(fx, 0.58), (hx, hy)], fill="#8493A0", width=1)
            d.ellipse([hx - 2, hy - 2, hx + 2, hy + 2], fill="#6C7A86")
            # mast and footing
            d.line([P(fx, 0.66), P(fx, 0.92)], fill="#9BABB6", width=2)
            bx((fx - 0.055, 0.90), (fx + 0.055, 0.96), fill="#6C7A86")
            if struck:
                d.line([P(fx - 0.07, 0.44), P(fx + 0.07, 0.68)],
                       fill=rgb(RED), width=2)
                d.line([P(fx + 0.07, 0.44), P(fx - 0.07, 0.68)],
                       fill=rgb(RED), width=2)
            else:
                d.line([P(fx - 0.04, 0.70), P(fx, 0.75), P(fx + 0.07, 0.62)],
                       fill="#3EB650", width=3)
        # plain readable text, no badge blocks
        put(d, (x0 + 7, y0 + 37), "IRAN: 2 HIT", font(8, True), "#FF9A8A")
        put(d, (x0 + bw / 2 + 5, y0 + 37), "BAHR: NONE", font(8, True), "#8DE89B")

    elif k == "factory":
        grad("#3A2E2A", "#6B5A4A")
        poly([(0.10, 0.46), (0.90, 0.46), (0.90, 0.86), (0.10, 0.86)],
             fill="#7C8A90", outline="#3A4248")
        bx((0.20, 0.22), (0.28, 0.46), fill="#8A99A4")
        bx((0.56, 0.16), (0.64, 0.46), fill="#8A99A4")
        poly([(0.34, 0.46), (0.39, 0.26), (0.47, 0.46)], fill="#E26B1D")
        poly([(0.60, 0.46), (0.65, 0.28), (0.72, 0.46)], fill="#F2A03D")
        puff(0.42, 0.20, 0.09, "#9A9A96")
        puff(0.66, 0.14, 0.08, "#9A9A96")
        px, py = P(0.82, 0.92)
        detail_figure(d, px, py, 22, "#B5342E", helmet="#F2C14E")

    else:
        el((0.34, 0.30), (0.66, 0.62), outline=col, width=2)

    tag(d, x0 + 5, y0 + 4, s["place"], "#181818", 8)
    times = {
        "cop": "22 NOV 2026",
        "hormuz": "22 NOV 2026",
        "drones": "00:30 LOCAL · 22 NOV",
        "radar": "22 NOV 2026",
        "poland": "22 NOV 2026",
        "westbank": "OVERNIGHT · 22 NOV",
        "factory": "22 NOV 2026",
        "ice": "08:00 LOCAL · 22 NOV",
        "tariff": "22 NOV 2026",
        "f1": "SAT NIGHT · 22 NOV",
        "flags_jp_in": "22 NOV 2026",
    }
    tt = times.get(k, "22 NOV 2026")
    tf = font(7, True)
    tw = d.textlength(tt, font=tf)
    tag(d, x1 - 9 - tw, y0 + 4, tt, "#181818", 8)



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
    f = font(8)
    labels = [f"{reg} {sum(1 for s in STORIES if s['region'] == reg)}"
              for reg in REGIONS]
    widths = [d.textlength(label, font=f) for label in labels]
    lx = mx0 + (mx1 - mx0 - sum(10 + w for w in widths)) / 2
    for reg, label, w in zip(REGIONS, labels, widths):
        d.ellipse([lx, ly, lx + 7, ly + 7], fill=rgb(REGION_COLORS[reg]))
        put(d, (lx + 10, ly + 3.5), label, f, INK, anchor="lm")
        lx += 10 + w


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
    f = font(10.5)

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
        for j, line in enumerate(wrap(s["brief"], f, (x1 - 10) - text_x - 70, d)[:2]):
            put(d, (text_x, cy - 2 + j * 12), line, f, INK)
        put(d, (x1 - 10, cy + 8), s["source"], font(8.5), MUTED, anchor="rm")


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
        font(10.5, True), "#FFFFFF", anchor="lm")
    put(d, (1012, BAR_H / 2),
        f"{len(STORIES)} STORIES IN {len(REGIONS)} REGIONS · "
        "EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
        font(10.5, True), "#FFFFFF", anchor="rm")
    put(d, (512, TITLE_Y), "Sunday 22 November 2026",
        font(45, True, True), INK, anchor="mm")
    put(d, (512, DECK_Y),
        "COP31 ends in collapse · Iran strikes tankers · Russian drone hits flats near Kyiv",
        font(13, False, True), MUTED, anchor="mm")
    d.line([12, RULE_Y, 1012, RULE_Y], fill=rgb(LINE), width=1)

    stats = [("44H", "COP31 ends with no deal"),
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
        put(d, (sx + 71, STAT_BIG_Y), big, font(24, True, True), RED, anchor="mm")
        put(d, (sx + 71, STAT_SMALL_Y), small, font(9), INK, anchor="mm")

    counts = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGIONS}
    for i, r in enumerate(REGIONS):
        bx = 12 + i * 142
        d.rectangle([bx, REG_Y0, bx + 140, REG_Y1], fill=rgb(REGION_COLORS[r]))
        put(d, (bx + 6, (REG_Y0 + REG_Y1) / 2), f"{r} · {counts[r]}",
            font(10, True), "#FFFFFF", anchor="lm")

    for i, s in enumerate([x for x in STORIES if x["size"] == "main"][:3]):
        x, y = 12 + i * 336, MAIN_Y
        d.rectangle([x, y, x + 326, y + MAIN_H], fill=rgb(CARD), outline=rgb(LINE))
        scene(d, (x + 3, y + 3, x + 323, y + 53), s)
        d.rectangle([x + 3, y + 55, x + 323, y + 69],
                    fill=rgb(REGION_COLORS[s["region"]]))
        square_badge(d, x + 7, y + 55, x + 21, y + 69, s["n"],
                     REGION_COLORS[s["region"]])
        put(d, (x + 26, y + 64), s["kicker"], font(10, True), "#FFFFFF", anchor="lm")
        put(d, (x + 315, y + 64), s["source"], font(8), "#FFFFFF", anchor="rm")
        head = font(22, True, True)
        hlines = wrap(s["headline"], head, 326 - 14, d)[:2]
        for j, line in enumerate(hlines):
            put(d, (x + 7, y + 73 + j * 25), line, head, INK)
        body_y = 73 + (len(hlines) - 1) * 25 + 20
        max_lines = max(2, int((188 - body_y - 21) / 21) + 1)
        for j, line in enumerate(wrap(s["body"], font(18), 300, d)[:max_lines]):
            put(d, (x + 7, y + body_y + j * 21), line, font(18), INK)

    for i, s in enumerate([x for x in STORIES if x["size"] == "small"][:8]):
        row, col = divmod(i, 4)
        x, y = 12 + col * 252, SMALL_Y0 + row * SMALL_STEP
        d.rectangle([x, y, x + 244, y + SMALL_H], fill=rgb(CARD), outline=rgb(LINE))
        scene(d, (x + 3, y + 4, x + 241, y + 54), s)
        d.rectangle([x + 3, y + 56, x + 241, y + 70],
                    fill=rgb(REGION_COLORS[s["region"]]))
        square_badge(d, x + 7, y + 56, x + 21, y + 70, s["n"],
                     REGION_COLORS[s["region"]])
        put(d, (x + 26, y + 63), s["kicker"], font(10, True), "#FFFFFF", anchor="lm")
        put(d, (x + 235, y + 63), s["source"], font(8), "#FFFFFF", anchor="rm")
        head = font(14, True, True)
        hlines = wrap(s["headline"], head, 244 - 12, d)[:2]
        for j, line in enumerate(hlines):
            put(d, (x + 6, y + 74 + j * 16), line, head, INK)
        sby = 74 + (len(hlines) - 1) * 16 + 16
        smax = max(2, int((140 - sby - 14) / 12) + 1)
        for j, line in enumerate(wrap(s["body"], font(11), 232, d)[:smax]):
            put(d, (x + 6, y + sby + j * 12), line, font(11), INK)

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
        font(10), INK)
    put(d, (76, 990), DATE_CHECK, font(10), INK)
    put(d, (1012, 1011), SOURCES_LINE, font(10), INK, anchor="rm")

    im.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    build()
