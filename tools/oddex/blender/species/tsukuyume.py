"""Tsukuyume: moon-and-night imagery after Tsukuyomi (not the god), asleep and dreaming (Rustboro
batch, docs/research/mask-designs.md). Fusion: Omotelle's chalk-white maiden face with its eyes
closed into crescents, Deigloom's strands of hair (indigo) falling across it, and a large
silver crescent moon behind. Floats with no base. Mask; dark/fairy."""
import math

NORMAL = {'face': (0.86, 0.90, 0.98), 'lacquer': (0.12, 0.10, 0.20), 'hair': (0.16, 0.14, 0.38),
          'moon': (0.85, 0.88, 0.95), 'line': (0.10, 0.08, 0.18), 'lid': (0.88, 0.76, 0.40),
          'lip': (0.55, 0.20, 0.35), 'star': (1.0, 0.95, 0.70)}
SHINY = {**NORMAL, 'moon': (0.85, 0.20, 0.18), 'hair': (0.90, 0.90, 0.92), 'lid': (0.90, 0.35, 0.30)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.2)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hair = k.toon('hair', c['hair'], two_tone=True)
    moon = k.toon('moon', c['moon'], glint=0.5, two_tone=True)
    line = k.flat('line', c['line'])
    lid = k.flat('lid', c['lid'])
    lip = k.flat('lip', c['lip'])
    star = k.flat('star', c['star'])
    k.set_light((-0.7, -0.6, 0.1))

    # A crescent moon behind: a disc with an offset disc cut out of it.
    disc = k.cylinder((0.15, 0.4, 0.15), 0.95, 0.08, moon, rot=(math.pi / 2, 0, 0), segments=48)
    cutter = k.cylinder((0.55, 0.4, 0.4), 0.85, 0.3, moon, rot=(math.pi / 2, 0, 0), segments=48)
    k.cut(disc, cutter)
    for x, z in ((0.75, 0.9), (0.95, 0.45), (-0.9, 0.95)):
        k.ellipsoid((x, 0.3, z), (0.05, 0.03, 0.05), star)

    face = k.mask_shell(face_m, lacquer, width=0.58, depth=0.42, height=0.76)
    # Eyes closed into downward crescents, with a faint gold lid line.
    for side in (-1, 1):
        x0 = side * 0.22
        pts = [k.on_face(face, x0 + dx, 0.12 - 0.05 * (1 - (dx / 0.12) ** 2), lift=0.01) for dx in (-0.12, -0.06, 0, 0.06, 0.12)]
        for a, b in zip(pts, pts[1:]):
            k.front_only(k.rod(a, b, 0.03, line))
        k.front_only(k.ellipsoid(k.on_face(face, x0, 0.2, lift=0.0), (0.14, 0.03, 0.03), lid))
    m = k.on_face(face, 0, -0.42, lift=0.0)
    k.front_only(k.ellipsoid(m, (0.09, 0.03, 0.04), lip))
    # Hair: a dark cap and strands falling across the face and down the back.
    k.ellipsoid((0, 0.3, 0.42), (0.62, 0.32, 0.48), hair)
    for x, z0, z1 in ((-0.35, 0.55, -0.4), (-0.12, 0.65, 0.0), (0.2, 0.62, -0.2), (0.4, 0.5, -0.6)):
        a = k.on_face(face, x, z0, lift=0.02)
        b = k.on_face(face, x * 1.1, z1, lift=0.02)
        k.front_only(k.rod(a, b, 0.025, hair))
    for side in (-1, 1):
        for i in range(3):
            k.spike((side * (0.45 + 0.05 * i), 0.15, 0.2), (side * (0.55 + 0.08 * i), 0.25, -0.9 + 0.1 * i), 0.07, hair)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -16}
