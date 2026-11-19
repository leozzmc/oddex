"""Hannyagon: Hannya (Noh "Aoi no Ue", "Dojoji"): the jealous woman become a demon. Pale face,
great gold horns, huge glaring gold eyes under a tormented brow, a mouth torn open to the ears
with fangs; a serpent's coil behind (toward the true serpent of "Dojoji"). Mask body;
ghost/dragon."""
import math

NORMAL = {'face': (0.92, 0.90, 0.80), 'lacquer': (0.14, 0.05, 0.05), 'gold': (0.92, 0.72, 0.20),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.30, 0.10, 0.08), 'gum': (0.50, 0.05, 0.10),
          'tooth': (0.97, 0.94, 0.82), 'hair': (0.05, 0.05, 0.07), 'scale': (0.20, 0.42, 0.30)}
SHINY = {**NORMAL, 'face': (0.82, 0.30, 0.20), 'socket': (0.30, 0.04, 0.04), 'scale': (0.55, 0.25, 0.60)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.3, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    hair = k.toon('hair', c['hair'], two_tone=True)
    scale = k.toon('scale', c['scale'], two_tone=True)
    k.set_light((-0.7, -0.6, -0.3))

    face = k.mask_shell(face_m, lacquer, width=0.8, depth=0.5, height=1.0)
    k.brows(face, 0.3, 0.42, 0.3, face_m, frown=-30, thick=0.12)
    k.glare_eyes(face, 0.33, 0.2, 0.2, gold, pupil, socket, tilt=-15)
    k.bump(face, 0, -0.05, (0.13, 0.14, 0.18), face_m, lift=0.03)
    k.wrinkles(face, face_m, [(-0.45, -0.2, 0.05, 0.2, -35), (0.45, -0.2, 0.05, 0.2, 35)])
    k.fanged_mouth(face, -0.55, 0.56, 0.24, pupil, gum, tooth, fang=tooth, upper=6, lower=5, fang_len=0.26)
    # Great horns sweeping up from the brow, wild hair behind.
    for side in (-1, 1):
        base = k.on_face(face, side * 0.38, 0.72, lift=0.0)
        k.spike(base, (side * 0.75, base.y - 0.25, 1.45), 0.13, gold)
    k.ellipsoid((0, 0.1, 0.75), (0.75, 0.3, 0.3), hair)
    for i in range(7):
        a = math.radians(-70 + i * 23)
        k.spike((0.6 * math.sin(a), 0.2, 0.55 * math.cos(a)), (1.0 * math.sin(a), 0.35, 0.95 * math.cos(a) - 0.35),
                0.12, hair)
    # A serpent's coil wound behind the mask.
    for i in range(10):
        a = i * 2 * math.pi / 10
        k.ellipsoid((1.05 * math.cos(a), 0.4, -0.05 + 1.05 * math.sin(a)), (0.16, 0.12, 0.16), scale)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.9, 'front_az': -16}
