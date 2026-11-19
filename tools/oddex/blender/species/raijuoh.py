"""Raijuoh: the grown raiju, Wattson's ace (Mauville batch, docs/research/mask-designs.md): a
bigger thunder-beast in a heavier blue mask, a ring of thunder drums behind it (only the drum
ring of thunder imagery; it is not the thunder god), a mane of lightning and a zigzag tail.
Fusion: Raijumen on Shachound's body, Kamorai's drum ring and lightning horns, Shishiblaze's
mane spikes turned into bolts. Masked quadruped; electric/dark."""
import math

NORMAL = {'mask': (0.14, 0.26, 0.66), 'lacquer': (0.05, 0.05, 0.12), 'gold': (0.98, 0.85, 0.25),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.04, 0.06, 0.20), 'gum': (0.45, 0.06, 0.16),
          'tooth': (0.96, 0.94, 0.86), 'body': (0.16, 0.16, 0.22), 'bolt': (1.0, 0.92, 0.30),
          'drum': (0.70, 0.18, 0.12)}
SHINY = {**NORMAL, 'mask': (0.72, 0.20, 0.30), 'body': (0.85, 0.82, 0.78), 'bolt': (0.65, 0.95, 1.0),
         'drum': (0.20, 0.30, 0.65)}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=k.HORROR_STEPS, glint=0.4, weathered=0.25)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], glint=0.5, two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    body = k.toon('body', c['body'], two_tone=True)
    bolt = k.flat('bolt', c['bolt'])
    drum = k.toon('drum', c['drum'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.1))

    # Ring of thunder drums behind the head.
    k.torus((0, 0.3, 0.15), 1.0, 0.05, gold, rot=(math.pi / 2, 0, 0))
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        k.cylinder((1.0 * math.cos(a), 0.3, 0.15 + 1.0 * math.sin(a)), 0.13, 0.12, drum, rot=(math.pi / 2, 0, 0))
        k.cylinder((1.0 * math.cos(a), 0.23, 0.15 + 1.0 * math.sin(a)), 0.08, 0.02, gold, rot=(math.pi / 2, 0, 0))
    face = k.mask_shell(mask_m, lacquer, width=0.7, depth=0.52, height=0.74)
    k.brows(face, 0.28, 0.4, 0.27, mask_m, frown=34, thick=0.12)
    k.glare_eyes(face, 0.29, 0.16, 0.19, gold, pupil, socket)
    k.fanged_mouth(face, -0.4, 0.4, 0.2, pupil, gum, tooth, fang=gold, upper=5, lower=5, fang_len=0.2)
    for side in (-1, 1):
        p = k.on_face(face, side * 0.24, 0.62, lift=0.01)
        k.front_only(k.spike(p, (p.x * 2.2, p.y, p.z + 0.5), 0.08, bolt))
    for i in range(10):
        a = math.pi * (0.12 + 0.76 * i / 9)
        base = k.Vector((0.75 * math.cos(a), 0.2, 0.75 * math.sin(a) * 0.9))
        k.spike(base, base * 1.45 + k.Vector((0, 0.1, 0.1)), 0.1, bolt if i % 2 else body)

    def tail(at, mat):
        pts = [at, at + k.Vector((0.25, 0.25, 0.35)), at + k.Vector((-0.12, 0.45, 0.65)),
               at + k.Vector((0.22, 0.65, 1.0)), at + k.Vector((-0.05, 0.8, 1.25))]
        for a, b in zip(pts, pts[1:]):
            k.rod(a, b, 0.07, bolt)

    k.beast_behind_mask(0.74, body, length=1.45, girth=0.48, leg=0.48, tail=tail)
    return {'kind': 'beast', 'size': 0.9, 'front_az': -24, 'side_az': -75}
