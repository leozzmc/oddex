"""Mandaloka: Mandalumb's third stage, the full mandala: the disc stands upright on a mound of
coloured sand, its rings, two petal rings, four gates and bead ring complete, enclosed by the
outer circle of flame that protects a mandala (docs/research/mask-designs.md, the Mandalumb
line). Layout only, no deity: the centre is the creature's own calm, open-eyed face.
Mask (upright disc); ground/fire."""
import math

NORMAL = {'sand': (0.86, 0.78, 0.58), 'blue': (0.15, 0.35, 0.80), 'white': (0.96, 0.96, 0.94),
          'red': (0.82, 0.16, 0.14), 'green': (0.18, 0.58, 0.28), 'yellow': (0.95, 0.80, 0.18),
          'face': (0.88, 0.32, 0.22), 'line': (0.15, 0.06, 0.05), 'gold': (0.92, 0.72, 0.24),
          'flame': (0.95, 0.35, 0.08), 'flame2': (1.0, 0.78, 0.25)}
SHINY = {**NORMAL, 'blue': (0.92, 0.80, 0.30), 'red': (0.95, 0.92, 0.80), 'green': (0.90, 0.75, 0.25),
         'sand': (0.98, 0.95, 0.88), 'flame': (0.25, 0.45, 0.95), 'flame2': (0.75, 0.90, 1.0)}


def build(k, c):
    sand = k.toon('sand', c['sand'], two_tone=True)
    blue = k.toon('blue', c['blue'], two_tone=True)
    white = k.toon('white', c['white'], two_tone=True)
    red = k.toon('red', c['red'], two_tone=True)
    green = k.toon('green', c['green'], two_tone=True)
    yellow = k.toon('yellow', c['yellow'], two_tone=True)
    face_m = k.toon('face', c['face'], glint=0.3)
    line = k.flat('line', c['line'])
    gold = k.toon('gold', c['gold'], glint=0.4, two_tone=True)
    flame = k.flat('flame', c['flame'])
    flame2 = k.flat('flame2', c['flame2'])
    k.set_light((-0.7, -0.6, 0.35))

    k.ellipsoid((0, 0.1, -1.05), (0.9, 0.5, 0.28), sand)   # mound of coloured sand
    for x, m in ((-0.45, blue), (0.0, red), (0.45, green)):
        k.ellipsoid((x, -0.3, -0.98), (0.2, 0.1, 0.08), m)
    tilt = 90
    e = k.Euler((math.radians(tilt), 0, 0))
    center, normal = k.mandala_disc((0, 0, 0.25), 1.05, [sand, green, red, white, blue, green], yellow,
                                    [blue, white, red, yellow], tilt=tilt)
    for i in range(16):
        a = 2 * math.pi * i / 16 + math.pi / 16
        v = k.Vector((0.62 * math.cos(a), 0.62 * math.sin(a), 0))
        v.rotate(e)
        k.ellipsoid(center + v + normal * 0.09, (0.09, 0.05, 0.03), red if i % 2 else white, rot=(e.x, e.y, a))
    for i in range(24):
        a = 2 * math.pi * i / 24
        v = k.Vector((1.12 * math.cos(a), 1.12 * math.sin(a), 0))
        v.rotate(e)
        k.ellipsoid(center + v + normal * 0.03, (0.05, 0.05, 0.05), gold, segments=12)
    k.flame_halo((0, 0.05, 0.25), 1.2, flame, inner=flame2, licks=20, length=0.32)
    hc = center + normal * 0.25
    hr = (0.28, 0.24, 0.28)
    k.ellipsoid(hc, hr, face_m)
    for side in (-1, 1):
        e1 = k.head_point(hc, hr, side * 0.11, hc.z + 0.05, 0.02)
        k.ellipsoid(e1, (0.05, 0.02, 0.05), white)
        k.ellipsoid((e1.x, e1.y - 0.02, e1.z), (0.025, 0.01, 0.03), line)
        k.ellipsoid(k.head_point(hc, hr, side * 0.11, hc.z + 0.12, 0.01), (0.07, 0.015, 0.012), line)
    k.ellipsoid(k.head_point(hc, hr, 0, hc.z - 0.11, 0.0), (0.09, 0.02, 0.02), line)
    return {'kind': 'mask', 'size': 0.9, 'front_az': -10, 'front_el': 6, 'squash': (1.04, 1.04, 0.96)}
