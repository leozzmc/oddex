"""Bekurama: O-beshimi (Noh "Kurama Tengu", the great tengu who taught swordsmanship). Red face,
glaring gold eyes, lips pressed so hard they bulge, a knitted brow; a yamabushi cap and a leaf
fan. Mask body; grass/steel."""
import math

NORMAL = {'face': (0.62, 0.14, 0.08), 'lacquer': (0.14, 0.05, 0.04), 'gold': (0.92, 0.72, 0.20),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.16, 0.03, 0.03), 'cap': (0.08, 0.08, 0.10),
          'fan': (0.24, 0.55, 0.20), 'blade': (0.80, 0.82, 0.86)}
SHINY = {**NORMAL, 'face': (0.18, 0.32, 0.18), 'fan': (0.85, 0.40, 0.12)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.35, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    cap = k.toon('cap', c['cap'], two_tone=True)
    fan = k.toon('fan', c['fan'], two_tone=True)
    blade = k.toon('blade', c['blade'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.2))

    face = k.mask_shell(face_m, lacquer, width=0.74, depth=0.48, height=0.86)
    k.brows(face, 0.3, 0.45, 0.3, face_m, frown=36, thick=0.14)
    k.glare_eyes(face, 0.31, 0.2, 0.19, gold, pupil, socket)
    k.bump(face, 0, -0.05, (0.15, 0.15, 0.2), face_m, lift=0.03)
    # Beshimi: the lips clamped shut, bulging, with the corners pulled down.
    m = k.on_face(face, 0, -0.45, lift=0.0)
    k.front_only(k.ellipsoid((m.x, m.y - 0.06, m.z + 0.04), (0.36, 0.1, 0.07), face_m))
    k.front_only(k.ellipsoid((m.x, m.y - 0.05, m.z - 0.07), (0.32, 0.09, 0.07), face_m))
    k.front_only(k.ellipsoid((m.x, m.y - 0.09, m.z - 0.015), (0.34, 0.03, 0.012), pupil))
    k.wrinkles(face, face_m, [(-0.4, -0.3, 0.05, 0.16, -30), (0.4, -0.3, 0.05, 0.16, 30)])
    # Tokin cap on the brow, a leaf fan and a sword hilt behind.
    p = k.on_face(face, 0, 0.78, lift=0.0)
    k.cylinder((p.x, p.y + 0.05, p.z + 0.08), 0.16, 0.18, cap)
    for i in range(7):
        a = math.radians(-50 + i * 17)
        k.ellipsoid((0.9 + 0.35 * math.sin(a), 0.2, 0.3 + 0.35 * math.cos(a)), (0.1, 0.03, 0.26), fan,
                    rot=(0, -a, 0))
    k.rod((0.9, 0.2, 0.25), (0.9, 0.2, -0.3), 0.04, cap)
    k.rod((-0.85, 0.25, -0.7), (-0.7, 0.25, 0.9), 0.04, blade)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.88, 'front_az': -18}
