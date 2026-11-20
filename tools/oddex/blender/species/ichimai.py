"""Ichimai: the plate-counting well ghost, after the public-domain Okiku of 'Bancho Sarayashiki' (not
Sadako, a copyrighted character; no videotape or TV motifs). Winona segment, a rare encounter on
Route 120 (docs/research/mask-designs.md, option A of its brief). Brief: a woman in white leaning
out of an old stone well, her long black hair falling over most of her face and spilling down
over the well's rim; through the hair one eye of a white woman's mask (ko-omote type) shows, the
mask split by a crack from brow to chin, the mouth a little open as if counting 'nine...'; she
holds three plates fanned out in front of her chest. Silhouette at 64px: the well below, the
curtain of hair, the white plates. Masked ghost; ghost/water."""
import math

NORMAL = {'face': (0.97, 0.95, 0.92), 'lacquer': (0.14, 0.06, 0.05), 'hollow': (0.02, 0.02, 0.03),
          'crack': (0.10, 0.06, 0.08), 'hair': (0.06, 0.06, 0.08), 'robe': (0.86, 0.87, 0.88),
          'plate': (0.98, 0.98, 0.96), 'pattern': (0.20, 0.36, 0.78), 'stone': (0.52, 0.52, 0.50),
          'stonedark': (0.30, 0.30, 0.30), 'well': (0.04, 0.05, 0.08), 'moss': (0.34, 0.48, 0.28)}
# Shiny: a drowned blue robe, a sea-green well, gold-rimmed plates (clearly apart from the grey well).
SHINY = {**NORMAL, 'robe': (0.40, 0.56, 0.92), 'pattern': (0.85, 0.65, 0.20), 'stone': (0.24, 0.50, 0.46),
         'stonedark': (0.10, 0.28, 0.28), 'moss': (0.80, 0.58, 0.18)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=(0.6, 0.85, 1.0))
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    crack = k.flat('crack', c['crack'])
    hair = k.toon('hair', c['hair'], two_tone=True)
    robe = k.toon('robe', c['robe'], steps=(0.6, 0.85, 1.0))
    plate = k.toon('plate', c['plate'], two_tone=True)
    pattern = k.flat('pattern', c['pattern'])
    stone = k.toon('stone', c['stone'], steps=k.HORROR_STEPS)
    stonedark = k.flat('stonedark', c['stonedark'])
    well = k.flat('well', c['well'])
    moss = k.flat('moss', c['moss'])
    k.set_light((-0.7, -0.6, 0.2))
    # The stone well: a wide drum of stone with a dark mouth, moss on the rim.
    k.cylinder((0, 0.15, -1.05), 0.82, 0.6, stone, segments=24)
    for i in range(12):   # joints between the stones
        a = 2 * math.pi * i / 12
        k.rod((0.83 * math.cos(a), 0.15 + 0.83 * math.sin(a), -1.33), (0.83 * math.cos(a), 0.15 + 0.83 * math.sin(a), -0.77), 0.02, stonedark)
    k.torus((0, 0.15, -0.75), 0.78, 0.09, stone)
    k.cylinder((0, 0.15, -0.74), 0.68, 0.03, well, segments=24)
    for a in (2.4, 3.6, 4.4):
        k.ellipsoid((0.8 * math.cos(a), 0.15 + 0.8 * math.sin(a), -0.72), (0.14, 0.1, 0.05), moss)
    # Her white-robed upper body leaning out of it.
    k.ellipsoid((0, 0.18, -0.3), (0.42, 0.3, 0.55), robe)
    for side in (-1, 1):   # sleeves reaching forward to hold the plates
        k.ellipsoid((side * 0.34, -0.12, -0.32), (0.16, 0.28, 0.14), robe, rot=(math.radians(20), 0, 0))
    # The white mask, split by a crack, one eye showing through the hair.
    before = k.snapshot()
    shell = k.mask_shell(face_m, lacquer, width=0.36, depth=0.28, height=0.46)
    k.hole(shell, -0.13, 0.08, (0.09, 0.05), backing=hollow)
    k.front_only(k.ellipsoid(k.on_face(shell, -0.13, 0.13, lift=0.005), (0.08, 0.015, 0.02), crack))   # heavy lid
    k.hole(shell, 0.0, -0.22, (0.08, 0.05), backing=hollow)   # mouth open, counting
    # The crack runs down the visible (left) half, beside the eye, so the hair does not hide it.
    pts = [(-0.02, 0.44), (-0.06, 0.3), (-0.01, 0.22), (-0.06, 0.06), (-0.02, -0.06), (-0.07, -0.18), (-0.03, -0.4)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        k.front_only(k.rod(k.on_face(shell, x0, z0, lift=0.01), k.on_face(shell, x1, z1, lift=0.01), 0.028, crack))
    k.transform(k.since(before), offset=(0, -0.02, 0.48))
    # Long black hair: a cap, a curtain down both sides and over the well's rim, strands over the
    # right side of the face.
    k.ellipsoid((0, 0.05, 0.78), (0.42, 0.34, 0.24), hair)
    for i, x in enumerate((-0.42, -0.3, 0.3, 0.42)):
        k.ellipsoid((x, 0.0, 0.0), (0.12, 0.14, 0.95 + 0.08 * (i % 2)), hair)
    k.ellipsoid((0, 0.36, 0.05), (0.48, 0.14, 0.85), hair)   # the curtain down her back, so the back view is all hair
    for x in (-0.55, -0.45, 0.45, 0.58):   # spilling over the rim
        k.ellipsoid((x, -0.2, -0.75), (0.08, 0.06, 0.28), hair)
    for x0, x1 in ((0.04, 0.12), (0.12, 0.2), (0.2, 0.24)):
        k.front_only(k.rod((x0, -0.32, 0.92), (x1, -0.34, 0.15), 0.05, hair))
    # Three plates fanned in front of her chest, blue-patterned rims.
    for x, z, tilt in ((-0.18, -0.38, 18), (0.0, -0.32, 0), (0.18, -0.38, -18)):
        k.cylinder((x, -0.42, z), 0.2, 0.04, plate, rot=(math.pi / 2, math.radians(tilt), 0), segments=24)
        k.torus((x, -0.445, z), 0.19, 0.03, pattern, rot=(math.pi / 2, math.radians(tilt), 0))   # rim
        k.torus((x, -0.45, z), 0.09, 0.02, pattern, rot=(math.pi / 2, math.radians(tilt), 0))
    for side in (-1, 1):   # hands at the edges of the plates
        k.ellipsoid((side * 0.36, -0.45, -0.4), (0.07, 0.06, 0.08), face_m)
    return {'kind': 'beast', 'size': 0.88, 'front_az': -14, 'side_az': -70}
