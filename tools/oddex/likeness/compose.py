#!/usr/bin/env python3
"""Build the private likeness sprites for head-only characters (the starters).

Usage (repository root, after `. tools/env.sh`):
  python3 tools/oddex/likeness/compose.py TREKKEYE [ID ...] [--preview sheet.png] [--keep DIR]

Everything this reads and writes lives outside the repository, under $ODDEX_PRIVATE
(default ~/oddex-private), and must never be committed (CLAUDE.md, private art):
  likeness/crop.toml        per id: photo (relative to $ODDEX_PRIVATE), the head ellipse
                            center/radii in that photo, and points to sample colours from
  likeness/<dir>/...        output, mirroring game/graphics/pokemon/oddex/<dir>/;
                            tools/oddex/build_private.sh lays it over the public sprites

For each id the species' Blender model is rendered with ODDEX_LAYERS (the parts behind the head,
the parts in front of it, and the head's pixel box) and with colours sampled from the photo
(ODDEX_PALETTE, so the back and overworld views match). The photo's head is cut out with an
egg-shaped mask, reduced to a few colours, and laid between the two layers in the front frames;
then the normal make_art pipeline writes every sprite and palette. The face pixels are identical
in the normal and shiny renders, so the shiny palette still shares indices.
"""
import argparse
import json
import os
import sys
import tempfile
import tomllib
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'blender'))
from make_art import preview_sheet, render, write_sprites  # noqa: E402
from species_data import load_species  # noqa: E402

PRIVATE = Path(os.environ.get('ODDEX_PRIVATE', Path.home() / 'oddex-private'))
FACE_COLOURS = 8


def to_linear(c):
    """sRGB 0-255 -> the linear 0-1 value a toon material needs to show that colour."""
    c = c / 255
    return round(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4, 4)


def sample(photo, xy, r=6):
    x, y = xy
    px = list(photo.crop((x - r, y - r, x + r + 1, y + r + 1)).get_flattened_data())
    px.sort(key=sum)
    return px[len(px) // 2]   # median by brightness: ignores a stray highlight or shadow


def head_cutout(photo, cfg):
    """The head ellipse from the photo as RGBA: an egg-shaped mask whose lower half narrows
    toward the chin, and the colours reduced so the 4x block downscale stays clean."""
    cx, cy = cfg['center']
    rx, ry = cfg['radii']
    chin = cfg.get('chin', 0.25)
    box = photo.crop((cx - rx, cy - ry, cx + rx, cy + ry))
    # Stretch contrast and colour a little first: a soft, low-contrast photo otherwise loses its
    # features when the face shares 15 colours with the rendered parts.
    box = ImageOps.autocontrast(box, cutoff=1)
    box = ImageEnhance.Color(box).enhance(cfg.get('saturation', 1.2))
    box = box.quantize(FACE_COLOURS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    mask = Image.new('L', box.size, 0)
    w, h = box.size
    m = mask.load()
    for y in range(h):
        dy = (y + 0.5 - h / 2) / (h / 2)
        narrow = 1 - chin * max(0.0, dy)
        for x in range(w):
            dx = (x + 0.5 - w / 2) / (w / 2) / narrow
            if dx * dx + dy * dy <= 1:
                m[x, y] = 255
    cut = box.convert('RGBA')
    cut.putalpha(mask)
    return cut


def compose_front(render_dir, frame, cut):
    behind = Image.open(render_dir / f'{frame}_behind.png').convert('RGBA')
    front = Image.open(render_dir / f'{frame}_front.png').convert('RGBA')
    x0, y0, x1, y1 = json.loads((render_dir / 'head_box.json').read_text())[frame]
    face = cut.resize((x1 - x0, y1 - y0), Image.NEAREST)
    out = behind.copy()
    out.alpha_composite(face, (x0, y0))
    out.alpha_composite(front)
    # Drop the anti-aliased half-alpha the layers do not have, so the majority downscale sees
    # only opaque colours.
    a = out.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
    out.putalpha(a)
    out.save(render_dir / f'{frame}.png')


def build(spec, cfg, keep=None):
    module = spec['graphics'].get('model', spec['id'].lower())
    photo = ImageOps.exif_transpose(Image.open(PRIVATE / cfg['photo'])).convert('RGB')
    colours = {k: tuple(to_linear(v) for v in sample(photo, xy)) for k, xy in cfg.get('sample', {}).items()}
    cut = head_cutout(photo, cfg)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(keep) / module if keep else Path(tmp)
        for variant in ('normal', 'shiny'):
            # Skin is the person's own in both; the shiny keeps its own hair and accessories.
            override = colours if variant == 'normal' else {k: v for k, v in colours.items() if k == 'skin'}
            pal = Path(tmp) / f'palette_{variant}.json'
            pal.write_text(json.dumps(override))
            render(module, variant, base / variant, env={'ODDEX_LAYERS': '1', 'ODDEX_PALETTE': str(pal)})
            for frame in ('front', 'front2'):
                compose_front(base / variant, frame, cut)
        out = PRIVATE / 'likeness' / Path(spec['graphics']['dir']).name
        return write_sprites(base, out), out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--keep', help='keep the layered renders under this directory (keep it private too)')
    ap.add_argument('--preview', help='write a contact sheet here (keep it private too)')
    args = ap.parse_args()
    for path in [args.keep, args.preview]:
        if path and Path(path).resolve().is_relative_to(HERE.parent.parent.parent):
            sys.exit('compose: --keep/--preview must point outside the repository')
    crops = tomllib.loads((PRIVATE / 'likeness' / 'crop.toml').read_text())
    by_id = {s['id']: s for s in load_species()}
    rows = []
    for sid in args.ids:
        if sid not in by_id or sid not in crops:
            sys.exit(f'compose: {sid} needs a content/species TOML and an entry in {PRIVATE}/likeness/crop.toml')
        (front, back, icon, ow, pal, s_pal, icon_index), out = build(by_id[sid], crops[sid], args.keep)
        print(f'{sid}: {len([c for c in pal[1:] if c != (0, 0, 0)])} palette colours, icon palette {icon_index} -> {out}')
        rows.append((front, back, icon, ow, pal, s_pal))
    if args.preview:
        preview_sheet(rows, args.preview)


if __name__ == '__main__':
    main()
