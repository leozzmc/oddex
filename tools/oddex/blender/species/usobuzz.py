"""Usobuzz: Usobuki (Kyogen, the pursed-lip mask of small spirits) as the mosquito spirit of
"Ka-zumo" who wants to wrestle sumo: bulging eyes, lips pursed into a long proboscis, thin
legs, a sumo belt. Mask body; bug/fighting."""
import math

NORMAL = {'face': (0.86, 0.78, 0.52), 'lacquer': (0.18, 0.10, 0.05), 'eye': (0.95, 0.88, 0.55),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.30, 0.18, 0.08), 'beak': (0.12, 0.08, 0.06),
          'leg': (0.20, 0.14, 0.10), 'belt': (0.45, 0.20, 0.55)}
SHINY = {**NORMAL, 'face': (0.62, 0.80, 0.52), 'belt': (0.85, 0.62, 0.15)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    beak = k.toon('beak', c['beak'], two_tone=True)
    leg = k.toon('leg', c['leg'], two_tone=True)
    belt = k.toon('belt', c['belt'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.15))

    face = k.mask_shell(face_m, lacquer, width=0.62, depth=0.4, height=0.66)
    k.glare_eyes(face, 0.27, 0.15, 0.19, eye_m, pupil, socket, tilt=-10)
    k.brows(face, 0.27, 0.4, 0.2, face_m, frown=-20, thick=0.08)
    # Pursed lips pushed out into a mosquito's proboscis.
    m = k.on_face(face, 0, -0.3, lift=0.0)
    k.front_only(k.ellipsoid((m.x, m.y - 0.06, m.z), (0.13, 0.12, 0.1), face_m))
    k.front_only(k.spike((m.x, m.y - 0.15, m.z), (m.x + 0.38, m.y - 0.35, m.z - 0.7), 0.07, beak))
    # Six thin legs and a sumo belt under the chin.
    for side in (-1, 1):
        for j, z in enumerate((0.1, -0.15, -0.38)):
            a = (side * 0.58, 0.0, z)
            b = (side * (0.95 + 0.05 * j), -0.05, z - 0.45)
            k.rod(a, b, 0.025, leg)
            k.rod(b, (b[0] + side * 0.12, b[1], b[2] - 0.25), 0.02, leg)
    k.torus((0, 0.0, -0.66), 0.42, 0.07, belt, rot=(0, 0, 0))
    k.ellipsoid((0, -0.3, -0.85), (0.12, 0.05, 0.18), belt)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.82, 'front_az': -22}
