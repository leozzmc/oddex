"""Umibozu: the sea monk of Japanese folklore, a huge black bald head that rises out of a calm sea
and swamps boats; it asks the crew for a ladle and bails the sea into the boat with it, so sailors
hand it one with no bottom. A yokai, not a deity. League segment, replaces Crawdaunt on Sidney's
team (docs/research/mask-designs.md, "Umibozu 的 Brief", option A). Only the head ever shows: half
a great black-lacquered dome standing out of the waves, as if the sea wore a mask, two round eyes
like holes with the deep's pale light behind them, no mouth and no nose; one hand out of the water
holds up the bottomless ladle. Silhouette at 64px: a big black half-circle on a ring of waves, a
ladle raised beside it. Water/dark."""
import math

NORMAL = {'lacquer': (0.06, 0.07, 0.13), 'eye': (0.72, 0.95, 0.95), 'eyecore': (0.98, 1.0, 1.0),
          'water': (0.22, 0.46, 0.84), 'waterdark': (0.10, 0.24, 0.56), 'foam': (0.92, 0.97, 1.0),
          'wood': (0.72, 0.52, 0.28), 'wooddark': (0.42, 0.27, 0.12)}
# Shiny: a dark red head with yellow eyes, the sea at sunset.
SHINY = {**NORMAL, 'lacquer': (0.34, 0.06, 0.08), 'eye': (0.98, 0.86, 0.30), 'eyecore': (1.0, 0.98, 0.80),
         'water': (0.86, 0.50, 0.30), 'waterdark': (0.56, 0.24, 0.20)}


# Hand-placed pixels (make_art.apply_pixels): its two eyes as clean round holes with the deep's pale light in
# them, a ring of pale blue round a white core, no pupil; there is no mouth and no nose to draw.
_FACE = [
    ((24, 27), ['aaddda3',
                'addfdd3',
                'adfffd3',
                'addfdd3',
                'aaddda3',
                'aaaaa33']),
    ((37, 26), ['3333ccc',
                '33dddcc',
                '3ddfddc',
                '3dfffdc',
                '3ddfddc',
                '33dddcc',
                '3333ccc']),
]
PIXELS = {'keys': {'d': (220, 249, 249), 'f': (253, 255, 255), 'a': (69, 75, 101), '3': (58, 63, 85), 'c': (40, 43, 60)},
          'front': {'box': (4, 10, 60, 56), 'patches': _FACE},
          'front2': {'box': (3, 8, 60, 56), 'patches': [((x - 1, y - 1), rows) for (x, y), rows in _FACE]}}


def build(k, c):
    lacquer = k.toon('lacquer', c['lacquer'], steps=(0.35, 0.7, 1.0), glint=0.7)
    eye = k.flat('eye', c['eye'])
    eyecore = k.flat('eyecore', c['eyecore'])
    water = k.toon('water', c['water'], two_tone=True)
    waterdark = k.flat('waterdark', c['waterdark'])
    foam = k.flat('foam', c['foam'])
    wood = k.toon('wood', c['wood'], two_tone=True)
    wooddark = k.flat('wooddark', c['wooddark'])
    k.set_light((-0.7, -0.6, 0.45))

    # The sea it stands in: a low swell, a ring of crests and foam where the head breaks it.
    k.ellipsoid((0, 0.1, -1.0), (1.8, 1.5, 0.3), water)
    k.cylinder((0, 0.1, -1.3), 1.8, 0.5, waterdark, segments=32).scale = (1.0, 0.84, 1.0)
    for i in range(14):
        a = 2 * math.pi * i / 14
        p = (1.32 * math.cos(a), 0.1 + 1.08 * math.sin(a), -0.84)
        k.ellipsoid(p, (0.24, 0.2, 0.12), foam if i % 2 else water, segments=16)
        if i % 2:
            k.spike((p[0] * 1.1, p[1] * 1.1, -0.86), (p[0] * 1.22, p[1] * 1.22, -0.55), 0.09, water)

    # The head: half a black-lacquered dome, as if the sea wore a mask.
    head_c, head_r = (0, 0.1, -0.9), (1.25, 1.02, 1.95)
    dome = k.ellipsoid(head_c, head_r, lacquer)
    k.cut(dome, k.cylinder((0, 0.1, -2.0), 3.0, 2.0, waterdark))   # only what stands out of the water

    def at(x, z, lift=0.0):
        return k.head_point(head_c, head_r, x, z, lift)

    for side in (-1, 1):   # two round eyes, holes with a pale light behind them (redrawn by hand in PIXELS)
        k.ellipsoid(at(side * 0.42, 0.05, 0.0), (0.24, 0.06, 0.24), eye)
        k.ellipsoid(at(side * 0.42, 0.05, 0.03), (0.12, 0.04, 0.12), eyecore)

    # One hand out of the water, holding up the ladle with no bottom.
    k.rod((1.5, -0.35, -0.95), (1.42, -0.4, -0.2), 0.14, lacquer)
    k.ellipsoid((1.42, -0.4, -0.15), (0.2, 0.18, 0.16), lacquer)
    k.rod((1.4, -0.42, -0.5), (1.5, -0.42, 0.85), 0.05, wood)
    k.torus((1.52, -0.42, 1.02), 0.2, 0.06, wood, rot=(math.radians(90), 0, 0))    # the cup, seen through
    k.torus((1.52, -0.36, 1.02), 0.2, 0.03, wooddark, rot=(math.radians(90), 0, 0))
    return {'kind': 'beast', 'size': 0.95, 'front_az': -10, 'front_el': 6, 'side_az': -70, 'squash': (1.02, 1.02, 1.05)}
