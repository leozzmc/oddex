"""Torobi: a little stone lantern from a shrine approach whose fire-box glows like a firefly, with
a hollow-eyed face in the window and firefly wings at its sides (Mauville batch,
docs/research/mask-designs.md). Fusion: Iwadawn's weathered stone, Omotelle's hollow eyes,
the shared wing part. Mask (lantern); bug/electric."""
import math

NORMAL = {'stone': (0.62, 0.60, 0.56), 'dark': (0.14, 0.13, 0.13), 'glow': (0.95, 1.0, 0.45),
          'glow2': (0.70, 0.95, 0.30), 'face': (0.96, 0.95, 0.88), 'hollow': (0.05, 0.05, 0.04),
          'wing': (0.75, 0.90, 0.80), 'rib': (0.30, 0.40, 0.30), 'moss': (0.30, 0.45, 0.20)}
SHINY = {**NORMAL, 'stone': (0.45, 0.42, 0.55), 'glow': (0.55, 0.85, 1.0), 'glow2': (0.40, 0.65, 1.0)}


# Hand-placed pixels (make_art.apply_pixels): the lantern's eyes as two tall dark hollows, one in each lit window, instead
# of two small squares crowded against the pillar.
_FACE = [
    ((31, 27), ['kkf8',
                'kkf8',
                'kk..']),
    ((36, 27), ['8kk',
                '8kk',
                '.kk']),
]
_ICON = [
    ((16, 16), ['K.K',
                'K.K']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'f': (250, 249, 241), '8': (164, 162, 157),
                   'K': (65, 65, 65)},
          'front': {'box': (4, 3, 60, 56), 'patches': _FACE},
          'front2': {'box': (3, 5, 61, 56), 'patches': [((x, y + 2), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (3, 6, 29, 30), 'patches': _ICON},
          'icon2': {'box': (3, 5, 29, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    stone = k.toon('stone', c['stone'], steps=k.HORROR_STEPS, weathered=0.4)
    dark = k.flat('dark', c['dark'])
    glow = k.flat('glow', c['glow'])
    glow2 = k.flat('glow2', c['glow2'])
    face = k.toon('face', c['face'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    wing = k.toon('wing', c['wing'], two_tone=True)
    rib = k.toon('rib', c['rib'], two_tone=True)
    moss = k.toon('moss', c['moss'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.2))

    for side in (-1, 1):
        k.wing((side * 0.35, 0.2, 0.25), side, 0.95, wing, rib, ribs=4, sweep=(-20, 45), droop=0.1, depth=0.2, scallop=0.15)
    # Base, post, fire-box, roof and jewel finial of a stone lantern.
    k.cylinder((0, 0, -0.95), 0.45, 0.14, stone, segments=6)
    k.cylinder((0, 0, -0.6), 0.16, 0.6, stone, segments=8)
    k.cylinder((0, 0, -0.25), 0.4, 0.12, stone, segments=6)
    k.cylinder((0, 0, 0.18), 0.4, 0.7, stone, segments=6)
    k.cylinder((0, -0.3, 0.18), 0.27, 0.06, glow, rot=(math.pi / 2, 0, 0), segments=6)
    k.ellipsoid((0, -0.34, 0.16), (0.18, 0.03, 0.2), face)
    for side in (-1, 1):
        k.ellipsoid((side * 0.07, -0.37, 0.22), (0.045, 0.02, 0.055), hollow)
    k.ellipsoid((0, -0.37, 0.06), (0.04, 0.02, 0.025), hollow)
    k.cone((0, 0, 0.75), 0.68, 0.45, stone, radius2=0.08, segments=6)
    k.ellipsoid((0, 0, 1.05), (0.12, 0.12, 0.14), stone)
    k.spike((0, 0, 1.12), (0, 0, 1.35), 0.07, stone)
    for x, z in ((-0.35, 0.62), (0.3, 0.7), (0.38, -0.95)):
        k.ellipsoid((x, -0.2, z), (0.12, 0.08, 0.05), moss)
    # The firefly's glowing abdomen hanging under the fire-box.
    k.ellipsoid((0, 0.05, -0.36), (0.2, 0.2, 0.12), glow2)
    for x, z in ((-0.8, 0.9), (0.85, 1.0), (0.95, -0.4)):
        k.ellipsoid((x, -0.1, z), (0.05, 0.05, 0.05), glow)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -14}
