"""Ningyomen: the ningyo, the human-faced fish of Japanese folklore, whose appearing foretells
harvest or disaster; in the tale of Yao Bikuni a girl who ate its flesh lived eight hundred
years. A yokai, not a deity. League segment, replaces Milotic, Wallace's ace
(docs/research/mask-designs.md, "Ningyomen 的 Brief", option A). A long fish curled in an S, its
scales bright as the inside of a shell; where the fish's head should be is the Noh face of a
young woman, her black hair streaming back along the spine; red fins, the tail open like a fan.
Silhouette at 64px: one smooth S of a body with a white face at one end and a fan at the other
(unlike Magaryu's string of beads and the flat catfish of Namazura and Onamazu). Water/psychic."""
import math

NORMAL = {'pearl': (0.94, 0.93, 0.97), 'pink': (0.96, 0.78, 0.84), 'mint': (0.74, 0.92, 0.86),
          'face': (0.97, 0.94, 0.86), 'lacquer': (0.16, 0.12, 0.12), 'hollow': (0.03, 0.03, 0.04),
          'hair': (0.07, 0.07, 0.10), 'fin': (0.88, 0.20, 0.16), 'findark': (0.56, 0.08, 0.12),
          'lip': (0.82, 0.34, 0.38)}
# Shiny: gold scales and blue fins.
SHINY = {**NORMAL, 'pearl': (0.97, 0.82, 0.36), 'pink': (0.98, 0.66, 0.24), 'mint': (1.0, 0.94, 0.62),
         'fin': (0.20, 0.42, 0.90), 'findark': (0.10, 0.20, 0.60)}

# The spine, from the neck to the root of the tail, and the body's radius at each end.
SPINE = [(-0.7, -0.3, -0.7), (-0.05, -0.2, -1.0), (0.7, -0.05, -0.8), (1.0, 0.1, -0.2), (0.55, 0.25, 0.25), (-0.1, 0.35, 0.4),
         (-0.55, 0.45, 0.8), (-0.3, 0.5, 1.3)]
R0, R1 = 0.38, 0.11


# Hand-placed pixels (make_art.apply_pixels): the Noh face of a young woman looking straight ahead: high
# brows, level eyes with a lash under each, a touch of nose and a closed straight mouth (no smile, no sorrow).
_FACE = [
    ((13, 42), ['....gg...gg.']),
    ((13, 44), ['..kkk...kkk.',
                '...k.....k..']),
    ((13, 47), ['......g.....']),
    ((13, 49), ['.....qqqe...']),
]
_ICON = [((11, 13), ['K.K'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'g': (176, 174, 167), 'q': (50, 50, 60), 'e': (252, 248, 239), 'K': (65, 65, 65)},
          'front': {'box': (12, 0, 51, 56), 'patches': _FACE},
          'front2': {'box': (11, 0, 53, 56), 'patches': _FACE},
          'icon': {'box': (6, 2, 26, 30), 'patches': _ICON},
          'icon2': {'box': (6, 1, 26, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    pearl = k.toon('pearl', c['pearl'], steps=(0.6, 0.82, 1.0), glint=0.5)
    pink = k.toon('pink', c['pink'], two_tone=True)
    mint = k.toon('mint', c['mint'], two_tone=True)
    face_m = k.toon('face', c['face'], two_tone=True)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    hair = k.toon('hair', c['hair'], two_tone=True)
    fin = k.toon('fin', c['fin'], two_tone=True)
    findark = k.flat('findark', c['findark'])
    lip = k.flat('lip', c['lip'])
    k.set_light((-0.7, -0.6, 0.25))

    # The body: one smooth tube along the spine, bands of shell colour on it.
    pts = [k.Vector(p) for p in SPINE]
    n = 8
    total = (len(pts) - 1) * n
    for s in range(len(pts) - 1):
        for j in range(n):
            i = s * n + j
            t = i / total
            p = pts[s].lerp(pts[s + 1], j / n)
            r = R0 + (R1 - R0) * t
            k.ellipsoid(p, (r, r, r), (pink if i % 8 == 3 else mint) if i % 4 == 3 else pearl, segments=20)
    # Red fins: a row along the back, a pair at the breast, and the tail open like a fan.
    for s in (1, 2, 3, 4, 5):
        p = pts[s].lerp(pts[s + 1], 0.5)
        r = R0 + (R1 - R0) * (s + 0.5) / (len(pts) - 1)
        k.ellipsoid((p.x, p.y + 0.05, p.z + r * 1.1), (0.2, 0.05, 0.22), fin)
    for side in (-1, 1):
        k.ellipsoid((-0.35 + side * 0.4, -0.4, -1.05), (0.26, 0.06, 0.14), fin, rot=(0, math.radians(side * 30), 0))
    root = pts[-1]
    for a_deg in (10, 45, 80, 115, 150):
        a = math.radians(a_deg)
        tip = root + k.Vector((0.7 * math.cos(a), 0.05, 0.7 * math.sin(a)))
        mid = root.lerp(tip, 0.55)
        k.ellipsoid(mid, (0.4, 0.05, 0.13), fin, rot=(0, -a, 0))
        k.rod(root, tip, 0.02, findark)

    # The face where the fish's head should be: a young woman's Noh face, hair streaming back.
    before = k.snapshot()
    shell = k.mask_shell(face_m, lacquer, width=0.5, depth=0.36, height=0.66)
    for x in (-0.19, 0.19):
        k.hole(shell, x, 0.1, (0.1, 0.022), backing=hollow)
    k.bump(shell, 0, -0.08, (0.04, 0.05, 0.1), face_m, lift=0.02)
    k.front_only(k.ellipsoid(k.on_face(shell, 0, -0.33, lift=0.015), (0.07, 0.02, 0.03), lip))
    k.ellipsoid((0, 0.18, 0.1), (0.52, 0.44, 0.58), hair)
    for side in (-1, 1):
        k.front_only(k.ellipsoid(k.on_face(shell, side * 0.36, 0.3, lift=0.03), (0.18, 0.06, 0.38), hair, rot=(0, math.radians(side * 12), 0)))
    k.transform(k.since(before), offset=(-0.78, -0.62, -0.5), scale=0.95)
    for dx in (-0.2, 0.0, 0.2):   # the hair lying back along the spine
        for a, b, r in zip(pts[:4], pts[1:5], (0.14, 0.12, 0.09, 0.06)):
            up = k.Vector((dx * 0.7, 0.08, 0.34))
            k.rod(a + up, b + up * 0.8, r, hair)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -12, 'front_el': 10, 'side_az': -70}
