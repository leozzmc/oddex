"""Yukinba: the snow hag (yukinba, the one-legged old woman of snowy nights in Ehime folklore)
and the mountain hag of Noh "Yamamba" who walks every peak through the snow; a yokai, not a
deity. Sootopolis segment, Yamambrr's evolution at Lv32, replaces Sealeo on Juan's team
(docs/research/mask-designs.md, "Yukinba 的 Brief", option A). Yamambrr after a whole winter of
walking: a straw cape crusted with ice has made her a cone, only one foot in a snowshoe is left
under it, her staff has frozen into a pillar of ice taller than she is, and her hair into a
spray of icicles (icicles, not a crown). The lined face has gone blue-white; small gold eyes
glare, the gap-toothed mouth hangs open breathing frost. Silhouette at 64px: an upright triangle
with a spiked head and a tall staff beside it. Ice/ghost."""
import math

NORMAL = {'face': (0.70, 0.80, 0.90), 'lacquer': (0.10, 0.14, 0.24), 'gold': (0.95, 0.78, 0.25),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.10, 0.12, 0.26), 'gum': (0.36, 0.06, 0.08),
          'tooth': (0.92, 0.90, 0.80), 'straw': (0.82, 0.68, 0.34), 'strawdark': (0.50, 0.38, 0.16),
          'ice': (0.60, 0.84, 0.98), 'snow': (0.96, 0.98, 1.0), 'foot': (0.42, 0.30, 0.20)}
# Shiny: a blood-red cape on a sunset snowfield, the ice gone pink-violet.
SHINY = {**NORMAL, 'straw': (0.66, 0.14, 0.12), 'strawdark': (0.36, 0.06, 0.08), 'ice': (0.86, 0.66, 0.96),
         'face': (0.86, 0.80, 0.92)}


# Hand-placed pixels (make_art.apply_pixels): no smile. Small gold eyes with pinpoint pupils glaring from under slate brows that
# slope down to the nose, and a gap-toothed mouth hanging open, its corners turned down.
_FACE = [
    ((31, 13), ['sss..',
                'ccsss',
                'ckccb',
                'buubb']),
    ((39, 13), ['..sss',
                'ssscc',
                'bcckc',
                'bbuub']),
    ((33, 22), ['.kkkkkkk.',
                '.kfkkkfk.',
                '.krrrrrk.',
                '.krfrrrk.',
                'kkkkkkkkk',
                'kgggggggk']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((31, 14), ['sss..',
                'ccsss',
                'ckccb',
                'buubb']),
    ((39, 14), ['..sss',
                'ssscc',
                'bcckc',
                'bbuub']),
    ((33, 23), ['.kkkkkkk.',
                '.kfkkkfk.',
                '.krrrrrk.',
                '.krfrrrk.',
                'kkkkkkkkk',
                'kgggggggk']),
]
_ICON = [
    ((15, 10), ['YK..KY']),
]
PIXELS = {'keys': {'k': (28, 18, 22),
                   's': (60, 71, 92),
                   'c': (234, 215, 158),
                   'b': (173, 184, 194),
                   'u': (89, 97, 139),
                   'g': (126, 134, 142),
                   'r': (112, 46, 53),
                   'f': (251, 253, 255),
                   'K': (65, 65, 65),
                   'Y': (246, 246, 139)},
          'front': {'box': (12, 0, 52, 56), 'patches': _FACE},
          'front2': {'box': (10, 0, 53, 56), 'patches': _FACE2},
          'icon': {'box': (6, 3, 25, 30), 'patches': _ICON},
          'icon2': {'box': (6, 2, 25, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    straw = k.toon('straw', c['straw'], two_tone=True)
    strawdark = k.toon('strawdark', c['strawdark'], two_tone=True)
    ice = k.toon('ice', c['ice'], two_tone=True, glint=0.5)
    snow = k.flat('snow', c['snow'])
    foot = k.toon('foot', c['foot'], two_tone=True)
    k.set_light((-0.8, -0.5, 0.0))

    # The head: Yamambrr's lined face, frostbitten, with icicles for hair swept up and back.
    before = k.snapshot()
    face = k.mask_shell(face_m, lacquer, width=0.66, depth=0.44, height=0.88)
    k.brows(face, 0.27, 0.42, 0.22, face_m, frown=25, thick=0.09)
    k.glare_eyes(face, 0.27, 0.2, 0.15, gold, pupil, socket)
    k.bump(face, 0, -0.05, (0.11, 0.12, 0.2), face_m, lift=0.03)
    k.wrinkles(face, lacquer, [(-0.35, -0.15, 0.04, 0.22, -20), (0.35, -0.15, 0.04, 0.22, 20),
                               (0, 0.6, 0.3, 0.03, 0), (0, 0.68, 0.25, 0.03, 0)])
    k.fanged_mouth(face, -0.5, 0.24, 0.2, pupil, gum, tooth, upper=2, lower=3)
    for i in range(9):
        a = math.radians(-100 + i * 25)
        base = (0.5 * math.sin(a), 0.2, 0.55 * math.cos(a))
        tip = (1.2 * math.sin(a), 0.5, 1.2 * math.cos(a) + 0.1)
        k.spike(base, tip, 0.15, ice)
        k.ellipsoid(base, (0.2, 0.16, 0.2), snow)
    k.ellipsoid((0, 0.3, 0.05), (0.55, 0.42, 0.62), snow)   # the back of the head, white hair packed with snow
    k.transform(k.since(before), offset=(0.08, -0.3, 0.74), scale=0.92)
    # A frozen breath hanging in front of the mouth.
    for x, z, s in ((-0.4, 0.2, 0.14), (-0.62, 0.34, 0.1), (-0.5, 0.02, 0.08)):
        k.ellipsoid((x, -0.85, z), (s, s * 0.6, s * 0.8), snow)

    # The straw cape: three flaring tiers, each hem ragged and hung with ice.
    for i, (z, r0, r1, m) in enumerate(((-0.05, 0.34, 0.66, straw), (-0.5, 0.52, 0.86, strawdark), (-0.95, 0.7, 1.04, straw))):
        k.cone((0.08, 0.1, z), r1, 0.62, m, radius2=r0, segments=24)
        n = 10 + 2 * i
        for j in range(n):
            a = 2 * math.pi * (j + 0.5 * i) / n
            p = k.Vector((0.08 + r1 * math.cos(a), 0.1 + r1 * math.sin(a), z - 0.3))
            k.spike(p + k.Vector((0, 0, 0.1)), p + k.Vector((0.04 * math.cos(a), 0.04 * math.sin(a), -0.22)), 0.07, ice if j % 2 else m)
    for x, y, z, s in ((-0.38, -0.05, 0.22, 0.2), (0.52, 0.0, 0.2, 0.18), (0.1, 0.4, 0.26, 0.22)):
        k.ellipsoid((x, y, z), (s, s, s * 0.5), snow)   # snow on the shoulders
    # The one foot left under the cape, in a round snowshoe.
    k.rod((0.08, 0.0, -1.15), (0.1, -0.1, -1.55), 0.1, foot)
    k.torus((0.1, -0.15, -1.6), 0.28, 0.05, strawdark)
    k.rod((-0.18, -0.15, -1.6), (0.38, -0.15, -1.6), 0.03, strawdark)
    # The staff, frozen into a pillar of ice taller than she is.
    k.rod((-1.12, 0.0, -1.6), (-1.02, 0.0, 1.25), 0.1, ice)
    k.spike((-1.02, 0.0, 1.2), (-0.98, 0.0, 1.85), 0.13, ice)
    for z, s in ((-0.6, 0.15), (0.3, 0.17), (0.95, 0.14)):
        k.ellipsoid((-1.07, 0.0, z), (s, s, s * 1.5), ice)
    k.ellipsoid((-1.1, 0.0, -1.6), (0.24, 0.24, 0.08), snow)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -16, 'front_el': 8, 'side_az': -70}
