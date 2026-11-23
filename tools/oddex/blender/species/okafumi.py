"""Okafumi: the thing that treads the hills. After the creature seen at the end of H. P.
Lovecraft's "The Dunwich Horror" (Weird Tales, April 1929; public domain): bigger than a barn,
shaped like a hen's egg, all made of squirming ropes, with dozens of legs like hogsheads, nothing
solid about it, great bulging eyes all over, ten or twenty mouths or trunks sticking out along
the sides as big as stovepipes, grey with blue or purple rings, and half a face on top. In the
story it is the child of a fictional god and a human; nothing here has any real worship, and
nothing comes from later writers, artists or games. Sootopolis segment, the Groudon slot (role
LEGEND_LAND; docs/research/mask-designs.md, "大地:Okafumi"). Its many mouths drink: the wells, the
rivers, the clouds, so the sky is bare and the sun beats down (its ability is Drought). The half
face on top is the only human thing about it, a pale half mask; each mouth is a pursed usobuki
mouth like Usobuzz's and Magatide's. Silhouette at 64px: a wide egg on a row of stubby legs, a
small white half face on top. Ground/ghost."""
import math

NORMAL = {'rope': (0.56, 0.56, 0.58), 'ropedark': (0.33, 0.33, 0.38), 'ring': (0.42, 0.36, 0.72),
          'face': (0.90, 0.90, 0.85), 'lacquer': (0.16, 0.14, 0.16), 'hollow': (0.03, 0.02, 0.03),
          'eye': (0.96, 0.86, 0.26), 'pupil': (0.03, 0.02, 0.02), 'lip': (0.66, 0.52, 0.58),
          'mud': (0.62, 0.50, 0.28)}
# Shiny: ropes dried ochre in the sun, dark red rings, the half face rust red.
SHINY = {**NORMAL, 'rope': (0.82, 0.68, 0.36), 'ropedark': (0.54, 0.40, 0.18), 'ring': (0.56, 0.12, 0.12),
         'face': (0.74, 0.32, 0.22), 'eye': (0.60, 0.92, 0.95)}

BODY_C, BODY_R = (0, 0, 0.1), (1.4, 1.05, 0.88)


# Hand-placed pixels (make_art.apply_pixels): the half face on top, the only human thing about it: a brow, one hollow eye, half a nose
# and half a flat mouth, ending at a jagged break with the broken edge showing (no smile).
_FACE = [
    ((21, 3), ['..........kd.',
               '.........kdd.',
               '..........kdd',
               '.........kddd',
               '........kdddd',
               '..ggggg..kddd',
               '........kddd.',
               '...qqqff.kd..',
               '..qqqqqfkdd..',
               '...qqqf..kd..',
               '........kdd..',
               '.......g.kd..',
               '......ggkd...',
               '.........kdd.',
               '...kkkkkkddd.',
               '.........kdd.',
               '.....ff.kddd.']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((22, 8), ['..........kd.',
               '.........kdd.',
               '..........kdd',
               '.........kddd',
               '........kdddd',
               '..ggggg..kddd',
               '........kddd.',
               '...qqqff.kd..',
               '..qqqqqfkdd..',
               '...qqqf..kd..',
               '........kdd..',
               '.......g.kd..',
               '......ggkd...',
               '.........kdd.',
               '...kkkkkkddd.',
               '.........kdd.']),
]
PIXELS = {'keys': {'k': (28, 18, 22),
                   'f': (243, 243, 237),
                   'd': (212, 191, 200),
                   'g': (148, 133, 140),
                   'q': (48, 39, 48)},
          'front': {'box': (1, 0, 62, 56), 'patches': _FACE},
          'front2': {'box': (0, 5, 64, 56), 'patches': _FACE2}}


def build(k, c):
    rope = k.toon('rope', c['rope'], two_tone=True)
    ropedark = k.toon('ropedark', c['ropedark'], two_tone=True)
    ring = k.toon('ring', c['ring'], two_tone=True)
    face_m = k.toon('face', c['face'], two_tone=True)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    eye = k.flat('eye', c['eye'])
    pupil = k.flat('pupil', c['pupil'])
    lip = k.toon('lip', c['lip'], two_tone=True)
    mud = k.toon('mud', c['mud'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.2))

    # The egg: a core wound round with coils of rope, every third coil a blue-purple ring.
    k.ellipsoid(BODY_C, (BODY_R[0] * 0.97, BODY_R[1] * 0.97, BODY_R[2] * 0.97), ropedark)
    n = 9
    for i in range(n):
        z = -0.72 + 1.62 * i / (n - 1)
        r = math.sqrt(max(0.02, 1 - ((z - BODY_C[2]) / BODY_R[2]) ** 2))
        coil = k.torus((0, 0, z), r, 0.1, ring if i % 3 == 1 else rope)
        coil.scale = (BODY_R[0], BODY_R[1], 1.0)

    def surf(az, z, lift=0.0):
        """Point on the egg at azimuth az (degrees, 0 = front, + to the viewer's right) and height z."""
        r = math.sqrt(max(0.02, 1 - ((z - BODY_C[2]) / BODY_R[2]) ** 2)) + lift
        a = math.radians(az - 90)
        return k.Vector((BODY_R[0] * r * math.cos(a), BODY_R[1] * r * math.sin(a), z))

    # The legs like hogsheads, mud on their soles.
    for az in (-78, -30, 26, 76, 140, -140):
        p = surf(az, -0.5)
        k.cylinder((p.x * 0.92, p.y * 0.92, -1.0), 0.17, 0.6, rope)
        k.cylinder((p.x * 0.92, p.y * 0.92, -1.3), 0.2, 0.1, mud)
    # Loose rope ends squirming out of the coils.
    for az, z, dz in ((-100, 0.5, 0.35), (112, -0.1, 0.3), (-118, -0.35, -0.2), (60, 0.78, 0.3), (-40, 0.85, 0.28)):
        a = surf(az, z)
        b = surf(az, z + dz * 0.5, 0.28)
        c2 = surf(az + 14, z + dz, 0.4)
        k.rod(a, b, 0.07, rope)
        k.rod(b, c2, 0.055, rope)
        k.ellipsoid(c2, (0.07, 0.07, 0.07), ropedark)
    # The mouths like stovepipes: a short trunk, pursed lips, a dark hole. They drink.
    for az, z in ((-66, 0.25), (62, 0.05), (6, -0.3), (-20, 0.62), (100, 0.42)):
        a, b = surf(az, z), surf(az, z, 0.3)
        k.rod(a, b, 0.17, ropedark)
        lips = k.ellipsoid(b, (0.22, 0.22, 0.22), lip)
        d = (b - a).normalized()
        k.ellipsoid(b + d * 0.16, (0.11, 0.11, 0.11), hollow)
    # Great bulging eyes all over it (redrawn by hand in PIXELS).
    for az, z, s in ((-22, 0.12, 0.17), (30, 0.4, 0.14), (-48, -0.3, 0.12), (34, -0.48, 0.11), (74, -0.25, 0.11),
                     (2, 0.66, 0.11), (150, 0.2, 0.14), (-150, 0.4, 0.12), (180, -0.2, 0.13)):
        p = surf(az, z, 0.04)
        k.ellipsoid(p, (s, s, s), eye)
        out = (p - k.Vector(BODY_C)).normalized()
        k.ellipsoid(p + out * s * 0.75, (s * 0.45, s * 0.45, s * 0.45), pupil)

    # The half face on top: one side of a pale human mask, the other side broken away.
    before = k.snapshot()
    shell = k.mask_shell(face_m, lacquer, width=0.44, depth=0.3, height=0.6)
    k.hole(shell, -0.2, 0.12, (0.1, 0.07), backing=hollow)
    k.bump(shell, -0.03, -0.05, (0.06, 0.06, 0.1), face_m, lift=0.02)
    k.hole(shell, -0.14, -0.3, (0.12, 0.025), backing=hollow)
    k.cut(shell, k.cylinder((0.42, 0, 0), 0.42, 1.2, hollow, rot=(math.radians(90), 0, 0), segments=5))
    k.transform(k.since(before), offset=(-0.05, -0.3, 1.22), scale=1.2)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -14, 'front_el': 8, 'side_az': -70, 'squash': (1.06, 1.06, 0.9)}
