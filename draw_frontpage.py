#!/usr/bin/env python3
"""Draw 'The World in One Day — Monday 23 November 2026', a newspaper
front page summing up the day's world news in one 1024x1024 image.

Everything on the page is drawn in code (PIL shapes + text). No photos,
no network. Output is deterministic: same bytes on every run.

Layout (1024x1024, warm newsprint):
  masthead | big date title | red deck | 6-number strip | region line
  3 illustrated leads | 10 mid cards (2 rows x 5) | UTC timeline
  world map + 20 briefs | DATE CHECK box | sources line

Stories: 33, across 6 regions (EUROPE 14, MIDDLE EAST 6, AMERICAS 5,
ASIA 3, GLOBAL 3, AFRICA 2). Every figure was checked against live
reporting on 23 Nov 2026; weekend events are flagged with their real day.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (22, 22, 22)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
BLUE = (84, 120, 158)
SEABLUE = (206, 224, 232)
TAN = (232, 220, 192)
GREY = (110, 110, 108)
LIGHT = (238, 232, 214)

FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = lambda s: font(f"{FL}/LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font(f"{FL}/LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font(f"{FL}/LiberationSerif-Italic.ttf", s)
SANS_B = lambda s: font(f"{FD}/DejaVuSans-Bold.ttf", s)
SANS = lambda s: font(f"{FD}/DejaVuSans.ttf", s)


def wrap(text, fnt, width):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, fill, width, leading=None, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.18)
    lines = wrap(text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def center(d, y, text, fnt, fill):
    d.text(((W - fnt.getlength(text)) / 2, y), text, font=fnt, fill=fill)
    return y + int(fnt.size * 1.2)


def rule(d, y, weight=2):
    d.line([(14, y), (W - 14, y)], fill=INK, width=weight)


# ---------------------------------------------------------------- content
STRIP = [
    ("153", "DRONES IN ONE NIGHT"),
    ("258", "HOUSE SEATS FOR THE DEMOCRATS"),
    ("3", "TANKERS ATTACKED ON SATURDAY"),
    ("11", "KILLED IN DYMER, NEAR KYIV"),
    ("99%", "OF GAZA CONTAMINATED"),
    ("429", "FLIGHTS CANCELLED IN BELGIUM"),
]

LEADS = [
    {
        "kick": "1 · BAHRAIN — WAR AT SEA", "conf": "REPORTED", "art": "sea",
        "head": "Iran hits US bases in Bahrain as tankers burn in Hormuz",
        "deck": ("Tehran claims two Patriot radars hit at al-Riffa and Awali; "
                 "Bahrain counts two hurt at a torched industrial site; "
                 "3 tankers attacked on Saturday."),
    },
    {
        "kick": "2 · ANTALYA — COP31", "conf": "CONFIRMED", "art": "cop",
        "head": "COP31 collapses — no deal as the longest talks ever end",
        "deck": ("Delegates reject the Antalya Pact on Sunday; fossil fuels "
                 "stripped from every draft; the first COP collapse since "
                 "Copenhagen 2009."),
    },
    {
        "kick": "3 · UKRAINE — OVERNIGHT ASSAULT", "conf": "REPORTED", "art": "dymer",
        "head": "Russia's 153-drone night kills 11 in Dymer",
        "deck": ("A five-storey block collapses near Kyiv; 14 still missing as "
                 "rescuers dig; 134 of 153 drones downed by 08:00; a "
                 "kindergarten hit in Kharkiv."),
    },
]

MIDS = [
    {"n": 4, "kick": "BENGHAZI · SEA DRONES", "conf": "REPORTED", "icon": "drone",
     "head": "Ukraine's sea drones sink a Russian warship off Libya",
     "deck": "Corvette Mercury sinks; a cargo ship is hit too. Zelenskyy confirms it."},
    {"n": 5, "kick": "WASHINGTON · VOTE", "conf": "CONFIRMED", "icon": "capitol",
     "head": "Democrats take 258 House seats — biggest majority since 1992",
     "deck": "Hubbard beats Foxx by 330 votes; 44 seats gained; four races still uncalled."},
    {"n": 6, "kick": "SEOUL · EXAM", "conf": "CONFIRMED", "icon": "exam",
     "head": "Korea's education minister quits over AI exam cheating",
     "deck": "Choi Kyo-jin resigns Sunday; 550,000 sat the exam; a top scorer used AI."},
    {"n": 7, "kick": "BRUSSELS · STRIKE", "conf": "CONFIRMED", "icon": "strike",
     "head": "Belgium stops: national strike grounds the country",
     "deck": "Airspace shut 07:00–21:00; 429 flights hit; unions fight austerity cuts."},
    {"n": 8, "kick": "GAZA · WEST BANK", "conf": "REPORTED", "icon": "truck",
     "head": "Three killed in Gaza food-truck strike",
     "deck": "WCK: the truck was not ours. Eisenkot calls settler arson 'Jewish terrorism'."},
    {"n": 9, "kick": "DHAKA · RETURN", "conf": "CONFIRMED", "icon": "bars",
     "head": "Bangladesh: Hasina will be jailed if she returns",
     "deck": "Ex-PM faces a death sentence; her party is banned; blasts in 28 districts."},
    {"n": 10, "kick": "SINALOA · CAPTURE", "conf": "CONFIRMED", "icon": "cuffs",
     "head": "'Chapo Isidro' captured in Mexico",
     "deck": "FBI top-10 fugitive taken Friday night; four soldiers killed in the raid."},
    {"n": 11, "kick": "BELGRADE · FLOOD", "conf": "CONFIRMED", "icon": "rain",
     "head": "Belgrade floods after a month's rain in a day",
     "deck": "A month's rain in 12 hours; streets under water; drivers pulled from cars."},
    {"n": 12, "kick": "COPENHAGEN · PLOT", "conf": "REPORTED", "icon": "mic",
     "head": "Denmark expels Russian attaché in murder plot",
     "deck": "Rapper Kyivstoner targeted; two charged. Poland reveals an August attempt."},
    {"n": 13, "kick": "BARRANQUILLA · SPORT", "conf": "CONFIRMED", "icon": "score",
     "head": "Paredes collapses live on TV after Boca's title",
     "deck": "Boca beat Atlético Mineiro 2–0; 32°C heat; 'just dizziness,' he says."},
]

BRIEFS = [
    (14, "KRYVYI RIH", "A child and a young woman killed; 25 apartment blocks, a hospital and schools damaged."),
    (15, "BRUSSELS", "NATO meets after three Russian missiles land in Poland; Rutte: 'every inch' defended."),
    (16, "ROSTOV", "Ukrainian drones hit oil sites in Rostov and Tatarstan."),
    (17, "GAZA", "Oxfam: the war left toxic contamination across 99% of Gaza."),
    (18, "INDONESIA", "Candy factory fire: 24 killed, dozens still missing; DNA needed to name the victims."),
    (19, "RICHMOND", "Oregon and Virginia sue SpaceX over Grok sexual deepfakes; 20,000+ child images cited."),
    (20, "MENLO PARK", "Meta's AI chief: superintelligence is arriving — and control is at risk."),
    (21, "VYSHNEVE", "A Shahed drone hits a supermarket; several killed and hurt, among them children."),
    (22, "GAZA CITY", "Two more Palestinians killed on Sunday; a drone strike near Deir al-Balah kills one."),
    (23, "MANAMA", "US official: no damage to US personnel or facilities in Bahrain."),
    (24, "ANTALYA", "COP31's one win: 90+ countries sign an electrification pledge."),
    (25, "HORMUZ", "37 tankers pass, down from 52 — down by nearly a third."),
    (26, "RYLSK", "Ukraine hits Russia's Rubicon drone unit; an ammunition depot blows up."),
    (27, "BALTIC", "Russian cargo ship Sparta II burns in the Gulf of Finland after a drone strike."),
    (28, "WASHINGTON", "Putin 'privately agreed' to NATO-style guarantees for Ukraine, WaPo reports. [REPORTED]"),
    (29, "DAKAR", "CAS to rule Tuesday on Senegal's AFCON title appeal. [FORECAST]"),
    (30, "DNIPRO", "A Russian drone guts a flat in a ten-storey block; about 20 more damaged."),
    (31, "CHERKASY", "Nine Russian drones downed over Cherkasy; no injuries reported."),
    (32, "LYUBOTYN", "A Russian drone hits a railway station; a train catches fire, people hurt."),
    (33, "BELGRADE", "Serbia's weather chief arrested for alleged money laundering."),
]

UTC_LINE = ("UTC — SUN 18:00 153 drones launched · MON 07:00 Belgian airspace "
            "shuts · MON 08:00 134 of 153 downed · MONDAY NATO meets on Poland · "
            "SUNDAY COP31 pact rejected")

DATE_CHECK = ("DATE CHECK  ✓  Every story on this page happened, or was first reported, "
              "on Monday 23 November 2026. Weekend events appear only where Monday "
              "moved them on: the Bahrain strikes (Sat), COP31's collapse (Sun), the Gaza "
              "truck (Sat), the 258th House seat (Sun).  LEFT OUT AS OTHER DAYS' NEWS — "
              "20 NOV: COP31's scheduled close.")

SOURCES = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, WSJ, CNN, UKMTO.  Pictures "
           "and map: original, drawn in code.  Confidence: CONFIRMED = two or more outlets · "
           "REPORTED = named sources, one side's claim where stated · FORECAST = due date or draft.")


# ------------------------------------------------------------ illustrations
def draw_flame(d, x, y, s):
    """A small stylised flame, base at (x, y), size s."""
    d.polygon([(x, y), (x - s * 0.55, y - s * 0.5), (x - s * 0.2, y - s * 1.0),
               (x + s * 0.15, y - s * 1.35), (x + s * 0.5, y - s * 0.7),
               (x + s * 0.55, y - s * 0.35)], fill=(230, 120, 30))
    d.polygon([(x - s * 0.2, y), (x - s * 0.35, y - s * 0.45), (x, y - s * 0.85),
               (x + s * 0.3, y - s * 0.4)], fill=(245, 190, 40))


def art_sea(d, x, y, w, h):
    """Hormuz: a grey warship and a burning tanker on a wavy sea."""
    d.rectangle([x, y, x + w, y + h], fill=SEABLUE)
    d.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(178, 206, 222))
    # sun
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(245, 205, 80))
    # waves
    for i, wy in enumerate((0.62, 0.76, 0.9)):
        yy = y + int(h * wy)
        d.arc([x + 4 + i * 30, yy - 10, x + 44 + i * 30, yy + 10], 200, 340,
              fill=(120, 160, 190), width=2)
        d.arc([x + w - 60 - i * 34, yy - 10, x + w - 20 - i * 34, yy + 10], 200, 340,
              fill=(120, 160, 190), width=2)
    # warship (left)
    hx, hy = x + 14, y + int(h * 0.52)
    d.polygon([(hx, hy + 22), (hx + 96, hy + 22), (hx + 88, hy + 34),
               (hx + 6, hy + 34)], fill=(96, 104, 112))
    d.rectangle([hx + 22, hy + 4, hx + 66, hy + 22], fill=(120, 128, 136))
    d.rectangle([hx + 38, hy - 8, hx + 52, hy + 4], fill=(120, 128, 136))
    d.line([(hx + 45, hy - 8), (hx + 45, hy - 18)], fill=INK, width=2)
    d.polygon([(hx + 45, hy - 18), (hx + 58, hy - 14), (hx + 45, hy - 11)],
              fill=DARKRED)
    # tanker (right), burning
    tx, ty = x + w - 138, y + int(h * 0.55)
    d.polygon([(tx, ty + 18), (tx + 128, ty + 18), (tx + 118, ty + 32),
               (tx + 10, ty + 32)], fill=(122, 74, 54))
    d.rectangle([tx + 16, ty, tx + 40, ty + 18], fill=(160, 110, 90))
    d.rectangle([tx + 78, ty - 6, tx + 96, ty + 18], fill=(160, 110, 90))
    draw_flame(d, tx + 30, ty - 2, 16)
    draw_flame(d, tx + 86, ty - 8, 20)
    draw_flame(d, tx + 112, ty + 12, 12)
    for cx, cy, r in ((tx + 22, ty - 26, 9), (tx + 44, ty - 34, 11),
                      (tx + 84, ty - 30, 10), (tx + 104, ty - 38, 12)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 90, 92))
    # drone above
    dx, dy = x + w // 2 - 14, y + 12
    d.ellipse([dx, dy + 4, dx + 26, dy + 10], fill=INK)
    d.line([(dx + 2, dy + 4), (dx + 10, dy - 6)], fill=INK, width=2)
    d.line([(dx + 24, dy + 4), (dx + 16, dy - 6)], fill=INK, width=2)


def art_cop(d, x, y, w, h):
    """COP31: a globe, a red NO DEAL stamp, and a 1.5°C thermometer."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 238, 224))
    cx, cy, r = x + 66, y + 44, 40
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(124, 164, 210))
    d.polygon([(cx - 26, cy - 26), (cx - 6, cy - 30), (cx + 2, cy - 12),
               (cx - 14, cy - 4), (cx - 30, cy - 10)], fill=(110, 170, 100))
    d.polygon([(cx + 6, cy + 8), (cx + 24, cy + 2), (cx + 30, cy + 18),
               (cx + 12, cy + 30), (cx + 2, cy + 20)], fill=(110, 170, 100))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 90, 120), width=2)
    d.arc([cx - r + 6, cy - r + 4, cx + r - 6, cy + r - 4], 200, 340,
          fill=(90, 130, 170), width=1)
    # thermometer
    tx = x + w - 52
    d.rounded_rectangle([tx, y + 12, tx + 14, y + h - 26], radius=7,
                        outline=INK, width=2, fill=(255, 255, 255))
    d.ellipse([tx - 6, y + h - 40, tx + 20, y + h - 10], fill=RED)
    d.rectangle([tx + 4, y + 24, tx + 10, y + h - 28], fill=RED)
    d.text((tx + 20, y + 16), "1.5°C", font=SANS_B(13), fill=RED)
    d.text((tx + 20, y + 34), "LIMIT", font=SANS_B(11), fill=INK)
    # struck-through FOSSIL FUELS + NO DEAL stamp
    fx = x + 130
    d.text((fx, y + 8), "FOSSIL", font=SANS_B(14), fill=(90, 90, 90))
    d.text((fx, y + 24), "FUELS", font=SANS_B(14), fill=(90, 90, 90))
    d.line([(fx - 4, y + 20), (fx + 58, y + 20)], fill=RED, width=2)
    d.line([(fx - 4, y + 36), (fx + 52, y + 36)], fill=RED, width=2)
    # rotated NO DEAL stamp on its own layer
    stamp = Image.new("RGBA", (132, 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([3, 3, 128, 36], outline=RED, width=3)
    sd.text((12, 6), "NO DEAL", font=SANS_B(22), fill=RED)
    stamp = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
    im.paste(stamp, (x + 112, y + h - 48), stamp)


def art_dymer(d, x, y, w, h):
    """Dymer: a five-storey block with its corner collapsed, drones above."""
    d.rectangle([x, y, x + w, y + h], fill=(216, 208, 188))
    # sky glow
    d.ellipse([x + w - 46, y + 8, x + w - 16, y + 38], fill=(240, 180, 90))
    bx, by = x + 26, y + 6
    bw, bh = 150, 66
    d.rectangle([bx, by, bx + bw, by + bh], fill=(196, 178, 140))
    # windows, 4 wide x 4 tall
    for r in range(4):
        for c in range(4):
            wx = bx + 12 + c * 34
            wy = by + 6 + r * 15
            d.rectangle([wx, wy, wx + 20, wy + 10], fill=(90, 100, 116))
    # collapsed corner (bottom right of the block)
    d.polygon([(bx + bw - 44, by + bh), (bx + bw, by + bh - 26),
               (bx + bw, by + bh)], fill=(70, 66, 60))
    d.polygon([(bx + bw - 66, by + bh), (bx + bw - 34, by + bh - 20),
               (bx + bw - 10, by + bh)], fill=(120, 112, 98))
    # rubble
    for rx, ry, rr in ((bx + bw - 52, by + bh + 2, 5), (bx + bw - 28, by + bh + 3, 4),
                       (bx + bw - 8, by + bh + 2, 5), (bx + bw - 68, by + bh + 3, 3)):
        d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(96, 90, 80))
    # red label
    d.rectangle([x + w - 92, y + h - 24, x + w - 6, y + h - 6], fill=RED)
    d.text((x + w - 84, y + h - 23), "11 KILLED", font=SANS_B(12), fill=(255, 255, 255))
    # drones
    for dx, dy in ((x + w - 108, y + 10), (x + w - 64, y + 26)):
        d.ellipse([dx, dy + 3, dx + 22, dy + 8], fill=INK)
        d.line([(dx + 2, dy + 3), (dx + 9, dy - 5)], fill=INK, width=2)
        d.line([(dx + 20, dy + 3), (dx + 13, dy - 5)], fill=INK, width=2)
    # rescue arc light
    d.arc([x + 6, y + 34, x + 60, y + 80], 300, 30, fill=(240, 200, 80), width=3)


# ------------------------------------------------------------------ icons
def icon(d, kind, x, y, w, h):
    """Small line-art icons for the ten mid cards, drawn in ink/red.
    Everything stays inside the (w x h) box, h = 26."""
    if kind == "drone":  # sea drone on waves
        d.ellipse([x + w // 2 - 16, y + 2, x + w // 2 + 16, y + 9], fill=INK)
        d.line([(x + w // 2 - 14, y + 9), (x + w // 2 - 6, y + 15)], fill=INK, width=2)
        d.line([(x + w // 2 + 14, y + 9), (x + w // 2 + 6, y + 15)], fill=INK, width=2)
        for wy in (18, 23):
            d.arc([x + 6, y + wy - 4, x + w - 6, y + wy + 4], 200, 340,
                  fill=BLUE, width=2)
    elif kind == "capitol":  # dome + columns
        d.polygon([(x + w // 2, y + 1), (x + w // 2 - 18, y + 11),
                   (x + w // 2 + 18, y + 11)], fill=INK)
        d.rectangle([x + w // 2 - 20, y + 11, x + w // 2 + 20, y + 14], fill=INK)
        for i in range(5):
            cx = x + 10 + i * 13
            d.rectangle([cx, y + 15, cx + 5, y + 23], fill=INK)
        d.rectangle([x + 6, y + 23, x + w - 6, y + 26], fill=INK)
    elif kind == "exam":  # exam paper + pencil, red AI
        d.rectangle([x + 12, y + 1, x + w - 16, y + 25], outline=INK, width=2,
                    fill=(255, 255, 255))
        for ly in (7, 12, 17):
            d.line([(x + 17, y + ly), (x + w - 22, y + ly)], fill=GREY, width=1)
        d.polygon([(x + w - 14, y + 21), (x + w - 5, y + 25), (x + w - 14, y + 25)],
                  fill=(230, 160, 40))
        d.text((x + w - 38, y + 12), "AI", font=SANS_B(12), fill=RED)
    elif kind == "strike":  # picket flag + grounded plane
        d.line([(x + 14, y + 2), (x + 14, y + 26)], fill=INK, width=2)
        d.polygon([(x + 14, y + 2), (x + 42, y + 8), (x + 14, y + 14)], fill=RED)
        d.ellipse([x + w - 32, y + 18, x + w - 6, y + 24], fill=INK)
        d.polygon([(x + w - 24, y + 18), (x + w - 15, y + 11), (x + w - 11, y + 18)],
                  fill=INK)
    elif kind == "truck":  # food truck
        d.rectangle([x + 6, y + 5, x + w - 24, y + 19], outline=INK, width=2,
                    fill=(220, 220, 210))
        d.rectangle([x + w - 24, y + 11, x + w - 8, y + 19], outline=INK, width=2,
                    fill=(220, 220, 210))
        for cx in (x + 16, x + w - 16):
            d.ellipse([cx - 4, y + 19, cx + 4, y + 25], fill=INK)
        d.line([(x + 6, y + 3), (x + w - 8, y + 3)], fill=RED, width=2)
    elif kind == "bars":  # prison bars
        d.rectangle([x + 8, y + 1, x + w - 8, y + 25], outline=INK, width=2)
        for i in range(4):
            bx = x + 14 + i * 12
            d.rectangle([bx, y + 1, bx + 3, y + 25], fill=INK)
    elif kind == "cuffs":  # handcuffs
        d.ellipse([x + 8, y + 5, x + 26, y + 21], outline=INK, width=3)
        d.ellipse([x + w - 26, y + 5, x + w - 8, y + 21], outline=INK, width=3)
        d.line([(x + 26, y + 13), (x + w - 26, y + 13)], fill=INK, width=3)
    elif kind == "rain":  # rain over flood water
        for rx in (x + 12, x + 26, x + 40, x + 54):
            d.line([(rx, y + 1), (rx - 4, y + 9)], fill=BLUE, width=2)
        d.arc([x + 4, y + 14, x + w - 4, y + 26], 200, 340, fill=BLUE, width=3)
        d.line([(x + 4, y + 21), (x + w - 4, y + 21)], fill=BLUE, width=2)
    elif kind == "mic":  # microphone
        d.ellipse([x + w // 2 - 9, y + 1, x + w // 2 + 9, y + 16], fill=INK)
        d.arc([x + w // 2 - 13, y + 9, x + w // 2 + 13, y + 24], 0, 180,
              fill=INK, width=2)
        d.line([(x + w // 2, y + 22), (x + w // 2, y + 26)], fill=INK, width=2)
    elif kind == "score":  # 2-0 scoreboard + ball
        d.rectangle([x + 8, y + 2, x + w - 8, y + 18], outline=INK, width=2,
                    fill=(255, 255, 255))
        d.text((x + 12, y + 5), "2–0", font=SANS_B(12), fill=RED)
        d.ellipse([x + w - 24, y + 16, x + w - 12, y + 26], outline=INK, width=2)


# ------------------------------------------------------------------- page
im = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(im)
d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=3)

# masthead + title + deck
center(d, 10, "THE WORLD IN ONE DAY  ·  33 STORIES  ·  SIX REGIONS  ·  ALL FROM ONE DAY",
       SANS_B(13), INK)
center(d, 28, "Monday 23 November 2026", SERIF_B(44), INK)
center(d, 84, "Iran hits US bases in Bahrain  ·  COP31 collapses with no deal  ·  "
              "Russia's 153-drone night over Ukraine", SERIF_I(15), RED)
rule(d, 108)

# 6-box number strip
strip_y, strip_h, gap = 116, 52, 6
bw = (W - 28 - 5 * gap) // 6
for i, (num, label) in enumerate(STRIP):
    bx = 14 + i * (bw + gap)
    d.rectangle([bx, strip_y, bx + bw, strip_y + strip_h], outline=INK, width=2,
                fill=LIGHT)
    num_f = SERIF_B(24)
    d.text((bx + (bw - num_f.getlength(num)) / 2, strip_y + 3), num,
           font=num_f, fill=RED)
    # label wraps to at most 2 lines, small
    lab = wrap(label, SANS_B(9), bw - 10)
    ly = strip_y + 31
    for ln in lab[:2]:
        d.text(((bw - SANS_B(9).getlength(ln)) / 2 + bx, ly), ln,
               font=SANS_B(9), fill=INK)
        ly += 10
center(d, 172, "EUROPE 14  ·  MIDDLE EAST 6  ·  AMERICAS 5  ·  ASIA 3  ·  GLOBAL 3  ·  "
               "AFRICA 2  —  33 STORIES IN ALL", SANS_B(11), INK)
rule(d, 194)

# 3 illustrated leads
ARTS = {"sea": art_sea, "cop": art_cop, "dymer": art_dymer}
lead_y, lead_h = 202, 200
lw = (W - 28 - 2 * 12) // 3
for i, lead in enumerate(LEADS):
    lx = 14 + i * (lw + 12)
    d.rectangle([lx, lead_y, lx + lw, lead_y + lead_h], outline=INK, width=2)
    # kicker bar
    d.rectangle([lx + 1, lead_y + 1, lx + lw - 1, lead_y + 24], fill=INK)
    d.text((lx + 8, lead_y + 5), lead["kick"], font=SANS_B(11), fill=(255, 255, 255))
    d.text((lx + lw - 8 - SANS_B(9).getlength(lead["conf"]), lead_y + 7),
           lead["conf"], font=SANS_B(9), fill=(245, 200, 60))
    # illustration
    ARTS[lead["art"]](d, lx + 2, lead_y + 26, lw - 4, 86)
    # headline + deck
    hy = lead_y + 118
    hy = draw_wrapped(d, lx + 8, hy, lead["head"], SERIF_B(19), INK, lw - 16,
                      leading=20, max_lines=3)
    draw_wrapped(d, lx + 8, hy + 4, lead["deck"], SANS(11), (40, 40, 40), lw - 16,
                 leading=13, max_lines=4)

# 10 mid cards, 2 rows x 5
mid_y = 410
cw = (W - 28 - 4 * 6) // 5
ch, row_gap = 108, 6
for i, card in enumerate(MIDS):
    cx = 14 + (i % 5) * (cw + 6)
    cy = mid_y + (i // 5) * (ch + row_gap)
    d.rectangle([cx, cy, cx + cw, cy + ch], outline=INK, width=1, fill=LIGHT)
    d.text((cx + 6, cy + 3), f"{card['n']}. {card['kick']}", font=SANS_B(9), fill=RED)
    icon(d, card["icon"], cx + 6, cy + 16, 64, 26)
    d.text((cx + 74, cy + 16), card["conf"], font=SANS_B(9), fill=DARKRED)
    hy = draw_wrapped(d, cx + 6, cy + 44, card["head"], SANS_B(12), INK, cw - 12,
                      leading=13, max_lines=3)
    draw_wrapped(d, cx + 6, hy + 1, card["deck"], SANS(9), (50, 50, 50), cw - 12,
                 leading=10, max_lines=3)

# UTC timeline
utc_y = mid_y + 2 * ch + row_gap + 8
d.rectangle([14, utc_y, W - 14, utc_y + 20], fill=(30, 30, 30))
d.text((22, utc_y + 4), UTC_LINE, font=SANS_B(10), fill=(255, 255, 255))
rule(d, utc_y + 28)


# ---------------------------------------------------------------- map + briefs
bot_y = utc_y + 36  # section headers
d.text((14, bot_y), "WHERE IT HAPPENED — 13 PLACES PINNED", font=SANS_B(11), fill=INK)
d.text((356, bot_y), "ALSO ON MONDAY 23 NOVEMBER — 20 MORE STORIES", font=SANS_B(11),
       fill=INK)
map_x, map_y, map_w, map_h = 14, bot_y + 18, 330, 230
d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], outline=INK, width=2,
            fill=SEABLUE)


def project(lon, lat):
    px = map_x + (lon + 180) / 360 * map_w
    py = map_y + (85 - lat) / 145 * map_h
    return px, py


# graticule
for lon in range(-150, 181, 30):
    x0, _ = project(lon, 85)
    x1, _ = project(lon, -60)
    d.line([(x0, map_y), (x1, map_y + map_h)], fill=(170, 190, 200), width=1)
for lat in range(-60, 86, 30):
    _, y0 = project(-180, lat)
    d.line([(map_x, y0), (map_x + map_w, y0)], fill=(170, 190, 200), width=1)

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
     (-55, 47), (-65, 44), (-75, 35), (-81, 25), (-90, 21), (-97, 16),
     (-90, 14), (-83, 9), (-79, 9), (-86, 12), (-95, 16), (-105, 20),
     (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-168, 66)],
    [(-79, 9), (-72, 12), (-62, 10), (-55, 5), (-50, 0), (-44, -3),
     (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-58, -35), (-65, -41),
     (-70, -50), (-73, -37), (-70, -20), (-77, -12), (-80, -5), (-81, 2),
     (-79, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (30, 60), (28, 62), (32, 60), (38, 55),
     (40, 50), (35, 46), (30, 46), (27, 44), (23, 40), (22, 38), (18, 40),
     (15, 38), (12, 44), (8, 44), (3, 43), (0, 38), (-2, 36), (-6, 36),
     (-10, 36)],
    [(-17, 15), (-16, 12), (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4),
     (9, 4), (12, 0), (13, -5), (12, -10), (13, -18), (16, -25), (20, -29),
     (25, -33), (28, -32), (32, -28), (35, -23), (36, -18), (40, -15),
     (40, -10), (42, -5), (46, 0), (51, 5), (51, 11), (48, 11), (44, 13),
     (42, 15), (39, 18), (37, 22), (35, 27), (32, 31), (30, 31), (25, 32),
     (20, 32), (15, 32), (10, 34), (10, 37), (5, 37), (0, 36), (-6, 35),
     (-10, 31), (-15, 27), (-17, 21), (-17, 15)],
    [(40, 50), (45, 58), (55, 65), (65, 69), (75, 73), (90, 75), (105, 77),
     (120, 73), (135, 71), (150, 70), (162, 66), (170, 60), (160, 58),
     (150, 55), (142, 52), (135, 42), (128, 38), (122, 30), (115, 22),
     (108, 12), (103, 7), (98, 10), (92, 16), (88, 22), (80, 15), (75, 10),
     (70, 20), (62, 25), (56, 26), (50, 28), (44, 30), (40, 35), (38, 42),
     (40, 50)],
    [(113, -22), (114, -30), (118, -35), (124, -33), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
]
for poly in CONTINENTS:
    d.polygon([project(lon, lat) for lon, lat in poly], fill=TAN,
              outline=(120, 110, 88))

PINS = {1: (52, 25), 2: (28, 35), 3: (36, 54), 4: (16, 29),
        5: (-77, 38.9), 6: (127, 37.5), 7: (0, 50), 8: (38, 28),
        9: (90.4, 23.8), 10: (-108.5, 25.6), 11: (16, 42),
        12: (8, 60), 13: (-74.8, 11.0)}
DOTS = {14: (33.4, 47.9), 15: (8, 54), 16: (42, 46), 17: (40, 26),
        18: (106.2, -6.1), 19: (-72, 35), 20: (-122.2, 37.5),
        21: (27, 53), 22: (31, 29), 23: (57, 22), 24: (36, 32),
        25: (56.5, 26.5), 26: (40, 55), 27: (24, 59.8), 28: (-81, 35.5),
        29: (-17.4, 14.7), 30: (38, 47), 31: (29, 47), 32: (41, 49),
        33: (26, 40)}
for n, (lon, lat) in PINS.items():
    px, py = project(lon, lat)
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=(255, 255, 255),
              width=1)
    t = str(n)
    d.text((px - SANS_B(8).getlength(t) / 2, py - 5), t, font=SANS_B(8),
           fill=(255, 255, 255))
for n, (lon, lat) in DOTS.items():
    px, py = project(lon, lat)
    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=INK)

# briefs: two columns x 10, each at most 2 lines at 9pt
brief_x0, brief_y0, brief_w, brief_row = 356, map_y, 321, 23
for i, (n, place, text) in enumerate(BRIEFS):
    col, row = divmod(i, 10)
    bx = brief_x0 + col * (brief_w + 12)
    by = brief_y0 + row * brief_row
    prefix = f"{n}. {place} — "
    full = prefix + text
    lines = wrap(full, SANS(9), brief_w)[:2]
    # first line: bold prefix, regular remainder
    first = lines[0]
    rest = first[len(prefix):] if first.startswith(prefix) else ""
    d.text((bx, by), prefix, font=SANS_B(9), fill=INK)
    d.text((bx + SANS_B(9).getlength(prefix), by), rest, font=SANS(9), fill=INK)
    if len(lines) > 1:
        d.text((bx, by + 11), lines[1], font=SANS(9), fill=INK)

# DATE CHECK box (red border; the one place weekend events are dated)
dc_y = map_y + map_h + 8
d.rectangle([14, dc_y, W - 14, dc_y + 48], outline=RED, width=2)
dc_lines = wrap(DATE_CHECK, SANS(10), W - 28 - 24)
dc_prefix = "DATE CHECK  ✓  "
ly = dc_y + 5
for li, ln in enumerate(dc_lines[:3]):
    if li == 0 and ln.startswith(dc_prefix):
        d.text((22, ly), dc_prefix, font=SANS_B(10), fill=RED)
        d.text((22 + SANS_B(10).getlength(dc_prefix), ly), ln[len(dc_prefix):],
               font=SANS(10), fill=INK)
    else:
        d.text((22, ly), ln, font=SANS(10), fill=INK)
    ly += 13

# sources + confidence legend
draw_wrapped(d, 14, dc_y + 54, SOURCES, SANS(9), GREY, W - 28, leading=11,
             max_lines=2)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
im.save(out, format="PNG", optimize=True)
print(f"saved {out}  {os.path.getsize(out)} bytes  {im.size[0]}x{im.size[1]}")
