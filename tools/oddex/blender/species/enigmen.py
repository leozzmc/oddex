"""Enigmen: the riddling winged Sphinx of Greek myth (a monster, not a deity) in the gold mask of
a pharaoh. Mossdeep segment, Sphinmen's evolution at Lv36, replaces Claydol on Tate & Liza's team
(docs/research/mask-designs.md, "Enigmen 的 Brief", option A). Sphinmen's lion and striped nemes,
but the chalk-white Noh face has become polished gold with a braided false beard, a red glint
burns in the hollow eyes, and a pair of great feathered wings has opened from its shoulders
(white feathers tipped teal). Silhouette at 64px: the two raised wings above the masked lion
(Sphinmen has none). Ground/psychic."""
import math
from pathlib import Path

_path = Path(__file__).with_name('sphinmen.py')
_base = {'__file__': str(_path)}
exec(compile(_path.read_text(), str(_path), 'exec'), _base)

NORMAL = {**_base['NORMAL'], 'face': (1.0, 0.92, 0.58), 'gold': (0.84, 0.54, 0.12), 'body': (0.60, 0.38, 0.20), 'feather': (0.96, 0.96, 0.92),
          'feathertip': (0.16, 0.60, 0.58), 'ember': (0.95, 0.12, 0.10)}
# Shiny: a silver mask with red stripes on a black lion, gold-tipped wings.
SHINY = {**NORMAL, 'face': (0.94, 0.95, 1.0), 'gold': (0.62, 0.64, 0.72), 'blue': (0.70, 0.10, 0.12),
         'body': (0.16, 0.15, 0.18), 'tuft': (0.50, 0.10, 0.10), 'feathertip': (0.92, 0.72, 0.22)}


# Hand-placed pixels (make_art.apply_pixels): kohl-rimmed Egyptian eyes, a red iris in a white eye
# with the kohl drawn out into a wing at the outer corner, and the thin fixed smile.
_FACE = [((31, 30), ['eekkkee',
                     'kkfrrke',
                     'eekkkee',
                     'eeeeeee']),
         ((38, 32), ['e']),
         ((39, 30), ['eekkkdd.',
                     'ekrrfkkk',
                     'eekkkddd',
                     '...d....']),
         ((36, 40), ['k....k',     # the rendered mouth line, its corners turned up
                     '.kkkkd'])]
_ICON = [((16, 18), ['BBBBB', 'KRBRK'])]
PIXELS = {'keys': {'k': (28, 18, 22), 'f': (251, 251, 246), 'r': (249, 97, 89), 'e': (237, 229, 186), 'd': (207, 199, 162),
                   'B': (246, 246, 172), 'K': (65, 65, 65), 'R': (213, 98, 65)},
          'front': {'box': (2, 5, 62, 56), 'patches': _FACE},
          'front2': {'box': (1, 7, 63, 56), 'patches': [((x, y + 1), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (2, 6, 30, 30), 'patches': _ICON},
          'icon2': {'box': (2, 5, 30, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    opts = _base['build'](k, c)
    feather = k.toon('feather', c['feather'], two_tone=True)
    tip = k.toon('feathertip', c['feathertip'], two_tone=True)
    ember = k.flat('ember', c['ember'])
    gold = k.toon('gold2', c['gold'], glint=0.4, two_tone=True)
    blue = k.toon('blue2', c['blue'], two_tone=True)
    # Wings: a fan of long feathers from each shoulder, raised, teal at the tips.
    for side in (-1, 1):
        root = k.Vector((side * 0.55, 0.75, 0.3))
        for i in range(6):
            t = i / 5
            a = math.radians(8 + 70 * t)
            d = k.Vector((side * math.cos(a), 0.12 * t, math.sin(a)))
            length = 1.45 - 0.35 * abs(t - 0.45)
            theta = math.atan2(d.z, d.x)
            k.ellipsoid(root + d * length * 0.5, (length * 0.5, 0.05, 0.17), feather, rot=(0, -theta, 0))
            k.ellipsoid(root + d * length * 0.9, (length * 0.16, 0.055, 0.15), tip, rot=(0, -theta, 0))
        k.ellipsoid(root, (0.3, 0.14, 0.3), feather)
    # The braided false beard under the chin, and a red glint in each eye.
    for j in range(4):
        k.front_only(k.ellipsoid((0, -0.3 + 0.02 * j, -0.74 - 0.13 * j), (0.085 - 0.008 * j, 0.07, 0.075), blue if j % 2 else gold))
    for x in (-0.19, 0.19):
        k.front_only(k.ellipsoid((x * 0.95, -0.37, 0.18), (0.075, 0.03, 0.06), ember))
    return {**opts, 'size': 0.94, 'front_az': -24}
