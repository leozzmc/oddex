#!/usr/bin/env python3
"""Draw 16x16 decoration dolls of original species (content/dolls.toml).

Usage (repository root): python3 tools/oddex/make_dolls.py [ID ...] [--preview sheet.png]

Each doll is the species' overworld front frame (graphics/pokemon/oddex/<dir>/overworld.png,
frame 0, in overworld_normal.pal) cropped to its outline, shrunk to fit 14x14 without blending,
recoloured to the nearest colours of whichever shared NPC object palette (npc_1..npc_4 in
graphics/object_events/palettes/) fits it best, given a 1px dark outline and placed
bottom-centre on a 16x16 canvas. Writes graphics/object_events/pics/dolls/<species lower>_doll.png
and prints the palette; the doll's ObjectEventGraphicsInfo must use that OBJ_EVENT_PAL_TAG_NPC_n
(the tool checks it and fails if they differ). With no ids, draws every doll in content/dolls.toml.
"""
import argparse
import sys
import tomllib
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from species_data import GAME, ROOT, load_species  # noqa: E402

NPC_PALS = {n: GAME / f'graphics/object_events/palettes/npc_{n}.pal' for n in (1, 2, 3, 4)}
GFX_INFO = GAME / 'src/data/object_events/object_event_graphics_info.h'
DOLLS = GAME / 'graphics/object_events/pics/dolls'


def read_jasc(path):
    lines = path.read_text().split('\n')
    n = int(lines[2])
    return [tuple(int(v) for v in lines[3 + i].split()) for i in range(n)]


def frame0(species):
    d = GAME / species['graphics']['dir']
    ow = Image.open(d / 'overworld.png')
    pal = read_jasc(d / 'overworld_normal.pal')
    f = ow.crop((0, 0, 32, 32)).load()
    out = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    o = out.load()
    for y in range(32):
        for x in range(32):
            i = f[x, y]
            if i:
                o[x, y] = pal[i] + (255,)
    return out


def doll(species, pals):
    """The doll in the NPC palette with the smallest total colour error: (palette number, image)."""
    src = frame0(species)
    best = None
    for n, npc in pals.items():
        im, err = doll_in(src, npc)
        if best is None or err < best[2]:
            best = (n, im, err)
    return best[0], best[1]


def doll_in(src, npc):
    box = src.getchannel('A').getbbox()
    src = src.crop(box)
    scale = min(14 / src.width, 14 / src.height, 1.0)
    w, h = max(1, round(src.width * scale)), max(1, round(src.height * scale))
    small = src.resize((w, h), Image.NEAREST)
    colours = npc[1:]
    outline = min(range(len(colours)), key=lambda i: sum(colours[i]))

    err = 0

    def nearest(rgb):
        nonlocal err
        i = min(range(len(colours)), key=lambda i: sum((a - b) ** 2 for a, b in zip(rgb, colours[i])))
        err += sum((a - b) ** 2 for a, b in zip(rgb, colours[i]))
        return i

    canvas = Image.new('P', (16, 16), 0)
    canvas.putpalette([v for rgb in npc for v in rgb])
    c = canvas.load()
    ox, oy = (16 - w) // 2, 15 - h
    s = small.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = s[x, y]
            if a >= 128:
                c[ox + x, oy + y] = 1 + nearest((r, g, b))
    body = {(x, y) for y in range(16) for x in range(16) if c[x, y]}
    for x, y in [(x, y) for y in range(16) for x in range(16) if not c[x, y]]:
        if any((x + dx, y + dy) in body for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c[x, y] = 1 + outline
    return canvas, err


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='*')
    ap.add_argument('--preview', help='write a 4x contact sheet here')
    args = ap.parse_args()
    table = tomllib.loads((ROOT / 'content/dolls.toml').read_text())['dolls']
    by_id = {s['id']: s for s in load_species()}
    ids = args.ids or list(dict.fromkeys(table.values()))
    for sid in ids:
        if sid not in by_id:
            sys.exit(f'make_dolls: no content/species TOML with id {sid}')
    pals = {n: read_jasc(p) for n, p in NPC_PALS.items()}
    info = GFX_INFO.read_text()
    bad = []
    sheet = Image.new('RGB', (20 * len(ids), 20), (152, 200, 176))
    for i, sid in enumerate(ids):
        n, im = doll(by_id[sid], pals)
        out = DOLLS / f'{sid.lower()}_doll.png'
        im.save(out, bits=4)
        print(f'{sid}: {out.relative_to(ROOT)} (OBJ_EVENT_PAL_TAG_NPC_{n})')
        name = ''.join(w.capitalize() for w in sid.split('_')) + 'Doll'
        block = info.split(f'gObjectEventGraphicsInfo_{name} = {{', 1)
        if len(block) == 2 and f'OBJ_EVENT_PAL_TAG_NPC_{n},' not in block[1].split('};', 1)[0]:
            bad.append(f'gObjectEventGraphicsInfo_{name} must use OBJ_EVENT_PAL_TAG_NPC_{n} / PALSLOT_NPC_{n}')
        sheet.paste(im.convert('RGBA'), (2 + 20 * i, 2), im.convert('RGBA'))
    if bad:
        sys.exit('make_dolls: ' + '\n'.join(bad))
    if args.preview:
        sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(args.preview)


if __name__ == '__main__':
    main()
