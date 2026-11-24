"""Yukijoro: the snow woman (yuki-onna, also yuki-joro) of Japanese folklore, the white woman of
snowy nights whose breath freezes travellers; the best-known telling is "Yuki-Onna" in Lafcadio
Hearn's Kwaidan (1904, public domain). A yokai, not a deity. League segment, replaces Glalie and
Walrein on Glacia's team (docs/research/mask-designs.md, "Yukijoro 的 Brief", option A). A tall,
narrow white figure with the Noh face of a young woman; her long black hair is blown out level by
the storm like a flag, her white robe has no feet and scatters into snow at the hem, her breath
hangs white. Silhouette at 64px: a slim upright triangle with a bar of black hair out to one
side (unlike Froslass's wide sleeves and head crystals, and unlike Yukinba's straw cone, icicle
hair and staff). Ice/fairy."""
import math

NORMAL = {'robe': (0.93, 0.95, 1.0), 'robeshade': (0.66, 0.74, 0.90), 'sash': (0.52, 0.70, 0.95),
          'face': (0.97, 0.94, 0.86), 'lacquer': (0.16, 0.12, 0.12), 'hollow': (0.03, 0.03, 0.04),
          'hair': (0.07, 0.07, 0.10), 'hairsheen': (0.22, 0.24, 0.36), 'lip': (0.82, 0.34, 0.38),
          'snow': (0.82, 0.92, 1.0)}
# Shiny: a pale violet robe, silver-white hair.
SHINY = {**NORMAL, 'robe': (0.84, 0.76, 0.96), 'robeshade': (0.56, 0.46, 0.76), 'sash': (0.94, 0.70, 0.80),
         'hair': (0.84, 0.86, 0.94), 'hairsheen': (0.98, 0.98, 1.0)}


# Hand-placed pixels (make_art.apply_pixels): the young woman's Noh face, as little as it needs: two high
# smudged brows, two short level eyes, a small closed mouth (no smile).
_FACE = [
    ((19, 5), ['.gg..gg.']),
    ((19, 8), ['.kk..kk.']),
    ((19, 12), ['...rr...']),
]
_ICON = [((9, 8), ['K..K'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'g': (176, 174, 167), 'r': (234, 158, 166), 'K': (65, 65, 65)},
          'front': {'box': (4, 0, 59, 56), 'patches': _FACE},
          'front2': {'box': (1, 0, 62, 56), 'patches': [((x - 1, y + 1), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (2, 2, 30, 30), 'patches': _ICON},
          'icon2': {'box': (2, 1, 30, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    robe = k.toon('robe', c['robe'], steps=(0.6, 0.82, 1.0))
    robeshade = k.flat('robeshade', c['robeshade'])
    sash = k.toon('sash', c['sash'], two_tone=True)
    face_m = k.toon('face', c['face'], two_tone=True)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    hair = k.toon('hair', c['hair'], two_tone=True)
    hairsheen = k.flat('hairsheen', c['hairsheen'])
    lip = k.flat('lip', c['lip'])
    snow = k.flat('snow', c['snow'])
    k.set_light((-0.75, -0.6, 0.15))

    # The robe: a tall narrow cone with no feet, a sash, long sleeves hanging at the sides.
    k.cone((0, 0.05, -0.45), 0.66, 2.0, robe, radius2=0.2, segments=24)
    k.ellipsoid((0, 0.05, 0.5), (0.34, 0.26, 0.2), robe)
    k.torus((0, 0.05, 0.05), 0.33, 0.07, sash)
    for side in (-1, 1):
        k.ellipsoid((side * 0.42, 0.0, -0.1), (0.14, 0.12, 0.62), robe, rot=(0, math.radians(side * 10), 0))
        k.rod((side * 0.1, -0.28, 0.42), (side * 0.2, -0.5, -0.9), 0.02, robeshade)   # the fold of the robe
    # The hem scatters into blowing snow.
    for x, y, z, s in ((-0.62, -0.1, -1.38, 0.16), (-0.25, -0.35, -1.46, 0.14), (0.2, -0.3, -1.44, 0.15), (0.6, 0.0, -1.38, 0.17),
                       (0.95, 0.1, -1.25, 0.12), (1.25, 0.1, -1.05, 0.09), (1.5, 0.15, -0.85, 0.07), (-0.9, 0.2, -1.3, 0.1),
                       (0.1, 0.4, -1.42, 0.16)):
        k.ellipsoid((x, y, z), (s, s, s * 0.8), snow, segments=12)

    # The head: a young woman's Noh face, black hair parted in the middle.
    before = k.snapshot()
    shell = k.mask_shell(face_m, lacquer, width=0.5, depth=0.36, height=0.66)
    for x in (-0.19, 0.19):
        k.hole(shell, x, 0.1, (0.1, 0.022), backing=hollow)
    k.bump(shell, 0, -0.08, (0.04, 0.05, 0.1), face_m, lift=0.02)
    k.front_only(k.ellipsoid(k.on_face(shell, 0, -0.33, lift=0.015), (0.07, 0.02, 0.03), lip))
    k.ellipsoid((0, 0.16, 0.12), (0.5, 0.42, 0.56), hair)
    for side in (-1, 1):
        k.front_only(k.ellipsoid(k.on_face(shell, side * 0.36, 0.3, lift=0.03), (0.18, 0.06, 0.4), hair, rot=(0, math.radians(side * 12), 0)))
    k.transform(k.since(before), offset=(0, -0.2, 0.98), scale=0.82)
    # Her hair, blown out level to one side by the storm.
    end = k.Vector((2.2, 0.4, 1.22))   # the strands run together into one pennant
    for i, (dz, r) in enumerate(((0.26, 0.12), (0.1, 0.14), (-0.06, 0.13), (-0.22, 0.11), (-0.36, 0.08))):
        a = k.Vector((0.25, 0.25, 1.05 + dz))
        wave = 0.1 * (1 if i % 2 else -1)
        pts = [a, a.lerp(end, 0.35) + k.Vector((0, 0, wave)), a.lerp(end, 0.7) - k.Vector((0, 0, wave * 0.6)), a.lerp(end, 0.9 + 0.025 * i)]
        for p, q, rr in zip(pts, pts[1:], (r, r * 0.8, r * 0.45)):
            k.rod(p, q, rr, hair)
            k.ellipsoid(q, (rr * 0.98,) * 3, hair, segments=12)
    k.rod((0.5, 0.18, 1.3), (1.5, 0.28, 1.3), 0.03, hairsheen)
    # Her breath, hanging white in front of her mouth.
    for x, z, s in ((-0.32, 0.7, 0.12), (-0.52, 0.76, 0.09), (-0.68, 0.7, 0.06)):
        k.ellipsoid((x, -0.5, z), (s, s * 0.6, s * 0.8), snow, segments=12)
    return {'kind': 'beast', 'size': 0.96, 'front_az': -10, 'front_el': 6, 'side_az': -70}
