#!/usr/bin/env python3
"""Draw placeholder sprites for original species that have a [graphics.placeholder] table.

Usage (repository root):
  python3 tools/oddex/placeholder_art.py              # every species with a placeholder table
  python3 tools/oddex/placeholder_art.py SHADEPUP ... # only these
  python3 tools/oddex/placeholder_art.py --preview out.png   # also write a contact sheet

Placeholders must be told apart at a glance: body colour from the first type, belly/markings
and the head emblem from the second type (or a lighter shade for single-type species),
one of a few silhouettes, plus optional features. Real art later replaces the files in
[graphics] dir; delete [graphics.placeholder] and nothing else in the TOML changes.

[graphics.placeholder] keys:
  body     = "blob" | "biped" | "quadruped" | "bird" | "worm"
  size     = 0.6 .. 1.2           (default 0.8; later evolution stages should be larger)
  features = ["ears", "antennae", "horn", "tail", "crest", "spikes", "leaf", "fins"]
  eyes     = "round" | "sleepy" | "fierce"     (default "round")
"""
import argparse
import colorsys
import hashlib
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from species_data import GAME, load_species  # noqa: E402

TYPE_COLORS = {
    'NORMAL': (200, 188, 152), 'FIRE': (240, 120, 48), 'WATER': (72, 136, 232),
    'GRASS': (88, 184, 72), 'ELECTRIC': (248, 208, 48), 'ICE': (136, 216, 232),
    'FIGHTING': (192, 72, 48), 'POISON': (168, 80, 184), 'GROUND': (216, 176, 96),
    'FLYING': (152, 168, 240), 'PSYCHIC': (240, 88, 136), 'BUG': (168, 184, 32),
    'ROCK': (168, 152, 104), 'GHOST': (112, 88, 152), 'DRAGON': (112, 64, 232),
    'DARK': (96, 80, 72), 'STEEL': (184, 184, 208), 'FAIRY': (240, 160, 200),
}

# Palette slots.
T, OUTLINE = 0, 1
BODY = 2          # 2..5 dark..highlight of the first type
ACCENT = 6        # 6..9 dark..highlight of the second type (or a lighter body shade)
WHITE, EYE, CHEEK, CREAM, BEAK, EMBLEM2 = 10, 11, 12, 13, 14, 15


def type_color(name):
    if name in TYPE_COLORS:
        return TYPE_COLORS[name]
    # Unknown (future original) types still get a stable, distinct colour.
    hue = int(hashlib.sha1(name.encode()).hexdigest()[:4], 16) / 0xFFFF
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.85)
    return int(r * 255), int(g * 255), int(b * 255)


def ramp(rgb):
    def mix(c, t, k):
        return tuple(int(c[i] + (t[i] - c[i]) * k) for i in range(3))
    return [mix(rgb, (0, 0, 0), 0.45), mix(rgb, (0, 0, 0), 0.2), rgb, mix(rgb, (255, 255, 255), 0.45)]


def palette(types, shiny=False):
    body = type_color(types[0])
    accent = type_color(types[1]) if len(types) > 1 else tuple(min(255, int(c * 0.6 + 255 * 0.4)) for c in body)
    if shiny:
        def rot(c):
            h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
            r, g, b = colorsys.hsv_to_rgb((h + 0.45) % 1, s, v)
            return int(r * 255), int(g * 255), int(b * 255)
        body, accent = rot(body), rot(accent)
    outline = tuple(int(c * 0.18) for c in body)
    emblem2 = (248, 232, 120) if 'FIRE' in types or 'ELECTRIC' in types else (248, 248, 216)
    pal = [(152, 200, 176), outline] + ramp(body) + ramp(accent)
    pal += [(248, 248, 248), (24, 24, 32), (240, 128, 136), (240, 232, 200), (232, 160, 56), emblem2]
    return pal


LIGHT = (-0.45, -0.6, 0.66)


def shade(nx, ny, base):
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    lum = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
    return base + (0 if lum < 0.15 else 1 if lum < 0.55 else 2 if lum < 0.85 else 3)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[0] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[int(y)][int(x)] = c

    def ellipse(self, cx, cy, rx, ry, fill, only_on=None):
        """fill: palette index, or a ramp base (2/6) for shaded fill when fill in (BODY, ACCENT)."""
        rx, ry = max(rx, 0.6), max(ry, 0.6)
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if dx * dx + dy * dy > 1 or not (0 <= x < self.w and 0 <= y < self.h):
                    continue
                if only_on is not None and self.px[y][x] not in only_on:
                    continue
                self.px[y][x] = shade(dx, dy, fill) if fill in (BODY, ACCENT) else fill

    def poly(self, pts, fill):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                if self._inside(x + 0.5, y + 0.5, pts):
                    self.set(x, y, fill)

    @staticmethod
    def _inside(x, y, pts):
        inside = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
                inside = not inside
            j = i
        return inside

    def outline(self):
        out = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x]:
                    continue
                for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + ox, y + oy
                    if 0 <= nx < self.w and 0 <= ny < self.h and self.px[ny][nx] not in (0, OUTLINE):
                        out[y][x] = OUTLINE
                        break
        self.px = out

    def bbox(self):
        ys = [y for y in range(self.h) if any(self.px[y])]
        xs = [x for x in range(self.w) if any(self.px[y][x] for y in range(self.h))]
        return (min(xs), min(ys), max(xs), max(ys)) if xs else None

    def shifted(self, dx, dy):
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x]:
                    out.set(x + dx, y + dy, self.px[y][x])
        return out


def emblem(cv, kind, x, y, u):
    """Small type mark centred at (x, y); u = pixel unit."""
    c3, c4 = ACCENT + 2, ACCENT + 3
    if kind == 'GRASS':
        cv.ellipse(x - u * 1.4, y, u * 1.6, u * 0.8, ACCENT)
        cv.ellipse(x + u * 1.4, y - u * 0.4, u * 1.6, u * 0.8, ACCENT)
    elif kind == 'FIRE':
        cv.poly([(x - u * 1.6, y + u), (x, y - u * 2.6), (x + u * 1.6, y + u)], c3)
        cv.poly([(x - u * 0.7, y + u), (x, y - u), (x + u * 0.7, y + u)], EMBLEM2)
    elif kind == 'WATER':
        cv.ellipse(x, y + u * 0.5, u * 1.3, u * 1.3, c4)
        cv.poly([(x - u * 1.2, y + u * 0.2), (x, y - u * 2.4), (x + u * 1.2, y + u * 0.2)], c4)
    elif kind == 'ELECTRIC':
        cv.poly([(x - u * 0.3, y - u * 2.2), (x + u * 1.2, y - u * 2.2), (x + u * 0.2, y - u * 0.2),
                 (x + u * 1.0, y - u * 0.2), (x - u * 1.0, y + u * 2.2), (x - u * 0.2, y + u * 0.2),
                 (x - u * 1.0, y + u * 0.2)], EMBLEM2)
    elif kind == 'PSYCHIC':
        cv.ellipse(x, y, u * 1.4, u * 1.4, c3)
        cv.ellipse(x - u * 0.4, y - u * 0.4, u * 0.5, u * 0.5, WHITE)
    elif kind == 'FAIRY':
        for a in range(4):
            ang = a * math.pi / 2
            cv.poly([(x, y), (x + math.cos(ang - 0.35) * u, y + math.sin(ang - 0.35) * u),
                     (x + math.cos(ang) * u * 2.4, y + math.sin(ang) * u * 2.4),
                     (x + math.cos(ang + 0.35) * u, y + math.sin(ang + 0.35) * u)], c4)
    elif kind == 'DARK':
        cv.ellipse(x, y, u * 1.6, u * 1.6, c3)
        cv.ellipse(x + u * 0.8, y - u * 0.5, u * 1.4, u * 1.4, 0, only_on=(c3,))
    elif kind == 'FLYING':
        cv.ellipse(x - u * 1.2, y, u * 1.8, u * 0.7, c4)
        cv.ellipse(x + u * 1.2, y, u * 1.8, u * 0.7, c4)
    elif kind == 'POISON':
        cv.ellipse(x - u, y, u, u, c3)
        cv.ellipse(x + u * 0.8, y - u * 0.8, u * 0.8, u * 0.8, c3)
        cv.ellipse(x + u * 0.4, y + u * 0.9, u * 0.6, u * 0.6, c4)
    elif kind == 'BUG':
        cv.ellipse(x, y, u * 1.2, u * 1.6, c3)
        cv.set(x, y - u * 0.4, OUTLINE)
        cv.set(x, y + u * 0.6, OUTLINE)
    elif kind == 'ROCK' or kind == 'GROUND' or kind == 'STEEL':
        cv.poly([(x - u * 1.6, y + u), (x - u * 0.8, y - u * 1.4), (x + u * 1.2, y - u * 1.0), (x + u * 1.6, y + u)], c3)
    elif kind == 'ICE':
        cv.poly([(x, y - u * 2.2), (x + u * 1.2, y), (x, y + u * 2.2), (x - u * 1.2, y)], c4)
    elif kind == 'GHOST':
        cv.ellipse(x, y - u * 0.4, u * 1.4, u * 1.4, c4)
        cv.poly([(x - u * 1.4, y - u * 0.4), (x + u * 1.4, y - u * 0.4), (x + u * 0.4, y + u * 2), (x, y + u)], c4)
    elif kind == 'FIGHTING':
        cv.ellipse(x, y, u * 1.6, u * 1.3, c3)
        for i in (-1, 0, 1):
            cv.set(x + i * u * 0.8, y - u * 0.3, OUTLINE)
    elif kind == 'DRAGON':
        cv.poly([(x - u * 1.4, y + u), (x - u * 0.4, y - u * 2.4), (x, y + u)], c3)
        cv.poly([(x, y + u), (x + u * 0.4, y - u * 2.4), (x + u * 1.4, y + u)], c3)
    else:  # NORMAL and unknown types: a tuft
        for i in (-1, 0, 1):
            cv.ellipse(x + i * u, y - abs(i) * u * 0.3, u * 0.7, u * 1.4, c3)


def draw_eyes(cv, cx, cy, sep, u, style, view):
    if view == 'back':
        return
    eyes = [cx - sep] if view == 'side' else [cx - sep, cx + sep]
    for ex in eyes:
        ry = u * (1.0 if style == 'sleepy' else 1.7)
        cv.ellipse(ex, cy, u * 1.2, ry, EYE)
        cv.set(ex - u * 0.4, cy - ry * 0.5, WHITE)
        if style == 'fierce':
            cv.poly([(ex - u * 1.6, cy - ry * 1.4), (ex + u * 1.6, cy - ry * 0.6), (ex + u * 1.6, cy - ry * 1.6)], OUTLINE)
    if view == 'front' and u >= 1.4:
        cv.ellipse(cx - sep * 1.6, cy + u * 2, u * 1.1, u * 0.6, CHEEK)
        cv.ellipse(cx + sep * 1.6, cy + u * 2, u * 1.1, u * 0.6, CHEEK)


def draw(cv, spec, view, cx, bottom, scale, step=0, squish=0.0):
    """view: front/back/side. scale: 1.0 ~ fills a 64x64 frame comfortably."""
    ph = spec['graphics']['placeholder']
    body = ph.get('body', 'blob')
    feats = set(ph.get('features', []))
    eyes = ph.get('eyes', 'round')
    types = spec['types']
    emb_type = types[1] if len(types) > 1 else types[0]
    u = max(0.8, 2.2 * scale)
    R = 18 * scale
    rx, ry = R * (1 + squish), R * (1 - squish)
    lift = step

    def feet(xs, y, r):
        for i, fx in enumerate(xs):
            cv.ellipse(fx, y - (lift if i % 2 == 0 else 1 - lift) * 0.8, r * 1.1, r * 0.7, BODY)

    if body == 'blob':
        cy = bottom - ry
        feet([cx - rx * 0.5, cx + rx * 0.5], bottom, u * 2)
        cv.ellipse(cx, cy, rx, ry, BODY)
        if view != 'back':
            cv.ellipse(cx, cy + ry * 0.45, rx * 0.6, ry * 0.45, ACCENT, only_on=range(BODY, BODY + 4))
        head_cy, top, sep = cy - ry * 0.05, cy - ry, rx * 0.36
    elif body == 'biped':
        by = bottom - ry * 0.75
        feet([cx - rx * 0.4, cx + rx * 0.4], bottom, u * 1.8)
        cv.ellipse(cx, by, rx * 0.75, ry * 0.7, BODY)
        if view != 'back':
            cv.ellipse(cx, by + ry * 0.1, rx * 0.45, ry * 0.5, ACCENT, only_on=range(BODY, BODY + 4))
        for side in (-1, 1):
            if view != 'side' or side == -1:
                cv.ellipse(cx + side * rx * 0.8, by - ry * 0.05 + (lift * side), u * 1.6, u * 2.6, BODY)
        hr = rx * 0.68
        head_cy = by - ry * 0.7 - hr * 0.55
        cv.ellipse(cx, head_cy, hr, hr * 0.92, BODY)
        top, sep = head_cy - hr * 0.92, hr * 0.42
    elif body == 'quadruped':
        by = bottom - ry * 0.75
        if view == 'side':
            cv.ellipse(cx + rx * 0.15, by, rx * 0.9, ry * 0.55, BODY)
            feet([cx - rx * 0.45, cx - rx * 0.15, cx + rx * 0.35, cx + rx * 0.65], bottom, u * 1.6)
            hr = rx * 0.5
            head_cy, hx = by - ry * 0.45, cx - rx * 0.6
            cv.ellipse(hx, head_cy, hr, hr * 0.9, BODY)
            top, sep = head_cy - hr * 0.9, -hr * 0.3
            cx = hx
        else:
            cv.ellipse(cx, by, rx * 0.85, ry * 0.6, BODY)
            feet([cx - rx * 0.55, cx - rx * 0.2, cx + rx * 0.2, cx + rx * 0.55], bottom, u * 1.5)
            hr = rx * 0.58
            head_cy = by - ry * 0.25 if view == 'front' else by - ry * 0.55
            if view == 'front':
                cv.ellipse(cx, head_cy, hr, hr * 0.88, BODY)
                cv.ellipse(cx, head_cy + hr * 0.45, hr * 0.5, hr * 0.35, ACCENT, only_on=range(BODY, BODY + 4))
            else:
                cv.ellipse(cx, head_cy, hr * 0.8, hr * 0.7, BODY)
            top, sep = head_cy - hr * 0.88, hr * 0.42
    elif body == 'bird':
        cy = bottom - ry * 0.85
        feet([cx - rx * 0.25, cx + rx * 0.25], bottom, u * 1.2)
        for side in (-1, 1):
            if view != 'side' or side == 1:
                flap = (lift - 0.5) * u * 2
                cv.ellipse(cx + side * rx * 0.85, cy - ry * 0.1 + flap, rx * 0.55, ry * 0.3, ACCENT)
        cv.ellipse(cx, cy, rx * 0.72, ry * 0.8, BODY)
        if view != 'back':
            cv.ellipse(cx, cy + ry * 0.3, rx * 0.4, ry * 0.4, CREAM, only_on=range(BODY, BODY + 4))
            bx = cx - (rx * 0.5 if view == 'side' else 0)
            cv.poly([(bx - u * 1.4, cy - ry * 0.05), (bx + u * 1.4, cy - ry * 0.05), (bx, cy + u * 2.2)], BEAK)
        head_cy, top, sep = cy - ry * 0.35, cy - ry * 0.8, rx * 0.3
    else:  # worm
        cy = bottom - ry * 0.55
        segs = 4
        for i in range(segs - 1, -1, -1):
            off = (i - 0.5) * rx * 0.45 if view == 'side' else 0
            yy = cy + (0 if view == 'side' else -i * ry * 0.18) + (lift if i % 2 else 0) * 0.8
            rr = ry * (0.55 - i * 0.06)
            cv.ellipse(cx + off, yy, rr * 1.05, rr, BODY if i % 2 == 0 else ACCENT)
        head_cy, top, sep = cy - ry * 0.05, cy - ry * 0.55, rx * 0.22
        if view == 'side':
            cx = cx - rx * 0.22

    # Features drawn behind/around the head.
    if 'ears' in feats:
        for side in (-1, 1):
            cv.poly([(cx + side * sep * 0.6, top + u * 2), (cx + side * sep * 1.9, top - u * 3.5),
                     (cx + side * sep * 2.0, top + u * 3)], BODY + 1)
    if 'antennae' in feats:
        for side in (-1, 1):
            for k in range(int(u * 3)):
                cv.set(cx + side * (sep * 0.5 + k * 0.5), top - k, OUTLINE)
            cv.ellipse(cx + side * (sep * 0.5 + u * 1.5), top - u * 3, u * 0.9, u * 0.9, ACCENT + 2)
    if 'horn' in feats:
        cv.poly([(cx - u, top + u), (cx, top - u * 4), (cx + u, top + u)], CREAM)
    if 'crest' in feats:
        for i in (-1, 0, 1):
            cv.ellipse(cx + i * u * 1.4, top - u * (1.5 - abs(i) * 0.5), u * 0.9, u * 2, ACCENT + 1)
    if 'spikes' in feats and view != 'front':
        for i in range(3):
            cv.poly([(cx - rx * 0.5 + i * rx * 0.5 - u, head_cy + ry * 0.2), (cx - rx * 0.5 + i * rx * 0.5, head_cy - u * 2),
                     (cx - rx * 0.5 + i * rx * 0.5 + u, head_cy + ry * 0.2)], ACCENT + 1)
    if 'tail' in feats:
        tx = cx + rx * (0.9 if view != 'side' else 1.3)
        cv.ellipse(tx, bottom - ry * 0.6, u * 2.2, u * 1.4, ACCENT + 1, only_on=(0,))
    if 'fins' in feats:
        for side in (-1, 1):
            cv.poly([(cx + side * rx * 0.6, bottom - ry * 0.9), (cx + side * rx * 1.15, bottom - ry * 1.2),
                     (cx + side * rx * 0.7, bottom - ry * 0.5)], ACCENT + 2)

    draw_eyes(cv, cx, head_cy, sep, u, eyes, view)
    emblem(cv, emb_type, cx + (0 if view != 'side' else sep), top - u * 1.2, u)
    if 'leaf' in feats:
        emblem(cv, 'GRASS', cx, top - u * 2.6, u)
    cv.outline()


def normalize(cv, bottom_row, center=True):
    box = cv.bbox()
    if not box:
        return cv
    dx = (cv.w - 1 - box[2] - box[0]) // 2 if center else 0
    dy = bottom_row - box[3]
    if box[1] + dy < 0:
        dy = -box[1]
    return cv.shifted(dx, dy)


def to_image(canvases, pal, layout='vertical'):
    w, h = canvases[0].w, canvases[0].h
    size = (w, h * len(canvases)) if layout == 'vertical' else (w * len(canvases), h)
    im = Image.new('P', size, 0)
    im.putpalette([c for rgb in pal for c in rgb])
    for i, cv in enumerate(canvases):
        ox, oy = (0, h * i) if layout == 'vertical' else (w * i, 0)
        for y in range(h):
            for x in range(w):
                im.putpixel((ox + x, oy + y), cv.px[y][x])
    return im


def read_jasc(path):
    rows = Path(path).read_text().split()
    return [tuple(int(v) for v in rows[3 + i * 3: 6 + i * 3]) for i in range(int(rows[2]))]


def write_jasc(path, pal):
    Path(path).write_text('\r\n'.join(['JASC-PAL', '0100', str(len(pal))] + [f'{r} {g} {b}' for r, g, b in pal]) + '\r\n')


def best_icon_palette(pal, used):
    """Pick the shared icon palette (pal0..pal5) closest to the colours we use; return (index, mapping)."""
    best = None
    for idx in range(6):
        icon = read_jasc(GAME / f'graphics/pokemon/icon_palettes/pal{idx}.pal')
        mapping, err = {0: 0}, 0
        for c in used:
            if c == 0:
                continue
            d, j = min((sum((a - b) ** 2 for a, b in zip(pal[c], icon[k])), k) for k in range(1, 16))
            mapping[c], err = j, err + d
        if best is None or err < best[0]:
            best = (err, idx, mapping)
    return best[1], best[2]


def footprint(body):
    im = Image.new('P', (16, 16), 0)
    im.putpalette([255, 255, 255, 0, 0, 0])
    if body in ('bird',):
        lines = [((8, 13), (8, 5)), ((8, 9), (3, 4)), ((8, 9), (13, 4))]
        for (x0, y0), (x1, y1) in lines:
            for t in range(13):
                im.putpixel((round(x0 + (x1 - x0) * t / 12), round(y0 + (y1 - y0) * t / 12)), 1)
    elif body == 'worm':
        for i in range(4):
            for y in range(16):
                for x in range(16):
                    if (x - 3 - i * 3) ** 2 + (y - 8 - (i % 2)) ** 2 <= 4:
                        im.putpixel((x, y), 1)
    else:
        toes = 4 if body == 'quadruped' else 3
        for y in range(16):
            for x in range(16):
                if ((x + 0.5 - 8) / 4.5) ** 2 + ((y + 0.5 - 10) / 4) ** 2 <= 1:
                    im.putpixel((x, y), 1)
        for t in range(toes):
            tx = 3 + t * (10 // (toes - 1))
            for y in range(2, 5):
                for x in range(tx - 1, tx + 1):
                    im.putpixel((x, y), 1)
    return im


def render(spec):
    ph = spec['graphics']['placeholder']
    scale = ph.get('size', 0.8)
    pal, shiny = palette(spec['types']), palette(spec['types'], shiny=True)
    out = GAME / spec['graphics']['dir']
    out.mkdir(parents=True, exist_ok=True)

    frames = []
    for squish in (0.0, 0.12):
        cv = Canvas(64, 64)
        draw(cv, spec, 'front', 32, 52, scale, squish=squish)
        frames.append(normalize(cv, 55))
    front = to_image(frames, pal)
    b = Canvas(64, 64)
    draw(b, spec, 'back', 32, 52, scale * 1.05)
    back = to_image([normalize(b, 55)], pal)

    icons = []
    for bounce in (0, 1):
        cv = Canvas(32, 32)
        draw(cv, spec, 'front', 16, 28, scale * 0.45)
        icons.append(normalize(cv, 29 - bounce))
    used = {c for cv in icons for row in cv.px for c in row}
    icon_index, mapping = best_icon_palette(pal, used)
    for cv in icons:
        cv.px = [[mapping[c] for c in row] for row in cv.px]
    icon = to_image(icons, read_jasc(GAME / f'graphics/pokemon/icon_palettes/pal{icon_index}.pal'))

    ow = []
    for view, step in (('front', 0), ('front', 1), ('back', 0), ('back', 1), ('side', 0), ('side', 1)):
        cv = Canvas(32, 32)
        draw(cv, spec, view, 16, 28, scale * 0.42, step=step)
        ow.append(normalize(cv, 30 - step))
    overworld = to_image(ow, pal, layout='horizontal')

    front.save(out / 'anim_front.png', bits=4)
    back.save(out / 'back.png', bits=4)
    icon.save(out / 'icon.png', bits=4)
    overworld.save(out / 'overworld.png', bits=4)
    footprint(ph.get('body', 'blob')).save(out / 'footprint.png', bits=1)
    for name, p in (('normal', pal), ('shiny', shiny), ('overworld_normal', pal), ('overworld_shiny', shiny)):
        write_jasc(out / f'{name}.pal', p)
    return front, back, icon, overworld, icon_index


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='*')
    ap.add_argument('--preview', help='write a 4x contact sheet of every rendered species here')
    args = ap.parse_args()
    todo = [s for s in load_species() if 'placeholder' in s['graphics'] and (not args.ids or s['id'] in args.ids)]
    sheet_rows = []
    for spec in todo:
        front, back, icon, ow, icon_index = render(spec)
        print(f'{spec["id"]}: {spec["graphics"]["dir"]} (icon palette {icon_index})')
        if spec['graphics'].get('icon_palette') != icon_index:
            print(f'  note: set [graphics] icon_palette = {icon_index} in {spec["_file"]}')
        sheet_rows.append((front, back, icon, ow))
    if args.preview and sheet_rows:
        W, H = 64 * 2 + 32 + 192 + 30, 64
        sheet = Image.new('RGB', (W, H * len(sheet_rows)), (255, 255, 255))
        for r, (front, back, icon, ow) in enumerate(sheet_rows):
            x = 0
            for im in (front.crop((0, 0, 64, 64)), back, icon.crop((0, 0, 32, 32)), ow):
                sheet.paste(im.convert('RGB'), (x, r * H))
                x += im.width + 10 if im.width < 192 else im.width
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(args.preview)


if __name__ == '__main__':
    main()
