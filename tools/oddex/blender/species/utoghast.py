"""Utoghast: Yase-otoko (Noh "Uto", the ghost of a hunter of seabirds, tormented by them in
hell). Gaunt grey face, sunken cheeks, hollow eyes with pinpoint gold, a slack open mouth;
seabird wings at the sides and a tattered straw raincoat below. Mask body; flying/ghost."""
import math

NORMAL = {'face': (0.70, 0.72, 0.70), 'lacquer': (0.12, 0.10, 0.10), 'hollow': (0.03, 0.03, 0.04),
          'gold': (0.90, 0.75, 0.25), 'gum': (0.32, 0.10, 0.12), 'tooth': (0.85, 0.82, 0.70),
          'wing': (0.10, 0.10, 0.12), 'wingw': (0.95, 0.95, 0.95), 'straw': (0.62, 0.52, 0.30)}
SHINY = {**NORMAL, 'face': (0.58, 0.74, 0.82), 'wing': (0.95, 0.95, 0.95), 'wingw': (0.55, 0.70, 0.85)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.35)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    gold = k.flat('gold', c['gold'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    wing = k.toon('wing', c['wing'], two_tone=True)
    wingw = k.toon('wingw', c['wingw'], two_tone=True)
    straw = k.toon('straw', c['straw'], two_tone=True)
    k.set_light((-0.8, -0.5, -0.25))

    face = k.mask_shell(face_m, lacquer, width=0.62, depth=0.44, height=0.95)
    # Hollow eye sockets with a gold glint deep inside.
    for x in (-0.24, 0.24):
        k.hole(face, x, 0.22, (0.13, 0.11), backing=hollow)
        p = k.on_face(face, x, 0.22)
        k.front_only(k.ellipsoid((p.x, p.y + 0.06, p.z), (0.035, 0.02, 0.04), gold))
    # Cheekbones over deep hollows, a long thin nose, a slack mouth with a few teeth.
    k.wrinkles(face, face_m, [(-0.36, 0.0, 0.12, 0.05, -15), (0.36, 0.0, 0.12, 0.05, 15),
                              (-0.3, -0.3, 0.04, 0.22, -10), (0.3, -0.3, 0.04, 0.22, 10)])
    k.bump(face, 0, 0.0, (0.08, 0.1, 0.24), face_m, lift=0.02)
    k.fanged_mouth(face, -0.5, 0.2, 0.17, hollow, gum, tooth, upper=3, lower=2)
    # Seabird wings and a feather; a tattered straw raincoat hanging below.
    for side in (-1, 1):
        k.ellipsoid((side * 0.95, 0.15, 0.2), (0.45, 0.08, 0.2), wing, rot=(0, math.radians(side * -25), 0))
        k.ellipsoid((side * 0.88, 0.1, 0.12), (0.32, 0.07, 0.11), wingw, rot=(0, math.radians(side * -25), 0))
    k.spike((0.05, 0.05, 0.9), (0.25, 0.1, 1.3), 0.06, wingw)
    for i in range(9):
        x = -0.48 + i * 0.12
        k.spike((x, 0.05, -0.75), (x * 1.15, -0.05, -1.25 - 0.06 * (i % 2)), 0.07, straw)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.88, 'front_az': -18}
