"""Hand-placed pixel art for GBA sprites (docs/ART_GUIDELINES.md): shapes are laid out directly
on the pixel grid in palette indices, never rendered and shrunk.

A Canvas is a w x h grid of palette indices (0 = transparent). Shapes are masks (sets of (x, y));
`part()` fills a mask with a colour (or a per-pixel shading function) and draws its own 1px
outline, so parts drawn later overlap earlier ones with a clean edge, painter's style.
`write_species()` turns finished canvases into every sprite file the game needs
(tools/oddex/pixel/<species>.py are the designs).
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from import_art import TRANSPARENT_RGB, best_icon, to_indexed, write_jasc  # noqa: E402
from placeholder_art import footprint  # noqa: E402


def ellipse(cx, cy, rx, ry):
    """Pixels whose centres fall inside the ellipse."""
    return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}


def polygon(points):
    """Pixels whose centres fall inside the polygon (even-odd rule)."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    out = set()
    for y in range(int(min(ys)), int(max(ys)) + 1):
        for x in range(int(min(xs)), int(max(xs)) + 1):
            px, py, inside = x + 0.5, y + 0.5, False
            for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
                if (y0 > py) != (y1 > py) and px < x0 + (py - y0) * (x1 - x0) / (y1 - y0):
                    inside = not inside
            if inside:
                out.add((x, y))
    return out


def rect(x, y, w, h):
    return {(i, j) for j in range(y, y + h) for i in range(x, x + w)}


def edge(mask):
    """Pixels of the mask with a 4-neighbour outside it: the mask's own 1px outline."""
    return {(x, y) for x, y in mask if any(n not in mask for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}


def line(x0, y0, x1, y1):
    """A 1px line (Bresenham): diagonal steps stay connected corner to corner."""
    out, dx, dy = set(), abs(x1 - x0), -abs(y1 - y0)
    sx, sy, err = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1), abs(x1 - x0) - abs(y1 - y0)
    while True:
        out.add((x0, y0))
        if (x0, y0) == (x1, y1):
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def mirror(mask, width):
    """Flip left-right: x -> width - 1 - x, i.e. about the pixel-centre line x = (width - 1) / 2."""
    return {(width - 1 - x, y) for x, y in mask}


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[0] * w for _ in range(h)]

    def put(self, mask, colour):
        """colour: a palette index, or a function (x, y) -> index."""
        for x, y in mask:
            if 0 <= x < self.w and 0 <= y < self.h:
                self.px[y][x] = colour(x, y) if callable(colour) else colour

    def part(self, mask, colour, outline):
        self.put(mask, colour)
        if outline is not None:
            self.put(edge(mask), outline)

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else 0

    def shifted(self, dx, dy):
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                out.px[y][x] = self.get(x - dx, y - dy)
        return out

    def image(self, pal):
        """RGBA image in `pal` colours (index 0 transparent)."""
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                i = self.px[y][x]
                if i:
                    im.putpixel((x, y), pal[i] + (255,))
        return im

    def orphans(self):
        """Opaque pixels with no neighbour of the same index, diagonals included: stray noise
        (a diagonal 1px line still counts as connected)."""
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.px[y][x]
                and all(self.get(x + i, y + j) != self.px[y][x] for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j)]

    def colours(self):
        return {i for row in self.px for i in row if i}


def write_species(out, fronts, back, icons, overworld, pal, shiny, ow_pal=None, ow_shiny=None, body='blob'):
    """Write anim_front (2 frames), back, icon (2 frames, nearest shared icon palette), overworld
    (6 frames: S, S-walk, N, N-walk, W, W-walk), footprint and the four palettes. pal and shiny
    are 16-entry lists (entry 0 is the transparent colour); the shiny palette keeps the indices."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ow_pal, ow_shiny = ow_pal or pal, ow_shiny or shiny

    def pad(p):
        return [TRANSPARENT_RGB] + list(p[1:]) + [(0, 0, 0)] * (16 - len(p))

    pal, shiny, ow_pal, ow_shiny = pad(pal), pad(shiny), pad(ow_pal), pad(ow_shiny)
    to_indexed([c.image(pal) for c in fronts], pal).save(out / 'anim_front.png', bits=4)
    to_indexed([back.image(pal)], pal).save(out / 'back.png', bits=4)
    icon_imgs = [c.image(pal) for c in icons]
    icon_index, icon_pal = best_icon(icon_imgs)
    to_indexed(icon_imgs, icon_pal).save(out / 'icon.png', bits=4)
    to_indexed([c.image(ow_pal) for c in overworld], ow_pal, layout='horizontal').save(out / 'overworld.png', bits=4)
    footprint(body).save(out / 'footprint.png', bits=1)
    write_jasc(out / 'normal.pal', pal)
    write_jasc(out / 'shiny.pal', shiny)
    write_jasc(out / 'overworld_normal.pal', ow_pal)
    write_jasc(out / 'overworld_shiny.pal', ow_shiny)
    return icon_index


def preview(path, rows, scale=4):
    """Contact sheet: rows of (canvas, palette) pairs, each drawn at `scale` on the transparent green."""
    width = max(sum(c.w * scale + 8 for c, _ in row) for row in rows) + 8
    height = sum(max(c.h for c, _ in row) * scale + 8 for row in rows) + 8
    sheet = Image.new('RGBA', (width, height), TRANSPARENT_RGB + (255,))
    y = 8
    for row in rows:
        x = 8
        for c, pal in row:
            sheet.alpha_composite(c.image(pal).resize((c.w * scale, c.h * scale), Image.NEAREST), (x, y))
            x += c.w * scale + 8
        y += max(c.h for c, _ in row) * scale + 8
    sheet.save(path)
