"""Trekkeye: the fire starter, one of the mountain-trail trio (docs/research/friends-designs.md).
Head only, after the wanyudo (a head in a burning ox-cart wheel): a big head with wild black
hair smouldering at the tips and huge blank round sunglasses, set in front of an iron wheel
ringed with flame whose spokes run out into spider legs. An action camera has grown onto the
brow as a third eye with a burning recording light. Fire/steel.

The face, hair and sunglasses are tagged 'head' (a private likeness replaces them); the brow
camera is tagged 'front' so it stays on top of either face."""
import math

NORMAL = {'skin': (0.84, 0.72, 0.58), 'hair': (0.07, 0.06, 0.07), 'lens': (0.20, 0.25, 0.23),
          'rim': (0.82, 0.80, 0.74), 'iron': (0.22, 0.21, 0.24), 'camera': (0.11, 0.11, 0.12),
          'white': (0.95, 0.93, 0.86), 'pupil': (0.03, 0.02, 0.02), 'mouth': (0.32, 0.12, 0.12),
          'ember': (1.0, 0.42, 0.06), 'flame': (1.0, 0.86, 0.32)}
SHINY = {**NORMAL, 'hair': (0.86, 0.86, 0.82), 'lens': (0.85, 0.66, 0.20), 'iron': (0.55, 0.40, 0.22),
         'ember': (0.25, 0.55, 1.0), 'flame': (0.78, 0.94, 1.0)}


def build(k, c):
    skin = k.toon('skin', c['skin'], steps=k.HORROR_STEPS)
    hair = k.toon('hair', c['hair'], two_tone=True)
    lens = k.toon('lens', c['lens'], two_tone=True)
    rim = k.toon('rim', c['rim'], two_tone=True)
    iron = k.toon('iron', c['iron'], steps=k.HORROR_STEPS, glint=0.4, weathered=0.3)
    camera = k.toon('camera', c['camera'], two_tone=True)
    white = k.toon('white', c['white'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    mouth = k.flat('mouth', c['mouth'])
    ember = k.flat('ember', c['ember'])
    flame = k.flat('flame', c['flame'])
    k.set_light((-0.75, -0.6, -0.12))   # lit from below

    hc, hr = (0, 0, 1.3), (0.62, 0.5, 0.6)

    # The burning wheel behind the head, and its spokes running out into spider legs.
    wc = k.Vector((0, 0.38, 1.3))
    k.torus(wc, 1.0, 0.09, iron, rot=(math.pi / 2, 0, 0))
    k.cylinder(wc, 0.2, 0.16, iron, rot=(math.pi / 2, 0, 0))
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4
        k.rod(wc, wc + k.Vector((math.cos(a), 0, math.sin(a))) * 0.95, 0.04, iron)
    for i in range(14):
        a = i * 2 * math.pi / 14 + 0.2
        out = k.Vector((math.cos(a), 0, math.sin(a)))
        base = wc + out * 1.02
        k.spike(base, base + out * 0.32 + k.Vector((0, 0, 0.12)), 0.12, ember)
        k.spike(base + out * 0.05, base + out * 0.2 + k.Vector((0, -0.02, 0.08)), 0.06, flame)
    for side in (-1, 1):
        for j, ang in enumerate((-50, 0, 50)):
            a = math.radians(ang)
            r = math.radians(-35 - j * 12)
            root = wc + k.Vector((side * 0.75 * math.cos(r), 0, 0.75 * math.sin(r)))
            k.spider_leg(root, (side * math.cos(a), math.sin(a)), 1.25, iron, ember, radius=0.05, lift=0.35)

    # The head: everything below is replaced by a private likeness.
    before = k.snapshot()
    k.ellipsoid(hc, hr, skin, name='head')
    for side in (-1, 1):
        k.ellipsoid((side * 0.62, 0.02, 1.25), (0.07, 0.05, 0.12), skin)
    k.ellipsoid((0, 0.07, 1.48), (0.66, 0.55, 0.46), hair)
    locks = [(-0.55, 0.0, 1.6, -1.0, 0.0, 0.35), (0.55, 0.05, 1.6, 1.0, 0.1, 0.3), (-0.3, -0.1, 1.85, -0.4, 0.0, 0.45),
             (0.28, -0.05, 1.88, 0.35, 0.1, 0.5), (0.0, 0.1, 1.95, 0.05, 0.2, 0.5), (-0.62, 0.25, 1.4, -1.0, 0.3, -0.1),
             (0.62, 0.25, 1.4, 1.0, 0.35, -0.05), (-0.35, 0.45, 1.75, -0.5, 0.8, 0.4), (0.35, 0.45, 1.75, 0.6, 0.8, 0.35)]
    for x, y, z, dx, dy, dz in locks:
        tip = (x + dx * 0.26, y + dy * 0.26, z + dz * 0.4)
        k.spike((x, y, z), tip, 0.14, hair)
        mid = (x + dx * 0.17, y + dy * 0.17, z + dz * 0.26)
        k.spike(mid, (tip[0] + dx * 0.07, tip[1] + dy * 0.07, tip[2] + dz * 0.1 + 0.04), 0.06, ember)
    for x in (-0.3, -0.1, 0.1, 0.3):   # fringe over the brow
        p = k.head_point(hc, hr, x, 1.56, lift=0.02)
        k.spike((p.x, p.y + 0.05, p.z + 0.08), (p.x + 0.04, p.y - 0.06, p.z - 0.17), 0.065, hair)
    for side in (-1, 1):
        p = k.head_point(hc, hr, side * 0.25, 1.3, lift=0.05)
        k.ellipsoid(k.head_point(hc, hr, side * 0.25, 1.1, lift=-0.01), (0.17, 0.03, 0.05), mouth)   # sunken shadow
        k.cylinder(p, 0.21, 0.035, lens, rot=(math.pi / 2, 0, 0))
        k.ellipsoid((p.x - 0.08, p.y - 0.025, p.z + 0.08), (0.04, 0.01, 0.028), white)   # cold reflection
        k.torus((p.x, p.y - 0.01, p.z), 0.22, 0.02, rim, rot=(math.pi / 2, 0, 0))
        k.rod((side * 0.46, p.y, 1.33), (side * 0.6, 0.15, 1.36), 0.016, rim)
    b = k.head_point(hc, hr, 0, 1.36, lift=0.08)
    k.rod((-0.05, b.y, b.z), (0.05, b.y, b.z), 0.016, rim)
    k.ellipsoid(k.head_point(hc, hr, 0, 1.08, lift=0.0), (0.06, 0.05, 0.07), skin)
    k.ellipsoid(k.head_point(hc, hr, 0, 0.92, lift=-0.01), (0.1, 0.025, 0.02), mouth)   # deadpan, too small
    head = k.tag(k.since(before), 'head')

    # The brow camera: a third eye whose recording light has caught fire.
    before = k.snapshot()
    p = k.head_point(hc, hr, 0.0, 1.62, lift=0.0)
    k.ellipsoid((p.x, p.y - 0.05, p.z), (0.12, 0.07, 0.09), camera)
    k.cylinder((p.x, p.y - 0.13, p.z), 0.075, 0.08, camera, rot=(math.pi / 2, 0, 0))
    k.ellipsoid((p.x, p.y - 0.17, p.z), (0.06, 0.025, 0.06), white)
    k.ellipsoid((p.x, p.y - 0.195, p.z), (0.032, 0.01, 0.032), pupil)
    k.spike((p.x + 0.09, p.y - 0.1, p.z + 0.06), (p.x + 0.11, p.y - 0.1, p.z + 0.25), 0.05, ember)
    k.spike((p.x + 0.09, p.y - 0.11, p.z + 0.07), (p.x + 0.1, p.y - 0.11, p.z + 0.17), 0.025, flame)
    front = k.tag(k.since(before), 'front')
    k.transform(head + front, offset=(-0.0, -0.0, -0.39), scale=1.3)   # the head is the whole body
    return {'kind': 'head', 'size': 0.84, 'front_az': -10, 'side_az': -70, 'squash': (1.04, 1.04, 0.96)}
