"""Mandaring: Mandalumb's second stage. The disc has grown a second ring of sixteen petals and an
outer ring of gold beads, and it has begun to rise toward upright (docs/research/mask-designs.md,
the Mandalumb line). Layout only, no deity: the centre is still the creature's own face, now
with eyes half open. Mask (disc); normal/ground."""
import math

NORMAL = {'sand': (0.86, 0.78, 0.58), 'blue': (0.15, 0.35, 0.80), 'white': (0.96, 0.96, 0.94),
          'red': (0.82, 0.16, 0.14), 'green': (0.18, 0.58, 0.28), 'yellow': (0.95, 0.80, 0.18),
          'face': (0.88, 0.32, 0.22), 'line': (0.15, 0.06, 0.05), 'gold': (0.92, 0.72, 0.24)}
SHINY = {**NORMAL, 'blue': (0.92, 0.80, 0.30), 'red': (0.95, 0.92, 0.80), 'green': (0.90, 0.75, 0.25),
         'sand': (0.98, 0.95, 0.88)}
TILT = 74


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
    k.set_light((-0.7, -0.6, 0.4))

    e = k.Euler((math.radians(TILT), 0, 0))
    center, normal = k.mandala_disc((0, 0, 0.5), 1.15, [sand, green, red, white, blue, green], yellow,
                                    [blue, white, red, yellow], tilt=TILT)
    # The back of the disc: concentric coloured rings, so the back view is not a plain oval.
    for rr, m in ((1.15 * 0.92, red), (1.15 * 0.7, blue), (1.15 * 0.48, yellow), (1.15 * 0.26, white)):
        k.torus(center - normal * 0.06, rr, 0.05 * 1.15, m, rot=(math.radians(TILT), 0, 0))
    for i in range(16):
        a = 2 * math.pi * i / 16 + math.pi / 16
        v = k.Vector((0.68 * math.cos(a), 0.68 * math.sin(a), 0))
        v.rotate(e)
        k.ellipsoid(center + v + normal * 0.09, (0.1, 0.05, 0.03), red if i % 2 else white, rot=(e.x, e.y, a))
    for i in range(24):
        a = 2 * math.pi * i / 24
        v = k.Vector((1.2 * math.cos(a), 1.2 * math.sin(a), 0))
        v.rotate(e)
        k.ellipsoid(center + v, (0.05, 0.05, 0.05), gold, segments=12)
    hc = center + normal * 0.22 + k.Vector((0, -0.05, 0.1))
    hr = (0.3, 0.26, 0.3)
    k.ellipsoid(hc, hr, face_m)
    for side in (-1, 1):
        a = k.head_point(hc, hr, side * 0.12, hc.z + 0.05, 0.01)
        k.ellipsoid(a, (0.06, 0.02, 0.025), line)
        k.ellipsoid(k.head_point(hc, hr, side * 0.12, hc.z + 0.09, 0.01), (0.07, 0.015, 0.012), line)
    for i in range(5):
        x = (i - 2) / 2 * 0.12
        k.ellipsoid(k.head_point(hc, hr, x, hc.z - 0.1 + 0.04 * (x / 0.12) ** 2, -0.005), (0.035, 0.02, 0.03), line)
    return {'kind': 'mask', 'size': 0.88, 'front_az': -10, 'front_el': 12, 'squash': (1.05, 1.05, 0.95)}
