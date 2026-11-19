"""Karuvajra: a wrathful-faced training mask holding a vajra before a garuda-flame mandorla
(karura-en), after the imagery around Fudo Myoo but not the deity: no sword, no lasso, no rock
seat, no attendants, no seed syllable (Rustboro batch, docs/research/mask-designs.md).
Fusion: Kamorai's gold glare and knitted brows, Hannyagon's two rows of fangs, Kamorai's drum
ring as the halo's base with Shishiblaze's mane spikes turned into flames. Mask with two
arms; fighting/flying."""
import math

NORMAL = {'face': (0.12, 0.16, 0.30), 'lacquer': (0.05, 0.05, 0.10), 'gold': (0.95, 0.75, 0.22),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.04, 0.05, 0.12), 'gum': (0.50, 0.06, 0.12),
          'tooth': (0.95, 0.92, 0.80), 'flame': (0.92, 0.25, 0.08), 'flame2': (1.0, 0.70, 0.18),
          'arm': (0.18, 0.22, 0.38)}
SHINY = {**NORMAL, 'face': (0.88, 0.88, 0.86), 'arm': (0.80, 0.80, 0.78), 'socket': (0.35, 0.35, 0.40),
         'flame': (0.20, 0.45, 0.95), 'flame2': (0.70, 0.90, 1.0)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.4, weathered=0.25)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], glint=0.5, two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    flame = k.flat('flame', c['flame'])
    flame2 = k.flat('flame2', c['flame2'])
    arm = k.toon('arm', c['arm'])
    k.set_light((-0.75, -0.55, -0.2))

    k.torus((0, 0.35, 0.05), 0.95, 0.07, gold, rot=(math.pi / 2, 0, 0))
    k.flame_halo((0, 0.35, 0.05), 0.98, flame, inner=flame2, licks=16, length=0.42, bird=flame)
    face = k.mask_shell(face_m, lacquer, width=0.7, depth=0.46, height=0.86)
    k.brows(face, 0.3, 0.46, 0.3, face_m, frown=34, thick=0.13)
    k.glare_eyes(face, 0.31, 0.22, 0.2, gold, pupil, socket)
    k.bump(face, 0, -0.02, (0.13, 0.12, 0.17), face_m, lift=0.02)
    k.fanged_mouth(face, -0.45, 0.4, 0.22, pupil, gum, tooth, fang=gold, upper=6, lower=5, fang_len=0.2)
    # Two thick arms holding a vajra across the chest, below the mask.
    hands = []
    for side in (-1, 1):
        sh = k.Vector((side * 0.62, 0.05, -0.35))
        el = k.Vector((side * 0.95, -0.15, -0.75))
        hand = k.Vector((side * 0.32, -0.55, -0.95))
        k.rod(sh, el, 0.12, arm)
        k.ellipsoid(el, (0.13, 0.13, 0.13), arm)
        k.rod(el, hand, 0.11, arm)
        k.ellipsoid(hand, (0.14, 0.13, 0.13), arm)
        hands.append(hand)
    k.vajra((hands[0] + hands[1]) / 2 + k.Vector((0, -0.05, 0)), 1.2, gold, axis=(1, 0, 0))
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -18}
