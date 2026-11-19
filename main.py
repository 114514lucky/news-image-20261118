# news-image-20261118: draws one 1024x1024 PNG that sums up the world news
# of Wednesday 18 November 2026, in the style of a broadsheet front page.
# Python 3.13, standard library only, no network, no clock, no randomness:
# two runs write identical bytes. All artwork is hand-drawn vector shapes
# and an embedded vector stroke font (no external images, no bitmap font).
# Stories were first reported on 18 November 2026 (sources in the file:
# Reuters, AP, AFP, BBC, Al Jazeera, Anadolu, Dawn, Bloomberg, ATP Tour).
# Design modelled on the 17 November competition's top entries: cream
# paper, big serif-style date title, UTC timeline, illustrated leads,
# secondary grid, world map with pins, numbered briefs, DATE CHECK bar.
import os, struct, zlib

W, H = 1024, 1024

# --- vector stroke font: glyph = list of strokes, each a "x,y x,y ..." string
# Grid: x 0..6, y 0..12, baseline y=9, descenders to 12.
FONT_SRC = {
"A": ["0,9 3,0 6,9", "1,6 5,6"],
"B": ["0,0 0,9", "0,0 4,0 5,1 5,3 4,4 0,4", "0,4 4,4 5,5 5,8 4,9 0,9"],
"C": ["5,1 4,0 2,0 1,1 0,3 0,6 1,8 2,9 4,9 5,8"],
"D": ["0,0 0,9 3,9 5,7 5,2 3,0 0,0"],
"E": ["5,0 0,0 0,9 5,9", "0,4 3,4"],
"F": ["0,0 5,0", "0,0 0,9", "0,4 3,4"],
"G": ["5,1 4,0 2,0 1,1 0,3 0,6 1,8 2,9 4,9 5,8 5,5", "5,5 3,5"],
"H": ["0,0 0,9", "6,0 6,9", "0,4 6,4"],
"I": ["1,0 5,0", "3,0 3,9", "1,9 5,9"],
"J": ["1,0 5,0", "5,0 5,7 4,9 2,9 1,7"],
"K": ["0,0 0,9", "5,0 0,5 5,9"],
"L": ["0,0 0,9 5,9"],
"M": ["0,9 0,0 3,6 6,0 6,9"],
"N": ["0,9 0,0 6,9 6,0"],
"O": ["2,0 4,0 5,2 5,7 4,9 2,9 1,7 1,2 2,0"],
"P": ["0,9 0,0 4,0 5,1 5,4 4,5 0,5"],
"Q": ["2,0 4,0 5,2 5,7 4,9 2,9 1,7 1,2 2,0", "4,6 6,9"],
"R": ["0,9 0,0 4,0 5,1 5,4 4,5 0,5", "3,5 6,9"],
"S": ["5,1 4,0 2,0 1,1 0,3 0,4 1,5 3,5 5,6 5,8 4,9 2,9 1,8"],
"T": ["0,0 6,0", "3,0 3,9"],
"U": ["0,0 0,7 1,9 2,9 4,9 5,7 6,7 6,0"],
"V": ["0,0 3,9 6,0"],
"W": ["0,0 1,9 3,4 5,9 6,0"],
"X": ["0,0 6,9", "6,0 0,9"],
"Y": ["0,0 3,4 6,0", "3,4 3,9"],
"Z": ["0,0 6,0 0,9 6,9"],
"a": ["1,4 1,8 2,9 4,9 5,8 5,3 4,3 2,3 1,4", "5,3 5,9"],
"b": ["1,0 1,9", "5,4 4,3 2,3 1,4 1,8 2,9 4,9 5,8 5,4"],
"c": ["5,4 4,3 2,3 1,4 1,7 2,9 4,9 5,8"],
"d": ["5,0 5,9", "5,6 5,9 4,9 2,9 1,8 1,4 2,3 4,3 5,4"],
"e": ["4,3 2,3 1,4 1,6 2,8 4,9 5,8", "1,6 5,6"],
"f": ["3,9 3,1 4,0 5,0", "1,4 4,4"],
"g": ["1,4 1,8 2,9 4,9 5,8 5,4 4,3 2,3 1,4", "5,8 5,11 4,12 2,12 1,11"],
"h": ["1,0 1,9", "1,5 2,3 4,3 5,4 5,9"],
"i": ["2,3 2,9", "2,0 3,0"],
"j": ["4,3 4,10 3,12 1,12", "4,0 5,0"],
"k": ["1,0 1,9", "4,3 1,6 5,9"],
"l": ["2,0 2,9", "1,9 3,9"],
"m": ["1,9 1,3 2,3 3,4 3,9", "3,4 4,3 5,4 5,9"],
"n": ["1,9 1,3 2,3 4,3 5,4 5,9"],
"o": ["2,3 4,3 5,4 5,8 4,9 2,9 1,8 1,4 2,3"],
"p": ["1,3 1,12", "1,6 1,9 2,9 4,9 5,8 5,4 4,3 2,3 1,4"],
"q": ["5,3 5,12", "5,6 5,9 4,9 2,9 1,8 1,4 2,3 4,3 5,4"],
"r": ["1,3 1,9", "1,4 2,3 4,3 5,4"],
"s": ["5,4 4,3 2,3 1,4 1,5 2,6 4,6 5,7 5,8 4,9 2,9 1,8"],
"t": ["3,0 3,9 4,9", "1,4 4,4"],
"u": ["1,3 1,8 2,9 4,9 5,8 5,3"],
"v": ["1,3 3,9 5,3"],
"w": ["1,3 2,9 3,6 4,9 5,3"],
"x": ["1,3 5,9", "5,3 1,9"],
"y": ["1,3 3,8 5,3", "3,8 3,12 2,12"],
"z": ["1,3 5,3 1,9 5,9"],
"0": ["2,0 4,0 5,2 5,7 4,9 2,9 1,7 1,2 2,0"],
"1": ["2,2 3,0 3,9", "1,9 5,9"],
"2": ["1,1 2,0 4,0 5,1 5,3 4,5 1,9 5,9"],
"3": ["1,1 2,0 4,0 5,1 5,4 4,5 2,5", "4,5 5,6 5,8 4,9 2,9 1,8"],
"4": ["1,0 1,6 5,6", "4,0 4,9"],
"5": ["5,0 1,0 1,4 3,4 5,5 5,8 4,9 2,9 1,8"],
"6": ["5,0 4,0 2,0 1,2 1,7 2,9 4,9 5,8 5,6 4,5 2,5"],
"7": ["1,0 5,0 2,9"],
"8": ["1,3 1,1 2,0 4,0 5,1 5,3 4,4 2,4 1,3", "1,6 1,7 2,9 4,9 5,8 5,6 4,5 2,5 1,6"],
"9": ["5,9 5,1 4,0 2,0 1,1 1,3 2,4 4,4 5,3", "5,4 5,8 4,9 2,9 1,8"],
".": ["2,8 3,8"],
",": ["2,8 3,8", "3,9 2,11"],
":": ["2,2 3,2", "2,7 3,7"],
";": ["2,2 3,2", "2,7 3,7", "3,8 2,11"],
"!": ["3,0 3,6", "3,8 3,9"],
"?": ["1,2 2,0 4,0 5,1 5,3 4,4 3,5 3,6", "3,8 3,9"],
"'": ["2,0 3,2"],
'"': ["2,0 2,2", "4,0 4,2"],
"-": ["1,5 5,5"],
"(": ["3,0 2,2 1,4 1,6 2,8 3,9"],
")": ["0,0 1,2 2,4 2,6 1,8 0,9"],
"/": ["5,0 1,9"],
"&": ["5,0 4,0 2,1 1,3 1,5 2,6 4,6 5,7 5,9 4,9 2,9 1,8"],
"%": ["1,0 2,0 2,2 1,2 1,0", "5,0 1,9", "4,7 5,7 5,9 4,9 4,7"],
"+": ["3,2 3,7", "1,4 5,4"],
"=": ["1,3 5,3", "1,6 5,6"],
"$": ["3,0 3,9", "5,1 4,0 2,0 1,1 1,3 2,4 4,4 5,5 5,7 4,9 2,9 1,8"],
"#": ["2,0 2,9", "4,0 4,9", "0,3 6,3", "0,6 6,6"],
"*": ["3,1 3,6", "1,2 5,5", "5,2 1,5"],
"_": ["0,10 6,10"],
"·": ["2,4 3,4"],
}

def _pts(stroke):
    return [tuple(int(v) for v in p.split(",")) for p in stroke.split()]

VF = {ch: [_pts(s) for s in strokes] for ch, strokes in FONT_SRC.items()}
NARROW = {" ": 4, "i": 4, "j": 4, "l": 4, "t": 4, "f": 4, "'": 3, ".": 4,
          ",": 4, ":": 4, ";": 4, "!": 4, '"': 5, "-": 5, "(": 4, ")": 4,
          "/": 4, "·": 4, "I": 4, "r": 5}

def adv(ch):
    return NARROW.get(ch, 7)

def text_w(s, scale):
    return sum(adv(ch) for ch in s) * scale

# --- pixel buffer ---
buf = bytearray(W * H * 3)

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(c)

def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            buf[base + (xx - x0) * 3: base + (xx - x0) * 3 + 3] = bytes(c)

def hline(x, y, w, c):
    rect(x, y, w, 1, c)

def vline(x, y, h, c):
    rect(x, y, 1, h, c)

def line(x0, y0, x1, y1, w, c):
    # Bresenham with a square brush of side w.
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    r = w // 2
    while True:
        if w <= 1:
            px(x0, y0, c)
        else:
            rect(x0 - r, y0 - r, w, w, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def circle(cx, cy, r, c, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill:
                if d2 <= r * r:
                    px(xx, yy, c)
            else:
                if r * r - 2 * r <= d2 <= r * r:
                    px(xx, yy, c)

def tri(x1, y1, x2, y2, x3, y3, c):
    ys = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = ys
    def edge(xa, ya, xb, yb, y):
        if yb == ya:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)
    for y in range(ay, cy + 1):
        if y < by:
            xa = edge(ax, ay, bx, by, y)
            xb = edge(ax, ay, cx, cy, y)
        else:
            xa = edge(bx, by, cx, cy, y)
            xb = edge(ax, ay, cx, cy, y)
        x0, x1 = int(min(xa, xb)), int(max(xa, xb))
        hline(x0, y, x1 - x0 + 1, c)

def poly(points, c):
    # filled polygon via triangle fan
    if len(points) < 3:
        return
    x0, y0 = points[0]
    for i in range(1, len(points) - 1):
        tri(x0, y0, points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], c)

def text(s, x, y, scale, c, w=None, bold=False):
    # y = top of cap height. Returns end x.
    width = w if w is not None else max(1, round(scale * 0.24))
    if bold:
        width += 1
    cx = x
    for ch in s:
        strokes = VF.get(ch)
        if strokes is None:
            cx += adv(ch) * scale
            continue
        for pts in strokes:
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                line(int(round(cx + ax * scale)), int(round(y + ay * scale)),
                     int(round(cx + bx * scale)), int(round(y + by * scale)), width, c)
        cx += adv(ch) * scale
    return cx

def wrap(s, scale, width):
    lines, cur = [], ""
    for word in s.split(" "):
        t = word if not cur else cur + " " + word
        if text_w(t, scale) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def para(s, x, y, scale, width, c, lh=None, w=None, bold=False, max_lines=None):
    lh = lh or int(round(11 * scale)) + 3
    lines = wrap(s, scale, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        text(ln, x, y, scale, c, w=w, bold=bold)
        y += lh
    return y

def fit(s, scale, width):
    # shorten with ".." until it fits (deterministic)
    if text_w(s, scale) <= width:
        return s
    while len(s) > 4 and text_w(s + "..", scale) > width:
        s = s[:-1]
    return s + ".."

def centre(s, y, scale, c, w=None, bold=False):
    text(s, int((W - text_w(s, scale)) // 2), y, scale, c, w=w, bold=bold)

# --- colours ---
PAPER = (247, 242, 228)
CARD = (252, 249, 240)
INK = (26, 26, 26)
RED = (178, 34, 34)
NAVY = (24, 48, 90)
GOLD = (184, 134, 11)
GREY = (96, 96, 96)
LGREY = (150, 150, 150)
WHITE = (255, 255, 255)
SKY = (186, 219, 233)
SEA = (176, 214, 228)
LAND = (233, 216, 172)
LANDLINE = (196, 176, 128)
CAT = {"EUROPE": (38, 84, 160), "MIDDLE EAST": (178, 96, 30),
       "ASIA": (14, 120, 110), "AMERICAS": (178, 34, 34),
       "AFRICA": (34, 120, 60), "OCEANIA": (102, 45, 145),
       "GLOBAL": (90, 90, 90), "MARKETS": (20, 90, 50),
       "TECH": (60, 60, 140), "SPORT": (150, 60, 140),
       "CULTURE": (120, 80, 20), "WEATHER": (40, 110, 160),
       "HEALTH": (170, 40, 90), "US": (178, 34, 34)}

# --- small drawing helpers ---
def flag(x, y, w, h, stripes, pole=True):
    if pole:
        vline(x, y - 8, h + 8, (60, 60, 60))
        circle(x, y - 9, 2, GOLD)
    band = max(1, h // len(stripes))
    for i, c in enumerate(stripes):
        rect(x + 1, y + i * band, w, band if i < len(stripes) - 1 else h - i * band, c)

def person(x, y, s, suit, skin=(232, 190, 150), hair=(40, 40, 40)):
    circle(x, y, int(0.45 * s), skin)
    rect(x - int(0.45 * s), y - int(0.45 * s) - 2, int(0.9 * s), 3, hair)
    rect(x - int(0.6 * s), y + int(0.5 * s), int(1.2 * s), int(1.5 * s), suit)
    line(x, y + int(0.5 * s), x, y + int(1.7 * s), 1, WHITE)

def skyline(x, ybase, w, h, c, seed):
    # deterministic skyline: buildings from a fixed pattern
    bx = x
    i = 0
    while bx < x + w - 8:
        bw = 8 + (seed + i * 7) % 14
        bh = int(h * (0.35 + ((seed + i * 13) % 60) / 100.0))
        rect(bx, ybase - bh, bw, bh, c)
        for wy in range(ybase - bh + 4, ybase - 4, 8):
            for wx in range(bx + 2, bx + bw - 2, 5):
                if (wx + wy) % 11 < 4:
                    rect(wx, wy, 2, 3, (255, 220, 120))
        bx += bw + 2
        i += 1

def scene(x, y, w, h, kind):
    # one flat hand-drawn illustration inside (x, y, w, h)
    if kind == "base":
        rect(x, y, w, h, (214, 226, 235))
        rect(x, y + int(h * 0.62), w, h - int(h * 0.62), (222, 205, 160))
        rect(x, y + int(h * 0.55), w, 5, (120, 120, 120))
        rect(x + 8, y + int(h * 0.30), 34, int(h * 0.32), (90, 96, 104))
        rect(x + 14, y + int(h * 0.36), 22, int(h * 0.26), (60, 64, 72))
        line(x + 60, y + 12, x + w - 70, y + int(h * 0.45), 2, (70, 70, 70))
        tri(x + w - 78, y + int(h * 0.42), x + w - 58, y + int(h * 0.42),
            x + w - 68, y + int(h * 0.52), (70, 70, 70))
        circle(x + w - 30, y + 22, 10, (240, 120, 30))
        circle(x + w - 30, y + 22, 6, (250, 200, 60))
        circle(x + w - 52, y + 34, 6, (120, 120, 120))
        circle(x + w - 64, y + 26, 4, (140, 140, 140))
    elif kind == "summit":
        rect(x, y, w, h, (200, 220, 235))
        skyline(x, y + int(h * 0.55), w, int(h * 0.45), (70, 90, 120), 3)
        rect(x + 10, y + int(h * 0.72), w - 20, 7, (120, 72, 32))
        rect(x + 16, y + int(h * 0.72) + 7, 4, int(h * 0.22), (90, 54, 24))
        rect(x + w - 20, y + int(h * 0.72) + 7, 4, int(h * 0.22), (90, 54, 24))
        flag(x + 22, y + 8, 22, 13, [(200, 20, 20), (200, 20, 20)])
        flag(x + w // 2 - 11, y + 8, 22, 13,
             [(190, 40, 40), (255, 255, 255), (190, 40, 40), (255, 255, 255),
              (190, 40, 40), (255, 255, 255), (190, 40, 40)])
        flag(x + w - 46, y + 8, 22, 13, [(255, 255, 255), (30, 80, 190), (200, 20, 20)])
        person(x + 52, y + int(h * 0.55), 9, (30, 30, 60))
        person(x + w // 2, y + int(h * 0.55), 9, (120, 20, 20))
        person(x + w - 52, y + int(h * 0.55), 9, (30, 60, 90))
    elif kind == "quad":
        rect(x, y, w, h, (220, 210, 235))
        skyline(x, y + int(h * 0.55), w, int(h * 0.45), (90, 70, 130), 7)
        rect(x + 8, y + int(h * 0.74), w - 16, 6, (110, 60, 30))
        flag(x + 14, y + 6, 18, 11,
             [(190, 40, 40), (255, 255, 255), (190, 40, 40), (255, 255, 255), (190, 40, 40)])
        flag(x + 62, y + 6, 18, 11, [(255, 153, 51), (255, 255, 255), (19, 136, 8)])
        flag(x + 110, y + 6, 18, 11, [(255, 255, 255)])
        circle(x + 119, y + 11, 3, (190, 30, 30))
        flag(x + 158, y + 6, 18, 11, [(0, 40, 120)])
        person(x + 40, y + int(h * 0.58), 8, (30, 30, 60))
        person(x + 88, y + int(h * 0.58), 8, (120, 20, 20))
        person(x + 136, y + int(h * 0.58), 8, (30, 60, 90))
        person(x + 184, y + int(h * 0.58), 8, (20, 90, 60))
    elif kind == "gaza":
        rect(x, y, w, h, (232, 226, 210))
        for i, bh in enumerate([52, 70, 44, 62]):
            bx = x + 10 + i * 52
            rect(bx, y + h - 18 - bh, 42, bh, (150, 148, 140))
            for wy in range(y + h - 18 - bh + 6, y + h - 22, 12):
                rect(bx + 6, wy, 8, 7, (70, 70, 70))
                rect(bx + 26, wy, 8, 7, (70, 70, 70))
        circle(x + w - 46, y + 26, 9, (120, 120, 120))
        circle(x + w - 30, y + 18, 6, (140, 140, 140))
        rect(x + 18, y + h - 26, 44, 10, (240, 240, 240))
        rect(x + 62, y + h - 30, 26, 14, (40, 110, 180))
        circle(x + 28, y + h - 13, 4, (40, 40, 40))
        circle(x + 54, y + h - 13, 4, (40, 40, 40))
        circle(x + 80, y + h - 13, 4, (40, 40, 40))
    elif kind == "storm":
        rect(x, y, w, h, (70, 90, 110))
        rect(x, y + int(h * 0.66), w, h - int(h * 0.66), (40, 80, 110))
        for r, c in [(26, WHITE), (19, (200, 220, 235)), (12, WHITE), (6, (200, 220, 235))]:
            circle(x + w // 2, y + int(h * 0.36), r, c, fill=False)
        for i in range(8):
            lx = x + 12 + i * 26
            line(lx, y + 12, lx - 8, y + 34, 1, (200, 220, 235))
        rect(x, y + int(h * 0.66), 60, 10, (222, 205, 160))
    elif kind == "chip":
        rect(x, y, w, h, (30, 34, 44))
        rect(x + w // 2 - 26, y + h // 2 - 20, 52, 40, (20, 120, 70))
        rect(x + w // 2 - 16, y + h // 2 - 10, 32, 20, (40, 180, 110))
        for i in range(5):
            rect(x + w // 2 - 32, y + h // 2 - 16 + i * 8, 6, 3, GOLD)
            rect(x + w // 2 + 26, y + h // 2 - 16 + i * 8, 6, 3, GOLD)
        line(x + 12, y + h - 16, x + 60, y + h - 34, 2, (60, 220, 130))
        line(x + 60, y + h - 34, x + 110, y + h - 44, 2, (60, 220, 130))
        line(x + 110, y + h - 44, x + w - 14, y + h - 60, 2, (60, 220, 130))
        tri(x + w - 14, y + h - 60, x + w - 22, y + h - 58, x + w - 16, y + h - 50, (60, 220, 130))
    elif kind == "refinery":
        rect(x, y, w, h, (240, 220, 190))
        rect(x + 12, y + h - 44, 16, 44, (120, 120, 120))
        rect(x + 34, y + h - 58, 12, 58, (140, 140, 140))
        rect(x + 52, y + h - 36, 60, 36, (110, 110, 110))
        circle(x + 130, y + 26, 12, (240, 120, 30))
        circle(x + 130, y + 26, 7, (250, 200, 60))
        tri(x + 130, y + 8, x + 122, y + 24, x + 138, y + 24, (240, 90, 20))
        circle(x + 160, y + 18, 8, (130, 130, 130))
        circle(x + 176, y + 12, 5, (150, 150, 150))
    elif kind == "court":
        rect(x, y, w, h, (235, 230, 220))
        for i in range(3):
            cx = x + 26 + i * 66
            rect(cx - 14, y + 16, 28, 6, (240, 240, 235))
            rect(cx - 8, y + 22, 16, int(h * 0.55), (245, 245, 240))
            rect(cx - 14, y + 22 + int(h * 0.55), 28, 6, (240, 240, 235))
        rect(x + w // 2 - 22, y + h - 22, 44, 6, (120, 72, 32))
        rect(x + w // 2 + 6, y + h - 34, 30, 5, (120, 72, 32))
    elif kind == "game":
        rect(x, y, w, h, (20, 20, 50))
        circle(x + w - 30, y + 18, 9, (240, 230, 180))
        skyline(x, y + h - 14, w, int(h * 0.5), (8, 8, 20), 11)
        text("VI", x + 14, y + 12, 3.2, GOLD, w=2, bold=True)
        line(x + 10, y + h - 40, x + w - 10, y + h - 40, 1, (120, 80, 200))
    elif kind == "ipo":
        rect(x, y, w, h, (245, 240, 230))
        rect(x + 16, y + 14, 60, int(h * 0.6), (60, 80, 120))
        for wy in range(y + 22, y + 14 + int(h * 0.6) - 6, 10):
            rect(x + 24, wy, 10, 6, (255, 220, 120))
            rect(x + 42, wy, 10, 6, (255, 220, 120))
        line(x + 84, y + h - 18, x + 130, y + h - 44, 2, (20, 140, 70))
        line(x + 130, y + h - 44, x + 176, y + h - 58, 2, (20, 140, 70))
        tri(x + 176, y + h - 58, x + 168, y + h - 54, x + 176, y + h - 48, (20, 140, 70))
        text("$", x + 96, y + 10, 2.0, (20, 140, 70), w=2, bold=True)
    elif kind == "market":
        rect(x, y, w, h, (245, 240, 230))
        line(x + 10, y + 14, x + w - 10, y + h - 14, 2, (190, 30, 30))
        for i, bh in enumerate([10, 16, 12, 22, 18]):
            bx = x + 22 + i * 34
            rect(bx, y + 20 + i * 6, 14, bh, (190, 30, 30))
            vline(bx + 7, y + 14 + i * 6, bh + 12, (190, 30, 30))
        text("-1.1%", x + 12, y + 8, 1.1, (190, 30, 30), bold=True)
    elif kind == "train":
        rect(x, y, w, h, (214, 226, 235))
        rect(x + 8, y + 26, 84, 26, (40, 90, 180))
        rect(x + 100, y + 26, 84, 26, (240, 200, 40))
        for wx in range(x + 16, x + 84, 18):
            rect(wx, y + 32, 10, 10, WHITE)
        for wx in range(x + 108, x + 176, 18):
            rect(wx, y + 32, 10, 10, (40, 40, 40))
        line(x + 92, y + 26, x + 100, y + 52, 2, (60, 60, 60))
        line(x + 96, y + 20, x + 92, y + 30, 1, (250, 200, 60))
        line(x + 96, y + 20, x + 104, y + 28, 1, (250, 200, 60))
        rect(x, y + 56, w, 5, (120, 120, 120))
    elif kind == "screen":
        rect(x, y, w, h, (30, 40, 70))
        rect(x + 22, y + 10, w - 44, int(h * 0.6), (10, 14, 26))
        rect(x + 28, y + 16, w - 56, int(h * 0.6) - 12, (120, 200, 230))
        tri(x + w // 2, y + 22, x + w // 2 - 12, y + 44, x + w // 2 + 12, y + 44, (240, 180, 20))
        text("!", x + w // 2 - 3, y + 26, 1.4, (120, 20, 20), bold=True)
        for i in range(4):
            rect(x + 30 + i * 34, y + h - 18, 26, 5, (200, 60, 60))
    elif kind == "code":
        rect(x, y, w, h, (28, 28, 40))
        for i, cc in enumerate([(120, 200, 120), (240, 200, 90), (140, 180, 250), (120, 200, 230)]):
            rect(x + 14, y + 10 + i * 13, 60 + i * 22, 6, cc)
        rect(x + w - 52, y + 10, 38, 44, (20, 140, 90))
        text("9.2", x + w - 48, y + 20, 1.2, WHITE, bold=True)
    elif kind == "bridge":
        rect(x, y, w, h, SKY)
        rect(x, y + int(h * 0.62), w, h - int(h * 0.62), (60, 130, 190))
        rect(x + 6, y + int(h * 0.34), 78, 8, (120, 120, 120))
        line(x + 88, y + int(h * 0.34), x + 108, y + int(h * 0.52), 3, (120, 120, 120))
        rect(x + 110, y + int(h * 0.52), 76, 8, (120, 120, 120))
        vline(x + 20, y + int(h * 0.34), int(h * 0.30), (90, 90, 90))
        vline(x + 150, y + int(h * 0.52), int(h * 0.14), (90, 90, 90))
        circle(x + w - 30, y + 20, 7, (130, 130, 130))
        for i in range(4):
            line(x + 14 + i * 46, y + int(h * 0.72), x + 34 + i * 46, y + int(h * 0.72), 1, WHITE)
    elif kind == "virus":
        rect(x, y, w, h, (250, 240, 235))
        cx, cy = x + w // 2, y + h // 2
        for a in range(0, 360, 30):
            import math as _m
            ex = cx + int(30 * _m.cos(a * 3.14159 / 180))
            ey = cy + int(30 * _m.sin(a * 3.14159 / 180))
            line(cx, cy, ex, ey, 2, (190, 40, 40))
        circle(cx, cy, 22, (200, 50, 50))
        circle(cx - 6, cy - 6, 5, (240, 120, 120))
        circle(cx + 7, cy + 5, 4, (240, 120, 120))
        text("5,400+", x + 10, y + 8, 1.0, (170, 40, 90), bold=True)

def mini_scene(x, y, w, h, kind):
    # small panoramic icon strip for grid cells; every shape stays in the box
    if kind == "storm":
        rect(x, y, w, h, (70, 90, 110))
        rect(x, y + int(h * 0.66), w, h - int(h * 0.66), (40, 80, 110))
        for r in (11, 8, 5):
            circle(x + 30, y + int(h * 0.38), r, WHITE, fill=False)
        for i in range(6):
            lx = x + 60 + i * 26
            line(lx, y + 6, lx - 6, y + 18, 1, (200, 220, 235))
        rect(x + w - 70, y + int(h * 0.66), 60, 8, (222, 205, 160))
    elif kind == "chip":
        rect(x, y, w, h, (30, 34, 44))
        rect(x + 20, y + 6, 26, 18, (20, 120, 70))
        rect(x + 26, y + 11, 14, 8, (40, 180, 110))
        for i in range(3):
            rect(x + 14, y + 9 + i * 6, 6, 2, GOLD)
            rect(x + 46, y + 9 + i * 6, 6, 2, GOLD)
        line(x + 70, y + h - 8, x + 120, y + 12, 2, (60, 220, 130))
        line(x + 120, y + 12, x + w - 16, y + 6, 2, (60, 220, 130))
    elif kind == "refinery":
        rect(x, y, w, h, (240, 220, 190))
        rect(x + 16, y + 12, 12, 18, (120, 120, 120))
        rect(x + 32, y + 6, 10, 24, (140, 140, 140))
        rect(x + 48, y + 16, 50, 14, (110, 110, 110))
        circle(x + 130, y + 12, 7, (240, 120, 30))
        circle(x + 130, y + 12, 4, (250, 200, 60))
        circle(x + 160, y + 10, 5, (130, 130, 130))
        line(x + 180, y + 20, x + w - 12, y + 20, 1, (90, 90, 90))
    elif kind == "court":
        rect(x, y, w, h, (225, 220, 208))
        for i in range(4):
            cx = x + 30 + i * 52
            rect(cx - 10, y + 4, 20, 3, (140, 135, 125))
            rect(cx - 6, y + 7, 12, 16, (248, 246, 238))
            vline(cx - 6, y + 7, 16, (150, 145, 135))
            vline(cx + 5, y + 7, 16, (150, 145, 135))
            rect(cx - 10, y + 23, 20, 3, (140, 135, 125))
        rect(x + w - 30, y + 20, 22, 3, (120, 72, 32))
    elif kind == "game":
        rect(x, y, w, h, (20, 20, 50))
        circle(x + w - 24, y + 8, 5, (240, 230, 180))
        skyline(x, y + h - 4, w, int(h * 0.55), (8, 8, 20), 11)
        text("VI", x + 12, y + 6, 1.4, GOLD, w=2, bold=True)
        line(x + 8, y + h - 6, x + w - 8, y + h - 6, 1, (120, 80, 200))
    elif kind == "ipo":
        rect(x, y, w, h, (245, 240, 230))
        rect(x + 14, y + 6, 34, 20, (60, 80, 120))
        for wy in (10, 17, 24):
            rect(x + 19, wy, 8, 4, (255, 220, 120))
            rect(x + 32, wy, 8, 4, (255, 220, 120))
        line(x + 62, y + h - 6, x + 120, y + 12, 2, (20, 140, 70))
        line(x + 120, y + 12, x + w - 14, y + 6, 2, (20, 140, 70))
        text("$", x + 66, y + 4, 1.4, (20, 140, 70), w=2, bold=True)
    elif kind == "market":
        rect(x, y, w, h, (245, 240, 230))
        line(x + 10, y + 6, x + w - 10, y + h - 6, 2, (190, 30, 30))
        for i, bh in enumerate([6, 9, 7, 12, 10]):
            bx = x + 24 + i * 38
            rect(bx, y + 8 + i * 2, 12, bh, (190, 30, 30))
    elif kind == "train":
        rect(x, y, w, h, (214, 226, 235))
        rect(x + 14, y + 8, 70, 14, (40, 90, 180))
        rect(x + 92, y + 8, 70, 14, (240, 200, 40))
        for wx in range(x + 20, x + 76, 16):
            rect(wx, y + 11, 8, 6, WHITE)
        for wx in range(x + 98, x + 154, 16):
            rect(wx, y + 11, 8, 6, (40, 40, 40))
        line(x + 84, y + 8, x + 92, y + 22, 2, (60, 60, 60))
        line(x + 88, y + 4, x + 84, y + 10, 1, (250, 200, 60))
        line(x + 88, y + 4, x + 94, y + 10, 1, (250, 200, 60))
        rect(x, y + h - 5, w, 3, (120, 120, 120))
    elif kind == "screen":
        rect(x, y, w, h, (30, 40, 70))
        rect(x + 16, y + 4, 70, 20, (10, 14, 26))
        rect(x + 20, y + 7, 62, 14, (120, 200, 230))
        tri(x + 51, y + 9, x + 43, y + 19, x + 59, y + 19, (240, 180, 20))
        text("!", x + 49, y + 10, 0.9, (120, 20, 20), bold=True)
        for i in range(5):
            rect(x + 100 + i * 26, y + h - 8, 20, 3, (200, 60, 60))
    elif kind == "code":
        rect(x, y, w, h, (28, 28, 40))
        for i, cc in enumerate([(120, 200, 120), (240, 200, 90), (140, 180, 250)]):
            rect(x + 14, y + 5 + i * 8, 70 + i * 30, 4, cc)
        rect(x + w - 46, y + 4, 34, 22, (20, 140, 90))
        text("9.2", x + w - 42, y + 9, 1.0, WHITE, bold=True)
    elif kind == "bridge":
        rect(x, y, w, h, SKY)
        rect(x, y + int(h * 0.62), w, h - int(h * 0.62), (60, 130, 190))
        rect(x + 10, y + 8, 70, 5, (120, 120, 120))
        line(x + 80, y + 8, x + 96, y + 18, 2, (120, 120, 120))
        rect(x + 96, y + 18, 70, 5, (120, 120, 120))
        circle(x + w - 26, y + 8, 4, (130, 130, 130))
        for i in range(4):
            line(x + 14 + i * 50, y + int(h * 0.76), x + 30 + i * 50, y + int(h * 0.76), 1, WHITE)
    elif kind == "virus":
        rect(x, y, w, h, (250, 240, 235))
        cx, cy = x + 30, y + h // 2
        for a in range(0, 360, 45):
            import math as _m
            ex = cx + int(13 * _m.cos(a * 3.14159 / 180))
            ey = cy + int(13 * _m.sin(a * 3.14159 / 180))
            line(cx, cy, ex, ey, 1, (190, 40, 40))
        circle(cx, cy, 9, (200, 50, 50))
        circle(cx - 3, cy - 3, 2, (240, 120, 120))
        for i in range(5):
            circle(x + 70 + i * 30, y + 8 + (i % 2) * 12, 3, (190, 40, 40))

# --- world map (normalized 0..100 x 0..62) ---
CONTINENTS = [
    [(2, 10), (12, 4), (24, 3), (30, 7), (28, 14), (24, 18), (20, 24), (14, 27), (8, 24), (4, 18)],
    [(31, 2), (37, 2), (36, 7), (31, 7)],
    [(24, 30), (31, 29), (36, 34), (35, 42), (30, 51), (26, 50), (23, 40)],
    [(45, 7), (52, 5), (58, 7), (57, 12), (53, 15), (47, 14), (44, 10)],
    [(46, 19), (58, 18), (63, 24), (60, 34), (55, 44), (51, 45), (47, 34), (45, 26)],
    [(59, 5), (74, 3), (88, 4), (96, 8), (94, 15), (88, 19), (80, 24), (73, 22), (68, 16), (62, 12), (59, 9)],
    [(80, 24), (86, 24), (84, 28), (79, 27)],
    [(81, 43), (93, 42), (96, 47), (88, 51), (82, 48)],
]
# (nx, ny, region colour, story number)
PINS = [
    (66, 17, "MIDDLE EAST", 1), (87, 17, "ASIA", 2), (89, 21, "ASIA", 3),
    (58, 15, "MIDDLE EAST", 4), (76, 20, "ASIA", 5), (13, 14, "AMERICAS", 6),
    (52, 6, "EUROPE", 7), (60, 13, "EUROPE", 8), (45, 7, "EUROPE", 9),
    (12, 11, "AMERICAS", 10), (20, 13, "MARKETS", 11), (49, 11, "EUROPE", 12),
    (19, 15, "US", 13), (88, 11, "ASIA", 14), (58, 8, "EUROPE", 15),
    (14, 18, "HEALTH", 16),
]
# unnumbered dots: (nx, ny, region)
DOTS = [
    (24, 33, "AMERICAS"), (70, 30, "ASIA"), (54, 30, "AFRICA"),
    (84, 30, "ASIA"), (16, 44, "OCEANIA"), (48, 22, "AFRICA"),
    (30, 12, "AMERICAS"), (92, 47, "OCEANIA"), (63, 12, "MIDDLE EAST"),
    (76, 7, "ASIA"),
]

def draw_map(mx, my, mw, mh):
    rect(mx, my, mw, mh, SEA)
    s = min(mw / 100.0, mh / 62.0)
    ox = mx + (mw - 100 * s) / 2
    oy = my + (mh - 62 * s) / 2
    for cont in CONTINENTS:
        pts = [(int(ox + px_ * s), int(oy + py_ * s)) for px_, py_ in cont]
        poly(pts, LAND)
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            line(ax, ay, bx, by, 1, LANDLINE)
    for nx, ny, reg in DOTS:
        circle(int(ox + nx * s), int(oy + ny * s), 3, CAT[reg])
    for nx, ny, reg, num in PINS:
        cx, cy = int(ox + nx * s), int(oy + ny * s)
        r = 7 if num >= 10 else 6
        circle(cx, cy, r, CAT[reg])
        circle(cx, cy, r, INK, fill=False)
        ns = str(num)
        text(ns, cx - int(text_w(ns, 0.62) // 2), cy - 4, 0.62, WHITE, bold=True)

# --- the day's news: 46 stories, first reported on 18 November 2026 ---
# LEADS: (number, region, tag, headline, summary, source, scene)
LEADS = [
    (1, "MIDDLE EAST", "CLAIM - REUTERS",
     "Iran strikes US base in Kuwait",
     "Drones hit Ali Al Salem air base; Gulf states intercept missiles and drones.",
     "Reuters", "base"),
    (2, "ASIA", "CONFIRMED - AP",
     "Trump lands in China for Xi-Putin talks",
     "Trilateral meeting in Shenzhen; Xi and Putin denounce Western sanctions.",
     "AP", "summit"),
    (3, "ASIA", "CONFIRMED - AP",
     "Quad leaders meet in Manila",
     "First leaders' meeting in over two years; Trump seals a trade and defence deal.",
     "AP", "quad"),
    (4, "MIDDLE EAST", "CONFIRMED - ANADOLU",
     "Israel opens new Gaza operation",
     "Army begins a 'concentrated operation' in three areas of central Gaza.",
     "Anadolu", "gaza"),
]

# GRID: (number, region, tag, headline, summary, source, scene)
GRID = [
    (5, "WEATHER", "CONFIRMED",
     "Cyclone Akvan bears down on Odisha",
     "Storm strengthens to a severe cyclone; people moved to shelters.",
     "Reuters", "storm"),
    (6, "TECH", "CONFIRMED",
     "Nvidia beats; Huang will not return",
     "Bumper results; board says former chief will not be reinstated.",
     "Reuters", "chip"),
    (7, "EUROPE", "CLAIM - REUTERS",
     "Ukraine drones cut Russian refining by 45%",
     "Daily processing fell to ~400,000t; 15 of 35 refineries hit.",
     "Reuters", "refinery"),
    (8, "EUROPE", "CONFIRMED",
     "Imamoglu gets 2 more years and a new ban",
     "Mayor jailed 2 years 1 month over 2023 CHP convention case.",
     "Reuters", "court"),
    (9, "TECH", "CONFIRMED",
     "GTA VI launches at midnight",
     "Out 19 Nov at midnight local time on PS5 and Xbox Series X|S.",
     "USA Today", "game"),
    (10, "TECH", "CONFIRMED",
     "Anthropic IPO priced at $83 a share",
     "Claude maker valued at about $1.5tn; biggest debut on record.",
     "Reuters", "ipo"),
    (11, "MARKETS", "CONFIRMED",
     "Dow plunges 560 as Nasdaq snaps skid",
     "Dow -1.1%, S&P -0.2% for 5th day; Nasdaq +0.4% on Nvidia.",
     "Investopedia", "market"),
    (12, "EUROPE", "CONFIRMED",
     "Prague trains collide, 46 injured",
     "Two trains hit near main station; 4 seriously hurt, no deaths.",
     "Qatar Tribune", "train"),
    (13, "US", "CONFIRMED",
     "NSA network down in outage wave",
     "Classified network down after Microsoft, FAA and bank outages.",
     "Reuters", "screen"),
    (14, "TECH", "CONFIRMED",
     "Critical Java flaw rated 9.2, patch urged",
     "Java4Shell allows remote code execution; US, Korea urge fixes.",
     "Korea Times", "code"),
    (15, "EUROPE", "CLAIM - AFP",
     "Ukraine missile strike severs Crimea bridge",
     "Road span destroyed overnight; Zelensky calls it unprecedented.",
     "Dawn / AFP", "bridge"),
    (16, "US", "CONFIRMED",
     "US loses measles-free status as cases spike",
     "PAHO ends 26-year status; cases pass 5,400, 10 deaths reported.",
     "AFP / Dawn", "virus"),
]

# ALSO ON: (number, one-line brief) - kept short to fit one line per column
ALSO = [
    (17, "UK inflation hits 3.6% in October"),
    (18, "UniCredit seals Commerzbank deal"),
    (19, "Gold slides to over one-year low"),
    (20, "Oil falls as supply rises"),
    (21, "Bitcoin slides to $62,300"),
    (22, "Copper plunges 5.7% on AI unwind"),
    (23, "Waller floats half-point Fed hike"),
    (24, "Russia accuses France over troops"),
    (25, "EU proposes 45bn euros for Kyiv"),
    (26, "Serbia students enter parliament"),
    (27, "Thaci guilty of witness-tamper bid"),
    (28, "Russian An-12 crashes, 19 killed"),
    (29, "Bangladesh troops out over Hasina"),
    (30, "India-US trade deal nearly final"),
    (31, "IAEA backs US-Saudi nuclear deal"),
    (32, "IAEA: N. Korea expanding Yongbyon"),
    (33, "US strikes Iranian island in Hormuz"),
    (34, "Five tankers hit around Hormuz"),
    (35, "Saudi-led strikes kill 17 in Yemen"),
    (36, "Knesset elects new speaker"),
    (37, "Democrats win Alaska Senate race"),
    (38, "Thousands in Haiti praise Bukele"),
    (39, "Canary arrivals spike to 11,000"),
    (40, "Van Gogh sells for record $190.4m"),
    (41, "Alcaraz reaches ATP semis in Turin"),
    (42, "Chelsea beat PSG 1-0 in Women's UCL"),
    (43, "Duckett 133 seals England ODI win"),
    (44, "William and Kate meet Modi in Delhi"),
    (45, "Leasehold system set to be scrapped"),
    (46, "Magnitude 5.9 quake strikes Flores"),
]

TIMELINE = [
    ("Overnight", "Iran strikes Kuwait"),
    ("~06:00 UTC", "Trump lands in China"),
    ("09:30 UTC", "Quad opens in Manila"),
    ("~14:30 UTC", "Israel opens Gaza op"),
    ("Evening", "Nvidia beats; Dow slides"),
    ("Night", "GTA VI launches"),
]

def badge(x, y, num, col, r=9, scale=0.8):
    circle(x, y, r, col)
    ns = str(num)
    text(ns, x - int(text_w(ns, scale) // 2), y - int(4.5 * scale) - 1, scale, WHITE, bold=True)

def draw():
    rect(0, 0, W, H, PAPER)
    # outer frame
    rect(3, 3, W - 6, 2, INK)
    rect(3, H - 5, W - 6, 2, INK)
    rect(3, 3, 2, H - 6, INK)
    rect(W - 5, 3, 2, H - 6, INK)
    # ---- header ----
    centre("ONE DAY OF WORLD NEWS, ONE PICTURE", 16, 1.15, RED, bold=True)
    centre("Wednesday 18 November 2026", 34, 4.4, INK, w=3, bold=True)
    centre("46 STORIES · 7 REGIONS · EVERY ONE FROM THIS WEDNESDAY", 86, 1.15, INK, bold=True)
    hline(14, 108, W - 28, INK)
    # ---- UTC timeline ----
    rect(14, 116, 96, 44, RED)
    text("THE DAY", 24, 122, 1.0, WHITE, bold=True)
    text("IN UTC", 24, 138, 1.0, WHITE, bold=True)
    slot_w = (W - 28 - 110) // 6
    for i, (tm, label) in enumerate(TIMELINE):
        sx = 118 + i * slot_w
        if i:
            vline(sx - 4, 118, 40, LGREY)
        text(tm, sx, 118, 1.05, RED, bold=True)
        para(label, sx, 132, 0.95, slot_w - 12, INK, lh=12, max_lines=2)
    hline(14, 164, W - 28, INK)
    # ---- 4 leads ----
    lw, lgap, ly, lh = 241, 8, 170, 248
    for i, (num, reg, tag, head, sub, src, kind) in enumerate(LEADS):
        x = 14 + i * (lw + lgap)
        col = CAT.get(reg, INK)
        scene(x, ly, lw, 100, kind)
        rect(x, ly + 100, lw, 2, col)
        badge(x + 11, ly + 120, num, col)
        text(reg, x + 24, ly + 113, 0.85, col, bold=True)
        text(tag, x + lw - int(text_w(tag, 0.75)), ly + 113, 0.75, GREY)
        y = para(head, x, ly + 130, 1.45, lw, INK, lh=17, bold=True, max_lines=3)
        y = para(sub, x, y + 4, 1.05, lw, GREY, lh=13, max_lines=3)
        text("Source: " + src, x, ly + lh - 14, 0.85, GREY)
    hline(14, 424, W - 28, INK)
    # ---- 12-item grid ----
    gw, ggap, gy, gh = 241, 6, 432, 100
    for i, (num, reg, tag, head, sub, src, kind) in enumerate(GRID):
        x = 14 + (i % 4) * (gw + ggap)
        y = gy + (i // 4) * (gh + ggap)
        col = CAT.get(reg, INK)
        mini_scene(x, y, gw, 30, kind)
        rect(x, y + 30, gw, 2, col)
        badge(x + 8, y + 39, num, col, r=7, scale=0.65)
        text(reg, x + 18, y + 34, 0.8, col, bold=True)
        text(tag, x + gw - int(text_w(tag, 0.7)), y + 34, 0.7, GREY)
        y2 = para(head, x, y + 50, 1.12, gw, INK, lh=13, bold=True, max_lines=2)
        para(sub + " (" + src + ")", x, y2 + 2, 0.86, gw, GREY, lh=10, max_lines=2)
    hline(14, 746, W - 28, INK)
    # ---- map + also on ----
    text("WHERE IT HAPPENED", 14, 752, 1.1, RED, bold=True)
    draw_map(14, 772, 316, 132)
    lx = 14
    for j, (label, col) in enumerate([("Europe", "EUROPE"), ("Middle East", "MIDDLE EAST"),
                                      ("Asia", "ASIA"), ("Americas", "AMERICAS"),
                                      ("Africa", "AFRICA"), ("Oceania", "OCEANIA")]):
        jx = lx + (j % 3) * 108
        jy = 910 + (j // 3) * 13
        circle(jx + 4, jy + 4, 3, CAT[col])
        text(label, jx + 10, jy, 0.75, INK)
    text("ALSO ON WEDNESDAY 18 NOVEMBER", 344, 752, 1.1, RED, bold=True)
    colw = 215
    for k, (num, brief) in enumerate(ALSO):
        cx = 344 + (k // 10) * (colw + 7)
        cy = 772 + (k % 10) * 17
        badge(cx + 6, cy + 6, num, CAT["GLOBAL"], r=6, scale=0.55)
        text(fit(brief, 0.88, colw - 16), cx + 15, cy + 1, 0.88, INK)
        hline(cx + 15, cy + 14, colw - 16, (220, 212, 196))
    # ---- date check ----
    rect(14, 946, 92, 24, RED)
    text("DATE CHECK", 22, 952, 0.95, WHITE, bold=True)
    para("Left out on purpose because they broke before today: the Shenzhen trilateral "
         "was announced 17 Nov; Huang's Nvidia exit was decided 12-13 Nov; tankers hit "
         "in Hormuz 16 Nov. Not yet: the trilateral itself is Thursday 19 Nov; the "
         "COP31 final draft lands Friday.",
         116, 948, 0.95, W - 130, INK, lh=12, max_lines=2)
    # ---- footer ----
    centre("Every story here happened or was first reported on Wednesday 18 November 2026. "
           "CLAIM = one side's account, not independently confirmed.", 984, 0.9, INK)
    centre("Sources: Reuters, AP, AFP, BBC, Al Jazeera, Anadolu, Dawn, Bloomberg, ATP Tour. "
           "Original drawings.", 1000, 0.8, GREY)

def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return out

def main():
    draw()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png_bytes())

if __name__ == "__main__":
    main()
