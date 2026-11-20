"""Jatai: the jatai, Toriyama Sekien's sash that turns into a snake (left by a jealous woman),
with a Hashihime mask (Noh's jealous woman of the bridge) for its head (Lavaridge segment,
docs/research/mask-designs.md). Not the Dojoji serpent (kept for the Omotelle line) and not the
deigan mask (Deigloom). A thick patterned obi coiled in an S, rising into the mask: reddened
face, glaring gold eyes, half-open mouth with a forked red tongue, loose black hair; an obijime
cord knotted round it. Masked serpent; poison/ghost."""
import math

NORMAL = {'face': (0.94, 0.84, 0.80), 'blush': (0.86, 0.42, 0.40), 'lacquer': (0.16, 0.06, 0.05),
          'gold': (0.92, 0.74, 0.22), 'pupil': (0.03, 0.02, 0.02), 'socket': (0.40, 0.08, 0.10),
          'gum': (0.45, 0.05, 0.10), 'tooth': (0.95, 0.92, 0.84), 'tongue': (0.85, 0.10, 0.14),
          'hair': (0.06, 0.05, 0.07), 'obi': (0.38, 0.18, 0.52), 'obidark': (0.20, 0.08, 0.30),
          'pattern': (0.92, 0.76, 0.30), 'cord': (0.85, 0.22, 0.30)}
SHINY = {**NORMAL, 'obi': (0.20, 0.42, 0.40), 'obidark': (0.08, 0.22, 0.22), 'pattern': (0.88, 0.88, 0.92),
         'cord': (0.95, 0.70, 0.20)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.3, weathered=0.15)
    blush = k.flat('blush', c['blush'])
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    tongue = k.toon('tongue', c['tongue'], two_tone=True)
    hair = k.toon('hair', c['hair'], two_tone=True)
    obi = k.toon('obi', c['obi'], two_tone=True)
    obidark = k.flat('obidark', c['obidark'])
    pattern = k.flat('pattern', c['pattern'])
    cord = k.toon('cord', c['cord'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.1))
    # The obi: a thick flat band coiled in an S from the ground up behind the mask.
    pts = []
    for i in range(26):
        t = i / 25
        pts.append(k.Vector((0.85 * math.sin(t * 2.6 * math.pi) * (1 - 0.45 * t), 0.45 + 0.3 * math.cos(t * 2.6 * math.pi),
                             -1.35 + 1.4 * t)))
    for i, p in enumerate(pts):
        w = 0.34 - 0.08 * (i / 25)
        k.ellipsoid(p, (w, w * 0.8, w * 0.7), obi)
        if i % 3 == 0:   # gold pattern bands, every few segments: the scales
            k.ellipsoid(p + k.Vector((0, -w * 0.5, 0)), (w * 0.75, w * 0.45, w * 0.18), pattern)
        elif i % 3 == 1:
            k.ellipsoid(p + k.Vector((0, -w * 0.55, 0)), (w * 0.5, w * 0.35, w * 0.12), obidark)
    k.ellipsoid(pts[0] + k.Vector((0.25, -0.1, -0.05)), (0.3, 0.12, 0.1), obi)   # the sash's tail end on the ground
    # The obijime cord knotted round the coil.
    k.ring_rope((pts[8].x, pts[8].y, pts[8].z), 0.34, 0.06, cord, rot=(90, 0, 0), segments=14)
    # Loose black hair behind the mask.
    k.ellipsoid((0, 0.2, 1.05), (0.62, 0.3, 0.2), hair)
    for x in (-0.5, -0.3, 0.3, 0.5):
        k.ellipsoid((x, 0.22, 0.25), (0.1, 0.06, 0.62), hair)
    # The Hashihime mask: reddened, glaring gold eyes, half-open mouth, forked tongue.
    shell = k.mask_shell(face_m, lacquer, width=0.6, depth=0.4, height=0.78)
    k.transform([shell], offset=(0, 0, 0.35))
    for x in (-0.32, 0.32):
        k.bump(shell, x, -0.08, (0.12, 0.05, 0.09), blush, lift=0.0)
    k.glare_eyes(shell, 0.22, 0.12, 0.13, gold, pupil, socket, tilt=24)
    k.fanged_mouth(shell, -0.38, 0.26, 0.13, pupil, gum, tooth, upper=4, lower=3)
    m = k.on_face(shell, 0, -0.42, lift=0.06)
    base = k.Vector((m.x, m.y, m.z + 0.35))
    k.front_only(k.spike(base, base + k.Vector((0.0, -0.4, -0.22)), 0.05, tongue))
    for side in (-1, 1):
        k.front_only(k.spike(base + k.Vector((0, -0.36, -0.2)), base + k.Vector((side * 0.1, -0.55, -0.3)), 0.025, tongue))
    k.cord_holes(shell, lacquer)
    return {'kind': 'beast', 'size': 0.86, 'front_az': -22, 'side_az': -75}
