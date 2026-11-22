"""Nobusumen: the nobusuma, the old bat of Japanese folklore that grows into a flying quilt, drops
over a traveller's face and blows out the lantern before it feeds (a yokai, not a deity).
Mossdeep segment, Komorimen's evolution, replaces Golbat and Crobat (docs/research/mask-designs.md,
"Nobusumen 的 Brief", option A). The bat mask sits in the middle of one square sheet of skin
stretched between four clawed limbs like a flying squirrel, dark red on the inside with the
finger bones showing; the mouth gapes with two long blood-drinking fangs, the eyes glow yellow;
a paper lantern it has just blown out hangs from its tail, still smoking. Silhouette at 64px: a
square with scalloped edges and a claw at each corner (Komorimen is a wide pair of bat wings).
Poison/flying."""
import math

NORMAL = {'face': (0.62, 0.58, 0.68), 'lacquer': (0.14, 0.10, 0.18), 'hollow': (0.03, 0.02, 0.04),
          'eye': (1.0, 0.86, 0.20), 'wing': (0.36, 0.22, 0.48), 'inner': (0.40, 0.08, 0.16),
          'rib': (0.16, 0.08, 0.22), 'fang': (0.97, 0.95, 0.88), 'paper': (0.93, 0.86, 0.66),
          'frame': (0.24, 0.16, 0.12), 'smoke': (0.62, 0.62, 0.66), 'gum': (0.40, 0.05, 0.10)}
# Shiny: a teal skin, and the lantern still burns with a blue ghost flame.
SHINY = {**NORMAL, 'wing': (0.14, 0.46, 0.44), 'inner': (0.10, 0.28, 0.34), 'rib': (0.05, 0.16, 0.18),
         'paper': (0.55, 0.80, 1.0), 'smoke': (0.30, 0.55, 1.0), 'eye': (0.70, 1.0, 0.60)}


# Hand-placed pixels (make_art.apply_pixels): two glaring yellow eyes under slanted lids, each with
# a slit pupil, and the gaping mouth with gums and two long fangs kept apart from them.
_FACE = [((27, 16), ['kkkaaa',
                     'kcckka',
                     'kckcck',
                     'akkkka']),
         ((35, 16), ['asskkk',
                     'akkcck',
                     'kcckck',
                     'skkkks']),
         ((30, 23), ['akkkkkks',
                     'kffggffk',
                     'kfmmmmfk',
                     'kfmmmmfk',
                     'akmmmmks',
                     'aakkkkss'])]
_ICON = [((15, 12), ['YY.YY']), ((15, 15), ['KWKWK', '.KKK.'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'c': (255, 239, 124), 'a': (164, 159, 171), 's': (120, 116, 125),
                   'g': (170, 80, 111), 'm': (48, 39, 56), 'f': (252, 249, 241),
                   'Y': (246, 246, 41), 'K': (65, 65, 65), 'W': (255, 255, 255)},
          'front': {'box': (5, 0, 59, 56), 'patches': _FACE},
          'front2': {'box': (3, 1, 61, 56), 'patches': [((x, y + 1), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (3, 3, 29, 30), 'patches': _ICON},
          'icon2': {'box': (3, 2, 29, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    eye = k.flat('eye', c['eye'])
    wing_m = k.toon('wing', c['wing'], two_tone=True)
    inner = k.toon('inner', c['inner'], two_tone=True)
    rib = k.toon('rib', c['rib'], two_tone=True)
    fang = k.toon('fang', c['fang'], two_tone=True)
    paper = k.toon('paper', c['paper'], two_tone=True)
    frame = k.flat('frame', c['frame'])
    smoke = k.flat('smoke', c['smoke'])
    gum = k.flat('gum', c['gum'])
    k.set_light((-0.75, -0.55, -0.1))

    # The quilt: one sheet between four limbs, each edge scalloped inward between the corners.
    V = k.Vector
    corners = [V((-1.5, 0.2, 1.05)), V((1.5, 0.2, 1.05)), V((1.15, 0.2, -1.15)), V((-1.15, 0.2, -1.15))]
    centre = V((0, 0.2, 0))
    rim = []
    for a, b in zip(corners, corners[1:] + corners[:1]):
        rim += [a, centre.lerp((a + b) / 2, 0.72)]
    rim.append(corners[0])
    k.membrane([centre + V((0, -0.03, 0))] + [p + V((0, -0.03, 0)) for p in rim], inner)   # the inside, facing the prey
    k.membrane([centre + V((0, 0.03, 0))] + [p + V((0, 0.03, 0)) for p in rim], wing_m)    # its back
    for p in corners:
        k.rod(centre, p, 0.05, rib)
        d = (p - centre).normalized()
        for spread in (-0.35, 0, 0.35):   # three claws at each corner
            side = V((-d.z, 0, d.x)) * spread
            k.spike(p, p + (d + side) * 0.3 + V((0, -0.08, 0)), 0.045, fang)
    for a, b in zip(corners, corners[1:] + corners[:1]):   # the finger bones in between
        k.rod(centre, centre.lerp((a + b) / 2, 0.7), 0.03, rib)

    # The bat mask in the middle: big ears, yellow eyes, a gaping mouth with two long fangs.
    face = k.mask_shell(face_m, lacquer, width=0.56, depth=0.4, height=0.64)
    for side in (-1, 1):
        k.hole(face, side * 0.22, 0.16, (0.14, 0.11), backing=hollow)
        p = k.on_face(face, side * 0.22, 0.16)
        k.front_only(k.ellipsoid((p.x, p.y + 0.02, p.z), (0.085, 0.03, 0.07), eye))
        k.front_only(k.ellipsoid((p.x, p.y - 0.01, p.z), (0.025, 0.02, 0.06), hollow))
        k.spike((side * 0.32, 0.05, 0.48), (side * 0.62, 0.15, 1.15), 0.16, face_m)
        k.front_only(k.spike((side * 0.34, -0.02, 0.56), (side * 0.58, 0.08, 1.02), 0.07, inner))
    k.hole(face, 0, -0.32, (0.26, 0.17), backing=hollow)
    g = k.on_face(face, 0, -0.2, lift=0.0)
    k.front_only(k.ellipsoid((g.x, g.y + 0.02, g.z), (0.24, 0.04, 0.05), gum))
    for side in (-1, 1):
        f = k.on_face(face, side * 0.13, -0.2, lift=0.02)
        k.front_only(k.spike((f.x, f.y, f.z + 0.02), (f.x, f.y - 0.03, f.z - 0.3), 0.055, fang))
    # The tail and the blown-out lantern hanging from it, a wisp of smoke rising.
    k.rod((0, 0.2, -0.95), (0.28, 0.05, -1.5), 0.04, rib)
    lc = V((0.28, 0.02, -1.82))
    k.ellipsoid(lc, (0.24, 0.24, 0.3), paper)
    for dz in (-0.3, 0.3):
        k.cylinder((lc.x, lc.y, lc.z + dz), 0.15, 0.06, frame)
    for dz in (-0.12, 0.0, 0.12):
        k.torus((lc.x, lc.y, lc.z + dz), 0.245, 0.015, frame)
    for i, (dx, dz, r) in enumerate(((0.3, 0.42, 0.07), (0.42, 0.62, 0.09), (0.34, 0.86, 0.07))):
        k.ellipsoid((lc.x + dx, lc.y - 0.05, lc.z + dz), (r, r, r), smoke)
    return {'kind': 'beast', 'size': 0.92, 'front_az': -14, 'front_el': 6, 'side_az': -62}
