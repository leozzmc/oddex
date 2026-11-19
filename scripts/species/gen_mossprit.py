#!/usr/bin/env python3
"""Procedurally draw the original placeholder species "Mossprit" and write every
graphics file a pokeemerald-expansion species folder needs.

Usage: python3 scripts/species/gen_mossprit.py <species_gfx_dir>
  e.g. python3 scripts/species/gen_mossprit.py game/graphics/pokemon/treecko
"""
import math
import sys
from pathlib import Path

from PIL import Image

# Index 0 is the transparent colour on GBA; the RGB value itself is never shown.
NORMAL_PAL = [
    (152, 200, 176),  # 0 transparent
    (24, 32, 24),     # 1 outline
    (72, 72, 80),     # 2 stone dark
    (120, 120, 128),  # 3 stone mid
    (168, 168, 176),  # 4 stone light
    (216, 216, 216),  # 5 stone highlight
    (40, 88, 40),     # 6 moss dark
    (72, 144, 56),    # 7 moss mid
    (128, 200, 80),   # 8 moss light
    (192, 232, 128),  # 9 moss highlight
    (248, 248, 248),  # 10 eye white
    (232, 168, 48),   # 11 eye iris
    (240, 128, 136),  # 12 cheek
    (248, 224, 96),   # 13 petal
    (232, 120, 40),   # 14 flower centre
    (120, 88, 56),    # 15 feet
]

# Shiny keeps the same indices: sandstone body, teal moss, pink flower.
SHINY_PAL = list(NORMAL_PAL)
SHINY_PAL[2:6] = [(112, 72, 48), (168, 112, 72), (208, 160, 112), (240, 208, 168)]
SHINY_PAL[6:10] = [(24, 80, 96), (40, 136, 152), (88, 192, 200), (160, 232, 232)]
SHINY_PAL[13] = (248, 160, 200)
SHINY_PAL[14] = (200, 64, 120)

# Remap onto shared icon palette graphics/pokemon/icon_palettes/pal1.pal (iconPalIndex = 1).
ICON_REMAP = {0: 0, 1: 15, 2: 14, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 6,
              10: 3, 11: 10, 12: 7, 13: 10, 14: 13, 15: 9}

OUTLINE = 1
LIGHT = (-0.45, -0.6, 0.66)


def shade(nx, ny, base):
    """base = first index of a 4-step ramp (dark..highlight)."""
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    lum = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
    step = 0 if lum < 0.15 else 1 if lum < 0.55 else 2 if lum < 0.85 else 3
    return base + step


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[0] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def ellipse(self, cx, cy, rx, ry, color_fn):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if dx * dx + dy * dy <= 1:
                    c = color_fn(x, y, dx, dy)
                    if c is not None:
                        self.set(x, y, c)

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


def draw_mon(cv, cx, bottom, rx, ry, view, squish=0.0, step=0):
    """view: 'front', 'back', 'side'. Coordinates in pixels; bottom = lowest body row."""
    rx_s, ry_s = rx * (1 + squish), ry * (1 - squish)
    cy = bottom - ry_s
    foot_r = max(1.5, rx * 0.22)

    # Feet first so the body overlaps them.
    if view == 'side':
        for fx, lift in ((cx - rx * 0.35, step), (cx + rx * 0.3, 1 - step)):
            cv.ellipse(fx, bottom - foot_r * 0.4 - lift, foot_r * 1.1, foot_r * 0.8, lambda *_: 15)
    else:
        for i, fx in enumerate((cx - rx * 0.5, cx + rx * 0.5)):
            lift = (step if i == 0 else 1 - step) if step is not None else 0
            cv.ellipse(fx, bottom - foot_r * 0.4 - lift, foot_r * 1.2, foot_r * 0.8, lambda *_: 15)

    moss_line = {'front': -0.2, 'back': 0.25, 'side': -0.05}[view]

    def body(x, y, dx, dy):
        wave = 0.13 * math.sin(x * 1.3) + 0.07 * math.sin(x * 0.55 + 1)
        if dy < moss_line + wave:
            return shade(dx, dy, 6)
        return shade(dx, dy, 2)

    cv.ellipse(cx, cy, rx_s, ry_s, body)

    # Moss speckles on the stone, deterministic.
    for k in range(int(rx * ry / 18)):
        sx = cx + rx_s * 0.8 * math.sin(k * 2.39 + 0.7)
        sy = cy + ry_s * (0.25 + 0.5 * abs(math.sin(k * 1.71)))
        dx, dy = (sx - cx) / rx_s, (sy - cy) / ry_s
        if dx * dx + dy * dy < 0.75 and int(sy) < cv.h and cv.px[int(sy)][int(sx)] in (2, 3, 4, 5):
            cv.set(int(sx), int(sy), 7)

    unit = max(1.0, rx / 10)

    if view == 'front':
        eye_y = cy + ry_s * 0.12
        for side in (-1, 1):
            ex = cx + side * rx_s * 0.38
            erx, ery = max(1.5, unit * 2.0), max(2.0, unit * 2.6)
            cv.ellipse(ex, eye_y, erx, ery, lambda *_: OUTLINE)
            cv.ellipse(ex, eye_y + ery * 0.15, erx * 0.6, ery * 0.65, lambda *_: 11)
            cv.set(int(ex - erx * 0.3), int(eye_y - ery * 0.35), 10)
            if unit >= 1.5:
                cv.set(int(ex - erx * 0.3) + 1, int(eye_y - ery * 0.35), 10)
            cv.ellipse(cx + side * rx_s * 0.62, eye_y + ery * 1.3, unit * 1.6, unit * 0.9, lambda *_: 12)
        my = int(eye_y + unit * 3.2)
        for mx in range(int(cx - unit), int(cx + unit) + 1):
            cv.set(mx, my + (1 if abs(mx + 0.5 - cx) < unit * 0.5 else 0), OUTLINE)
    elif view == 'side':
        ex = cx - rx_s * 0.55
        ey = cy + ry_s * 0.1
        cv.ellipse(ex, ey, max(1.0, unit * 1.3), max(1.5, unit * 2.2), lambda *_: OUTLINE)
        cv.set(int(ex), int(ey), 11)
        cv.set(int(ex - rx_s * 0.15), int(ey + unit * 2.5), 12)
    else:
        # Small leaf tail on the back.
        cv.ellipse(cx + rx_s * 0.15, bottom - ry_s * 0.35, unit * 2.2, unit * 1.4, lambda x, y, dx, dy: shade(dx, dy, 6))

    # Sprout: stem, two leaves, flower.
    top = cy - ry_s
    tilt = squish * 6
    stem_h = max(2, int(unit * 5))
    for i in range(stem_h):
        cv.set(int(cx + tilt * i / stem_h), int(top - i + 1), 7)
    leaf_y = top - stem_h * 0.45
    lr = max(1.2, unit * 2.6)
    cv.ellipse(cx - lr * 1.05, leaf_y, lr, lr * 0.55, lambda x, y, dx, dy: shade(dx, dy, 6))
    cv.ellipse(cx + lr * 1.05, leaf_y - unit * 0.5, lr, lr * 0.55, lambda x, y, dx, dy: shade(dx, dy, 6))
    fx, fy = cx + tilt, top - stem_h
    pr = max(1.0, unit * 1.3)
    for a in range(5):
        ang = a * 2 * math.pi / 5 - math.pi / 2
        cv.ellipse(fx + math.cos(ang) * pr * 1.3, fy + math.sin(ang) * pr * 1.3, pr, pr, lambda *_: 13)
    cv.ellipse(fx, fy, pr * 0.9, pr * 0.9, lambda *_: 14)

    cv.outline()


def to_image(canvases, palette, layout='vertical'):
    w, h = canvases[0].w, canvases[0].h
    size = (w, h * len(canvases)) if layout == 'vertical' else (w * len(canvases), h)
    im = Image.new('P', size, 0)
    flat = [c for rgb in palette for c in rgb]
    im.putpalette(flat)
    for i, cv in enumerate(canvases):
        ox, oy = (0, h * i) if layout == 'vertical' else (w * i, 0)
        for y in range(h):
            for x in range(w):
                im.putpixel((ox + x, oy + y), cv.px[y][x])
    return im


def remap(cv, table):
    for row in cv.px:
        for i, c in enumerate(row):
            row[i] = table[c]
    return cv


def write_pal(path, palette):
    lines = ['JASC-PAL', '0100', str(len(palette))] + [f'{r} {g} {b}' for r, g, b in palette]
    Path(path).write_text('\r\n'.join(lines) + '\r\n')


def save_png(im, path):
    im.save(path, bits=4 if len(im.getpalette()) // 3 <= 16 else 8)


def read_jasc(path):
    rows = Path(path).read_text().split()
    n = int(rows[2])
    return [tuple(int(v) for v in rows[3 + i * 3: 6 + i * 3]) for i in range(n)]


def main(out_dir):
    out = Path(out_dir)
    gfx_root = out.parent

    # Front: 64x128, two 64x64 animation frames. Feet end on row 55, leaving the
    # 8 empty bottom rows that frontPicYOffset/backPicYOffset = 8 expect.
    f0, f1 = Canvas(64, 64), Canvas(64, 64)
    draw_mon(f0, 32, 53, 21, 17, 'front', 0.0, None)
    draw_mon(f1, 32, 53, 21, 17, 'front', 0.12, None)
    front = to_image([f0, f1], NORMAL_PAL)

    b = Canvas(64, 64)
    draw_mon(b, 32, 53, 22, 15, 'back', 0.0, None)
    back = to_image([b], NORMAL_PAL)

    # Icon: 32x64, two 32x32 frames, shared icon palette 1.
    i0, i1 = Canvas(32, 32), Canvas(32, 32)
    draw_mon(i0, 16, 28, 10, 8, 'front', 0.0, None)
    draw_mon(i1, 16, 27, 10, 8, 'front', 0.1, None)
    icon_pal = read_jasc(gfx_root / 'icon_palettes' / 'pal1.pal')
    icon = to_image([remap(i0, ICON_REMAP), remap(i1, ICON_REMAP)], icon_pal)

    # Overworld: 192x32 = 6 frames: S, S-walk, N, N-walk, W, W-walk (E = hflip of W).
    ow = []
    for view, step in (('front', 0), ('front', 1), ('back', 0), ('back', 1), ('side', 0), ('side', 1)):
        cv = Canvas(32, 32)
        draw_mon(cv, 16, 29 - (1 if step else 0), 9, 7, view, 0.0, step)
        ow.append(cv)
    overworld = to_image(ow, NORMAL_PAL, layout='horizontal')

    # Footprint: 16x16 1bpp, a pebble-shaped print with three toe dots.
    fp = Image.new('P', (16, 16), 0)
    fp.putpalette([255, 255, 255, 0, 0, 0])
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - 8) / 4.5, (y + 0.5 - 10) / 4
            if dx * dx + dy * dy <= 1:
                fp.putpixel((x, y), 1)
    for tx in (3, 8, 13):
        for y in range(2, 5):
            for x in range(tx - 1, tx + 1):
                fp.putpixel((x, y), 1)

    for suffix in ('', '_gba'):
        save_png(front, out / f'anim_front{suffix}.png')
        save_png(back, out / f'back{suffix}.png')
        save_png(icon, out / f'icon{suffix}.png')
        write_pal(out / f'normal{suffix}.pal', NORMAL_PAL)
        write_pal(out / f'shiny{suffix}.pal', SHINY_PAL)
    save_png(overworld, out / 'overworld.png')
    write_pal(out / 'overworld_normal.pal', NORMAL_PAL)
    write_pal(out / 'overworld_shiny.pal', SHINY_PAL)
    fp.save(out / 'footprint.png', bits=1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
