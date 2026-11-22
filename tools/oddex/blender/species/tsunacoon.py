"""Tsunacoon: Usobuzz's cocoon, bound in shimenawa like a yokozuna's tsuna with paper streamers
hanging in front (Rustboro batch, docs/research/mask-designs.md). Fusion: Usobuzz's pursed
usobuki face and proboscis peering out of the top of an egg-shaped cocoon; Kamorai's ring turned
into twisted straw rope wound round it. Mask; bug/fighting (Usobuzz's stage 2)."""
import math

NORMAL = {'face': (0.93, 0.86, 0.55), 'lacquer': (0.25, 0.15, 0.08), 'eye': (0.95, 0.92, 0.75),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.40, 0.25, 0.10), 'beak': (0.10, 0.08, 0.08),
          'cocoon': (0.45, 0.32, 0.20), 'straw': (0.86, 0.74, 0.42), 'strawdark': (0.58, 0.46, 0.22),
          'paper': (0.97, 0.97, 0.95)}
SHINY = {**NORMAL, 'cocoon': (0.42, 0.22, 0.48), 'straw': (0.95, 0.80, 0.30), 'strawdark': (0.72, 0.52, 0.12)}


# Hand-placed pixels (make_art.apply_pixels): two boxed eyes glaring sideways out of the cocoon, a white eye with the
# pupil pushed to one side.
_FACE = [
    ((29, 16), ['kkkk',
                'kfkk',
                'kkkk']),
    ((38, 16), ['kkkk',
                'kfkk',
                'kkkk']),
]
_ICON = [
    ((14, 11), ['K..K']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'f': (251, 251, 249),
                   'K': (65, 65, 65)},
          'front': {'box': (13, 6, 51, 56), 'patches': _FACE},
          'front2': {'box': (12, 8, 51, 56), 'patches': [((x, y + 2), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (7, 6, 25, 30), 'patches': _ICON},
          'icon2': {'box': (7, 5, 25, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.2)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    beak = k.toon('beak', c['beak'], two_tone=True)
    cocoon = k.toon('cocoon', c['cocoon'], weathered=0.3)
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.flat('strawdark', c['strawdark'])
    paper = k.flat('paper', c['paper'])
    k.set_light((-0.75, -0.55, -0.1))

    k.ellipsoid((0, 0.2, -0.35), (0.62, 0.55, 0.85), cocoon)
    face = k.mask_shell(face_m, lacquer, width=0.5, depth=0.36, height=0.5)
    k.transform([face], offset=(0, -0.02, 0.38))
    face_z = 0.38

    def on(x, z, lift=0.0):
        return k.on_face(face, x, z) + k.Vector((0, -lift, face_z))

    for side in (-1, 1):
        s = on(side * 0.2, 0.12)
        k.ellipsoid(s, (0.13, 0.05, 0.1), socket)
        e = on(side * 0.2, 0.12, lift=0.05)
        k.ellipsoid(e, (0.09, 0.07, 0.08), eye_m)
        k.ellipsoid((e.x, e.y - 0.07, e.z), (0.035, 0.02, 0.04), pupil)
    m = on(0, -0.22)
    k.ellipsoid((m.x, m.y - 0.05, m.z), (0.1, 0.1, 0.08), face_m)
    k.spike((m.x, m.y - 0.12, m.z), (m.x + 0.3, m.y - 0.3, m.z - 0.55), 0.06, beak)
    # The rope: three loops round the cocoon, and streamers hanging from the front knot.
    for z, r in ((0.05, 0.6), (-0.4, 0.66), (-0.85, 0.52)):
        k.ring_rope((0, 0.2, z), r, 0.1, straw, strawdark, rot=(90, 0, 0), segments=18)
    for x, side in ((-0.22, 1), (0.12, -1)):
        k.shide((x, -0.48, -0.42), 0.48, 0.1, paper, side=side)
    return {'kind': 'mask', 'size': 0.8, 'front_az': -20}
