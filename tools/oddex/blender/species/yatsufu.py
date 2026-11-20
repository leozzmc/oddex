"""Yatsufu: a long-necked grass beast with two great yatsude leaves on its back (the tengu's
feather fan) that it beats once to ride the wind. Winona segment, replaces Tropius
(docs/research/mask-designs.md, "Yatsufu 的 Brief", option A). A kindly carved-wood old man's
face (not the Okina mask, which is a god), a shimenawa round its neck with paper streamers,
and strings of dried persimmons hanging under its chin like a beard. Silhouette at 64px: the two
round-lobed leaves spread like wings above a sturdy four-legged body. Grass/flying."""
import math

NORMAL = {'wood': (0.86, 0.70, 0.46), 'wooddark': (0.30, 0.16, 0.08), 'hollow': (0.05, 0.03, 0.02),
          'leaf': (0.26, 0.56, 0.22), 'vein': (0.66, 0.84, 0.40), 'body': (0.46, 0.34, 0.22),
          'kaki': (0.95, 0.52, 0.12), 'calyx': (0.20, 0.30, 0.12), 'straw': (0.86, 0.74, 0.40),
          'strawdark': (0.58, 0.44, 0.20), 'paper': (0.97, 0.97, 0.95)}
# Shiny: autumn leaves, vermilion with gold veins.
SHINY = {**NORMAL, 'leaf': (0.86, 0.26, 0.12), 'vein': (0.98, 0.80, 0.30), 'body': (0.36, 0.30, 0.30)}


def leaf(k, root, side, size, mat, vein, lobes=7, spread=(-30, 150)):
    """A palmate yatsude leaf in the XZ plane (facing -Y): round-tipped lobes fanning out from
    root between spread degrees (0 = straight out to the side, 90 = up), mirrored by side."""
    root = k.Vector(root)
    for i in range(lobes):
        t = i / (lobes - 1)
        a = math.radians(spread[0] + (spread[1] - spread[0]) * t)
        d = k.Vector((side * math.cos(a), 0, math.sin(a)))
        length = size * (0.8 + 0.2 * math.sin(math.pi * t))
        theta = math.atan2(d.z, d.x)   # rotate the lobe's long X axis onto d (about Y)
        k.ellipsoid(root + d * length * 0.55, (length * 0.55, 0.04, size * 0.2), mat, rot=(0, -theta, 0))
        k.rod(root, root + d * length * 0.95 + k.Vector((0, -0.045, 0)), 0.025, vein)
    k.ellipsoid(root, (size * 0.28, 0.05, size * 0.28), mat)


def build(k, c):
    wood = k.toon('wood', c['wood'], steps=(0.55, 0.8, 1.0), weathered=0.2)
    wooddark = k.toon('wooddark', c['wooddark'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    leaf_m = k.toon('leaf', c['leaf'], two_tone=True)
    vein = k.flat('vein', c['vein'])
    body = k.toon('body', c['body'], two_tone=True)
    kaki = k.toon('kaki', c['kaki'], two_tone=True)
    calyx = k.flat('calyx', c['calyx'])
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.flat('strawdark', c['strawdark'])
    paper = k.flat('paper', c['paper'])
    k.set_light((-0.7, -0.6, 0.1))

    # The old man's carved face: smiling crescent eyes, laugh lines, a broad nose.
    face = k.mask_shell(wood, wooddark, width=0.5, depth=0.36, height=0.56)
    for x in (-0.2, 0.2):   # crescent eyes, thick white brows of an old man
        k.hole(face, x, 0.1, (0.13, 0.05), backing=hollow)
        k.front_only(k.ellipsoid(k.on_face(face, x, 0.25, lift=0.02), (0.15, 0.05, 0.05), paper,
                                 rot=(0, math.radians(-20 if x < 0 else 20), 0)))
    k.bump(face, 0, -0.02, (0.08, 0.08, 0.11), wood, lift=0.03)
    k.hole(face, 0, -0.26, (0.2, 0.06), backing=hollow)   # a wide smile
    k.wrinkles(face, wooddark, [(-0.22, -0.16, 0.03, 0.1, 20), (0.22, -0.16, 0.03, 0.1, -20),
                                (0, 0.36, 0.2, 0.025, 0)])
    # Dried persimmons on strings under the chin, the beard.
    for x, n in ((-0.24, 2), (-0.08, 3), (0.08, 3), (0.24, 2)):
        k.rod((x, -0.2, -0.45), (x, -0.22, -0.45 - 0.17 * n), 0.012, strawdark)
        for j in range(n):
            z = -0.55 - 0.17 * j
            k.ellipsoid((x, -0.24, z), (0.075, 0.06, 0.085), kaki)
            k.ellipsoid((x, -0.29, z + 0.07), (0.035, 0.02, 0.02), calyx)

    # The body: a sturdy quadruped set back and below, joined to the face by a long neck.
    before = k.snapshot()
    k.quadruped(body, length=1.5, girth=0.5, leg=0.55)
    k.transform(k.since(before), offset=(0, 0.75, -1.45))
    k.rod((0, 0.75, -0.55), (0, 0.25, 0.0), 0.22, body)
    k.ellipsoid((0, 0.22, 0.02), (0.36, 0.3, 0.38), body)   # the head behind the mask
    # Shimenawa round the neck, paper streamers hanging in front.
    k.ring_rope((0, 0.5, -0.3), 0.3, 0.08, straw, strawdark, rot=(70, 0, 0), segments=16)
    for x in (-0.16, 0.16):
        k.shide((x, 0.18, -0.42), 0.32, 0.09, paper, side=1 if x < 0 else -1)

    # The two great leaves rising from the shoulders like wings.
    for side in (-1, 1):
        leaf(k, (side * 0.75, 1.0, -0.2), side, 0.95, leaf_m, vein, spread=(-15, 115))
    return {'kind': 'beast', 'size': 0.92, 'front_az': -24, 'side_az': -70}
