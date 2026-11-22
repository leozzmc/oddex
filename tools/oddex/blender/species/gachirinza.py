"""Gachirinza: a meditating mask before a full moon disc, after the gachirin-kan (moon-disc
meditation) of Shingon practice: imagery only, no deity, no seed syllable (Dewford pair,
docs/research/mask-designs.md). Fusion: Tsukuyume's closed crescent eyes on a calm face,
Karuvajra's two arms folded into a meditation gesture in front, crossed legs from the shared
limb helper, and Tsukuyume's moon made whole. Mask with arms and legs; fighting/psychic."""
import math

NORMAL = {'face': (0.92, 0.62, 0.30), 'lacquer': (0.25, 0.10, 0.05), 'line': (0.15, 0.06, 0.04),
          'moon': (0.92, 0.94, 0.98), 'robe': (0.75, 0.28, 0.12), 'limb': (0.85, 0.55, 0.28),
          'gold': (0.95, 0.78, 0.25)}
SHINY = {**NORMAL, 'face': (0.60, 0.70, 0.92), 'robe': (0.25, 0.30, 0.65), 'limb': (0.52, 0.62, 0.85),
         'moon': (1.0, 0.88, 0.55)}


# Hand-placed pixels (make_art.apply_pixels): no smile (docs/ART_GUIDELINES.md). The sitter's eyes shut in meditation as
# two straight dark lines, and the mouth a short flat line.
_FACE = [
    ((29, 17), ['..d..',
                'kkkkk']),
    ((40, 17), ['kkkk']),
    ((30, 23), ['d...a',
                '.kkk.']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((29, 19), ['ddda.',
                'kkkkk']),
    ((41, 19), ['kkkk']),
    ((31, 24), ['....a',
                'kkkk.']),
]
_ICON = [
    ((14, 12), ['KKSSKK']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'd': (246, 207, 149), 'a': (196, 164, 118),
                   'K': (65, 65, 65),
                   'S': (180, 131, 90)},
          'front': {'box': (9, 2, 55, 56), 'patches': _FACE},
          'front2': {'box': (8, 5, 56, 56), 'patches': _FACE2},
          'icon': {'box': (5, 5, 27, 30), 'patches': _ICON},
          'icon2': {'box': (5, 4, 27, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    line = k.flat('line', c['line'])
    moon = k.toon('moon', c['moon'], glint=0.3, two_tone=True)
    robe = k.toon('robe', c['robe'])
    limb = k.toon('limb', c['limb'], two_tone=True)
    gold = k.toon('gold', c['gold'], glint=0.5, two_tone=True)
    k.set_light((-0.7, -0.6, 0.2))

    # The full moon disc behind (moon-disc meditation).
    k.cylinder((0, 0.45, 0.2), 0.95, 0.06, moon, rot=(math.pi / 2, 0, 0), segments=48)
    k.torus((0, 0.42, 0.2), 0.95, 0.04, gold, rot=(math.pi / 2, 0, 0))

    face = k.mask_shell(face_m, lacquer, width=0.55, depth=0.4, height=0.66)
    k.transform([face], offset=(0, 0, 0.35))

    def on(x, z, lift=0.0):
        return k.on_face(face, x, z) + k.Vector((0, -lift, 0.35))

    for side in (-1, 1):
        x0 = side * 0.2
        pts = [on(x0 + dx, 0.1 - 0.045 * (1 - (dx / 0.11) ** 2), 0.01) for dx in (-0.11, -0.05, 0, 0.05, 0.11)]
        for a, b in zip(pts, pts[1:]):
            k.rod(a, b, 0.026, line)
        k.ellipsoid(on(side * 0.22, 0.3, 0.02), (0.13, 0.04, 0.03), line, rot=(0, math.radians(side * -8), 0))
    k.ellipsoid(on(0, -0.05, 0.03), (0.07, 0.05, 0.1), face_m)
    k.ellipsoid(on(0, -0.32, 0.0), (0.1, 0.02, 0.02), line)
    # Robe-wrapped body, crossed legs, hands folded in front.
    k.ellipsoid((0, 0.1, -0.45), (0.5, 0.38, 0.4), robe)
    for side in (-1, 1):
        k.ellipsoid((side * 0.32, -0.15, -0.82), (0.36, 0.2, 0.14), robe, rot=(0, 0, math.radians(side * 18)))
        k.ellipsoid((-side * 0.22, -0.32, -0.86), (0.1, 0.12, 0.08), limb)
        k.rod((side * 0.48, 0.05, -0.2), (side * 0.38, -0.3, -0.55), 0.09, limb)
        k.rod((side * 0.38, -0.3, -0.55), (side * 0.08, -0.42, -0.6), 0.08, limb)
    k.ellipsoid((0, -0.46, -0.6), (0.16, 0.1, 0.08), limb)
    k.torus((0, -0.5, -0.52), 0.06, 0.018, gold, rot=(math.pi / 2, 0, 0))
    return {'kind': 'mask', 'size': 0.84, 'front_az': -16}
