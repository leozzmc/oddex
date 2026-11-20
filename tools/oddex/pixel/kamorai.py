#!/usr/bin/env python3
"""Kamorai, the popeye-goldfish o-tobide mask (design A of its brief, docs/research/mask-designs.md),
laid out directly in pixels with tools/oddex/pixelkit.py: no rendering, no shrinking.

Usage (repository root): python3 tools/oddex/pixel/kamorai.py [--preview sheet.png] [--dry-run]

Writes every sprite file and palette into graphics/pokemon/oddex/kamorai/. Front (2 frames),
back, icon (2 frames) and overworld (6 frames) all come from the same shapes and the same
11-colour palette; the shiny palette swaps colours on the same indices.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from pixelkit import Canvas, edge, ellipse, line, mirror, polygon, preview, write_species  # noqa: E402
from species_data import GAME  # noqa: E402

OUT, FS, FB, FL, G, GL, MD, GUM, T, B, BS = range(1, 12)
PAL = [None,
       (40, 20, 24),     # OUT  outline and pupils
       (152, 40, 32),    # FS   face shadow (also the back of the mask)
       (208, 64, 40),    # FB   face (vermilion)
       (240, 120, 80),   # FL   face light
       (224, 168, 32),   # G    gold eyes
       (255, 232, 120),  # GL   gold light, lightning fin
       (80, 16, 24),     # MD   inside the mouth
       (184, 48, 80),    # GUM  gums, the cord on the back
       (248, 240, 208),  # T    teeth
       (64, 136, 224),   # B    fins
       (32, 72, 160)]    # BS   fin roots
# The bolt fin on the crown, at least 3px wide everywhere so it never breaks into single pixels.
BOLT = [(27, 21), (31, 11), (27, 11), (33, 0), (42, 0), (37, 7), (42, 7), (31, 21)]
AXIS = 63   # mirror(mask, 63) flips about x = 31.5, the face's centre line
SMALL_BOLT = [(13, 10), (16, 5), (13, 5), (16, 0), (21, 0), (19, 3), (21, 3), (16, 10)]   # icon/overworld
SHINY = list(PAL)
SHINY[FS], SHINY[FB], SHINY[FL] = (40, 40, 72), (64, 72, 128), (112, 128, 184)   # blue-black face
SHINY[G], SHINY[GL] = (176, 184, 200), (244, 248, 255)                          # silver eyes
SHINY[B], SHINY[BS] = (224, 168, 40), (152, 96, 24)                            # gold fins


def two_tone(root, near, far, d=7):
    """Fin shading: the darker colour within d pixels of the fin's root."""
    return lambda x, y: near if (x - root[0]) ** 2 + (y - root[1]) ** 2 < d * d else far


def mouth_parts(c, mask, top_teeth, low_teeth, fang_len):
    """A roaring mouth in mask: dark inside, gums along the top and bottom, square teeth, two fangs."""
    c.part(mask, MD, OUT)
    inner = mask - edge(mask)
    cols = {}
    for x, y in inner:
        cols.setdefault(x, []).append(y)
    top = min(y for _, y in inner)
    gum = {(x, y) for x, y in inner if y < top + 2}
    gum |= {(x, y) for x, ys in cols.items() for y in ys if y > max(ys) - 2}
    c.put(gum, GUM)
    for x0 in top_teeth:
        c.put({(x, y) for x in range(x0, x0 + 3) for y in range(top + 2, top + 5)} & inner, T)
    for x0 in low_teeth:
        c.put({(x, y) for x in range(x0, x0 + 3) if x in cols for y in range(max(cols[x]) - 3, max(cols[x]) - 1)} & inner, T)
    for x0 in (min(cols) + 2, max(cols) - 3):
        fang = {(x, y) for x in (x0, x0 + 1) for y in range(top + 2, top + 2 + fang_len)} | {(x0 + (x0 < 32), top + 2 + fang_len)}
        c.put(fang & inner, T)


def eye(c, cx, cy, r, look=(0.5, 1.5)):
    c.part(ellipse(cx, cy, r, r), G, OUT)
    c.put(ellipse(cx - r * 0.35, cy - r * 0.4, r * 0.38, r * 0.3), GL)
    c.put(ellipse(cx + look[0], cy + look[1], 1.6, 1.6), OUT)


def front(frame):
    c = Canvas(64, 64)
    dy = -1 if frame else 0   # the eyes bob and the mouth opens wider on the second frame
    # Forked tail behind the lower right, and a pectoral fin at the lower left.
    # Twin goldfish tail: two broad lobes fanning out from a narrow root, with a notch between.
    flick = -2 if frame else 0
    upper = polygon([(40, 38), (55, 24 + flick), (62, 27 + flick), (61, 38 + flick), (47, 44)])
    lower = polygon([(41, 47), (60, 47), (62, 55), (55, 62), (39, 52)])
    for lobe, root, tips in ((upper, (44, 40), [(57, 28 + flick), (59, 35 + flick)]), (lower, (44, 50), [(58, 51), (56, 58)])):
        c.part(lobe, two_tone(root, BS, B), OUT)
        for tip in tips:   # fin rays
            c.put(line(*root, *tip) & (lobe - edge(lobe)), BS)
    c.part(polygon([(18, 43), (7, 44), (5, 51), (10, 54), (19, 49)]), two_tone((18, 46), BS, B, 5), OUT)
    # A chunky lightning-bolt dorsal fin rising from the crown.
    c.part(polygon(BOLT), lambda x, y: G if x > 34 else GL, OUT)
    # The face: light from the upper left, a shadow crescent on the lower right, one highlight.
    cx, cy, rx, ry = 31.5, 33, 17.5, 19.5
    face = ellipse(cx, cy, rx, ry)
    light = ellipse(cx - 7, cy - 8, 5, 4)

    def shade(x, y):
        if ((x + 0.5 - cx + 3) / rx) ** 2 + ((y + 0.5 - cy + 3) / ry) ** 2 > 1:
            return FS
        return FL if (x, y) in light else FB
    c.part(face, shade, OUT)
    # Heavy brows knotted over the eyes, and a flared nose.
    brow = polygon([(15, 16), (29, 21), (28, 26), (14, 21)])
    for m in (brow, mirror(brow, AXIS)):
        c.part(m, FS, OUT)
    c.put(ellipse(31.5, 35.5, 3.5, 2.5), FS)
    c.put({(28, 36), (29, 36), (34, 36), (35, 36)}, OUT)
    # The roaring mouth, down to the chin.
    mouth = {p for p in ellipse(31.5, 44.5 - dy * 0.5, 13, 7 - dy) if p[1] >= 38}
    mouth_parts(c, mouth, top_teeth=range(23, 40, 4), low_teeth=range(24, 39, 4), fang_len=4)
    # Popping gold eyes, out past the sides of the face, staring down at the player.
    left = 12.5
    eye(c, left, 27.5 + dy, 7)
    eye(c, 63 - left, 27.5 + dy, 7, look=(-0.5, 1.5))
    return c


def back():
    c = Canvas(64, 64)
    # The backs of the popping eyes stick out on either side.
    for x in (11.5, 51.5):
        c.part(ellipse(x, 30.5, 7, 7), G, OUT)
        c.put(ellipse(x - 2, 28, 2.5, 2), GL)
    c.part(polygon([(x, y - 2) for x, y in BOLT]), lambda x, y: G if x > 34 else GL, OUT)
    # The back of the mask: shadow red with a lighter rim on the upper left.
    cx, cy, rx, ry = 31.5, 35, 18.5, 20
    shell = ellipse(cx, cy, rx, ry)

    def rim(x, y):
        return FB if ((x + 0.5 - cx - 2.5) / rx) ** 2 + ((y + 0.5 - cy - 2.5) / ry) ** 2 > 1 else FS
    c.part(shell, rim, OUT)
    # The red cord tied in a bow, so it reads as a mask.
    cord = {(x, y) for x in range(14, 50) for y in (30, 31)}
    c.put(cord, GUM)
    c.put({(x, y) for x in range(14, 50) for y in (29, 32)} - polygon([(24, 24), (40, 24), (40, 37), (24, 37)]), OUT)
    loop = ellipse(26.5, 30.5, 5, 4)
    for m in (loop, mirror(loop, AXIS)):
        c.part(m, GUM, OUT)
        c.put(ellipse(sum(x for x, _ in m) / len(m) + 0.5, 30.5, 1.5, 1.2), OUT)
    tail = polygon([(30, 32), (26, 43), (29, 44), (32, 34)])
    for m in (tail, mirror(tail, AXIS)):
        c.part(m, GUM, OUT)
    c.part({(x, y) for x in range(29, 35) for y in range(28, 34)}, GUM, OUT)
    # The big forked tail spread out toward the player at the bottom.
    lobe = polygon([(31, 46), (14, 52), (9, 60), (18, 64), (32, 55)])
    for m in (lobe, mirror(lobe, AXIS)):
        c.part(m, two_tone((31, 50), BS, B), OUT)
    return c


def icon(frame):
    c = Canvas(32, 32)
    c.part(polygon([(21, 21), (30, 17), (31, 23), (23, 26)]), two_tone((22, 23), BS, B, 4), OUT)
    c.part(polygon(SMALL_BOLT), GL, OUT)
    c.part(ellipse(15.5, 17.5, 9, 10), lambda x, y: FS if x > 19 and y > 20 else FB, OUT)
    mouth = {p for p in ellipse(15.5, 22.5, 6.5, 3.5 if frame == 0 else 2.5) if p[1] >= 20}
    c.part(mouth, MD, OUT)
    inner = mouth - edge(mouth)
    if inner:
        top = min(y for _, y in inner)
        c.put({(x, top) for x, y in inner if x % 2 == 1}, T)
    for x in (5.5, 25.5):
        c.part(ellipse(x, 13.5, 4, 4), G, OUT)
        c.put({(int(x), 14)}, OUT)
    return c


def ow_front(bob):
    c = Canvas(32, 32)
    c.part(polygon([(21, 20), (29, 15), (30, 22), (23, 25)]), B, OUT)
    c.part(polygon([(x, y + 2) for x, y in SMALL_BOLT]), GL, OUT)
    c.part(ellipse(15.5, 19.5, 8, 9), lambda x, y: FS if x > 19 and y > 22 else FB, OUT)
    mouth = {p for p in ellipse(15.5, 24, 5.5, 3) if p[1] >= 22}
    c.part(mouth, MD, OUT)
    c.put({(x, y) for x, y in mouth - edge(mouth) if y == 23 and x % 2}, T)
    for x in (6.5, 24.5):
        c.part(ellipse(x, 16.5, 3.5, 3.5), G, OUT)
        c.put({(int(x), 17)}, OUT)
    return c.shifted(0, -bob)


def ow_back(bob):
    c = Canvas(32, 32)
    for x in (6.5, 24.5):
        c.part(ellipse(x, 17.5, 3.5, 3.5), G, OUT)
    c.part(polygon([(x, y + 2) for x, y in SMALL_BOLT]), GL, OUT)
    c.part(ellipse(15.5, 19.5, 8, 9), FS, OUT)
    c.put({(x, 17) for x in range(9, 23)}, GUM)
    c.part({(x, y) for x in range(14, 18) for y in range(16, 19)}, GUM, OUT)
    lobe = polygon([(15, 25), (6, 31), (11, 32), (16, 28)])
    for m in (lobe, mirror(lobe, 31)):
        c.part(m, B, OUT)
    return c.shifted(0, -bob)


def ow_side(bob):
    """Facing west (the game mirrors it for east)."""
    c = Canvas(32, 32)
    c.part(polygon([(20, 17), (30, 11), (29, 18)]), B, OUT)
    c.part(polygon([(20, 21), (30, 27), (28, 20)]), B, OUT)
    c.part(polygon([(x + 1, y + 2) for x, y in SMALL_BOLT]), GL, OUT)
    c.part(ellipse(16.5, 19.5, 7, 9), lambda x, y: FS if x > 19 else FB, OUT)
    mouth = polygon([(9, 21), (16, 21), (16, 26), (11, 27)])
    c.part(mouth, MD, OUT)
    c.put({(x, 22) for x in range(11, 16) if x % 2}, T)
    c.part(ellipse(8.5, 16.5, 3.5, 3.5), G, OUT)
    c.put({(7, 17)}, OUT)
    return c.shifted(0, -bob)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--preview', help='write a 4x contact sheet here')
    ap.add_argument('--dry-run', action='store_true', help='only check and preview, write no sprite files')
    args = ap.parse_args()

    fronts, bk = [front(0), front(1)], back()
    icons = [icon(0), icon(1)]
    ow = [ow_front(0), ow_front(1), ow_back(0), ow_back(1), ow_side(0), ow_side(1)]
    for name, c in [('front', fronts[0]), ('front2', fronts[1]), ('back', bk)]:
        print(f'{name}: {len(c.colours())} colours, {len(c.orphans())} stray pixels {c.orphans()[:6]}')
    if args.preview:
        preview(args.preview, [[(fronts[0], PAL), (fronts[1], PAL), (bk, PAL)],
                               [(fronts[0], SHINY), (fronts[1], SHINY), (bk, SHINY)],
                               [(i, PAL) for i in icons] + [(o, PAL) for o in ow]])
    if not args.dry_run:
        idx = write_species(GAME / 'graphics/pokemon/oddex/kamorai', fronts, bk, icons, ow, PAL, SHINY)
        print(f'wrote graphics/pokemon/oddex/kamorai (icon palette {idx})')


if __name__ == '__main__':
    main()
