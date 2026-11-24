#!/usr/bin/env python3
"""64x64 scene sprites of the three legendaries, for the story scenes where the 32px map sprite is too
small (the storm over Sootopolis). Same layout as the vanilla scene objects they stand in for:

  sokonemu, okafumi   scene.png 256x64: front, front (breathing), side (facing west), side (breathing)
                      scene.pal awake, scene_asleep.pal the same pictures as dormant stone, eyes out
  utsuroban           scene_still.png 64x64, and scene.png 320x64 in the order of sAnimTable_Rayquaza:
                      landed and dark, landed and lit, crying out, hovering on its beam, flying off

The front pictures are the approved battle sprites (anim_front.png), so the eyes placed by hand carry
over; only the side views are rendered again, larger. Every picture gets a pale rim outside its dark
outline, from a colour its own palette already has: a dark outline alone disappears on storm-dark water.

  . tools/env.sh && python3 tools/oddex/scene_art.py [--preview OUT.png]
"""
import argparse
import colorsys
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'blender'))
import make_art  # noqa: E402
from import_art import to_indexed  # noqa: E402
from placeholder_art import write_jasc  # noqa: E402

GAME = HERE.parent.parent / 'game' / 'graphics' / 'pokemon' / 'oddex'
SIZE, OUTLINE = 64, 1
# rim: palette index of the pale rim. eyes: indices that glow, put out in the asleep palette.
BEASTS = {'sokonemu': {'rim': 15, 'eyes': (14,)}, 'okafumi': {'rim': 15, 'eyes': (14,)}}
SHIP = {'rim': 13, 'hull_rows': 33, 'glass': {12: 15, 9: 12}, 'dark': {12: 4, 9: 2, 14: 6, 11: 7}, 'streak': 13}


def grid(im):
    return [[im.getpixel((x, y)) for x in range(im.width)] for y in range(im.height)]


def image(g, pal):
    im = Image.new('P', (len(g[0]), len(g)), 0)
    im.putpalette([c for rgb in pal for c in rgb])
    im.putdata([v for row in g for v in row])
    return im


def box(g):
    ys = [y for y, row in enumerate(g) if any(row)]
    xs = [x for row in g for x, v in enumerate(row) if v]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def seat(g, bottom=SIZE - 2, top=None):
    """The content centred in a 64x64 frame, standing on row `bottom` (or hanging from row `top`):
    an object sprite is anchored at the foot of its frame."""
    x0, y0, x1, y1 = box(g)
    w, h = x1 - x0, y1 - y0
    ox, oy = (SIZE - w) // 2, top if top is not None else bottom + 1 - h
    out = [[0] * SIZE for _ in range(SIZE)]
    for y in range(h):
        for x in range(w):
            if 0 <= ox + x < SIZE and 0 <= oy + y < SIZE:
                out[oy + y][ox + x] = g[y0 + y][x0 + x]
    return out


def ring(g, index, around=lambda v: v != 0):
    """Paint `index` on every empty pixel that touches (4 ways) a pixel `around` accepts."""
    out = [row[:] for row in g]
    for y in range(len(g)):
        for x in range(len(g[0])):
            if g[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(g) and 0 <= nx < len(g[0]) and around(g[ny][nx]):
                    out[y][x] = index
                    break
    return out


def breathe(g):
    """The idle frame: one row a third of the way down is dropped and everything above settles 1px."""
    _, y0, _, y1 = box(g)
    cut = y0 + (y1 - y0) // 3
    return [[0] * len(g[0])] + g[:cut] + g[cut + 1:]


def asleep(pal, eyes):
    """Dormant stone: colour mostly drained and a little darker; whatever glows goes as dark as shadow."""
    out = [pal[0]]
    for i, (r, g, b) in enumerate(pal[1:], 1):
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if i in eyes:
            s, v = 0.1, 0.3
        out.append(tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s * 0.25, v * 0.85)))
    return out


def battle_frames(name):
    im = Image.open(GAME / name / 'anim_front.png')
    pal = im.getpalette()[:48]
    pal = [tuple(pal[i * 3:i * 3 + 3]) for i in range(16)]
    return grid(im.crop((0, 0, SIZE, SIZE))), grid(im.crop((0, SIZE, SIZE, 2 * SIZE))), pal


def side_view(name, pal):
    """The model from its right front quarter, facing west as the game's west frames must (the game
    mirrors them for east), at the 64px scale. shortcut: no hand-placed eyes here, the render's own
    are kept; add a PIXELS-style table if a side view ever needs them."""
    with tempfile.TemporaryDirectory() as tmp:
        make_art.render(name, 'normal', Path(tmp), env={'ODDEX_OW_RES': '256', 'ODDEX_SIDE_AZ': '30'})
        view = make_art.outline(make_art.majority(Image.open(Path(tmp) / 'ow_side.png').convert('RGBA'), 4))
    return grid(to_indexed([view], pal))


def beast(name, side=None):
    spec = BEASTS[name]
    a, b, pal = battle_frames(name)
    side = side or side_view(name, pal)
    frames = [seat(a), seat(b), seat(side), seat(breathe(side))]
    return [ring(f, spec['rim']) for f in frames], pal, asleep(pal, spec['eyes'])


def ship():
    a, b, pal = battle_frames('utsuroban')
    swap = lambda g, table: [[table.get(v, v) for v in row] for row in g]  # noqa: E731
    # Without its beam: the hull rows only, the beam's core that shows through the last one filled in,
    # and the outline closed underneath.
    hull = [[2 if v == 15 else v for v in row] for row in a[:SHIP['hull_rows']]] + [[0] * SIZE]
    hull = ring(hull, OUTLINE, around=lambda v: v not in (0, OUTLINE))
    flying = seat(hull, top=2)
    for x, y0, y1 in ((24, 40, 52), (32, 44, 60), (40, 40, 52)):   # three streaks of light left behind
        for y in range(y0, y1):
            flying[y][x] = SHIP['streak']
    frames = [seat(swap(hull, SHIP['dark'])), seat(hull), seat(swap(b, SHIP['glass'])), seat(a), flying]
    return [ring(f, SHIP['rim']) for f in frames], pal


def sheet(frames, pal):
    out = Image.new('P', (SIZE * len(frames), SIZE), 0)
    out.putpalette([c for rgb in pal for c in rgb])
    for i, f in enumerate(frames):
        out.paste(image(f, pal), (SIZE * i, 0))
    return out


def build(sides=None):
    """{name: {file name: indexed image or palette}}. sides: ready side grids, for the test."""
    out = {}
    for name in BEASTS:
        frames, pal, stone = beast(name, (sides or {}).get(name))
        out[name] = {'scene.png': sheet(frames, pal), 'scene.pal': pal, 'scene_asleep.pal': stone}
    frames, pal = ship()
    out['utsuroban'] = {'scene.png': sheet(frames, pal), 'scene_still.png': sheet(frames[3:4], pal), 'scene.pal': pal}
    return out


def write(built):
    for name, files in built.items():
        for file, data in files.items():
            if file.endswith('.pal'):
                write_jasc(GAME / name / file, data)
            else:
                data.save(GAME / name / file, bits=4)


def preview(built, path, scale=3):
    """Every sheet on storm water (darkened the way the rain darkens sprites) and on pale cave sand."""
    rows = []
    for name, files in built.items():
        for file in ('scene.png', 'scene_still.png'):
            if file in files:
                rows += [(files[file], files['scene.pal'])]
        if 'scene_asleep.pal' in files:
            rows += [(files['scene.png'].crop((0, 0, 2 * SIZE, SIZE)), files['scene_asleep.pal'])]
    out = Image.new('RGB', (5 * SIZE * scale, len(rows) * 2 * SIZE * scale), (33, 49, 90))
    for r, (im, pal) in enumerate(rows):
        for half, (back, dim) in enumerate((((33, 49, 90), 0.8), ((214, 198, 165), 1.0))):
            im = im.copy()
            im.putpalette([round(c * dim) for rgb in pal for c in rgb])
            rgba = im.convert('RGBA')
            rgba.putdata([(0, 0, 0, 0) if v == 0 else px for v, px in zip(im.tobytes(), rgba.get_flattened_data())])
            tile = Image.new('RGB', rgba.size, back)
            tile.paste(rgba, (0, 0), rgba)
            out.paste(tile.resize((tile.width * scale, tile.height * scale), Image.NEAREST), (0, (2 * r + half) * SIZE * scale))
    out.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--preview', help='also write an enlarged sheet of every frame on dark and pale ground')
    args = ap.parse_args()
    built = build()
    write(built)
    if args.preview:
        preview(built, args.preview)


if __name__ == '__main__':
    main()
