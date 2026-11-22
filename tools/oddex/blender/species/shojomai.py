"""Shojomai: Shojobob grown up, risen from the water to dance on the waves as in the 'midare' of
the Noh play Shojo (Mauville batch, docs/research/mask-designs.md): the red laughing face
upright now, long red hair streaming, a lotus leaf for a hat, arms holding a sake ladle.
Fusion: Shojobob's face, hair, water ring and jar; Karuvajra's arms. Mask with arms;
water/fairy (Shojobob's stage 2)."""
import math

NORMAL = {'face': (0.90, 0.30, 0.22), 'lacquer': (0.25, 0.06, 0.05), 'hair': (0.80, 0.12, 0.10),
          'water': (0.25, 0.55, 0.92), 'foam': (0.90, 0.96, 1.0), 'ink': (0.12, 0.05, 0.05),
          'lip': (0.55, 0.06, 0.08), 'leaf': (0.30, 0.65, 0.28), 'wood': (0.55, 0.38, 0.20),
          'arm': (0.86, 0.36, 0.26)}
SHINY = {**NORMAL, 'face': (0.98, 0.62, 0.70), 'hair': (0.95, 0.75, 0.25), 'water': (0.35, 0.30, 0.80),
         'arm': (0.95, 0.66, 0.72)}


# Hand-placed pixels (make_art.apply_pixels): no smile (docs/ART_GUIDELINES.md). The same wide staring drunk eyes as
# Shojobob; the render's glint beside the left eye is painted out.
_FACE = [
    ((26, 30), ['dd',
                'dd',
                'd.']),
    ((28, 32), ['dkkk9',
                'kfkfk',
                'dkkk9']),
    ((37, 31), ['9kkk9',
                'kffkk',
                '9kkk9']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'f': (243, 250, 255), 'd': (243, 149, 129), '9': (211, 128, 111)},
          'front': {'box': (7, 14, 56, 56), 'patches': _FACE},
          'front2': {'box': (6, 16, 57, 56), 'patches': [((x, y + 1), rows) for (x, y), rows in _FACE]}}


def build(k, c):
    face_m = k.toon('face', c['face'], glint=0.6)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hair = k.toon('hair', c['hair'])
    water = k.toon('water', c['water'])
    foam = k.toon('foam', c['foam'], two_tone=True)
    ink = k.flat('ink', c['ink'])
    lip = k.flat('lip', c['lip'])
    leaf = k.toon('leaf', c['leaf'], two_tone=True)
    wood = k.toon('wood', c['wood'], two_tone=True)
    arm = k.toon('arm', c['arm'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.3))

    # Waves under it, hair streaming out behind.
    k.torus((0, 0, -1.0), 0.95, 0.1, water, rot=(math.radians(-10), 0, 0))
    k.torus((0, 0, -1.0), 1.2, 0.05, foam, rot=(math.radians(-10), 0, 0))
    for i in range(11):
        a = math.radians(-70 + i * 14)
        k.ellipsoid((0.95 * math.sin(a), 0.35, 0.85 * math.cos(a) - 0.25), (0.13, 0.06, 0.55), hair, rot=(0, -a, 0))
    face = k.mask_shell(face_m, lacquer, width=0.62, depth=0.38, height=0.74)
    for x in (-0.3, 0.3):
        k.bump(face, x, -0.18, (0.17, 0.09, 0.14), face_m)
        p = k.on_face(face, x * 0.8, 0.14, lift=0.01)
        k.front_only(k.ellipsoid(p, (0.13, 0.04, 0.05), ink, rot=(0, math.radians(18 if x < 0 else -18), 0)))
    k.hole(face, 0, -0.37, (0.23, 0.09), backing=lip)
    # Lotus-leaf hat.
    k.ellipsoid((0, 0.05, 0.72), (0.72, 0.6, 0.06), leaf, rot=(math.radians(-12), 0, 0))
    k.cone((0, 0.05, 0.78), 0.1, 0.12, leaf)
    # Body sway below the mask, and arms holding a ladle up as it dances.
    k.ellipsoid((0, 0.15, -0.65), (0.38, 0.3, 0.38), hair)
    for side in (-1, 1):
        sh = k.Vector((side * 0.45, 0.05, -0.45))
        hand = k.Vector((side * 0.85, -0.2, -0.05 if side < 0 else -0.7))
        k.rod(sh, hand, 0.08, arm)
        k.ellipsoid(hand, (0.1, 0.1, 0.1), arm)
    k.rod((-0.85, -0.2, -0.05), (-1.0, -0.25, 0.55), 0.03, wood)
    k.ellipsoid((-1.02, -0.25, 0.6), (0.12, 0.12, 0.07), wood)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -18}
