"""Okinoir: Kokushiki-jo (Noh "Okina", the black old man of the seed-sowing Sanbaso). Black
lacquered face with a separately carved jaw tied on by cords, white tufted brows and beard,
hollow crescent eyes; a string of gold bells. Quiet and uncanny rather than fierce. Mask body;
grass/ground."""
import math

NORMAL = {'face': (0.20, 0.13, 0.10), 'lacquer': (0.10, 0.04, 0.03), 'tuft': (0.92, 0.90, 0.84),
          'hollow': (0.02, 0.02, 0.02), 'bell': (0.90, 0.70, 0.20), 'cord': (0.75, 0.12, 0.10),
          'leaf': (0.30, 0.62, 0.22)}
SHINY = {**NORMAL, 'face': (0.10, 0.24, 0.14), 'bell': (0.80, 0.82, 0.88), 'cord': (0.20, 0.30, 0.75)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.6, weathered=0.25)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    tuft = k.toon('tuft', c['tuft'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    bell = k.toon('bell', c['bell'], two_tone=True)
    cord = k.toon('cord', c['cord'], two_tone=True)
    leaf = k.toon('leaf', c['leaf'], two_tone=True)
    k.set_light((-0.75, -0.6, 0.1))

    face = k.mask_shell(face_m, lacquer, width=0.78, depth=0.44, height=0.78)
    # Smiling crescent eye holes that show nothing behind them.
    for x in (-0.3, 0.3):
        p = k.on_face(face, x, 0.18, lift=0.005)
        k.front_only(k.ellipsoid(p, (0.22, 0.03, 0.09), bell, rot=(0, k.math.radians(-12 if x < 0 else 12), 0)))
        k.hole(face, x, 0.18, (0.17, 0.05), backing=hollow)
    k.bump(face, 0, -0.05, (0.13, 0.12, 0.18), face_m, lift=0.02)
    k.wrinkles(face, face_m, [(-0.4, -0.15, 0.05, 0.16, -25), (0.4, -0.15, 0.05, 0.16, 25),
                              (-0.3, 0.32, 0.12, 0.03, 10), (0.3, 0.32, 0.12, 0.03, -10)])
    # Pom-pom brows.
    for x in (-0.3, 0.3):
        for dx, dz in ((-0.09, 0.0), (0.09, 0.02), (0.0, 0.09)):
            p = k.on_face(face, x + dx, 0.45 + dz, lift=0.06)
            k.front_only(k.ellipsoid(p, (0.11, 0.09, 0.1), tuft))
    # The separately carved jaw, hanging a little below on cords: the mask's signature.
    before = k.snapshot()
    jaw = k.mask_shell(face_m, lacquer, width=0.5, depth=0.36, height=0.3)
    k.hole(jaw, 0, 0.12, (0.32, 0.06), backing=hollow)
    for x, z in ((-0.15, -0.18), (0.0, -0.24), (0.15, -0.18)):
        p = k.on_face(jaw, x, z, lift=0.05)
        k.front_only(k.ellipsoid(p, (0.12, 0.1, 0.13), tuft))
    k.transform(k.since(before), offset=(0, -0.02, -0.92))
    for x in (-0.4, 0.4):
        k.rod((x, -0.12, -0.55), (x * 0.9, -0.1, -0.8), 0.025, cord)
    # Bell rattle and a sprouting leaf: the sowing dance.
    for i in range(5):
        a = math.radians(-60 + i * 30)
        k.ellipsoid((0.95 + 0.18 * math.sin(a), -0.05, 0.55 + 0.18 * math.cos(a)), (0.08, 0.08, 0.08), bell)
    k.rod((0.95, -0.05, 0.4), (0.95, -0.05, 0.05), 0.03, cord)
    for side in (-1, 1):
        k.ellipsoid((-0.75 + side * 0.08, -0.05, 0.75), (0.1, 0.04, 0.2), leaf, rot=(0, math.radians(side * 30), 0))
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.88, 'front_az': -18}
