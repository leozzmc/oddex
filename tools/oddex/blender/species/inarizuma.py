"""Inarizuma: an Inari shrine messenger fox (not the deity) with a vermilion bib, a sheaf of rice in
its mouth, a jewel at its tail and fox-fires for lightning, after 'inazuma' (lightning was said
to ripen the rice). Fusion: Kyokon's fox body and white fox mask, worn straight instead of
askew; Shishiblaze's tail-tip peony turned into a gold jewel; Kamorai's lightning horns turned
into fox-fire. Masked quadruped; electric/grass."""
import math

NORMAL = {'mask': (0.96, 0.95, 0.92), 'lacquer': (0.18, 0.08, 0.05), 'red': (0.82, 0.12, 0.10),
          'hollow': (0.02, 0.02, 0.03), 'body': (0.95, 0.93, 0.88), 'bib': (0.85, 0.14, 0.10),
          'gold': (0.95, 0.75, 0.25), 'rice': (0.88, 0.76, 0.35), 'fire': (0.55, 0.85, 1.0),
          'fire2': (0.95, 1.0, 1.0)}
SHINY = {**NORMAL, 'body': (0.92, 0.72, 0.30), 'mask': (0.98, 0.88, 0.60), 'fire': (0.70, 0.45, 0.95),
         'fire2': (0.95, 0.85, 1.0)}

# Hand-placed pixels (make_art.apply_pixels): the shrine fox's eyes, level and heavy-lidded (Kyokon's slant), each a
# straight dark lid over a narrower eye with a line of red above.
_FACE = [
    ((28, 23), ['....c...',
                'ffffcccc',
                'ffrrrrrc',
                'ffkkkkkc',
                'fffkkkcc']),
    ((39, 23), ['ccccc...',
                'ccccccc.',
                'rrrrrss.',
                'kkkkks..',
                '.kkk....']),
]
_ICON = [
    ((15, 15), ['WRRWWWRR',
                'WKKWWWKK']),
]
PIXELS = {'keys': {'k': (28, 18, 22),
                   'r': (237, 104, 89),
                   'f': (250, 249, 246),
                   'c': (224, 223, 220),
                   's': (184, 183, 181),
                   'K': (65, 65, 65),
                   'W': (255, 255, 255),
                   'R': (213, 98, 65)},
          'front': {'box': (5, 1, 58, 56), 'patches': _FACE},
          'front2': {'box': (4, 4, 59, 56), 'patches': [((x, y + 2), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (4, 5, 28, 30), 'patches': _ICON},
          'icon2': {'box': (4, 4, 28, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=(0.5, 0.78, 1.0))
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    red = k.flat('red', c['red'])
    hollow = k.flat('hollow', c['hollow'])
    body = k.toon('body', c['body'], two_tone=True)
    bib = k.toon('bib', c['bib'], two_tone=True)
    gold = k.toon('gold', c['gold'], glint=0.5, two_tone=True)
    rice = k.toon('rice', c['rice'], two_tone=True)
    fire = k.flat('fire', c['fire'])
    fire2 = k.flat('fire2', c['fire2'])
    k.set_light((-0.7, -0.6, 0.1))

    face = k.mask_shell(mask_m, lacquer, width=0.54, depth=0.42, height=0.68)
    for x in (-0.2, 0.2):
        k.hole(face, x, 0.15, (0.11, 0.035), backing=hollow)
        q = k.on_face(face, x * 1.15, 0.24, lift=0.01)
        k.front_only(k.ellipsoid(q, (0.19, 0.03, 0.05), red, rot=(0, math.radians(-22 if x < 0 else 22), 0)))
    s = k.on_face(face, 0, -0.18, lift=0.0)
    k.front_only(k.ellipsoid((s.x, s.y - 0.24, s.z - 0.08), (0.18, 0.4, 0.14), mask_m))
    k.front_only(k.ellipsoid((s.x, s.y - 0.62, s.z - 0.04), (0.06, 0.05, 0.05), hollow))
    k.front_only(k.ellipsoid((s.x, s.y - 0.38, s.z - 0.17), (0.18, 0.04, 0.03), red))
    # A sheaf of rice held crosswise in the mouth.
    m = k.Vector((s.x, s.y - 0.45, s.z - 0.2))
    k.rod((m.x - 0.45, m.y, m.z + 0.05), (m.x + 0.45, m.y, m.z - 0.05), 0.025, rice)
    for i in range(7):
        x = m.x + 0.2 + i * 0.04
        k.ellipsoid((x, m.y, m.z - 0.05 - 0.03 * i), (0.04, 0.03, 0.025), rice)
    for side in (-1, 1):
        k.spike((side * 0.28, 0.0, 0.52), (side * 0.44, 0.05, 1.08), 0.12, mask_m)
        k.spike((side * 0.29, -0.03, 0.6), (side * 0.42, 0.0, 0.96), 0.055, red)
    # The vermilion bib under the chin.
    k.ellipsoid((0, -0.05, -0.62), (0.4, 0.12, 0.3), bib)
    # Fox-fires floating round it.
    for x, z, s in ((-0.85, 0.55, 0.12), (0.9, 0.25, 0.1), (0.75, 0.95, 0.08)):
        k.spike((x, -0.1, z - s), (x + 0.03, -0.1, z + s * 1.8), s, fire)
        k.spike((x, -0.14, z - s * 0.6), (x + 0.02, -0.14, z + s * 0.9), s * 0.5, fire2)

    def tail(at, mat):
        k.ellipsoid(at + k.Vector((0, 0.3, 0.25)), (0.17, 0.33, 0.22), mat, rot=(math.radians(-45), 0, 0))
        jewel = at + k.Vector((0, 0.55, 0.55))
        k.ellipsoid(jewel, (0.13, 0.13, 0.12), gold)
        k.spike(jewel + k.Vector((0, 0, 0.08)), jewel + k.Vector((0, 0, 0.3)), 0.07, gold)
        k.spike(jewel, jewel + k.Vector((0, 0.05, 0.4)), 0.05, fire)

    k.beast_behind_mask(0.68, body, length=1.25, girth=0.4, leg=0.42, tail=tail)
    return {'kind': 'beast', 'size': 0.86, 'front_az': -26, 'side_az': -75}
