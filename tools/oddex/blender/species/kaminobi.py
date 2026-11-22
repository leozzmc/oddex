"""Kaminobi: the abandoned doll whose hair never stopped growing. Mossdeep segment, replaces Banette
(docs/research/mask-designs.md, "Kamikko → Kaminobi 的 Brief", option A); Kamikko's evolution at
Lv37. The whole doll now, in a red kimono with a gold sash, its own arms and legs hanging limp;
the hair has grown to the ground and parted into two great bundles that arch out to the sides and
stand on the earth like a spider's legs, lifting the doll off the ground. The same porcelain
face, the crack grown from brow to jaw, one eye fallen out, the mouth pulled askew by the crack.
Silhouette at 64px: two black arches of hair with the small red doll hung between them.
Ghost/fairy (stage 2 of 2)."""
import math
from pathlib import Path

_path = Path(__file__).with_name('kamikko.py')
_base = {'__file__': str(_path)}
exec(compile(_path.read_text(), str(_path), 'exec'), _base)

NORMAL = {**_base['NORMAL'], 'kimono': (0.80, 0.12, 0.14), 'kimonodark': (0.50, 0.05, 0.08), 'obi': (0.92, 0.74, 0.24)}
# Shiny: white hair and a violet kimono.
SHINY = {**NORMAL, 'hair': (0.86, 0.86, 0.92), 'kimono': (0.52, 0.26, 0.74), 'kimonodark': (0.30, 0.12, 0.46),
         'lip': (0.40, 0.20, 0.60)}


# Hand-placed pixels (make_art.apply_pixels): the whole 12x12 face. The good eye is a small almond
# with a glint; the other has fallen out and left a round black socket, bigger than the eye; one
# thin crack runs from the brow through the socket down to the corner of the flat mouth (no smile).
_K = {'k': (28, 18, 22), 'w': (255, 255, 255), 'e': (251, 248, 243), 'd': (238, 235, 230), 'b': (209, 206, 202),
      'x': (111, 89, 97), 'h': (75, 69, 85), 'c': (251, 218, 215), 'r': (231, 97, 104)}   # x: the crack, h: hair
_FACE = ['.h.dddddx...',
         '..edddddxb..',
         '.eedddddkkb.',
         'eekkkddkkkk.',
         'ekwkkddkkkkb',
         'eeddddddkkbb',
         'eeddddddxbbb',
         'ccdddddxbb..',
         'ddddddxbbbb.',
         'dddrrrbbbb..',
         'dddddbbbbb..',
         '.dbbbbbb....']
_ICON = [((15, 10), ['WWW', 'WWW', 'KWK', 'WWW'])]
PIXELS = {'keys': {**_K, 'K': (65, 65, 65), 'W': (255, 255, 255)},
          'front': {'box': (2, 5, 62, 56), 'patches': [((28, 12), _FACE)]},
          # The second frame is squashed: the face is one row shorter and sits two rows lower.
          'front2': {'box': (1, 7, 63, 56), 'patches': [((28, 14), _FACE[:10] + _FACE[11:])]},
          'icon': {'box': (2, 7, 30, 30), 'patches': _ICON},
          'icon2': {'box': (2, 6, 30, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def strand(k, pts, r0, r1, mat, n=12):
    """A tapering lock of hair along a quadratic curve through three points."""
    a, b, c = (k.Vector(p) for p in pts)
    prev = a
    for i in range(1, n + 1):
        t = i / n
        p = a * (1 - t) ** 2 + b * 2 * t * (1 - t) + c * t ** 2
        r = r0 + (r1 - r0) * t
        k.rod(prev, p, r, mat)
        k.ellipsoid(p, (r, r, r), mat, segments=12)
        prev = p


def build(k, c):
    mats = _base['materials'](k, c)
    hair = mats[1]
    kimono = k.toon('kimono', c['kimono'], two_tone=True)
    kimonodark = k.flat('kimonodark', c['kimonodark'])
    obi = k.toon('obi', c['obi'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.2))
    before = k.snapshot()
    _base['doll_face'](k, c, mats, missing_eye=True, crack=1.5)
    k.transform(k.since(before), offset=(0, 0, 0.55), scale=0.62)
    # The doll's body hanging under the head: kimono, sash, limp sleeves, feet off the ground.
    k.cone((0, 0.05, -0.45), 0.22, 0.95, kimono, radius2=0.4, rot=(math.pi, 0, 0), segments=24)
    k.cylinder((0, 0.05, -0.32), 0.29, 0.16, obi, segments=24)
    k.rod((0.0, -0.22, 0.02), (0.06, -0.3, -0.24), 0.03, kimonodark)   # the collar's fold
    for side in (-1, 1):
        k.ellipsoid((side * 0.34, 0.02, -0.3), (0.12, 0.14, 0.34), kimono, rot=(0, math.radians(side * 14), 0))
        k.ellipsoid((side * 0.42, 0.0, -0.66), (0.05, 0.05, 0.06), mats[0])   # a hand
        k.ellipsoid((side * 0.12, -0.04, -1.0), (0.07, 0.1, 0.06), mats[0])   # a foot
    # The hair: two bundles of three locks each, arching out and down to stand on the ground.
    ground = -1.45
    for side in (-1, 1):
        for j, (dx, dy, r) in enumerate(((1.25, -0.25, 0.15), (1.6, 0.1, 0.17), (1.2, 0.5, 0.15))):
            strand(k, [(side * 0.4, 0.1, 0.7), (side * (dx + 0.1), dy, 1.25 - 0.15 * j), (side * dx, dy, ground)], r, 0.04, hair)
    for x in (-0.2, 0, 0.2):   # the fall down its back
        k.ellipsoid((x, 0.42, -0.1), (0.14, 0.1, 0.85), hair)
    return {'kind': 'beast', 'size': 0.92, 'front_az': -14, 'front_el': 6, 'side_az': -70}
