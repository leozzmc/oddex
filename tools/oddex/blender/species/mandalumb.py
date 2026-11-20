"""Mandalumb: a spinning round mandala creature, the first stage of a line that will grow from a
simple circle into a full mandala (Rustboro batch, docs/research/mask-designs.md). Layout only:
rings, eight petals, four gates in the five colours, and the creature's own small laughing face
in the centre, never a deity. Ground from Tibetan sand mandalas. Fusion: Shojobob's red laughing
face, shrunk; Kamorai's drum ring and its eight drums turned into the petal ring.
Mask (disc); normal/ground."""
import math

NORMAL = {'sand': (0.86, 0.78, 0.58), 'blue': (0.15, 0.35, 0.80), 'white': (0.96, 0.96, 0.94),
          'red': (0.82, 0.16, 0.14), 'green': (0.18, 0.58, 0.28), 'yellow': (0.95, 0.80, 0.18),
          'face': (0.88, 0.32, 0.22), 'line': (0.15, 0.06, 0.05), 'gold': (0.92, 0.72, 0.24)}
SHINY = {**NORMAL, 'blue': (0.92, 0.80, 0.30), 'red': (0.95, 0.92, 0.80), 'green': (0.90, 0.75, 0.25),
         'sand': (0.98, 0.95, 0.88)}


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

    center, normal = k.mandala_disc((0, 0, 0.35), 1.0, [sand, red, white, blue, green], yellow,
                                    [blue, white, red, yellow], tilt=62, spin=0)
    # The back of the disc: concentric coloured rings, so the back view is not a plain oval.
    for rr, m in ((1.0 * 0.92, red), (1.0 * 0.7, blue), (1.0 * 0.48, yellow), (1.0 * 0.26, white)):
        k.torus(center - normal * 0.06, rr, 0.05 * 1.0, m, rot=(math.radians(62), 0, 0))
    # Small drums on the petal ring (Kamorai's drum ring).
    for i in range(8):
        a = 2 * math.pi * i / 8 + math.pi / 8
        v = k.Vector((0.62 * math.cos(a), 0.62 * math.sin(a), 0))
        v.rotate(k.Euler((math.radians(62), 0, 0)))
        k.cylinder(center + v + normal * 0.08, 0.07, 0.08, gold, rot=(math.radians(62), 0, 0))
    # The laughing face rising from the centre.
    hc = center + normal * 0.2 + k.Vector((0, -0.05, 0.18))
    hr = (0.3, 0.26, 0.3)
    k.ellipsoid(hc, hr, face_m)
    for side in (-1, 1):
        x0 = side * 0.12
        a = k.head_point(hc, hr, x0 - 0.06, hc.z + 0.04, 0.01)
        t = k.head_point(hc, hr, x0, hc.z + 0.09, 0.01)
        b = k.head_point(hc, hr, x0 + 0.06, hc.z + 0.04, 0.01)
        k.rod(a, t, 0.018, line)
        k.rod(t, b, 0.018, line)
    for i in range(5):
        x = (i - 2) / 2 * 0.12
        k.ellipsoid(k.head_point(hc, hr, x, hc.z - 0.1 + 0.04 * (x / 0.12) ** 2, -0.005), (0.035, 0.02, 0.03), line)
    k.ellipsoid(k.head_point(hc, hr, 0, hc.z - 0.1, 0.0), (0.09, 0.02, 0.035), line)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -12, 'front_el': 14, 'squash': (1.06, 1.06, 0.94)}
