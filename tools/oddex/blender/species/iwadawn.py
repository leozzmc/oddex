"""Iwadawn: the rock door of Ama-no-Iwato with the hidden sun's light leaking out (Rustboro batch,
docs/research/mask-designs.md). Not the goddess: the door. Fusion: a stone mask split by a
glowing rift (Okinoir's split jaw turned into two leaves), Bekurama's pressed lips (sealed),
Kamorai's gold eyes and drum ring turned into a sun disc; a bronze mirror on the brow and a
shimenawa with paper streamers across the lintel. Mask; rock/fairy."""
import math

NORMAL = {'stone': (0.40, 0.38, 0.40), 'lacquer': (0.14, 0.13, 0.14), 'light': (1.0, 0.82, 0.45),
          'gold': (0.95, 0.72, 0.22), 'pupil': (0.03, 0.02, 0.02), 'socket': (0.12, 0.11, 0.12),
          'lip': (0.30, 0.26, 0.28), 'mirror': (0.72, 0.58, 0.34), 'straw': (0.82, 0.70, 0.40),
          'strawdark': (0.55, 0.44, 0.20), 'paper': (0.97, 0.97, 0.95)}
SHINY = {**NORMAL, 'stone': (0.86, 0.84, 0.82), 'lacquer': (0.45, 0.42, 0.42), 'light': (1.0, 0.62, 0.70),
         'socket': (0.40, 0.35, 0.38), 'lip': (0.62, 0.56, 0.58)}


def build(k, c):
    stone = k.toon('stone', c['stone'], steps=k.HORROR_STEPS, weathered=0.45)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    light = k.flat('light', c['light'])
    gold = k.toon('gold', c['gold'], glint=0.4, two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    lip = k.toon('lip', c['lip'], two_tone=True)
    mirror = k.toon('mirror', c['mirror'], glint=0.8, two_tone=True)
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.flat('strawdark', c['strawdark'])
    paper = k.flat('paper', c['paper'])
    k.set_light((-0.75, -0.6, 0.2))

    # The sun disc behind the door: a gold ring with rays, light glowing through.
    k.torus((0, 0.35, 0.05), 1.0, 0.08, gold, rot=(math.pi / 2, 0, 0))
    k.flame_halo((0, 0.35, 0.05), 1.05, gold, inner=light, licks=14, length=0.3)
    face = k.mask_shell(stone, lacquer, width=0.82, depth=0.5, height=0.95)
    # The rift between the two leaves, light pouring out of it.
    for z0, z1, x in ((0.95, 0.4, 0.0), (0.4, -0.2, 0.04), (-0.2, -0.95, -0.02)):
        a = k.on_face(face, x, z0 - 0.02, lift=0.02)
        b = k.on_face(face, x, z1 + 0.02, lift=0.02)
        k.front_only(k.rod(a, b, 0.075, light))
        for dx in (-0.09, 0.09):
            k.front_only(k.rod((a.x + dx, a.y, a.z), (b.x + dx, b.y, b.z), 0.022, lacquer))
    k.wrinkles(face, stone, [(-0.45, 0.1, 0.08, 0.35, 10), (0.45, -0.1, 0.08, 0.3, -12), (-0.3, -0.6, 0.12, 0.06, 0)])
    k.brows(face, 0.33, 0.45, 0.3, stone, frown=24, thick=0.13)
    k.glare_eyes(face, 0.36, 0.2, 0.2, gold, pupil, socket)
    # Pressed, sealed lips.
    m = k.on_face(face, 0, -0.5, lift=0.04)
    k.front_only(k.ellipsoid(m, (0.34, 0.1, 0.11), lip))
    k.front_only(k.ellipsoid((m.x, m.y - 0.09, m.z), (0.3, 0.02, 0.018), pupil))
    # The mirror on the brow and the shimenawa across the lintel.
    b = k.on_face(face, 0, 0.62, lift=0.02)
    k.front_only(k.cylinder((b.x, b.y - 0.02, b.z), 0.13, 0.04, mirror, rot=(math.pi / 2, 0, 0)))
    k.rope([(-0.98, -0.1, 0.9), (-0.45, -0.3, 1.0), (0.45, -0.3, 1.0), (0.98, -0.1, 0.9)], 0.1, straw, strawdark)
    for x, side in ((-0.95, 1), (0.85, -1)):
        k.shide((x, -0.15, 0.82), 0.45, 0.11, paper, side=side)
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -16}
