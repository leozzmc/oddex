"""Namazura: a catfish wearing the white okina mask (Lavaridge segment, docs/research/mask-designs.md),
after the namazu-e prints of the earthquake catfish and the Otsu-e 'gourd and catfish'. Fusion:
Okinoir's okina face in white, filling the frame (after the user's 64px review): crescent eyes
under huge tufted brows, a big white beard, two long dark catfish whiskers sweeping out to both
sides; a flat mud-grey fish body and tail behind; the gourd that is meant to catch it. Imagery
only: no keystone god. Masked fish; water/ground."""
import math

NORMAL = {'face': (0.95, 0.92, 0.82), 'lacquer': (0.18, 0.12, 0.08), 'tuft': (0.99, 0.99, 0.97),
          'hollow': (0.03, 0.03, 0.03), 'body': (0.42, 0.42, 0.38), 'belly': (0.66, 0.62, 0.52),
          'barbel': (0.24, 0.22, 0.20), 'gourd': (0.82, 0.62, 0.28), 'cord': (0.75, 0.15, 0.12)}
# Shiny: a golden catfish in a gilded mask (the user asked for a shiny that clearly differs).
SHINY = {**NORMAL, 'face': (0.98, 0.80, 0.40), 'tuft': (1.0, 0.96, 0.80), 'body': (0.94, 0.70, 0.18), 'belly': (1.0, 0.90, 0.55), 'barbel': (0.58, 0.36, 0.08),
         'gourd': (0.30, 0.62, 0.62), 'cord': (0.20, 0.30, 0.75)}


# Hand-placed pixels (make_art.apply_pixels): the catfish's sluggish eyes, a straight dark lid over a narrower eye.
_FACE = [
    ((25, 34), ['kkkk',
                'ckkc']),
    ((35, 34), ['kkkk',
                'ckkc']),
]
_ICON = [
    ((12, 20), ['KK..KK']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'c': (199, 196, 186),
                   'K': (65, 65, 65)},
          'front': {'box': (2, 20, 62, 56), 'patches': _FACE},
          'front2': {'box': (1, 21, 63, 56), 'patches': [((x, y + 0), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (3, 13, 29, 30), 'patches': _ICON},
          'icon2': {'box': (3, 12, 29, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    tuft = k.toon('tuft', c['tuft'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    body = k.toon('body', c['body'], two_tone=True)
    belly = k.toon('belly', c['belly'], two_tone=True)
    barbel = k.toon('barbel', c['barbel'], two_tone=True)
    gourd = k.toon('gourd', c['gourd'], glint=0.3, two_tone=True)
    cord = k.flat('cord', c['cord'])
    k.set_light((-0.75, -0.6, 0.0))
    # The flat catfish body behind the mask (only its back, fins and tail show past the face).
    k.ellipsoid((0, 0.7, -0.2), (0.85, 0.7, 0.45), body)
    k.ellipsoid((0, 0.8, -0.45), (0.66, 0.75, 0.2), belly)
    k.ellipsoid((0, 1.35, 0.05), (0.5, 0.12, 0.42), body)
    k.spike((0, 0.55, 0.3), (0.1, 1.0, 0.95), 0.16, body)   # dorsal fin over the head
    for side in (-1, 1):
        k.ellipsoid((side * 0.95, 0.35, -0.5), (0.32, 0.12, 0.09), body, rot=(0, math.radians(side * 30), 0))
    # The white okina mask, filling the frame: crescent eyes under huge tufted brows.
    shell = k.mask_shell(face_m, lacquer, width=1.0, depth=0.5, height=0.84)
    for x in (-0.33, 0.33):
        k.hole(shell, x, 0.12, (0.18, 0.05), backing=hollow)
        for dx, dz, r in ((-0.14, 0.0, 0.13), (0.0, 0.1, 0.15), (0.14, 0.02, 0.13), (0.24 * (1 if x > 0 else -1), -0.06, 0.1)):
            k.front_only(k.ellipsoid(k.on_face(shell, x + dx, 0.38 + dz, lift=0.06), (r, r * 0.75, r * 0.8), tuft))
    k.bump(shell, 0, -0.08, (0.13, 0.12, 0.16), face_m, lift=0.02)
    k.hole(shell, 0, -0.36, (0.34, 0.06), backing=hollow)
    # A big white okina beard hanging from the chin.
    for x, z, r in ((0, -0.6, 0.2), (-0.17, -0.55, 0.15), (0.17, -0.55, 0.15), (-0.08, -0.8, 0.15), (0.08, -0.8, 0.15),
                    (0, -0.98, 0.12)):
        k.front_only(k.ellipsoid((x, -0.42, z), (r, r * 0.7, r), tuft))
    # Two long dark catfish whiskers sweeping out to both sides from the upper lip.
    for side in (-1, 1):
        root = k.on_face(shell, side * 0.22, -0.28, lift=0.03)
        pts = [root, root + k.Vector((side * 0.5, -0.12, 0.08)), root + k.Vector((side * 1.0, -0.1, 0.1)),
               root + k.Vector((side * 1.45, -0.02, -0.02)), root + k.Vector((side * 1.7, 0.05, -0.25))]
        for a, b, r in zip(pts, pts[1:], (0.08, 0.07, 0.055, 0.04)):
            k.front_only(k.rod(a, b, r, barbel))
    # The gourd hanging at its side on a red cord.
    k.rod((-0.8, 0.0, -0.3), (-1.0, -0.15, -0.62), 0.025, cord)
    k.ellipsoid((-1.02, -0.18, -0.72), (0.13, 0.13, 0.14), gourd)
    k.ellipsoid((-1.05, -0.2, -1.0), (0.2, 0.2, 0.22), gourd)
    k.cord_holes(shell, lacquer)
    return {'kind': 'beast', 'size': 0.92, 'front_az': -14, 'side_az': -75}
