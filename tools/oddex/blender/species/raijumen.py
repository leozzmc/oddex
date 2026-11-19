"""Raijumen: a raiju, the folk thunder-beast that falls to earth with lightning (a yokai, not a
god), wearing a blue thunder mask (Mauville batch, docs/research/mask-designs.md). Fusion:
Shachound's hound body, Kamorai's glaring thunder face recoloured blue with its lightning
horns, a zigzag lightning tail. Masked quadruped; electric/dark. Evolves into Raijuoh."""
import math

NORMAL = {'mask': (0.18, 0.32, 0.72), 'lacquer': (0.06, 0.06, 0.14), 'gold': (0.98, 0.85, 0.25),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.05, 0.08, 0.22), 'gum': (0.45, 0.06, 0.16),
          'tooth': (0.96, 0.94, 0.86), 'body': (0.20, 0.20, 0.26), 'bolt': (1.0, 0.92, 0.30)}
SHINY = {**NORMAL, 'mask': (0.72, 0.20, 0.30), 'body': (0.85, 0.82, 0.78), 'bolt': (0.65, 0.95, 1.0)}


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
    k.set_light((-0.75, -0.55, -0.1))

    face = k.mask_shell(mask_m, lacquer, width=0.62, depth=0.5, height=0.66)
    k.brows(face, 0.25, 0.36, 0.23, mask_m, frown=32, thick=0.1)
    k.glare_eyes(face, 0.26, 0.14, 0.17, gold, pupil, socket)
    k.fanged_mouth(face, -0.36, 0.34, 0.17, pupil, gum, tooth, fang=gold, upper=4, lower=4, fang_len=0.16)
    for side in (-1, 1):
        p = k.on_face(face, side * 0.22, 0.55, lift=0.01)
        k.front_only(k.spike(p, (p.x * 2.0, p.y, p.z + 0.38), 0.07, bolt))
        k.spike((side * 0.42, 0.1, 0.45), (side * 0.7, 0.2, 0.95), 0.13, body)

    def tail(at, mat):
        pts = [at, at + k.Vector((0.2, 0.2, 0.3)), at + k.Vector((-0.1, 0.35, 0.55)), at + k.Vector((0.18, 0.5, 0.85))]
        for a, b in zip(pts, pts[1:]):
            k.rod(a, b, 0.06, bolt)

    k.beast_behind_mask(0.66, body, length=1.25, girth=0.4, leg=0.42, tail=tail)
    return {'kind': 'beast', 'size': 0.84, 'front_az': -24, 'side_az': -75}
