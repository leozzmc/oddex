"""Kamikko: the head of an abandoned ichimatsu doll, floating on Mt. Pyre. Mossdeep segment, replaces
Shuppet (docs/research/mask-designs.md, "Kamikko → Kaminobi 的 Brief", option A): the public-domain
tale type of the doll whose hair keeps growing, no film character and no real temple's doll.
A round porcelain head with a chin-length black bob and a straight fringe, painted narrow eyes
that are hollow with a white glint, small red lips, a crack down one cheek, and only a torn scrap
of red kimono collar left under the chin. Silhouette at 64px: a ball of black bob hair round a
white face, with the little red collar under it. Ghost/fairy (stage 1 of 2)."""
import math

NORMAL = {'face': (0.97, 0.94, 0.90), 'hair': (0.07, 0.06, 0.09), 'hollow': (0.02, 0.02, 0.03),
          'glint': (1.0, 1.0, 1.0), 'lip': (0.80, 0.10, 0.12), 'crack': (0.16, 0.10, 0.12),
          'collar': (0.80, 0.12, 0.14), 'collardark': (0.48, 0.05, 0.08), 'blush': (0.96, 0.70, 0.68)}
# Shiny: silver-white hair and a blue collar.
SHINY = {**NORMAL, 'hair': (0.80, 0.82, 0.90), 'collar': (0.20, 0.36, 0.80), 'collardark': (0.10, 0.18, 0.48),
         'lip': (0.36, 0.30, 0.70)}

HEAD_C, HEAD_R = (0, 0, 0.1), (0.72, 0.66, 0.74)

# Hand-placed pixels (make_art.apply_pixels): the two painted eyes as clean almonds with one glint
# each, and the crack as a single thin line that starts clear of the eye.
_K = {'k': (28, 18, 22), 'w': (255, 255, 255), 'e': (252, 248, 244), 'd': (238, 235, 230), 'a': (209, 206, 202),
      'x': (111, 89, 97)}   # x, the crack: a colour the shiny palette keeps (the hair's turns silver)
_FACE = [((25, 28), ['eeeeeddd',
                     'eekkkkdd',
                     'ekkwkkkd',
                     'eekkkkdd',
                     'eeeedddd']),
         ((36, 28), ['dddaaaaa',
                     'ddkkkkaa',
                     'dkkwkkka',
                     'ddkkkkaa',
                     'dddaaaaa']),
         ((27, 33), ['.d..',
                     'xdd.',
                     '.xdd',
                     '..x.',
                     '.dx.',
                     '.x..',
                     '.x..',
                     '.dx.',
                     '..x.'])]
_ICON = [((11, 17), ['WWWWWWWWGG',
                     'WKKWWWKKGG',
                     'WWWWWWWWGG']),
         ((14, 22), ['W'])]
_IK = {'K': (65, 65, 65), 'W': (255, 255, 255), 'G': (189, 189, 189)}
PIXELS = {'keys': {**_K, **_IK},
          'front': {'box': (13, 10, 51, 56), 'patches': _FACE},
          'front2': {'box': (12, 12, 52, 56), 'patches': [((x, y + 1), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (7, 9, 25, 30), 'patches': _ICON},
          'icon2': {'box': (7, 8, 25, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def doll_face(k, c, mats, missing_eye=False, crack=1.0):
    """The doll's head and painted face at HEAD_C; shared with Kaminobi (bigger crack, one eye gone)."""
    face_m, hair, hollow, glint, lip, crack_m, blush = mats
    k.ellipsoid(HEAD_C, HEAD_R, face_m)

    def at(x, z, lift=0.0):
        return k.head_point(HEAD_C, HEAD_R, x, z, lift)

    for side in (-1, 1):
        gone = missing_eye and side > 0
        k.ellipsoid(at(side * 0.27, 0.12, 0.0), (0.19 if gone else 0.17, 0.05, 0.17 if gone else 0.075), hollow)
        if not gone:
            k.ellipsoid(at(side * 0.27, 0.12, 0.03), (0.045, 0.03, 0.04), glint)
        k.ellipsoid(at(side * 0.4, -0.16, 0.0), (0.11, 0.03, 0.07), blush)
    k.ellipsoid(at(0, -0.3, 0.01), (0.09, 0.04, 0.05), lip)
    # The crack: from under the left eye down to the jaw (longer and branching when crack > 1).
    pts = [(-0.3, 0.0), (-0.22, -0.14), (-0.3, -0.28), (-0.2, -0.44)]
    if crack > 1:
        pts = [(-0.38, 0.5), (-0.26, 0.3)] + pts + [(-0.05, -0.52)]
        k.rod(at(-0.22, -0.14, 0.02), at(-0.02, -0.3, 0.02), 0.03 * crack, crack_m)   # pulls the mouth askew
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        k.rod(at(x0, z0, 0.02), at(x1, z1, 0.02), 0.03 * crack, crack_m)
    # The bob: a cap over the top and back, a straight fringe, side locks to the chin.
    k.ellipsoid((0, 0.14, 0.2), (0.84, 0.74, 0.8), hair)
    k.ellipsoid((0, -0.3, 0.66), (0.62, 0.36, 0.2), hair)   # fringe
    for side in (-1, 1):
        k.ellipsoid((side * 0.7, -0.12, -0.05), (0.2, 0.36, 0.62), hair)


def materials(k, c):
    return (k.toon('face', c['face'], steps=(0.66, 0.88, 1.0)), k.toon('hair', c['hair'], two_tone=True),
            k.flat('hollow', c['hollow']), k.flat('glint', c['glint']), k.flat('lip', c['lip']),
            k.flat('crack', c['crack']), k.flat('blush', c['blush']))


def build(k, c):
    mats = materials(k, c)
    collar = k.toon('collar', c['collar'], two_tone=True)
    collardark = k.flat('collardark', c['collardark'])
    k.set_light((-0.7, -0.6, 0.2))
    doll_face(k, c, mats)
    # The torn scrap of collar: a short flared neck with ragged points.
    k.cone((0, 0.02, -0.72), 0.2, 0.36, collar, radius2=0.4, rot=(math.pi, 0, 0), segments=24)
    for i in range(7):
        a = 2 * math.pi * i / 7
        k.spike((0.36 * math.cos(a), 0.02 + 0.36 * math.sin(a), -0.86), (0.44 * math.cos(a), 0.02 + 0.44 * math.sin(a), -1.1 - 0.08 * (i % 2)), 0.09, collar)
    k.rod((-0.02, -0.34, -0.6), (0.1, -0.4, -0.9), 0.035, collardark)   # the fold of the collar
    return {'kind': 'beast', 'size': 0.74, 'front_az': -14, 'front_el': 6, 'side_az': -70}
