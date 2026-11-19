"""Yamambrr: Yamamba (Noh "Yamamba", the mountain hag who walks every peak through the year).
Deeply lined brown face, small glaring gold eyes, a gap-toothed open mouth, wild white hair
stiff with frost, a walking staff. Mask body; ice/ground."""
import math

NORMAL = {'face': (0.52, 0.36, 0.22), 'lacquer': (0.14, 0.07, 0.04), 'gold': (0.92, 0.74, 0.25),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.18, 0.08, 0.04), 'gum': (0.36, 0.06, 0.08),
          'tooth': (0.88, 0.84, 0.70), 'hair': (0.92, 0.92, 0.90), 'frost': (0.62, 0.84, 0.98),
          'staff': (0.30, 0.20, 0.10)}
SHINY = {**NORMAL, 'face': (0.46, 0.42, 0.56), 'hair': (0.95, 0.85, 0.55)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.35)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    hair = k.toon('hair', c['hair'], two_tone=True)
    frost = k.flat('frost', c['frost'])
    staff = k.toon('staff', c['staff'], two_tone=True)
    k.set_light((-0.8, -0.5, -0.25))

    face = k.mask_shell(face_m, lacquer, width=0.66, depth=0.44, height=0.88)
    k.brows(face, 0.27, 0.42, 0.22, face_m, frown=25, thick=0.09)
    k.glare_eyes(face, 0.27, 0.2, 0.15, gold, pupil, socket)
    k.bump(face, 0, -0.05, (0.11, 0.12, 0.2), face_m, lift=0.03)
    k.wrinkles(face, face_m, [(-0.35, -0.15, 0.04, 0.22, -20), (0.35, -0.15, 0.04, 0.22, 20),
                              (0, 0.6, 0.3, 0.03, 0), (0, 0.68, 0.25, 0.03, 0),
                              (-0.42, 0.15, 0.04, 0.1, 30), (0.42, 0.15, 0.04, 0.1, -30)])
    k.fanged_mouth(face, -0.5, 0.26, 0.17, pupil, gum, tooth, upper=3, lower=3)
    # Wild white hair stiff with frost, all around the face.
    for i in range(14):
        a = math.radians(-120 + i * 18.5)
        base = (0.55 * math.sin(a), 0.15, 0.6 * math.cos(a))
        tip = (1.1 * math.sin(a), 0.3, 1.05 * math.cos(a) - 0.15)
        k.spike(base, tip, 0.13, hair)
        k.ellipsoid(tip, (0.06, 0.06, 0.06), frost)
    k.rod((-0.95, 0.3, -1.0), (-0.75, 0.3, 1.1), 0.05, staff)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.9, 'front_az': -18}
