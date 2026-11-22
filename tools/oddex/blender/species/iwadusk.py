"""Iwadusk: Iwadawn's night twin. Mossdeep segment, replaces Lunatone on Tate & Liza's team
(docs/research/mask-designs.md, "Iwadusk 的 Brief", option A). The same great rock door, shut and
blue with night; a crescent-shaped crack runs down it and pale moonlight leaks out, and in the
hollow of the crescent sits the moon rabbit of folklore, lit by it (imagery only, no moon god). The
crescent is its closed, sleeping eye, with a small mouth under it; a shimenawa hangs across the
lintel, and on top sit a stack of moon-viewing dumplings and a sheaf of pampas grass. Silhouette
at 64px: Iwadawn's rock with a crescent instead of the sun disc and the plumes of grass on top.
Mask; rock/psychic."""
import math

NORMAL = {'stone': (0.34, 0.38, 0.52), 'lacquer': (0.10, 0.11, 0.18), 'light': (0.80, 0.92, 1.0),
          'glow': (0.50, 0.72, 0.98), 'rabbit': (0.10, 0.14, 0.34), 'lip': (0.20, 0.22, 0.34),
          'dango': (0.98, 0.98, 0.96), 'stand': (0.60, 0.42, 0.24), 'grass': (0.92, 0.78, 0.36),
          'stalk': (0.56, 0.60, 0.30), 'straw': (0.82, 0.70, 0.40), 'strawdark': (0.55, 0.44, 0.20),
          'paper': (0.97, 0.97, 0.95)}
# Shiny: a red moon.
SHINY = {**NORMAL, 'stone': (0.40, 0.30, 0.34), 'lacquer': (0.16, 0.08, 0.10), 'light': (1.0, 0.80, 0.62),
         'glow': (0.95, 0.40, 0.25), 'rabbit': (0.34, 0.06, 0.08), 'lip': (0.26, 0.16, 0.18)}


def build(k, c):
    stone = k.toon('stone', c['stone'], steps=k.HORROR_STEPS, weathered=0.45)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    light = k.flat('light', c['light'])
    glow = k.flat('glow', c['glow'])
    rabbit = k.flat('rabbit', c['rabbit'])
    lip = k.toon('lip', c['lip'], two_tone=True)
    dango = k.toon('dango', c['dango'], two_tone=True)
    stand = k.toon('stand', c['stand'], two_tone=True)
    grass = k.toon('grass', c['grass'], two_tone=True)
    stalk = k.flat('stalk', c['stalk'])
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.flat('strawdark', c['strawdark'])
    paper = k.flat('paper', c['paper'])
    k.set_light((-0.75, -0.6, 0.2))

    face = k.mask_shell(stone, lacquer, width=0.82, depth=0.5, height=0.95)
    k.wrinkles(face, stone, [(-0.5, -0.3, 0.08, 0.3, 10), (0.55, 0.3, 0.08, 0.3, -12), (0.3, -0.7, 0.14, 0.06, 0)])
    # The crescent crack: thick in the middle, tapering to both horns, a rim of blue glow round it.
    cx, cz, r = 0.12, 0.12, 0.48
    for layer, mat, grow, lift in ((0, glow, 1.35, 0.015), (1, light, 1.0, 0.03)):
        for i in range(19):
            t = i / 18
            a = math.radians(70 + 220 * t)
            w = 0.2 * math.sin(math.pi * t) ** 0.8 + 0.02
            x, z = cx + r * math.cos(a), cz + r * math.sin(a)
            k.front_only(k.ellipsoid(k.on_face(face, x, z, lift=lift), (w * grow, 0.03, w * grow), mat))
    # The moon rabbit, held in the hollow of the crescent and lit by it: body, head, two long ears.
    rx, rz = cx + 0.1, cz - 0.08
    for dx, dz, sx, sz in ((0.0, -0.1, 0.15, 0.17), (-0.05, 0.14, 0.1, 0.1), (-0.11, 0.36, 0.04, 0.15), (0.02, 0.37, 0.04, 0.15)):
        k.front_only(k.ellipsoid(k.on_face(face, rx + dx, rz + dz, lift=0.03), (sx, 0.02, sz), glow))
    # A small sleeping mouth under the crescent.
    m = k.on_face(face, 0.1, -0.62, lift=0.03)
    k.front_only(k.ellipsoid(m, (0.16, 0.06, 0.05), lip))
    k.front_only(k.ellipsoid((m.x, m.y - 0.05, m.z), (0.12, 0.02, 0.014), rabbit))
    # The shimenawa across the lintel.
    k.rope([(-0.98, -0.1, 0.9), (-0.45, -0.3, 1.0), (0.45, -0.3, 1.0), (0.98, -0.1, 0.9)], 0.1, straw, strawdark)
    for x, side in ((-0.95, 1), (0.85, -1)):
        k.shide((x, -0.15, 0.82), 0.45, 0.11, paper, side=side)
    # On top: the moon-viewing dumplings on their stand, and a sheaf of pampas grass.
    k.cylinder((-0.3, 0.0, 1.02), 0.3, 0.08, stand, segments=16)
    for x, z in ((-0.48, 1.16), (-0.3, 1.16), (-0.12, 1.16), (-0.39, 1.33), (-0.21, 1.33), (-0.3, 1.5)):
        k.ellipsoid((x, 0.0, z), (0.105, 0.105, 0.105), dango)
    for i, (dx, lean) in enumerate(((0.0, 0.1), (0.14, 0.32), (0.26, 0.55), (-0.1, -0.1))):
        base = k.Vector((0.42 + dx * 0.3, 0.05, 0.95))
        top = base + k.Vector((lean, 0, 0.75 - 0.05 * i))
        k.rod(base, top, 0.022, stalk)
        k.ellipsoid(top + k.Vector((lean * 0.25, 0, 0.14)), (0.075, 0.06, 0.24), grass, rot=(0, math.radians(lean * 40), 0))
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.9, 'front_az': -16}
