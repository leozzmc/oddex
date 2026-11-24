"""Amphorin: a young hydra in a wine jar. After the Lernaean Hydra of Greek myth, the many-headed
water serpent of the swamp of Lerna that Heracles killed: a monster, never worshipped (Lerna's own
cults were of Demeter and Dionysus), and foreign mythology the user has approved (like Enigmen's
Sphinx). League segment, the first stage of Drake's dragon line: replaces Bagon (wild in the inner
Meteor Falls) and Shelgon (docs/research/mask-designs.md, "Amphorin 和 Lernagon 的 Brief"). No
Heracles, and nothing from any modern work's hydra. A two-handled amphora, terracotta with a black
band, standing in swamp water; one small serpent's head looks out of its mouth, wearing a Greek
tragic mask (the frowning one, never the comic one), a coil of tail hanging over a handle, a few
reeds beside it. Silhouette at 64px: a jar with two handles and one masked head on top.
Dragon/grass."""
import math

NORMAL = {'clay': (0.80, 0.44, 0.24), 'claydark': (0.48, 0.22, 0.12), 'glaze': (0.10, 0.08, 0.08),
          'mask': (0.96, 0.94, 0.86), 'lacquer': (0.30, 0.24, 0.20), 'hollow': (0.03, 0.02, 0.02),
          'scale': (0.26, 0.52, 0.32), 'scaledark': (0.12, 0.30, 0.20), 'belly': (0.78, 0.80, 0.48),
          'reed': (0.56, 0.70, 0.28), 'water': (0.30, 0.44, 0.40)}
# Shiny: a black-glazed jar with a red band, a white serpent.
SHINY = {**NORMAL, 'clay': (0.16, 0.14, 0.16), 'claydark': (0.08, 0.07, 0.09), 'glaze': (0.78, 0.26, 0.16),
         'scale': (0.90, 0.90, 0.84), 'scaledark': (0.60, 0.62, 0.60)}


# Hand-placed pixels (make_art.apply_pixels): the tragic mask. Brows drawn up in the middle and down at the
# ends, two hollow eyes, an open mouth with the corners down. It grieves; it does not smile.
_FACE = [
    ((27, 3), ['...k.k...',
               '..k...k..',
               '.k.....k.',
               'fkkfffkkd',
               'fkkfffkkd']),
    ((27, 10), ['...kkk...',
                '..kkkkk..',
                '..kk.kk..']),
]
_ICON = [((12, 5), ['K.K']), ((12, 7), ['.K.'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'f': (250, 248, 238), 'd': (176, 174, 167), 'K': (65, 65, 65)},
          'front': {'box': (12, 0, 51, 56), 'patches': _FACE},
          'front2': {'box': (11, 0, 53, 56), 'patches': _FACE},
          'icon': {'box': (6, 2, 25, 30), 'patches': _ICON},
          'icon2': {'box': (6, 1, 25, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def tragic_mask(k, at, scale, mask, lacquer, hollow, tilt=0.0):
    """A Greek tragic mask at `at`, facing -Y: hollow eyes under brows drawn up in the middle, and an
    open mouth with the corners down. (Eyes and mouth are redrawn by hand in each model's PIXELS.)"""
    before = k.snapshot()
    shell = k.mask_shell(mask, lacquer, width=0.5, depth=0.36, height=0.62)
    for x in (-0.2, 0.2):
        k.hole(shell, x, 0.12, (0.1, 0.07), backing=hollow)
    k.bump(shell, 0, -0.05, (0.05, 0.05, 0.1), mask, lift=0.02)
    k.hole(shell, 0, -0.34, (0.15, 0.09), backing=hollow)
    k.transform(k.since(before), offset=at, scale=scale, rot_x=tilt)
    return shell


def build(k, c):
    clay = k.toon('clay', c['clay'], steps=(0.55, 0.8, 1.0))
    claydark = k.toon('claydark', c['claydark'], two_tone=True)
    glaze = k.flat('glaze', c['glaze'])
    mask = k.toon('mask', c['mask'], two_tone=True)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    scale = k.toon('scale', c['scale'], two_tone=True)
    scaledark = k.flat('scaledark', c['scaledark'])
    belly = k.toon('belly', c['belly'], two_tone=True)
    reed = k.toon('reed', c['reed'], two_tone=True)
    water = k.flat('water', c['water'])
    k.set_light((-0.7, -0.6, 0.2))

    # The swamp water it stands in, and a few reeds.
    k.ellipsoid((0, 0.1, -1.45), (1.25, 1.0, 0.12), water)
    for x, y, h, lean in ((-1.0, 0.2, 1.1, -0.15), (-0.82, 0.35, 0.8, 0.05), (0.95, 0.3, 0.95, 0.12)):
        k.spike((x, y, -1.45), (x + lean, y, -1.45 + h), 0.05, reed)

    # The amphora: a full belly on a small foot, a black band, a neck with a rolled lip, two handles.
    k.ellipsoid((0, 0, -0.5), (0.78, 0.74, 0.86), clay)
    k.cylinder((0, 0, -1.36), 0.3, 0.16, claydark)
    k.torus((0, 0, -0.35), 0.775, 0.1, glaze)
    k.torus((0, 0, -0.8), 0.68, 0.035, glaze)
    k.cylinder((0, 0, 0.4), 0.3, 0.42, clay)
    k.torus((0, 0, 0.62), 0.34, 0.08, claydark)
    for side in (-1, 1):
        k.torus((side * 0.52, 0, 0.2), 0.3, 0.07, claydark, rot=(math.radians(90), 0, 0))

    # One small serpent looking out of the mouth, in a tragic mask; a coil of its tail over a handle.
    for i in range(7):
        t = i / 6
        k.ellipsoid((0.22 * math.sin(t * 4.2), -0.1 * t, 0.6 + 0.78 * t), (0.22 - 0.03 * t,) * 3, scale if i % 2 else scaledark, segments=16)
    k.ellipsoid((-0.12, -0.1, 1.5), (0.36, 0.33, 0.33), scale)
    tragic_mask(k, (-0.12, -0.36, 1.5), 0.72, mask, lacquer, hollow)
    for i in range(6):
        t = i / 5
        a = math.radians(200 - 150 * t)
        k.ellipsoid((0.62 + 0.4 * math.cos(a), -0.3, 0.55 + 0.34 * math.sin(a) - 0.6 * t), (0.13 - 0.06 * t,) * 3, scale if i % 2 else scaledark, segments=12)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -10, 'front_el': 6, 'side_az': -70}
