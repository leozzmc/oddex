#!/usr/bin/env python3
"""Render Blender-modelled species and write their GBA sprite files.

Usage (repository root, after `. tools/env.sh`):
  python3 tools/oddex/blender/make_art.py KAMORAI [ID ...] [--keep DIR] [--preview sheet.png]

For each id the module tools/oddex/blender/species/<model>.py ([graphics] model, default the
id in lower case) is rendered twice (NORMAL and
SHINY colour tables, identical geometry), reduced 4x by per-block majority colour (keeps the
flat toon colours instead of averaging them), outlined, quantized to 15 colours + transparent,
and written to the species' [graphics] dir. The shiny palette is read off the shiny render at
the same pixels, so both palettes share indices exactly.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from import_art import TRANSPARENT_RGB, best_icon, to_indexed, write_jasc  # noqa: E402
from import_art import fit as fit_art, fit_scale  # noqa: E402
from placeholder_art import footprint  # noqa: E402
from species_data import GAME, load_species  # noqa: E402

OUTLINE = (28, 18, 22)


def quantize(images, colors=15):
    """Palette for flat toon renders: keep every exact colour when there are few enough;
    otherwise repeatedly merge the pair that costs least (distance x pixels of the smaller),
    so a small but distinct colour (eyes, water) survives and near-duplicates merge first."""
    counts = Counter()
    for im in images:
        for px in (im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata()):
            if px[3] >= 128:
                counts[px[:3]] += 1
    while len(counts) > colors:
        keys = list(counts)
        best = None
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                d = sum((x - y) ** 2 for x, y in zip(a, b))
                cost = d * min(counts[a], counts[b])
                if best is None or cost < best[0]:
                    best = (cost, a, b)
        _, a, b = best
        keep, drop = (a, b) if counts[a] >= counts[b] else (b, a)
        counts[keep] += counts.pop(drop)
    pal = sorted(counts, key=lambda c: sum(c))
    return [TRANSPARENT_RGB] + pal + [(0, 0, 0)] * (colors - len(pal))


def majority(im, factor):
    """Downscale RGBA by `factor`: a block is opaque if most of it is, coloured by its most
    common opaque colour."""
    w, h = im.size
    src = im.load()
    out = Image.new('RGBA', (w // factor, h // factor), (0, 0, 0, 0))
    dst = out.load()
    half = factor * factor // 2
    for by in range(h // factor):
        for bx in range(w // factor):
            counts = Counter()
            for y in range(by * factor, by * factor + factor):
                for x in range(bx * factor, bx * factor + factor):
                    r, g, b, a = src[x, y]
                    if a >= 128:
                        counts[(r, g, b)] += 1
            if sum(counts.values()) > half:
                dst[bx, by] = counts.most_common(1)[0][0] + (255,)
    return out


def outline(im):
    """1px dark outline around the silhouette."""
    w, h = im.size
    src = im.load()
    out = im.copy()
    dst = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3]:
                    dst[x, y] = OUTLINE + (255,)
                    break
    return out


def render(module, variant, out, env=None):
    """env: extra environment for render_species.py (ODDEX_LAYERS, ODDEX_PALETTE)."""
    blender = os.environ.get('BLENDER')
    if not blender:
        sys.exit('make_art: $BLENDER is not set; run `. tools/env.sh` first')
    cmd = [blender, '-b', '--factory-startup', '-P', str(HERE / 'render_species.py'), '--', module, str(out), variant]
    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, **(env or {})})
    if result.returncode or 'Traceback' in result.stderr + result.stdout:
        sys.exit(f'make_art: Blender failed for {module} ({variant}):\n{result.stdout[-2000:]}{result.stderr[-2000:]}')


def views(out):
    """Reduced, outlined RGBA images for every rendered view."""
    v = {}
    for name in ('front', 'front2', 'back'):
        v[name] = outline(majority(Image.open(out / f'{name}.png').convert('RGBA'), 4))
    v['icon'] = outline(majority(Image.open(out / 'front.png').convert('RGBA'), 9))
    for name in ('ow_front', 'ow_back', 'ow_side'):
        v[name] = outline(majority(Image.open(out / f'{name}.png').convert('RGBA'), 4))
    return v


def shiny_palette(indexed_images, shiny_images, pal):
    """For each palette index, the colour the shiny render has at those same pixels."""
    votes = [Counter() for _ in pal]
    for idx_im, sh_im in zip(indexed_images, shiny_images):
        ip, sp = idx_im.load(), sh_im.load()
        for y in range(idx_im.height):
            for x in range(idx_im.width):
                i = ip[x, y]
                if i and sp[x, y][3]:
                    votes[i][sp[x, y][:3]] += 1
    return [pal[0]] + [v.most_common(1)[0][0] if v else pal[i] for i, v in enumerate(votes) if i]


def make(spec, keep=None):
    module = spec['graphics'].get('model', spec['id'].lower())
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(keep) / module if keep else Path(tmp)
        render(module, 'normal', base / 'normal')
        render(module, 'shiny', base / 'shiny')
        return write_sprites(base, GAME / spec['graphics']['dir'])


def write_sprites(base, out):
    """Turn the renders in base/normal and base/shiny into every sprite file and palette in out
    (also used by tools/oddex/likeness/compose.py, which writes outside the repo)."""
    n, s = views(base / 'normal'), views(base / 'shiny')
    kind = json.loads((base / 'normal' / 'opts.json').read_text())['kind']

    def fit(im, size, bottom, scale=None):
        return fit_art(im, size, bottom, resample=Image.NEAREST, scale=scale)

    def placed(v, names, size, bottom):
        return [fit(v[name], size, bottom) for name in names]

    # Battle sprites share one palette; the second front frame is the squashed render.
    fronts, backs = placed(n, ('front', 'front2'), (64, 64), 55), placed(n, ('back',), (64, 64), 55)
    pal = quantize(fronts + backs)
    front_ix, back_ix = to_indexed(fronts, pal), to_indexed(backs, pal)
    s_fronts, s_backs = placed(s, ('front', 'front2'), (64, 64), 55), placed(s, ('back',), (64, 64), 55)
    frames_ix = [to_indexed([f], pal) for f in fronts + backs]
    s_pal = shiny_palette(frames_ix, s_fronts + s_backs, pal)

    icons = [fit(n['icon'], (32, 32), 29), fit(n['icon'], (32, 32), 28)]
    icon_index, icon_pal = best_icon(icons)
    icon_ix = to_indexed(icons, icon_pal)

    # Overworld: S, S-walk, N, N-walk, W, W-walk (east is mirrored by the game). One scale for
    # every frame (the renders share one too), so the creature keeps its size as it turns.
    names = ('ow_front', 'ow_back', 'ow_side')
    k = fit_scale([n[name] for name in names], (32, 32), 29)
    ow, s_ow = [], []
    for name in names:
        ow += [fit(n[name], (32, 32), 30, k), fit(n[name], (32, 32), 29, k)]
        s_ow += [fit(s[name], (32, 32), 30, k), fit(s[name], (32, 32), 29, k)]
    ow_pal = quantize(ow)
    ow_ix = to_indexed(ow, ow_pal, layout='horizontal')
    s_ow_pal = shiny_palette([to_indexed([f], ow_pal) for f in ow], s_ow, ow_pal)

    out.mkdir(parents=True, exist_ok=True)
    front_ix.save(out / 'anim_front.png', bits=4)
    back_ix.save(out / 'back.png', bits=4)
    icon_ix.save(out / 'icon.png', bits=4)
    ow_ix.save(out / 'overworld.png', bits=4)
    footprint('quadruped' if kind == 'beast' else 'blob').save(out / 'footprint.png', bits=1)
    write_jasc(out / 'normal.pal', pal)
    write_jasc(out / 'shiny.pal', s_pal)
    write_jasc(out / 'overworld_normal.pal', ow_pal)
    write_jasc(out / 'overworld_shiny.pal', s_ow_pal)
    return front_ix, back_ix, icon_ix, ow_ix, pal, s_pal, icon_index


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--keep', help='keep the raw renders under this directory')
    ap.add_argument('--preview', help='write a contact sheet (normal and shiny, 3x) here')
    args = ap.parse_args()
    by_id = {s['id']: s for s in load_species()}
    rows = []
    for sid in args.ids:
        if sid not in by_id:
            sys.exit(f'make_art: no content/species TOML with id {sid}')
        model = by_id[sid]['graphics'].get('model', sid.lower())
        if not (HERE / 'species' / f'{model}.py').exists():
            sys.exit(f'make_art: no model tools/oddex/blender/species/{model}.py')
        front, back, icon, ow, pal, s_pal, icon_index = make(by_id[sid], args.keep)
        print(f'{sid}: {len([c for c in pal[1:] if c != (0, 0, 0)])} palette colours, icon palette {icon_index}')
        rows.append((front, back, icon, ow, pal, s_pal))
    if args.preview:
        preview_sheet(rows, args.preview)


def preview_sheet(rows, path):
    """Contact sheet, 3x: front and back in normal and shiny colours, icon, overworld strip.
    rows: (front, back, icon, ow, pal, s_pal) per species."""
    sheet = Image.new('RGB', ((64 * 2 + 64 * 2 + 32 + 192 + 50), 64 * len(rows)), (152, 200, 176))
    for r, (front, back, icon, ow, pal, s_pal) in enumerate(rows):
        x = 0
        for im, p in ((front.crop((0, 0, 64, 64)), pal), (back, pal), (front.crop((0, 0, 64, 64)), s_pal), (back, s_pal)):
            c = im.copy()
            c.putpalette([v for rgb in p for v in rgb])
            sheet.paste(c.convert('RGB'), (x, r * 64))
            x += 74
        sheet.paste(icon.crop((0, 0, 32, 32)).convert('RGB'), (x, r * 64))
        sheet.paste(ow.convert('RGB'), (x + 42, r * 64))
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(path)


if __name__ == '__main__':
    main()
