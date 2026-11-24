"""Yukijoro: the snow woman (yuki-onna, also yuki-joro) of Japanese folklore, the white woman of
snowy nights whose breath freezes travellers; the best-known telling is "Yuki-Onna" in Lafcadio
Hearn's Kwaidan (1904, public domain). A yokai, not a deity. League segment, replaces Glalie and
Walrein on Glacia's team (docs/research/mask-designs.md, "Yukijoro 的 Brief"). Second design, the
user's own direction (2026-11-24): only the upper half of a woman, and where her robe's skirt
should be, a whirl of blizzard that is the bulk of her. A wide cone of driving snow fills the
lower half of the frame, bands of it winding round; out of its top rise her shoulders and wide
sleeves and a large Noh face of a young woman; her hair is white and stiff with frost, falling
behind her shoulders (it does not hide her face, unlike Ichimai's black hair). Silhouette at
64px: a broad white triangle of storm with a head and two sleeves on top. Ice/fairy."""
import math

NORMAL = {'robe': (0.95, 0.96, 1.0), 'collar': (0.20, 0.28, 0.66), 'face': (0.99, 0.93, 0.82),
          'lacquer': (0.20, 0.16, 0.18), 'hollow': (0.03, 0.03, 0.05), 'hair': (0.52, 0.68, 0.94),
          'hairshade': (0.28, 0.40, 0.78), 'lip': (0.82, 0.30, 0.36), 'storm': (0.46, 0.66, 0.96),
          'stormdark': (0.24, 0.38, 0.80), 'snow': (0.97, 0.99, 1.0)}
# Shiny: a violet storm at dusk, a pink collar, hair the colour of old silver.
SHINY = {**NORMAL, 'collar': (0.70, 0.16, 0.36), 'hair': (0.80, 0.78, 0.74), 'hairshade': (0.52, 0.50, 0.50),
         'storm': (0.72, 0.52, 0.94), 'stormdark': (0.44, 0.26, 0.74)}


# Hand-placed pixels (make_art.apply_pixels): the fringe cut level across the brow, and under it the young
# woman's Noh face: two high smudged brows, two narrow level eyes, a touch of nose, a small closed mouth
# (no smile).
_FACE = [
    ((24, 5), ['cccccccccccc',
               'hchchchchchc']),
    ((24, 8), ['..gg....gg..',
               '...........e']),
    ((24, 11), ['..kkk..kkk..']),
    ((24, 14), ['......g.....']),
    ((24, 16), ['.....mm.....']),
]
_ICON = [((12, 7), ['K.K'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'c': (191, 215, 248), 'h': (144, 169, 228), 'g': (178, 173, 163), 'e': (254, 247, 234),
                   'm': (85, 76, 80), 'K': (65, 65, 65)},
          'front': {'box': (6, 0, 58, 56), 'patches': _FACE},
          'front2': {'box': (4, 0, 60, 56), 'patches': [((x, y + 1), rows) for (x, y), rows in _FACE] + [((29, 10), ['e']), ((36, 10), ['g'])]},
          'icon': {'box': (3, 2, 29, 30), 'patches': _ICON},
          'icon2': {'box': (3, 1, 29, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    robe = k.toon('robe', c['robe'], steps=(0.62, 0.84, 1.0))
    collar = k.toon('collar', c['collar'], two_tone=True)
    face_m = k.toon('face', c['face'], two_tone=True)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    hair = k.toon('hair', c['hair'], two_tone=True)
    hairshade = k.flat('hairshade', c['hairshade'])
    lip = k.flat('lip', c['lip'])
    storm = k.toon('storm', c['storm'], two_tone=True)
    stormdark = k.flat('stormdark', c['stormdark'])
    snow = k.flat('snow', c['snow'])
    k.set_light((-0.75, -0.6, 0.15))

    # The whirl of blizzard where her skirt should be: a broad cone, bands of snow winding round it,
    # gusts thrown off its foot.
    k.cone((0, 0.1, -0.6), 1.32, 1.8, storm, radius2=0.42, segments=32)
    turns, n = 1.6, 44
    for phase, mat, fat in ((0.0, snow, 1.0), (0.5, snow, 1.0), (0.25, stormdark, 0.75), (0.75, stormdark, 0.75)):   # two white arms, two dark
        for i in range(n):
            t = i / (n - 1)
            a = 2 * math.pi * (turns * t + phase)
            z = -1.45 + 1.7 * t
            r = 1.35 - 0.91 * t
            b = (0.22 - 0.08 * t) * fat
            k.ellipsoid((r * math.cos(a), 0.1 + r * math.sin(a), z), (b, b, b * 0.8), mat, segments=12)
    for a_deg, d, z, s in ((-150, 1.45, -1.4, 0.22), (-100, 1.42, -1.44, 0.2), (-50, 1.45, -1.4, 0.24), (30, 1.45, -1.4, 0.2), (150, 1.45, -1.4, 0.2)):
        a = math.radians(a_deg)
        k.ellipsoid((d * math.cos(a), 0.1 + d * math.sin(a), z), (s, s, s * 0.7), snow, segments=12)
    for side in (-1, 1):   # gusts thrown off the foot of the whirl, the way it turns
        k.spike((side * 1.25, -0.3, -1.3 + 0.25 * (side < 0)), (side * 1.68, -0.2, -1.1 + 0.45 * (side < 0)), 0.16, snow)
        k.spike((side * 0.95, -0.4, -0.6), (side * 1.4, -0.3, -0.3 - 0.3 * (side < 0)), 0.11, snow)

    # Her upper half: shoulders, a crossed collar, wide sleeves held a little away from her.
    U = 0.3   # how far her upper half stands above the whirl
    k.ellipsoid((0, 0.05, 0.12 + U), (0.5, 0.36, 0.42), robe)
    for side in (-1, 1):
        k.ellipsoid((side * 0.74, 0.0, -0.02 + U), (0.3, 0.2, 0.5), robe, rot=(0, math.radians(side * 32), 0))
        k.ellipsoid((side * 0.98, -0.02, -0.4 + U), (0.22, 0.21, 0.07), collar, rot=(0, math.radians(side * 32), 0))   # the cuff
        k.rod((side * 0.3, -0.33, 0.46 + U), (0.0, -0.42, -0.1 + U), 0.085, collar)   # the two sides of the collar crossing
    # The head: a large Noh face of a young woman. Her hair is the blue-white of old ice, cut level over
    # the brow, a long lock in front of each shoulder and the rest down her back, frost at the ends.
    k.ellipsoid((0, 0.22, 0.9 + U), (0.52, 0.42, 0.58), hair)
    for i, x in enumerate((-0.5, -0.25, 0.0, 0.25, 0.5)):
        z1 = -0.3 - 0.1 * (i % 2) + U
        k.rod((x, 0.5, 1.0 + U), (x * 1.3, 0.55, z1), 0.14, hairshade)
        k.spike((x * 1.3, 0.55, z1 + 0.05), (x * 1.4, 0.55, z1 - 0.3), 0.1, snow)
    for side in (-1, 1):
        k.rod((side * 0.44, -0.2, 0.95 + U), (side * 0.5, -0.3, 0.12 + U), 0.1, hair)
        k.spike((side * 0.5, -0.3, 0.16 + U), (side * 0.52, -0.3, -0.12 + U), 0.08, snow)
    before = k.snapshot()
    shell = k.mask_shell(face_m, lacquer, width=0.56, depth=0.4, height=0.72)
    for x in (-0.21, 0.21):
        k.hole(shell, x, 0.1, (0.11, 0.025), backing=hollow)
    k.bump(shell, 0, -0.08, (0.045, 0.05, 0.11), face_m, lift=0.02)
    k.front_only(k.ellipsoid(k.on_face(shell, 0, -0.36, lift=0.015), (0.08, 0.02, 0.035), lip))
    k.front_only(k.ellipsoid(k.on_face(shell, 0, 0.58, lift=0.03), (0.34, 0.07, 0.16), hair))   # the fringe, cut level
    k.transform(k.since(before), offset=(0, -0.2, 0.9 + U), scale=0.86)
    return {'kind': 'beast', 'size': 0.96, 'front_az': -8, 'front_el': 6, 'side_az': -70}
