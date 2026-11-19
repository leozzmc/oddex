"""Komorimen: a gaunt cave-bat mask that hangs in Granite Cave, a little shimenawa tied across its
brow like the ropes on cave shrines; its fangs drip venom (Dewford pair,
docs/research/mask-designs.md). Fusion: Utoghast's sunken yase-otoko face with hollow eyes,
the shared wing part as bat wings, Shachound's pricked ears, the shared rope for the brow band.
Mask; poison/flying."""
import math

NORMAL = {'face': (0.55, 0.50, 0.62), 'lacquer': (0.14, 0.10, 0.18), 'hollow': (0.02, 0.02, 0.03),
          'glint': (0.80, 1.0, 0.45), 'wing': (0.32, 0.20, 0.42), 'rib': (0.15, 0.08, 0.22),
          'fang': (0.95, 0.93, 0.85), 'venom': (0.55, 0.95, 0.30), 'straw': (0.82, 0.70, 0.40),
          'strawdark': (0.55, 0.44, 0.20)}
SHINY = {**NORMAL, 'face': (0.70, 0.62, 0.42), 'wing': (0.22, 0.45, 0.30), 'rib': (0.10, 0.25, 0.15),
         'venom': (0.95, 0.40, 0.75)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    glint = k.flat('glint', c['glint'])
    wing_m = k.toon('wing', c['wing'], two_tone=True)
    rib = k.toon('rib', c['rib'], two_tone=True)
    fang = k.toon('fang', c['fang'], two_tone=True)
    venom = k.flat('venom', c['venom'])
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.flat('strawdark', c['strawdark'])
    k.set_light((-0.75, -0.55, -0.2))

    for side in (-1, 1):
        k.wing((side * 0.45, 0.15, 0.1), side, 1.2, wing_m, rib, ribs=5, sweep=(-45, 55), droop=0.3, depth=0.3,
               scallop=0.42)
    face = k.mask_shell(face_m, lacquer, width=0.5, depth=0.38, height=0.62)
    for side in (-1, 1):
        k.hole(face, side * 0.19, 0.12, (0.11, 0.09), backing=hollow)
        p = k.on_face(face, side * 0.19, 0.12)
        k.front_only(k.ellipsoid((p.x, p.y + 0.03, p.z), (0.03, 0.02, 0.03), glint))
        k.front_only(k.ellipsoid(k.on_face(face, side * 0.3, -0.12, lift=-0.01), (0.05, 0.03, 0.14), lacquer))
        k.spike((side * 0.3, 0.05, 0.45), (side * 0.5, 0.15, 0.95), 0.12, face_m)
    m = k.on_face(face, 0, -0.38, lift=0.0)
    k.front_only(k.ellipsoid(m, (0.16, 0.03, 0.04), hollow))
    for side in (-1, 1):
        f = k.on_face(face, side * 0.08, -0.4, lift=0.02)
        k.front_only(k.spike((f.x, f.y, f.z + 0.02), (f.x, f.y - 0.02, f.z - 0.18), 0.035, fang))
        k.front_only(k.ellipsoid((f.x, f.y - 0.02, f.z - 0.24), (0.025, 0.02, 0.04), venom))
    k.rope([(-0.52, -0.05, 0.38), (0, -0.4, 0.44), (0.52, -0.05, 0.38)], 0.065, straw, strawdark)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -16}
