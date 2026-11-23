#!/usr/bin/env python3
"""Draw the title screen's back layer (Utsuroban, the ship from the sky, where vanilla has Rayquaza), the
ODDEX version banner and the line under PRESS START.

    python3 tools/oddex/title_art.py [--preview OUT.png]

The layer keeps vanilla's format exactly (src/title_screen.c), so no C changes:
- BG0, 16 colours, a full 240x160 picture: graphics/title_screen/rayquaza.png is a sheet of at
  most 256 8x8 tiles (128x128) and rayquaza.bin a 32x32 tilemap, every visible cell on BG
  palette 14.
- Palette 14 (rayquaza_and_clouds.pal) is shared with the scrolling clouds, which use index 2
  (white) and 12, so those two colours are kept. Indices 4-10 are the sky bands and 11 the
  silhouette, as in vanilla.
- Index 15 is rewritten by UpdateLegendaryMarkingColor every fourth frame, from yellow
  (255, 255, 98) down to the silhouette colour and back: whatever is drawn in 15 pulses. Here that
  is the windows, the rim lights, the signs on the hull and the edges of the beam.
- Text is drawn over this layer: PRESS START (y 104-112, x 88-152) and the copyright line
  (y 144-152). Nothing in index 15 lies under PRESS START.
The box in the beam is a plain dark box on one cord: no cross on it (a protected emblem).
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pixelkit import ellipse, line, polygon, rect  # noqa: E402

OUT = HERE.parent.parent / 'game' / 'graphics' / 'title_screen'
W, H = 240, 160
SKY = [10, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4]   # the band of each tile row, as in vanilla
DARK, SEAM, EDGE, WHITE, GLOW = 11, 1, 3, 2, 15
# Palette 14. 2 and 12 belong to the clouds; 15 is overwritten at run time (its value here is the dark end).
PALETTE = [(189, 106, 8), (0, 49, 66), (255, 255, 255), (41, 123, 131), (8, 156, 106), (8, 139, 115), (8, 123, 123),
           (0, 115, 131), (0, 98, 139), (0, 82, 148), (0, 74, 164), (0, 74, 98), (180, 230, 172), (255, 255, 255),
           (255, 0, 0), (0, 74, 98)]
GLOW_BRIGHT = (255, 255, 98)
PRESS_START = (88, 104, 152, 112)   # x0, y0, x1, y1 of the text drawn over the layer
CX = 120


def draw():
    """The 240x160 picture as rows of palette indices."""
    g = [[SKY[y // 8]] * W for y in range(H)]

    def fill(mask, colour):
        for x, y in mask:
            if 0 <= x < W and 0 <= y < H:
                g[y][x] = colour

    # The beam first: two bright edges spreading down from under the hull, a few motes of light
    # between them. Its inside stays sky so the copyright line over it reads.
    for side in (-1, 1):
        for dx in (0, 1):
            fill(line(CX + side * (12 + dx), 136, CX + side * (36 + dx), H - 1), GLOW)
    for x, y in ((111, 146), (130, 150), (103, 156), (138, 158), (121, 157), (116, 152)):
        fill({(x, y)}, GLOW)
    # The box no one may touch, on one cord. Plain: nothing crosses it.
    fill(line(CX, 136, CX, 141), DARK)
    fill(rect(CX - 6, 141, 13, 8), DARK)
    fill(rect(CX - 6, 141, 13, 1), EDGE)

    # The ship: a dome over a wide rim over a deep hull, all one dark silhouette.
    dome = {p for p in ellipse(CX, 110, 58, 27) if p[1] <= 110}
    hull = {p for p in ellipse(CX, 111, 70, 26) if p[1] >= 111}
    rim = ellipse(CX, 111, 98, 7)
    fill(dome | hull | rim | ellipse(CX, 82, 5, 3), DARK)
    fill({(x, y) for x, y in dome if (x - 1, y - 1) not in dome and x < CX - 8}, EDGE)   # light on the dome's upper left
    fill({(x, y) for x, y in rim if (x, y - 1) not in rim | dome}, EDGE)                # and along the rim's top edge
    for dx in (-46, -23, 0, 23, 46):   # seams between the hull's iron plates
        fill({(CX + dx + (dx * (y - 111)) // 70, y) for y in range(118, 137)} & hull, SEAM)
    fill({(x, y) for x, y in hull if (x, y + 1) not in hull}, SEAM)

    # The band of windows, lit from inside. It ends above PRESS START.
    for x0, x1 in ((78, 98), (104, 136), (142, 162)):
        fill({(x, y) for x in range(x0, x1 + 1) for y in range(90, 103)} & dome, GLOW)
    # The visitor at the middle window: a large head, two large almond eyes, no mouth.
    fill({p for p in ellipse(CX, 100, 11, 9) if p[1] <= 102}, DARK)
    for side in (-1, 1):
        fill({(CX + side * dx, y) for dx, y in ((7, 96), (6, 96), (5, 96), (6, 97), (5, 97), (4, 97), (3, 97), (4, 98), (3, 98),
                                                 (2, 98))}, WHITE)
    for cx in (89, 151):   # and smaller heads behind the side windows
        fill({p for p in ellipse(cx, 102, 5, 6) if p[1] <= 102}, DARK)
        fill({(cx - 3, 100), (cx - 2, 100), (cx + 1, 100), (cx + 2, 100)}, WHITE)
    # Lights along the rim, none behind PRESS START.
    for dx in (-90, -75, -60, -45, 45, 60, 75, 90):
        fill(rect(CX + dx - 1, 111, 3, 2), GLOW)
    # Four signs on the hull that no one can read (plain shapes): a ring, two bars, a wedge, three dots.
    fill(ellipse(96, 124.5, 4.5, 4.5) - ellipse(96, 124.5, 2.4, 2.4), GLOW)
    fill(rect(109, 120, 2, 9) | rect(114, 120, 2, 9), GLOW)
    fill(polygon([(123, 129), (128, 119), (133, 129)]) - polygon([(126, 127), (128, 123), (130, 127)]), GLOW)
    fill(rect(141, 120, 3, 3) | rect(146, 123, 3, 3) | rect(141, 126, 3, 3), GLOW)
    return g


def tilemap(g):
    """(tiles, entries): the distinct 8x8 tiles (tile 0 blank) and a 32x32 map of
    tile | hflip << 10 | vflip << 11 | 14 << 12, reusing a tile for its mirror images."""
    tiles, index, entries = [bytes(64)], {bytes(64): (0, 0)}, []
    for ty in range(32):
        for tx in range(32):
            if tx >= W // 8 or ty >= H // 8:
                entries.append(14 << 12)
                continue
            rows = [g[ty * 8 + y][tx * 8:tx * 8 + 8] for y in range(8)]
            key = bytes(c for r in rows for c in r)
            if key not in index:
                n = len(tiles)
                tiles.append(key)
                for hf in (0, 1):
                    for vf in (0, 1):
                        flipped = [r[::-1] if hf else r for r in (rows[::-1] if vf else rows)]
                        index.setdefault(bytes(c for r in flipped for c in r), (n, hf << 10 | vf << 11))
            n, flips = index[key]
            entries.append(n | flips | 14 << 12)
    return tiles, entries


def untile(tiles, entries):
    """The visible 240x160 picture a tile sheet and map produce (for the test and the preview)."""
    g = [[0] * W for _ in range(H)]
    for i, e in enumerate(entries):
        tx, ty = i % 32, i // 32
        if tx >= W // 8 or ty >= H // 8:
            continue
        t = tiles[e & 0x3FF]
        for y in range(8):
            for x in range(8):
                g[ty * 8 + (7 - y if e >> 11 & 1 else y)][tx * 8 + (7 - x if e >> 10 & 1 else x)] = t[y * 8 + x]
    return g


def write(tiles, entries, out=OUT):
    if len(tiles) > 256:
        sys.exit(f'title_art: {len(tiles)} tiles, the sheet holds 256')
    sheet = Image.new('P', (128, 128), 0)
    sheet.putpalette([v for c in PALETTE for v in c])
    for n, t in enumerate(tiles):
        sheet.paste(Image.frombytes('P', (8, 8), t), (n % 16 * 8, n // 16 * 8))
    sheet.save(out / 'rayquaza.png', bits=4)
    (out / 'rayquaza.bin').write_bytes(struct.pack('<1024H', *entries))
    (out / 'rayquaza_and_clouds.pal').write_text('JASC-PAL\r\n0100\r\n16\r\n' + ''.join(f'{r} {g} {b}\r\n' for r, g, b in PALETTE))


def preview(g, path):
    """The layer with the glow at its bright and its dark end, side by side at 2x."""
    im = Image.new('RGB', (W * 2 + 8, H), (30, 30, 30))
    for k, glow in enumerate((GLOW_BRIGHT, PALETTE[GLOW])):
        pal = PALETTE[:GLOW] + [glow]
        for y in range(H):
            for x in range(W):
                im.putpixel((k * (W + 8) + x, y), pal[g[y][x]])
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(path)


# --- the version banner and the line under PRESS START --------------------------------------------

BANNER_PAL_KEY = 0                    # emerald_version.png: index 0 is the transparent key, the rest greys
BANNER_DARK = (24, 16, 24)


def banner(palette):
    """ODDEX as the 128x32 version banner (two 64x32 sprites side by side), in vanilla's style:
    chunky white letters rising a little to the right, a heavy dark edge and a drop shadow, the
    edges softened with the palette's greys. Returns rows of palette indices."""
    S = 8
    hi = Image.new('L', (128 * S, 32 * S), 0)
    w, h, t, gap, y0 = 19, 21, 7, 3, 5.5
    c = t * 0.8                       # the horizontal strokes are a little thinner than the stems
    x = (128 - (5 * w + 4 * gap)) / 2

    def letter(draw):
        """Draw one letter on its own layer (so a letter can cut holes without touching its neighbours)."""
        layer = Image.new('L', hi.size, 0)
        d = ImageDraw.Draw(layer)
        draw(lambda x0, y0_, x1, y1, fill=255: d.rectangle([x0 * S, y0_ * S, x1 * S - 1, y1 * S - 1], fill=fill),
             lambda x0, y0_, x1, y1, fill=255: d.ellipse([x0 * S, y0_ * S, x1 * S - 1, y1 * S - 1], fill=fill),
             lambda pts: d.polygon([(px * S, py * S) for px, py in pts], fill=255))
        hi.paste(ImageChops.lighter(hi, layer))

    def o(box, oval, poly, x=x):
        oval(x, y0, x + w, y0 + h)
        oval(x + t, y0 + c, x + w - t, y0 + h - c, 0)

    def dee(x):
        def draw(box, oval, poly):
            oval(x - w * 0.3, y0, x + w, y0 + h)          # the bowl
            box(x - w, y0, x, y0 + h, 0)                  # cut it off at the stem
            oval(x - w * 0.3 + t, y0 + c, x + w - t, y0 + h - c, 0)
            box(x, y0, x + t, y0 + h)                     # the stem
        return draw

    def e(box, oval, poly, x=x + 3 * (w + gap)):
        box(x, y0, x + t, y0 + h)
        box(x, y0, x + w - 2, y0 + c)
        box(x, y0 + h - c, x + w - 2, y0 + h)
        box(x, y0 + h / 2 - c / 2, x + w - 5, y0 + h / 2 + c / 2)

    def ex(box, oval, poly, x=x + 4 * (w + gap) - 1):
        poly([(x, y0), (x + t + 1, y0), (x + w, y0 + h), (x + w - t - 1, y0 + h)])
        poly([(x + w - t - 1, y0), (x + w, y0), (x + t + 1, y0 + h), (x, y0 + h)])

    for draw in (o, dee(x + w + gap), dee(x + 2 * (w + gap)), e, ex):
        letter(draw)
    hi = hi.rotate(3, resample=Image.BICUBIC)   # rising to the right, as vanilla's banner does
    edge = hi.filter(ImageFilter.MaxFilter(2 * 2 * S + 1))                      # a 2px dark edge
    edge = ImageChops.lighter(edge, ImageChops.offset(edge, S, int(1.5 * S)))   # and its drop shadow
    letter, edge = hi.resize((128, 32), Image.BOX), edge.resize((128, 32), Image.BOX)
    greys = [(i, c) for i, c in enumerate(palette) if i != BANNER_PAL_KEY]
    rows = []
    for y in range(32):
        row = []
        for x in range(128):
            if edge.getpixel((x, y)) < 110:
                row.append(BANNER_PAL_KEY)
                continue
            k = letter.getpixel((x, y)) / 255
            top = 255 - 34 * max(0, y - 14) / 14            # white, a little greyer toward the foot
            v = [BANNER_DARK[j] + (top - BANNER_DARK[j]) * k for j in range(3)]
            row.append(min(greys, key=lambda ic: sum((a - b) ** 2 for a, b in zip(ic[1], v)))[0])
        rows.append(row)
    return rows


# The line under PRESS START (press_start.png): the second 8px row of the sheet, from x = 8. In vanilla it
# is the copyright line; here it says what this is. 5 rows of body in the sheet's own shades, a 1px black edge.
FAN_LINE = 'FAN GAME, NOT OFFICIAL'
GLYPHS = {
    'F': ['######', '##....', '#####.', '##....', '##....'], 'A': ['.####.', '##..##', '######', '##..##', '##..##'],
    'N': ['##..##', '###.##', '######', '##.###', '##..##'], 'G': ['.#####', '##....', '##.###', '##..##', '.#####'],
    'M': ['##...##', '###.###', '#######', '##.#.##', '##...##'], 'E': ['######', '##....', '#####.', '##....', '######'],
    'O': ['.####.', '##..##', '##..##', '##..##', '.####.'], 'T': ['######', '..##..', '..##..', '..##..', '..##..'],
    'I': ['##', '##', '##', '##', '##'], 'C': ['.#####', '##....', '##....', '##....', '.#####'],
    'L': ['##....', '##....', '##....', '##....', '######'], ',': ['..', '..', '..', '.#', '.#', '#.'], ' ': ['...'] * 5,
}
LINE_SHADES = [5, 5, 4, 3, 3, 3]   # the sheet's palette indices for each body row, top to bottom
LINE_X0, LINE_X1, LINE_Y = 8, 152, 8   # vanilla's line spans x 8..152 of the row y 8..15


def fan_line(text=FAN_LINE):
    """The 8 rows (160 wide) of the line, as palette indices; the text is centred where vanilla's was."""
    width = sum(len(GLYPHS[ch][0]) + 1 for ch in text) - 1
    if width > LINE_X1 - LINE_X0:
        sys.exit(f'title_art: {text!r} is {width}px wide, the line holds {LINE_X1 - LINE_X0}')
    body = {}
    x = LINE_X0 + (LINE_X1 - LINE_X0 - width) // 2
    for ch in text:
        for j, row in enumerate(GLYPHS[ch]):
            for i, c in enumerate(row):
                if c == '#':
                    body[(x + i, 1 + j)] = LINE_SHADES[j]
        x += len(GLYPHS[ch][0]) + 1
    rows = [[0] * 160 for _ in range(8)]
    for (px, py) in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= px + dx < 160 and 0 <= py + dy < 8:
                    rows[py + dy][px + dx] = 1
    for (px, py), c in body.items():
        rows[py][px] = c
    return rows


def write_text(out=OUT):
    """Rewrite the version banner, and the line under PRESS START in place (PRESS START itself is kept)."""
    b = Image.open(out / 'emerald_version.png')
    pal = b.getpalette()[:48]
    rows = banner([tuple(pal[i * 3:i * 3 + 3]) for i in range(16)])
    b.putdata([c for r in rows for c in r])
    b.save(out / 'emerald_version.png', bits=8)
    p = Image.open(out / 'press_start.png')
    for y, r in enumerate(fan_line()):
        for x, c in enumerate(r):
            p.putpixel((x, LINE_Y + y), c)
    p.save(out / 'press_start.png', bits=8)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--preview')
    args = ap.parse_args()
    g = draw()
    tiles, entries = tilemap(g)
    write(tiles, entries)
    write_text()
    print(f'title_art: {len(tiles)} tiles (256 fit)')
    if args.preview:
        preview(g, args.preview)


if __name__ == '__main__':
    main()
