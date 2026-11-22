"""Omotelle: Ko-omote (Noh, the young woman). Quiet and unsettling: chalk-white, expressionless,
small hollow eyes, painted high brows, a faint smile showing blackened teeth (ohaguro), two
barely-there bumps on the brow where horns will come. Mask body; psychic/dragon."""

NORMAL = {'face': (0.96, 0.95, 0.92), 'lacquer': (0.16, 0.06, 0.05), 'hollow': (0.02, 0.02, 0.03),
          'ink': (0.06, 0.05, 0.06), 'lip': (0.72, 0.08, 0.12), 'hair': (0.05, 0.05, 0.07)}
SHINY = {**NORMAL, 'face': (0.98, 0.86, 0.90), 'hair': (0.80, 0.80, 0.84), 'lip': (0.40, 0.20, 0.55)}


# Hand-placed pixels (make_art.apply_pixels): heavy-lidded downcast eyes, a straight dark lid over
# a narrower eye, in the outline colour (which the shiny palette keeps).
_EYES = [((26, 27), ['kkkkkk', 'wkkkkw', '..w...']), ((36, 27), ['kkkkkk', 'ckkkkc'])]
_ICON = [((10, 17), ['WKKKWWKKKW'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'w': (250, 249, 245), 'c': (233, 232, 229), 'W': (255, 255, 255), 'K': (65, 65, 65)},
          'front': {'box': (12, 5, 52, 56), 'patches': _EYES},
          'front2': {'box': (12, 7, 52, 56), 'patches': [((x, y + 1), rows) for (x, y), rows in _EYES]},
          'icon': {'box': (6, 6, 25, 30), 'patches': _ICON},
          'icon2': {'box': (6, 5, 25, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=(0.62, 0.85, 1.0), weathered=0.12)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    ink = k.flat('ink', c['ink'])
    lip = k.flat('lip', c['lip'])
    hair = k.toon('hair', c['hair'], two_tone=True)
    k.set_light((-0.6, -0.75, 0.1))

    face = k.mask_shell(face_m, lacquer, width=0.66, depth=0.42, height=0.92)
    for x in (-0.24, 0.24):
        k.hole(face, x, 0.12, (0.13, 0.055), backing=hollow)
        p = k.on_face(face, x, 0.5, lift=0.005)
        k.front_only(k.ellipsoid(p, (0.07, 0.02, 0.045), ink))
    k.bump(face, 0, -0.08, (0.07, 0.07, 0.16), face_m, lift=0.01)
    # A faint closed smile parted on blackened teeth.
    k.hole(face, 0, -0.45, (0.17, 0.05), backing=ink)
    for z, sx in ((-0.42, 0.15), (-0.48, 0.13)):
        p = k.on_face(face, 0, z, lift=0.0)
        k.front_only(k.ellipsoid((p.x, p.y - 0.01, p.z), (sx, 0.03, 0.02), lip))
    for x in (-0.18, 0.18):
        k.bump(face, x, 0.72, (0.05, 0.05, 0.05), face_m, lift=0.0)
    # Black hair parted at the top and falling behind.
    k.ellipsoid((0, -0.12, 0.84), (0.7, 0.36, 0.22), hair)
    for x in (-0.55, 0.55):
        k.ellipsoid((x * 1.15, 0.0, -0.15), (0.2, 0.14, 0.95), hair)   # framing the face
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.8, 'front_az': -12}
