"""Komarock: a stone komainu crossed with the vajra of the temple-gate guardians (Rustboro batch,
docs/research/mask-designs.md). Fusion: Shachound's hound body under Shishiblaze's lion mask
(gold eyes, two rows of teeth) recoloured as weathered granite; stone curls for a mane; a single
horn; a vajra clenched across the open (a-form) mouth; a carved 'a' mark on the brow; a
shimenawa collar with paper streamers. Masked quadruped; rock/fighting."""
import math

NORMAL = {'stone': (0.52, 0.50, 0.47), 'lacquer': (0.18, 0.17, 0.16), 'moss': (0.30, 0.42, 0.18),
          'gold': (0.88, 0.70, 0.22), 'pupil': (0.03, 0.02, 0.02), 'socket': (0.16, 0.15, 0.14),
          'gum': (0.38, 0.30, 0.28), 'tooth': (0.86, 0.84, 0.78), 'straw': (0.82, 0.70, 0.40),
          'strawdark': (0.55, 0.44, 0.20), 'paper': (0.97, 0.97, 0.95), 'carve': (0.22, 0.20, 0.19)}
SHINY = {**NORMAL, 'stone': (0.42, 0.56, 0.46), 'moss': (0.22, 0.45, 0.40), 'lacquer': (0.14, 0.22, 0.18),
         'socket': (0.10, 0.18, 0.14), 'gum': (0.28, 0.38, 0.32)}


def build(k, c):
    stone = k.toon('stone', c['stone'], steps=k.HORROR_STEPS, weathered=0.4)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    moss = k.toon('moss', c['moss'], two_tone=True)
    gold = k.toon('gold', c['gold'], glint=0.5, two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.flat('strawdark', c['strawdark'])
    paper = k.flat('paper', c['paper'])
    carve = k.flat('carve', c['carve'])
    k.set_light((-0.75, -0.55, -0.1))

    face = k.mask_shell(stone, lacquer, width=0.7, depth=0.55, height=0.72)
    k.brows(face, 0.28, 0.4, 0.26, stone, frown=30, thick=0.12)
    k.glare_eyes(face, 0.3, 0.18, 0.18, gold, pupil, socket)
    k.bump(face, 0, -0.05, (0.17, 0.16, 0.14), stone, lift=0.05)
    k.fanged_mouth(face, -0.4, 0.4, 0.2, pupil, gum, tooth, fang=tooth, upper=5, lower=5, fang_len=0.18)
    # The vajra clenched across the open mouth.
    m = k.on_face(face, 0, -0.4, lift=0.12)
    k.vajra(m, 1.1, gold, axis=(1, 0, 0))
    # The carved 'a' mark on the brow: a ring with a stroke through it.
    b = k.on_face(face, 0, 0.5, lift=0.0)
    k.front_only(k.torus((b.x, b.y - 0.01, b.z), 0.07, 0.015, carve, rot=(math.pi / 2, 0, 0)))
    k.front_only(k.rod((b.x - 0.05, b.y - 0.02, b.z + 0.09), (b.x + 0.04, b.y - 0.02, b.z - 0.08), 0.014, carve))
    # A single horn (the horned one of the pair is the komainu proper) and stone curls for a mane.
    k.spike((0, 0.05, 0.62), (0.02, 0.15, 1.02), 0.11, stone)
    for i in range(12):
        a = math.pi * (0.1 + 0.8 * i / 11)
        for r, s in ((0.82, 0.13), (0.98, 0.1)):
            p = (r * math.cos(a) * 1.0, 0.18, r * math.sin(a) * 0.95 - 0.05)
            k.ellipsoid(p, (s, s * 0.9, s), moss if (i + int(r * 10)) % 3 == 0 else stone)
    # Shimenawa collar with shide, just under the mask.
    k.ring_rope((0, 0.25, -0.55), 0.48, 0.09, straw, strawdark, rot=(90, 0, 0), segments=18)
    for x in (-0.25, 0.22):
        k.shide((x, -0.22, -0.6), 0.36, 0.1, paper, side=1 if x < 0 else -1)

    def tail(at, mat):
        for i in range(3):
            k.ellipsoid(at + k.Vector((0, 0.12 * i, 0.15 + 0.14 * i)), (0.14, 0.12, 0.12), moss if i == 2 else mat)

    k.beast_behind_mask(0.72, stone, length=1.2, girth=0.46, leg=0.36, tail=tail)
    return {'kind': 'beast', 'size': 0.84, 'front_az': -24, 'side_az': -75}
