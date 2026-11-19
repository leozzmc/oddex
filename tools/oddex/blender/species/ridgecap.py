"""Ridgecap: the water starter, one of the mountain-trail trio (docs/research/friends-designs.md).
Head only, after the hitouban (a head that leaves its body at night and flies on its ears): a
big head whose red cap has grown into the skull, its crown risen into a crest; thin gold round
glasses blown up and filled with water so the eyes swim huge behind them; the ears spread into
finned wings; meltwater drips from the chin. Water/flying.

Face, cap, hair and glasses are tagged 'head' (a private likeness replaces them); the cap crest
is tagged 'front' so it rises out of either face."""
import math

NORMAL = {'skin': (0.85, 0.72, 0.58), 'hair': (0.08, 0.07, 0.07), 'cap': (0.86, 0.12, 0.20),
          'rim': (0.86, 0.68, 0.30), 'lens': (0.50, 0.76, 0.92), 'white': (0.97, 0.96, 0.92),
          'iris': (0.12, 0.08, 0.06), 'mouth': (0.30, 0.08, 0.10), 'tooth': (0.96, 0.93, 0.84),
          'fin': (0.25, 0.55, 0.85), 'rib': (0.10, 0.25, 0.50), 'water': (0.30, 0.62, 0.95)}
SHINY = {**NORMAL, 'cap': (0.15, 0.55, 0.30), 'rim': (0.75, 0.78, 0.82), 'fin': (0.90, 0.55, 0.20),
         'rib': (0.50, 0.22, 0.08), 'lens': (0.55, 0.90, 0.85), 'water': (0.40, 0.85, 0.80)}


def build(k, c):
    skin = k.toon('skin', c['skin'], steps=k.HORROR_STEPS)
    hair = k.toon('hair', c['hair'], two_tone=True)
    cap = k.toon('cap', c['cap'], glint=0.2)
    rim = k.toon('rim', c['rim'], two_tone=True)
    lens = k.toon('lens', c['lens'], glint=0.4, two_tone=True)
    white = k.toon('white', c['white'], two_tone=True)
    iris = k.flat('iris', c['iris'])
    mouth = k.flat('mouth', c['mouth'])
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    fin = k.toon('fin', c['fin'], two_tone=True)
    rib = k.toon('rib', c['rib'], two_tone=True)
    water = k.toon('water', c['water'], two_tone=True)
    k.set_light((-0.7, -0.6, -0.12))   # lit from below

    hc, hr = (0, 0, 1.0), (0.62, 0.52, 0.64)

    # Ear-wings and dripping meltwater (behind the head).
    for side in (-1, 1):
        k.wing((side * 0.55, 0.15, 1.0), side, 1.05, fin, rib, ribs=5, sweep=(-30, 60), droop=0.2, depth=0.25)
    for x, z, s in ((-0.12, 0.2, 0.06), (0.1, 0.05, 0.05), (0.0, -0.15, 0.045), (0.16, -0.3, 0.035)):
        k.ellipsoid((x, -0.05, z), (s, s, s * 1.4), water)
        k.spike((x, -0.05, z + s * 1.2), (x, -0.05, z + s * 2.6), s * 0.6, water)

    # The head.
    before = k.snapshot()
    k.ellipsoid(hc, hr, skin, name='head')
    for side in (-1, 1):
        k.ellipsoid((side * 0.5, 0.15, 1.0), (0.14, 0.32, 0.2), hair)   # short sides under the cap
    k.ellipsoid((0, 0.06, 1.24), (0.66, 0.57, 0.44), cap)
    k.ellipsoid((0, -0.62, 1.3), (0.5, 0.36, 0.045), cap, rot=(math.radians(-10), 0, 0))   # visor
    for side in (-1, 1):
        p = k.head_point(hc, hr, side * 0.25, 0.96, lift=0.06)
        k.cylinder(p, 0.25, 0.03, lens, rot=(math.pi / 2, 0, 0))
        k.torus((p.x, p.y - 0.01, p.z), 0.26, 0.018, rim, rot=(math.pi / 2, 0, 0))
        k.ellipsoid((p.x, p.y - 0.03, p.z), (0.2, 0.02, 0.17), white)
        k.ellipsoid((p.x + side * 0.025, p.y - 0.045, p.z - 0.02), (0.1, 0.015, 0.1), iris)
        k.ellipsoid((p.x - 0.04, p.y - 0.06, p.z + 0.04), (0.03, 0.01, 0.03), white)
        for bx, bz in ((0.14, -0.12), (-0.15, 0.1)):   # bubbles: the lenses are full of water
            k.ellipsoid((p.x + bx, p.y - 0.04, p.z + bz), (0.026, 0.018, 0.026), white)
        k.rod((side * 0.5, p.y, 1.0), (side * 0.6, 0.15, 1.02), 0.016, rim)
    b = k.head_point(hc, hr, 0, 1.02, lift=0.09)
    k.rod((-0.035, b.y, b.z), (0.035, b.y, b.z), 0.016, rim)
    k.ellipsoid(k.head_point(hc, hr, 0, 0.7, lift=0.0), (0.06, 0.05, 0.07), skin)
    for i in range(9):
        x = (i - 4) / 4 * 0.2
        z = 0.52 + 0.07 * (x / 0.2) ** 2
        k.ellipsoid(k.head_point(hc, hr, x, z, lift=-0.01), (0.035, 0.025, 0.045), mouth)
        if 1 <= i <= 7:
            k.ellipsoid(k.head_point(hc, hr, x, z + 0.012, lift=0.007), (0.02, 0.018, 0.024), tooth)
    head = k.tag(k.since(before), 'head')

    # The cap's crown risen into a crest.
    before = k.snapshot()
    for y, h in ((-0.3, 0.26), (-0.05, 0.4), (0.2, 0.34), (0.42, 0.2)):
        k.spike((0, y, 1.55), (0, y + 0.07, 1.55 + h), 0.13, cap)
    front = k.tag(k.since(before), 'front')
    k.transform(head + front, offset=(-0.0, -0.0, -0.25), scale=1.25)   # the head is the whole body
    return {'kind': 'head', 'size': 0.84, 'front_az': -10, 'side_az': -70, 'squash': (1.06, 1.0, 0.97)}
