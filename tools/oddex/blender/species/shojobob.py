"""Shojobob: Shojo (Noh, "Shojo"), the red-faced sea spirit who dances on the waves. The mask
floats tipped back on a ripple like a lily pad, red hair fanned out on the water, a small sake
jar bobbing beside it. Mask body; water/fairy."""
import math

NORMAL = {'face': (0.90, 0.20, 0.12), 'lacquer': (0.20, 0.06, 0.05), 'hair': (0.70, 0.08, 0.10),
          'water': (0.25, 0.55, 0.95), 'foam': (0.85, 0.95, 1.0), 'ink': (0.06, 0.04, 0.05),
          'jar': (0.95, 0.93, 0.86), 'lip': (0.55, 0.05, 0.08)}
# Moonlit sea: pink face, golden hair.
SHINY = {**NORMAL, 'face': (0.98, 0.62, 0.70), 'hair': (0.95, 0.75, 0.25), 'water': (0.35, 0.30, 0.80)}


def build(k, c):
    face_m = k.toon('face', c['face'], glint=0.6)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hair = k.toon('hair', c['hair'])
    water = k.toon('water', c['water'])
    foam = k.toon('foam', c['foam'], two_tone=True)
    ink = k.flat('ink', c['ink'])
    jar = k.toon('jar', c['jar'], two_tone=True)
    lip = k.flat('lip', c['lip'])

    before = k.snapshot()
    face = k.mask_shell(face_m, lacquer, width=0.72, depth=0.4, height=0.86)
    # Round boyish face: full cheeks, small nose, smiling crescent eyes and an upturned mouth.
    for x in (-0.36, 0.36):
        k.bump(face, x, -0.2, (0.2, 0.1, 0.16), face_m)
    k.bump(face, 0, -0.02, (0.1, 0.09, 0.12), face_m, lift=0.01)
    for x in (-0.25, 0.25):
        p = k.on_face(face, x, 0.16, lift=0.01)
        k.front_only(k.ellipsoid(p, (0.15, 0.04, 0.06), ink, rot=(0, math.radians(18 if x < 0 else -18), 0)))
    k.hole(face, 0, -0.42, (0.27, 0.1), backing=lip)
    for x in (-0.27, 0.27):
        p = k.on_face(face, x, -0.36, lift=0.0)
        k.front_only(k.ellipsoid(p, (0.07, 0.03, 0.05), lip))
    for x in (-0.42, 0.42):
        p = k.on_face(face, x, -0.12, lift=0.02)
        k.front_only(k.ellipsoid(p, (0.1, 0.03, 0.06), lip))
    # Long red hair fanned out behind the mask.
    for i in range(13):
        a = math.radians(-78 + i * 13)
        k.ellipsoid((1.0 * math.sin(a), 0.3, 0.95 * math.cos(a) - 0.05), (0.14, 0.06, 0.45), hair,
                    rot=(0, -a, 0))
    k.cord_holes(face, lacquer)
    mask_parts = k.since(before)
    # Tip the mask back so it floats face-up, then lay the sea around it.
    k.transform(mask_parts, offset=(0, 0, 0.45), rot_x=-38)
    k.torus((0, 0, 0.05), 1.05, 0.09, water, rot=(0, 0, 0))
    k.torus((0, 0, 0.05), 1.35, 0.06, foam, rot=(0, 0, 0))
    k.ellipsoid((0, 0, 0.0), (1.2, 1.2, 0.06), water)
    # A small sake jar bobbing on the water.
    k.ellipsoid((1.05, -0.55, 0.28), (0.17, 0.17, 0.22), jar)
    k.cylinder((1.05, -0.55, 0.52), 0.07, 0.12, jar)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -25, 'front_el': 30, 'squash': (1.06, 1.06, 0.92)}
