"""Onamazu: the giant catfish of the namazu-e prints, whose turning over shakes the land and
which carries a town on its back (folklore, not a deity; no keystone god, no keystone).
Sootopolis segment, Namazura's evolution at Lv30, replaces Whiscash on Juan's team
(docs/research/mask-designs.md, "Onamazu 的 Brief", option A). It has outgrown the gourd, whose
broken half still hangs from its tail, and the white okina mask has split and slid up onto its
forehead: only a brow and one eye hole are left of it, and the catfish's own face shows, a wide
closed mouth with the corners down and two small far-apart eyes. A row of crooked tiled roofs
rides on its back. Silhouette at 64px: a broad flat head with the jagged roof line above it and
two long whiskers flung out to the sides. Water/ground."""
import math

NORMAL = {'body': (0.38, 0.40, 0.40), 'belly': (0.86, 0.80, 0.64), 'mouth': (0.05, 0.04, 0.05),
          'barbel': (0.15, 0.14, 0.15), 'eye': (0.95, 0.76, 0.22), 'mask': (0.96, 0.94, 0.86),
          'tuft': (0.99, 0.99, 0.97), 'hollow': (0.03, 0.03, 0.03), 'roof': (0.26, 0.36, 0.56),
          'wall': (0.90, 0.84, 0.66), 'gourd': (0.82, 0.62, 0.28), 'cord': (0.75, 0.15, 0.12)}
# Shiny: the golden catfish, red roofs on its back.
SHINY = {**NORMAL, 'body': (0.92, 0.68, 0.16), 'belly': (1.0, 0.92, 0.62), 'barbel': (0.52, 0.30, 0.06),
         'eye': (0.20, 0.62, 0.66), 'roof': (0.74, 0.16, 0.12), 'gourd': (0.30, 0.62, 0.62), 'cord': (0.20, 0.30, 0.75)}


def house(k, at, size, lean, wall, roof):
    """A little house: a box with a pyramid roof, leaning lean degrees to the side."""
    x, y, z = at
    r = math.radians(lean)
    k.cylinder((x, y, z + size * 0.4), size * 0.62, size * 0.8, wall, rot=(0, r, math.pi / 4), segments=4)
    k.cone((x + math.sin(r) * size * 0.75, y, z + size * 0.4 + math.cos(r) * size * 0.75), size * 0.95, size * 0.75, roof,
           rot=(0, r, math.pi / 4), segments=4)

# Hand-placed pixels (make_art.apply_pixels): no smile (docs/ART_GUIDELINES.md). The catfish's own eyes, small and far apart under a heavy
# lid; its mouth one long closed line with the corners down; and what is left of the okina mask on its forehead, a
# broken shard with a brow ridge and one drooping eye hole.
_FACE = [
    ((18, 39), ['ckkkkk',
                'ckkkkk',
                'cddkkd',
                'ckdddk',
                'cckkkn',
                '...w..']),
    ((39, 39), ['mkkkkkm',
                'mkkkkkm',
                'mdkkddm',
                'mkdddkm',
                'mmkkkmm']),
    ((19, 44), ['.............nnnnnn......',
                '..kkkkkkkkkkkkkkkkkkkkk..',
                'kk...eeeeeee...........kk']),
    ((25, 26), ['.......kk.kk..',
                '.....kkffkffk.',
                'nnnnkffffffffk',
                'nnnkfeeeffffek',
                'nnkkkffffffffk',
                'nnnnkffffffffk',
                'nnnkfffffffffk',
                'nnkfffffffffek',
                'nnnkkffffeeekk',
                'nnnnnkkkkkkknn']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((18, 40), ['ckkkkk',
                'ckkkkk',
                'cddkkd',
                'ckdddk',
                'cckkkn',
                '...w..']),
    ((40, 40), ['mkkkkkm',
                'mkkkkkm',
                'mdkkddm',
                'mkdddkm',
                'mmkkkmm']),
    ((19, 44), ['.............nnnnnn......',
                '..kkkkkkkkkkkkkkkkkkkkk..',
                'kk...eeeeeee...........kk']),
    ((25, 27), ['.......kk.kk..',
                '.....kkffkffk.',
                'nnnnkffffffffk',
                'nnnkfeeeffffek',
                'nnkkkffffffffk',
                'nnnnkffffffffk',
                'nnnkfffffffffk',
                'nnkfffffffffek',
                'nnnkkffffeeekk',
                'nnnnnkkkkkkknn']),
]
_ICON = [
    ((10, 22), ['KYK......KYK']),
]
PIXELS = {'keys': {'k': (28, 18, 22),
                   'd': (249, 226, 129),
                   'c': (166, 170, 170),
                   'n': (148, 152, 152),
                   'm': (121, 124, 124),
                   'w': (73, 71, 73),
                   'e': (238, 231, 209),
                   'f': (250, 248, 238),
                   'K': (65, 65, 65),
                   'Y': (246, 246, 41)},
          'front': {'box': (1, 11, 63, 56), 'patches': _FACE},
          'front2': {'box': (0, 12, 64, 56), 'patches': _FACE2},
          'icon': {'box': (2, 9, 30, 30), 'patches': _ICON},
          'icon2': {'box': (2, 8, 30, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    body = k.toon('body', c['body'], steps=(0.5, 0.78, 1.0))
    belly = k.toon('belly', c['belly'], two_tone=True)
    mouth = k.flat('mouth', c['mouth'])
    barbel = k.toon('barbel', c['barbel'], two_tone=True)
    eye = k.flat('eye', c['eye'])
    mask = k.toon('mask', c['mask'], two_tone=True)
    tuft = k.toon('tuft', c['tuft'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    roof = k.toon('roof', c['roof'], two_tone=True)
    wall = k.toon('wall', c['wall'], two_tone=True)
    gourd = k.toon('gourd', c['gourd'], glint=0.3, two_tone=True)
    cord = k.flat('cord', c['cord'])
    k.set_light((-0.75, -0.6, 0.1))

    # The head: broad and flat, a pale lower jaw under a mud-grey skull.
    head_c, head_r = (0, 0, 0), (1.1, 0.75, 0.6)
    k.ellipsoid(head_c, head_r, body)
    k.ellipsoid((0, -0.06, -0.3), (1.0, 0.72, 0.4), belly)

    def at(x, z, lift=0.0):
        return k.head_point(head_c, head_r, x, z, lift)

    # The catfish's own mouth: a wide closed line, the corners lower than the middle.
    pts = [(-0.8, -0.3), (-0.55, -0.16), (-0.2, -0.1), (0.2, -0.1), (0.55, -0.16), (0.8, -0.3)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        k.rod(at(x0, z0, 0.02), at(x1, z1, 0.02), 0.045, mouth)
    # Two small eyes far apart (redrawn by hand in PIXELS).
    for x in (-0.62, 0.62):
        k.ellipsoid(at(x, 0.08, 0.01), (0.15, 0.05, 0.13), eye)
        k.ellipsoid(at(x, 0.08, 0.04), (0.06, 0.03, 0.08), mouth)
    # What is left of the okina mask, slid up onto the forehead: one side with its tufted brow
    # and an eye hole, the other side broken away.
    plate = k.ellipsoid((0.08, -0.4, 0.6), (0.46, 0.09, 0.27), mask, rot=(math.radians(-48), 0, math.radians(-10)))
    k.cut(plate, k.cylinder((-0.42, -0.4, 0.6), 0.3, 1.0, hollow, rot=(math.radians(90), 0, 0), segments=5))
    k.ellipsoid((0.22, -0.52, 0.55), (0.13, 0.04, 0.035), hollow, rot=(math.radians(-48), 0, 0))
    for dx, dz, r in ((0.06, 0.12, 0.1), (0.24, 0.16, 0.12), (0.42, 0.1, 0.1)):
        k.ellipsoid((dx, -0.42 + dz * 0.9, 0.62 + dz), (r, r * 0.7, r * 0.7), tuft)
    k.rod((0.5, -0.36, 0.56), (0.95, 0.1, 0.3), 0.025, cord)   # the cord it used to be tied on with
    # Long whiskers flung out to both sides, and two short ones under the chin.
    for side in (-1, 1):
        root = at(side * 0.5, -0.12, 0.03)
        pts3 = [root, root + k.Vector((side * 0.55, -0.1, -0.02)), root + k.Vector((side * 1.0, -0.05, 0.14)),
                root + k.Vector((side * 1.22, 0.0, 0.52)), root + k.Vector((side * 1.1, 0.05, 0.9))]
        for a, b, r in zip(pts3, pts3[1:], (0.1, 0.085, 0.07, 0.05)):
            k.rod(a, b, r, barbel)
        chin = at(side * 0.25, -0.4, 0.02)
        k.rod(chin, chin + k.Vector((side * 0.12, -0.05, -0.32)), 0.04, barbel)

    # The body behind: a high back, side fins, and the tail swung round to one side.
    k.ellipsoid((0, 1.0, 0.2), (0.95, 1.15, 0.72), body)
    k.ellipsoid((0, 1.0, -0.3), (0.8, 1.05, 0.3), belly)
    for side in (-1, 1):
        k.ellipsoid((side * 1.0, 0.55, -0.35), (0.42, 0.2, 0.08), body, rot=(0, math.radians(side * 25), 0))
    for i in range(5):
        t = i / 4
        k.ellipsoid((0.55 + 0.8 * t, 1.9 - 0.5 * t, -0.2 + 0.1 * t), (0.4 - 0.2 * t,) * 3, body, segments=16)
    k.ellipsoid((1.55, 1.25, -0.08), (0.34, 0.12, 0.3), body, rot=(0, math.radians(-15), math.radians(35)))   # tail fin
    # The broken gourd still tied to the tail.
    k.rod((1.4, 1.35, -0.1), (1.5, 1.1, -0.42), 0.03, cord)
    half = k.ellipsoid((1.52, 1.05, -0.6), (0.22, 0.22, 0.24), gourd)
    k.cut(half, k.cylinder((1.52, 1.05, -0.4), 0.32, 0.3, hollow, segments=6))

    # The town on its back: crooked little houses with tiled roofs.
    for x, y, size, lean in ((-0.55, 0.7, 0.44, -14), (0.0, 0.62, 0.52, 6), (0.55, 0.72, 0.42, 16)):
        z = 0.2 + 0.72 * math.sqrt(max(0.05, 1 - (x / 0.95) ** 2)) - 0.12
        house(k, (x, y, z), size, lean, wall, roof)
    return {'kind': 'beast', 'size': 0.94, 'front_az': -10, 'front_el': 14, 'side_az': -70}
