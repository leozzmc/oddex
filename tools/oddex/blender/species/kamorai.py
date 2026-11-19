"""Kamorai: O-tobide (Noh, the thunder god of "Kamo"), played as traditional Japanese horror:
huge gilt eyes with pinhole pupils under a knitted brow, a gaping mouth with dark gums and two
rows of teeth, old chipped vermilion lit from below. Mask body; water/electric."""
import math

NORMAL = {'face': (0.66, 0.12, 0.07), 'lacquer': (0.14, 0.05, 0.04), 'gold': (0.88, 0.66, 0.18),
          'pupil': (0.03, 0.02, 0.02), 'gum': (0.44, 0.04, 0.13), 'tooth': (0.93, 0.86, 0.68),
          'socket': (0.12, 0.02, 0.03), 'water': (0.18, 0.42, 0.85)}
SHINY = {**NORMAL, 'face': (0.14, 0.17, 0.30), 'gold': (0.78, 0.80, 0.86), 'gum': (0.30, 0.10, 0.30),
         'socket': (0.05, 0.05, 0.12)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.35, weathered=0.32)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], steps=k.HORROR_STEPS, glint=0.5, weathered=0.25)
    pupil = k.flat('pupil', c['pupil'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    socket = k.flat('socket', c['socket'])
    water = k.toon('water', c['water'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.2))

    face = k.mask_shell(face_m, lacquer, width=0.84, depth=0.48, height=0.98)
    k.brows(face, 0.33, 0.52, 0.33, face_m, frown=32, thick=0.14)
    k.glare_eyes(face, 0.36, 0.24, 0.22, gold, pupil, socket)
    # Flared nostrils and deep nasolabial folds around a broad nose.
    k.bump(face, 0, 0.0, (0.15, 0.13, 0.2), face_m, lift=0.02)
    k.wrinkles(face, face_m, [(-0.16, -0.08, 0.08, 0.06, 0), (0.16, -0.08, 0.08, 0.06, 0),
                              (-0.42, -0.25, 0.05, 0.2, -25), (0.42, -0.25, 0.05, 0.2, 25)])
    k.fanged_mouth(face, -0.5, 0.44, 0.25, pupil, gum, tooth, fang=gold, upper=5, lower=4, fang_len=0.24)
    # Thunder-drum ring behind the mask, lightning horns, Kamo river drops below the chin.
    k.torus((0, 0.15, 0.1), 1.08, 0.05, gold, rot=(1.5708, 0, 0))
    for i in range(8):
        a = i * math.pi / 4
        k.cylinder((1.08 * math.cos(a), 0.15, 0.1 + 1.08 * math.sin(a)), 0.11, 0.1, lacquer, rot=(1.5708, 0, 0))
    for x in (-0.22, 0.22):
        p = k.on_face(face, x, 0.72, lift=0.01)
        k.front_only(k.spike(p, (p.x * 1.8, p.y, p.z + 0.3), 0.06, gold))
    for x, z in ((-0.35, -1.02), (0.0, -1.14), (0.35, -1.02)):
        k.ellipsoid((x, -0.1, z), (0.09, 0.09, 0.13), water)
    k.cord_holes(face, lacquer)
    k.cord(face, lacquer)
    return {'kind': 'mask', 'size': 0.88, 'front_az': -16}
