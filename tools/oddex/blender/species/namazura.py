"""Namazura: a catfish wearing the white okina mask (Lavaridge segment, docs/research/mask-designs.md),
after the namazu-e prints of the earthquake catfish and the Otsu-e 'gourd and catfish'. Fusion:
Okinoir's okina face (smiling crescent eyes, tufted brows, the separately tied jaw) in white,
its beard drawn out into two long drooping catfish barbels; a flat mud-grey fish body and tail
behind; the gourd that is meant to catch it hanging at its side. Imagery
only: no keystone god. Masked fish; water/ground."""
import math

NORMAL = {'face': (0.95, 0.92, 0.82), 'lacquer': (0.18, 0.12, 0.08), 'tuft': (0.98, 0.98, 0.96),
          'hollow': (0.03, 0.03, 0.03), 'body': (0.42, 0.42, 0.38), 'belly': (0.66, 0.62, 0.52),
          'gourd': (0.82, 0.62, 0.28), 'cord': (0.75, 0.15, 0.12)}
SHINY = {**NORMAL, 'body': (0.62, 0.48, 0.22), 'belly': (0.88, 0.78, 0.50), 'gourd': (0.45, 0.65, 0.35)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.3, weathered=0.2)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    tuft = k.toon('tuft', c['tuft'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    body = k.toon('body', c['body'], two_tone=True)
    belly = k.toon('belly', c['belly'], two_tone=True)
    gourd = k.toon('gourd', c['gourd'], glint=0.3, two_tone=True)
    cord = k.flat('cord', c['cord'])
    k.set_light((-0.75, -0.6, 0.0))
    # The flat catfish body behind the mask, and its tail.
    k.ellipsoid((0, 0.7, -0.15), (0.78, 0.7, 0.45), body)
    k.ellipsoid((0, 0.85, -0.42), (0.62, 0.85, 0.2), belly)
    k.ellipsoid((0, 1.4, 0.0), (0.42, 0.12, 0.4), body, rot=(0, 0, 0))
    k.spike((0, 0.6, 0.18), (0, 1.2, 0.5), 0.14, body)   # dorsal fin
    for side in (-1, 1):
        k.ellipsoid((side * 0.75, 0.4, -0.45), (0.3, 0.12, 0.08), body, rot=(0, math.radians(side * 30), 0))
    # The white okina mask: crescent eyes, tufted brows, the tied-on jaw.
    shell = k.mask_shell(face_m, lacquer, width=0.82, depth=0.46, height=0.7)
    for x in (-0.27, 0.27):
        k.hole(shell, x, 0.14, (0.15, 0.045), backing=hollow)
        for dx, dz in ((-0.08, 0.0), (0.08, 0.02), (0.0, 0.08)):
            k.front_only(k.ellipsoid(k.on_face(shell, x + dx, 0.36 + dz, lift=0.05), (0.09, 0.07, 0.08), tuft))
    k.bump(shell, 0, -0.05, (0.11, 0.1, 0.14), face_m, lift=0.02)
    k.hole(shell, 0, -0.32, (0.3, 0.05), backing=hollow)
    # The beard drawn out into two long drooping barbels.
    for side in (-1, 1):
        root = k.on_face(shell, side * 0.18, -0.4, lift=0.02)
        # Swept out sideways like a long moustache, tips curling down (kept off the ground, so
        # they never read as legs).
        pts = [root, root + k.Vector((side * 0.4, -0.15, 0.06)), root + k.Vector((side * 0.85, -0.12, 0.02)),
               root + k.Vector((side * 1.15, -0.05, -0.18))]
        # White at the root (the okina's beard), darkening into catfish barbels.
        for (a, b, r), m in zip(zip(pts, pts[1:], (0.1, 0.085, 0.06)), (tuft, body, body)):
            k.front_only(k.rod(a, b, r, m))
    k.front_only(k.ellipsoid(k.on_face(shell, 0, -0.5, lift=0.04), (0.16, 0.08, 0.12), tuft))
    # The gourd hanging at its side on a red cord.
    k.rod((-0.7, 0.1, -0.2), (-0.95, -0.05, -0.5), 0.025, cord)
    k.ellipsoid((-0.98, -0.08, -0.62), (0.12, 0.12, 0.13), gourd)
    k.ellipsoid((-1.0, -0.1, -0.88), (0.18, 0.18, 0.2), gourd)
    k.cord_holes(shell, lacquer)
    return {'kind': 'beast', 'size': 0.92, 'front_az': -34, 'side_az': -75}
