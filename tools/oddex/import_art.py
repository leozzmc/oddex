#!/usr/bin/env python3
"""Import outside artwork (any PNG: RGBA, truecolour or indexed) into a species' sprite folder.

Usage (repository root):
  python3 tools/oddex/import_art.py SHADEPUP --front art/front.png --back art/back.png
      [--front2 art/front_frame2.png] [--icon art/icon.png] [--overworld art/overworld.png]
      [--out DIR]   # default: game/<[graphics] dir> from content/species/<id>.toml

What it does so the result passes tools/oddex/gen_species.py:
- transparency from the alpha channel, or from the top-left pixel when there is none;
- crops to the drawing, shrinks it to fit if needed, and bottom-aligns it on row 55 of a
  64x64 frame (Y offset 8), centred;
- quantizes front + back together to 15 colours plus transparent (they share normal.pal),
  and derives shiny.pal by rotating the hue;
- icon: given 32x32/32x64 art or a shrunk front sprite, remapped onto the closest shared
  icon palette (graphics/pokemon/icon_palettes/pal0..5);
- overworld: given 192x32 art or 6 frames shrunk from front/back; footprint: a plain print.
Afterwards delete [graphics.placeholder] from the species TOML so placeholder_art.py
leaves the folder alone. Sizes, offsets and the icon palette are derived at build time.
"""
import argparse
import colorsys
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from placeholder_art import footprint, read_jasc, write_jasc  # noqa: E402
from species_data import GAME, load_species  # noqa: E402

TRANSPARENT_RGB = (152, 200, 176)


def pixels(im):
    return list(im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata())


def load_rgba(path):
    im = Image.open(path)
    has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    im = im.convert('RGBA')
    if not has_alpha:
        key = im.getpixel((0, 0))[:3]
        im.putdata([(r, g, b, 0) if (r, g, b) == key else (r, g, b, 255) for r, g, b, _ in pixels(im)])
    return im


def fit(im, size, bottom, max_w=None, max_h=None):
    """Crop to content, shrink to fit, paste bottom-aligned and centred on a transparent canvas."""
    box = im.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox()
    canvas = Image.new('RGBA', size, (0, 0, 0, 0))
    if not box:
        return canvas
    im = im.crop(box)
    max_w = max_w or size[0]
    max_h = max_h or bottom + 1
    scale = min(1.0, max_w / im.width, max_h / im.height)
    if scale < 1.0:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    canvas.paste(im, ((size[0] - im.width) // 2, bottom + 1 - im.height), im)
    return canvas


def opaque(im):
    return [px[:3] for px in pixels(im) if px[3] >= 128]


def quantize(images, colors=15):
    """Shared palette for several RGBA images: index 0 transparent + up to `colors` colours."""
    pixels = [p for im in images for p in opaque(im)] or [(0, 0, 0)]
    strip = Image.new('RGB', (len(pixels), 1))
    strip.putdata(pixels)
    q = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    raw = q.getpalette()[: colors * 3]
    pal = [tuple(raw[i: i + 3]) for i in range(0, len(raw), 3)]
    pal += [(0, 0, 0)] * (colors - len(pal))
    return [TRANSPARENT_RGB] + pal


def nearest(pal, rgb, start=1):
    return min(range(start, len(pal)), key=lambda k: sum((a - b) ** 2 for a, b in zip(pal[k], rgb)))


def to_indexed(images, pal, layout='vertical'):
    w, h = images[0].size
    size = (w, h * len(images)) if layout == 'vertical' else (w * len(images), h)
    out = Image.new('P', size, 0)
    out.putpalette([c for rgb in pal for c in rgb] + [0] * (768 - 3 * len(pal)))
    cache = {}
    for i, im in enumerate(images):
        ox, oy = (0, h * i) if layout == 'vertical' else (w * i, 0)
        for y in range(h):
            for x in range(w):
                r, g, b, a = im.getpixel((x, y))
                if a >= 128:
                    if (r, g, b) not in cache:
                        cache[(r, g, b)] = nearest(pal, (r, g, b))
                    out.putpixel((ox + x, oy + y), cache[(r, g, b)])
    return out


def shiny(pal):
    out = [pal[0]]
    for r, g, b in pal[1:]:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        rr, gg, bb = colorsys.hsv_to_rgb((h + 0.45) % 1, s, v)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return out


def icon_frames(args, front):
    if args.icon:
        src = load_rgba(args.icon)
        frames = [src.crop((0, 0, 32, 32)), src.crop((0, 32, 32, 64))] if src.height >= 64 else [src, src]
        return [fit(f, (32, 32), 29) for f in frames]
    small = fit(front, (32, 32), 29, 28, 28)
    return [small, fit(front, (32, 32), 28, 28, 28)]


def best_icon(images):
    used = [p for im in images for p in opaque(im)]
    best = None
    for idx in range(6):
        pal = read_jasc(GAME / f'graphics/pokemon/icon_palettes/pal{idx}.pal')
        err = sum(min(sum((a - b) ** 2 for a, b in zip(pal[k], c)) for k in range(1, 16)) for c in set(used))
        if best is None or err < best[0]:
            best = (err, idx, pal)
    return best[1], best[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('id')
    ap.add_argument('--front', required=True)
    ap.add_argument('--front2')
    ap.add_argument('--back', required=True)
    ap.add_argument('--icon')
    ap.add_argument('--overworld')
    ap.add_argument('--out')
    args = ap.parse_args()

    if args.out:
        out = Path(args.out)
    else:
        spec = next((s for s in load_species() if s['id'] == args.id), None)
        if spec is None:
            sys.exit(f'import_art: no content/species TOML with id {args.id}')
        out = GAME / spec['graphics']['dir']
    out.mkdir(parents=True, exist_ok=True)

    front = fit(load_rgba(args.front), (64, 64), 55)
    front2 = fit(load_rgba(args.front2), (64, 64), 55) if args.front2 else front
    back = fit(load_rgba(args.back), (64, 64), 55)
    pal = quantize([front, front2, back])
    to_indexed([front, front2], pal).save(out / 'anim_front.png', bits=4)
    to_indexed([back], pal).save(out / 'back.png', bits=4)

    icons = icon_frames(args, front)
    icon_index, icon_pal = best_icon(icons)
    to_indexed(icons, icon_pal).save(out / 'icon.png', bits=4)

    if args.overworld:
        ow_src = load_rgba(args.overworld)
        ow = [fit(ow_src.crop((i * 32, 0, i * 32 + 32, 32)), (32, 32), 30) for i in range(6)]
    else:
        ow = []
        for src, step in ((front, 0), (front, 1), (back, 0), (back, 1), (front, 0), (front, 1)):
            ow.append(fit(src, (32, 32), 30 - step, 28, 28))
    ow_pal = quantize(ow)
    to_indexed(ow, ow_pal, layout='horizontal').save(out / 'overworld.png', bits=4)

    footprint('blob').save(out / 'footprint.png', bits=1)
    write_jasc(out / 'normal.pal', pal)
    write_jasc(out / 'shiny.pal', shiny(pal))
    write_jasc(out / 'overworld_normal.pal', ow_pal)
    write_jasc(out / 'overworld_shiny.pal', shiny(ow_pal))
    print(f'imported into {out} (icon palette {icon_index}); remove [graphics.placeholder] from the TOML if present')


if __name__ == '__main__':
    main()
