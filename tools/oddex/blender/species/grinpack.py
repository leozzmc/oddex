"""Grinpack: the grass starter, one of the mountain-trail trio (docs/research/friends-designs.md).
Head only, after the tsurube-otoshi (a huge head that drops out of the trees onto passers-by):
a big head under a blunt black fringe, eyes squeezed into arcs above a grin that runs from ear
to ear with two rows of far too bright teeth. It hangs from a vine on a branch, leaves sprouting
from its crown, long spider legs climbing the vine and dangling below. Grass/dark.

Face, hair and teeth are tagged 'head' (a private likeness replaces them); the crown leaves and
the vine knot are tagged 'front'."""
import math

NORMAL = {'skin': (0.86, 0.73, 0.58), 'hair': (0.07, 0.06, 0.07), 'gum': (0.62, 0.16, 0.20),
          'tooth': (1.0, 0.99, 0.94), 'throat': (0.18, 0.04, 0.06), 'line': (0.10, 0.05, 0.05),
          'vine': (0.30, 0.42, 0.16), 'bark': (0.30, 0.20, 0.12), 'leaf': (0.40, 0.72, 0.24),
          'leg': (0.16, 0.20, 0.10)}
SHINY = {**NORMAL, 'hair': (0.55, 0.30, 0.12), 'vine': (0.55, 0.35, 0.15), 'leaf': (0.92, 0.36, 0.14),
         'leg': (0.35, 0.16, 0.10)}


def build(k, c):
    skin = k.toon('skin', c['skin'], steps=k.HORROR_STEPS)
    hair = k.toon('hair', c['hair'], two_tone=True)
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], glint=0.8, two_tone=True)
    throat = k.flat('throat', c['throat'])
    line = k.flat('line', c['line'])
    vine = k.toon('vine', c['vine'], two_tone=True)
    bark = k.toon('bark', c['bark'], two_tone=True)
    leaf = k.toon('leaf', c['leaf'], two_tone=True)
    leg = k.toon('leg', c['leg'], steps=k.HORROR_STEPS)
    k.set_light((-0.7, -0.6, -0.12))   # lit from below

    hc, hr = (0, 0, 1.0), (0.66, 0.52, 0.62)

    # Branch, vine and the spider legs (behind the head).
    k.rod((-0.9, 0.2, 2.45), (0.9, 0.25, 2.55), 0.08, bark)
    for x, ang in ((-0.6, 0.6), (0.2, 2.0), (0.75, 4.0)):
        k.ellipsoid((x, 0.15, 2.62), (0.16, 0.06, 0.07), leaf, rot=(0, math.radians(25), ang))
    k.rod((0.0, 0.1, 1.55), (0.05, 0.22, 2.5), 0.05, vine)
    for side in (-1, 1):
        # Upper pair climbing the vine: root at the temple, knee flung out, tip hooked on the branch.
        root = k.Vector((side * 0.5, 0.25, 1.25))
        knee = k.Vector((side * 1.0, 0.3, 1.95))
        tip = k.Vector((side * 0.55, 0.22, 2.5))
        k.rod(root, knee, 0.04, leg)
        k.ellipsoid(knee, (0.06, 0.06, 0.06), leg)
        k.spike(knee, tip, 0.035, leg)
    k.spider_legs((0, 0.25, 0.75), 2, 1.0, leg, radius=0.04, spread=(-40, 40), lift=0.25, ground=0.0, ring=0.35)

    # The head.
    before = k.snapshot()
    k.ellipsoid(hc, hr, skin, name='head')
    for side in (-1, 1):
        k.ellipsoid((side * 0.66, 0.02, 0.97), (0.07, 0.05, 0.12), skin)
    k.ellipsoid((0, 0.08, 1.22), (0.7, 0.57, 0.45), hair)
    f = k.head_point(hc, hr, 0, 1.3, lift=0.02)
    k.ellipsoid((0, f.y + 0.05, 1.33), (0.64, 0.11, 0.12), hair)   # dead-straight fringe
    for side in (-1, 1):
        x0 = side * 0.26
        a = k.head_point(hc, hr, x0 - 0.1, 1.08, lift=0.01)
        top = k.head_point(hc, hr, x0, 1.15, lift=0.01)
        b = k.head_point(hc, hr, x0 + 0.1, 1.08, lift=0.01)
        k.rod(a, top, 0.024, line)
        k.rod(top, b, 0.024, line)
        k.ellipsoid(k.head_point(hc, hr, side * 0.4, 0.86, lift=0.0), (0.1, 0.04, 0.06), gum)   # flushed cheeks

    def smile_z(x):
        return 0.7 + 0.34 * (x / 0.52) ** 2

    for i in range(-10, 11):
        x = i / 10 * 0.52
        p = k.head_point(hc, hr, x, smile_z(x), lift=-0.02)
        k.ellipsoid(p, (0.06, 0.035, 0.1 - 0.05 * abs(x) / 0.52), throat)
    for row, n, dz in (('upper', 13, 0.04), ('lower', 11, -0.05)):
        for i in range(n):
            x = (i - (n - 1) / 2) / ((n - 1) / 2) * 0.46
            z = smile_z(x) + dz * (1 - 0.4 * abs(x) / 0.46)
            g = k.head_point(hc, hr, x, z + (0.04 if row == 'upper' else -0.04), lift=0.0)
            k.ellipsoid(g, (0.05, 0.025, 0.025), gum)
            t = k.head_point(hc, hr, x, z, lift=0.012)
            k.ellipsoid(t, (0.034, 0.025, 0.04), tooth)
    head = k.tag(k.since(before), 'head')

    # Leaves sprouting from the crown, and the knot where the vine grows into the scalp.
    before = k.snapshot()
    k.ellipsoid((0.02, 0.1, 1.62), (0.1, 0.1, 0.08), vine)
    for ang, tilt in ((0.3, 30), (2.2, 40), (3.6, 35), (5.2, 30)):
        q = k.Vector((0.25 * math.cos(ang), 0.1 + 0.15 * math.sin(ang), 1.66))
        k.ellipsoid(q, (0.16, 0.05, 0.07), leaf, rot=(0, math.radians(tilt), ang))
    front = k.tag(k.since(before), 'front')
    k.transform(head + front, offset=(-0.0, -0.0, -0.25), scale=1.25)   # the head is the whole body
    return {'kind': 'head', 'size': 0.84, 'front_az': -10, 'side_az': -70, 'squash': (1.0, 1.0, 1.06)}
