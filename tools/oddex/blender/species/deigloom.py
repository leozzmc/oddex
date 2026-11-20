"""Deigloom: Deigan (Noh, the woman whose eyes are painted gold as she turns toward a demon).
The same pale face as Omotelle, now with gilded eye rims that stare straight through you, a
slight frown, loosened strands of hair across the face, and horn buds. Mask body; psychic/ghost."""

NORMAL = {'face': (0.90, 0.92, 0.86), 'lacquer': (0.14, 0.06, 0.05), 'hollow': (0.02, 0.02, 0.03),
          'gold': (0.92, 0.74, 0.22), 'ink': (0.06, 0.05, 0.06), 'lip': (0.55, 0.06, 0.10),
          'hair': (0.05, 0.05, 0.07)}
SHINY = {**NORMAL, 'face': (0.78, 0.86, 0.96), 'gold': (0.55, 0.95, 0.80), 'hair': (0.82, 0.82, 0.88)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=(0.55, 0.8, 1.0), weathered=0.2)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    gold = k.toon('gold', c['gold'], two_tone=True)
    ink = k.flat('ink', c['ink'])
    lip = k.flat('lip', c['lip'])
    hair = k.toon('hair', c['hair'], two_tone=True)
    k.set_light((-0.65, -0.65, -0.1))

    face = k.mask_shell(face_m, lacquer, width=0.68, depth=0.44, height=0.96)
    for x in (-0.25, 0.25):
        p = k.on_face(face, x, 0.13, lift=0.01)
        k.front_only(k.ellipsoid(p, (0.19, 0.05, 0.12), gold))
        k.hole(face, x, 0.13, (0.09, 0.05), backing=hollow)
    k.brows(face, 0.24, 0.42, 0.14, face_m, frown=18, thick=0.05)
    k.bump(face, 0, -0.08, (0.07, 0.07, 0.17), face_m, lift=0.01)
    k.hole(face, 0, -0.47, (0.15, 0.05), backing=ink)
    p = k.on_face(face, 0, -0.43, lift=0.0)
    k.front_only(k.ellipsoid((p.x, p.y - 0.01, p.z), (0.16, 0.03, 0.02), lip))
    for x in (-0.2, 0.2):
        k.bump(face, x, 0.75, (0.07, 0.07, 0.09), gold, lift=0.0)
    # Hair parted at the top, a few loose strands fallen across the face.
    k.ellipsoid((0, -0.15, 0.86), (0.62, 0.32, 0.16), hair)
    for x in (-0.58, 0.58):
        k.ellipsoid((x * 1.12, 0.0, -0.15), (0.2, 0.14, 1.0), hair)   # framing the face
    for x0, x1 in ((-0.35, -0.42), (-0.12, -0.02), (0.3, 0.38)):
        a = k.on_face(face, x0, 0.75, lift=0.04)
        b = k.on_face(face, x1, -0.2, lift=0.04)
        k.front_only(k.rod(a, b, 0.02, hair))
    k.cord_holes(face, lacquer)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -12}
