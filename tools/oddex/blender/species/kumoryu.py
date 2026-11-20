"""Kumoryu: a dragon riding a great cumulus cloud. Winona segment, her ace, replaces Altaria
(docs/research/mask-designs.md, "Kumoryu 的 Brief", option B). A black-bearded dragon mask
(kurohige type, imagery only, not a deity) glares out of the middle of the cloud: red-brown face,
gold eyes, heavy black brows and beard, an open roaring mouth; branched gold horns above, two
clawed forelegs gripping the cloud below, cloud puffs bulging out at the sides like wings, and a
scaled teal tail curling up out of the back. Silhouette at 64px: the round cloud with the horned
face in it. Dragon/flying."""
import math

NORMAL = {'cloud': (0.96, 0.97, 1.0), 'cloudshade': (0.66, 0.74, 0.86), 'face': (0.70, 0.30, 0.18),
          'lacquer': (0.14, 0.06, 0.05), 'beard': (0.08, 0.07, 0.08), 'gold': (0.95, 0.76, 0.22),
          'pupil': (0.05, 0.04, 0.04), 'hollow': (0.12, 0.02, 0.03), 'tooth': (0.97, 0.95, 0.88),
          'scale': (0.20, 0.62, 0.58), 'scaledark': (0.10, 0.36, 0.38)}
# Shiny: a sunset cloud, peach and gold.
SHINY = {**NORMAL, 'cloud': (1.0, 0.86, 0.78), 'cloudshade': (0.92, 0.56, 0.48), 'scale': (0.86, 0.62, 0.20),
         'scaledark': (0.58, 0.36, 0.10)}


def build(k, c):
    cloud = k.toon('cloud', c['cloud'], steps=(0.62, 0.85, 1.0))
    shade = k.flat('cloudshade', c['cloudshade'])
    face_m = k.toon('face', c['face'], steps=(0.55, 0.8, 1.0))
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    beard = k.toon('beard', c['beard'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    hollow = k.flat('hollow', c['hollow'])
    tooth = k.flat('tooth', c['tooth'])
    scale_m = k.toon('scale', c['scale'], two_tone=True)
    scaledark = k.flat('scaledark', c['scaledark'])
    k.set_light((-0.7, -0.6, 0.2))

    # The cloud: a heap of puffs behind and around the face, shaded underneath.
    for x, y, z, r in ((0, 0.45, -0.1, 0.85), (-0.7, 0.35, -0.35, 0.55), (0.7, 0.35, -0.35, 0.55),
                       (-0.45, 0.2, -0.7, 0.45), (0.45, 0.2, -0.7, 0.45), (0, 0.25, -0.85, 0.5),
                       (-0.4, 0.6, 0.25, 0.4), (0.4, 0.6, 0.25, 0.4)):
        k.ellipsoid((x, y, z), (r, r * 0.9, r * 0.85), cloud)
    for x in (-0.55, 0, 0.55):
        k.ellipsoid((x, 0.15, -1.05), (0.35, 0.3, 0.12), shade)
    # Cloud wings: puffs bulging out and up at the sides.
    for side in (-1, 1):
        for i, (dx, dz, r) in enumerate(((1.15, 0.0, 0.42), (1.5, 0.3, 0.36), (1.75, 0.62, 0.28))):
            k.ellipsoid((side * dx, 0.35 + 0.05 * i, dz), (r, r * 0.8, r * 0.8), cloud)
        k.ellipsoid((side * 1.3, 0.3, -0.28), (0.3, 0.25, 0.1), shade)

    # The kurohige mask in the middle of the cloud.
    before = k.snapshot()
    face = k.mask_shell(face_m, lacquer, width=0.62, depth=0.4, height=0.7)
    k.brows(face, 0.24, 0.36, 0.2, beard, frown=24, thick=0.1)
    k.glare_eyes(face, 0.23, 0.16, 0.11, gold, pupil, lacquer)
    k.bump(face, 0, -0.03, (0.1, 0.08, 0.09), face_m, lift=0.03)
    k.fanged_mouth(face, -0.3, 0.22, 0.1, hollow, face_m, tooth, fang=tooth, upper=4, lower=4, fang_len=0.1)
    # The black beard below and long whiskers sweeping out from the nose.
    for x in (-0.18, 0, 0.18):
        k.front_only(k.ellipsoid(k.on_face(face, x * 1.2, -0.56, lift=0.02), (0.12, 0.08, 0.26), beard))
    for side in (-1, 1):
        p = k.on_face(face, side * 0.12, -0.08, lift=0.04)
        k.rod(p, (side * 0.95, p.y - 0.05, -0.32), 0.035, beard)
    k.transform(k.since(before), offset=(0, -0.5, 0.05))
    # Branched gold horns.
    for side in (-1, 1):
        base = k.Vector((side * 0.26, -0.4, 0.62))
        tip = k.Vector((side * 0.62, -0.25, 1.5))
        k.spike(base, tip, 0.1, gold)
        mid = base.lerp(tip, 0.5)
        k.spike(mid, mid + k.Vector((side * 0.28, 0.02, 0.12)), 0.05, gold)
    # Two clawed forelegs gripping the front of the cloud.
    for side in (-1, 1):
        k.rod((side * 0.42, -0.25, -0.45), (side * 0.5, -0.6, -0.72), 0.08, scale_m)
        for j in (-1, 0, 1):
            k.spike((side * 0.5, -0.62, -0.74), (side * 0.5 + j * 0.07, -0.78, -0.86), 0.03, gold)
    # The scaled tail curling up out of the back of the cloud.
    for i in range(10):
        t = i / 9
        a = math.radians(-30 + 220 * t)
        p = (1.05 + 0.35 * math.cos(a), 0.8 + 0.2 * t, 0.1 + 0.5 * math.sin(a) + 0.5 * t)
        r = 0.2 * (1 - 0.6 * t)
        k.ellipsoid(p, (r, r, r), scale_m if i % 2 else scaledark, segments=16)
    k.spike(p, (p[0] - 0.25, p[1], p[2] + 0.2), 0.08, gold)
    return {'kind': 'beast', 'size': 0.92, 'front_az': -16, 'front_el': 10, 'side_az': -70}
