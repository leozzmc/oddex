"""Magaryu: the jade magatama that dreamed of becoming a dragon, become one: a whole string of
comma-shaped jewels joined head to tail in an S (the bead's shape only, not the regalia; a dragon
in shape only, not a dragon god). Sootopolis segment, Magatide's evolution at Lv32, replaces
Kingdra, Juan's ace, and Seadra (docs/research/mask-designs.md, "Magaryu 的 Brief", option A).
The largest bead is the head: Magatide's round staring eyes and pursed usobuki lips, now blowing a
jet of water, and the two horn buds grown into branched gold antlers. A ring of tide under it.
Silhouette at 64px: a chain of round beads, large to small, in an S, antlers on the first.
Water/dragon."""
import math
from pathlib import Path

_path = Path(__file__).with_name('magatide.py')
_base = {'__file__': str(_path)}
exec(compile(_path.read_text(), str(_path), 'exec'), _base)

NORMAL = {**_base['NORMAL'], 'horn': (0.96, 0.78, 0.26)}
# Shiny: agate-red beads with silver antlers.
SHINY = {**_base['SHINY'], 'horn': (0.80, 0.82, 0.90), 'water': (0.30, 0.70, 0.72)}

# The string of beads: (centre, radius), the head first.
BEADS = [((-0.4, -0.3, -0.2), 0.64), ((0.32, 0.15, 0.0), 0.46), ((0.8, 0.45, 0.45), 0.4), ((0.68, 0.7, 0.98), 0.34),
         ((0.2, 0.9, 1.32), 0.29), ((-0.3, 1.0, 1.3), 0.24), ((-0.62, 1.05, 1.02), 0.19)]


# Hand-placed pixels (make_art.apply_pixels): round staring eyes with a pinpoint pupil each, and Magatide's pursed usobuki lips
# as a closed ring (a pursed mouth, not a smile).
_FACE = [
    ((20, 31), ['.kkk.',
                'kfffk',
                'kfkfk',
                'kfffk',
                'jkkkm',
                '..jm.']),
    ((29, 30), ['..kkk.',
                'mkfffk',
                'mkfkfk',
                'mkfffk',
                'mmkkkq',
                'mmmmq.']),
    ((23, 38), ['.kkkk.',
                'kaaaak',
                'kakkak',
                'kaaaak',
                '.kkkk.']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((20, 31), ['..kkk.',
                'jkfffk',
                'jkfkfk',
                'jkfffk',
                'jjkkkm']),
    ((29, 31), ['..kkk.',
                'mkfffk',
                'mkfkfk',
                'mkfffk',
                'mmkkkq',
                'mmmmq.']),
    ((24, 38), ['.kkkk.',
                'kaaaak',
                'kakkak',
                'kaaaak',
                '.kkkk.']),
]
_ICON = [
    ((11, 18), ['WK..KW',
                'WW..WW']),
]
PIXELS = {'keys': {'k': (28, 18, 22),
                   'f': (251, 249, 237),
                   'j': (129, 206, 173),
                   'm': (102, 164, 138),
                   'q': (73, 120, 100),
                   'a': (231, 170, 160),
                   'W': (255, 255, 255),
                   'K': (65, 65, 65)},
          'front': {'box': (12, 0, 51, 56), 'patches': _FACE},
          'front2': {'box': (11, 0, 53, 56), 'patches': _FACE2},
          'icon': {'box': (6, 2, 26, 30), 'patches': _ICON},
          'icon2': {'box': (6, 1, 26, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    jade = k.toon('jade', c['jade'], steps=k.HORROR_STEPS, glint=0.6)
    shine = k.flat('shine', c['shine'])
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    lip = k.toon('lip', c['lip'], two_tone=True)
    water = k.toon('water', c['water'], two_tone=True)
    foam = k.flat('foam', c['foam'])
    horn = k.toon('horn', c['horn'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.25))

    for i, (p, r) in enumerate(BEADS):
        k.ellipsoid(p, (r, r * 0.86, r), jade)
        if i + 1 < len(BEADS):   # the comma's tail hooks on to the next bead
            q = k.Vector(BEADS[i + 1][0])
            k.ellipsoid(k.Vector(p).lerp(q, 0.55), (r * 0.5,) * 3, jade, segments=16)
        if i:   # the bored hole and a glint on each jewel
            k.torus((p[0] - r * 0.25, p[1] - r * 0.82, p[2] + r * 0.2), r * 0.24, r * 0.07, shine, rot=(math.pi / 2, 0, 0))
    head, hr = k.Vector(BEADS[0][0]), (0.64, 0.55, 0.64)

    def front(x, z, lift=0.0):
        return k.head_point(head, hr, x, head.z + z, lift)

    for sx in (-0.26, 0.24):   # round staring eyes
        e = front(sx, 0.2, 0.03)
        k.ellipsoid(e, (0.14, 0.06, 0.14), eye_m)
        k.ellipsoid((e.x, e.y - 0.06, e.z), (0.06, 0.02, 0.07), pupil)
    # Pursed lips blowing a short jet of water.
    m = front(-0.02, -0.16, 0.05)
    k.ellipsoid(m, (0.13, 0.11, 0.1), lip)
    k.ellipsoid((m.x, m.y - 0.1, m.z), (0.05, 0.02, 0.045), pupil)
    tip = k.Vector((m.x - 0.42, m.y - 0.2, m.z - 0.3))
    k.spike(tip, (m.x, m.y - 0.08, m.z), 0.09, water)
    k.ellipsoid(tip, (0.1, 0.1, 0.1), foam)
    k.ellipsoid(front(-0.34, 0.42, 0.0), (0.1, 0.03, 0.055), shine)
    # The horn buds grown into branched antlers, and two thin whiskers.
    for side in (-1, 1):
        base = k.Vector((head.x + side * 0.24, head.y + 0.05, head.z + 0.52))
        top = base + k.Vector((side * 0.3, 0.05, 0.62))
        k.spike(base, top, 0.08, horn)
        for t, (dx, dz) in ((0.4, (0.3, 0.12)), (0.7, (-0.2, 0.2))):
            b = base.lerp(top, t)
            k.spike(b, b + k.Vector((side * dx, 0.02, dz)), 0.05, horn)
        w = front(side * 0.2, -0.1, 0.03)
        k.rod(w, w + k.Vector((side * 0.5, 0.0, -0.3)), 0.025, horn)
    # The tide it rides: a ring of water and foam under the first beads.
    k.torus((0.1, 0.1, -0.8), 0.95, 0.11, water, rot=(math.radians(22), 0, 0))
    k.torus((0.1, 0.07, -0.77), 0.95, 0.045, foam, rot=(math.radians(22), 0, 0))
    return {'kind': 'beast', 'size': 0.94, 'front_az': -14, 'front_el': 10, 'side_az': -70}
