"""Lernagon: the hydra that has burst its jar. After the Lernaean Hydra of Greek myth (see
amphorin.py: a monster, never worshipped; no Heracles; nothing from any modern work's hydra).
League segment, Amphorin's evolution at Lv50, replaces Salamence, Drake's ace
(docs/research/mask-designs.md, "Amphorin 和 Lernagon 的 Brief"). A mound of a body grown over
with swamp moss and reeds, shards of the amphora still stuck round it; necks fan up out of it,
each head in a Greek tragic mask (the frowning one; no comic mask, no smile). Nine heads do not
fit in 64px: five show from the front, the middle one the largest, two more behind. Silhouette at
64px: a mossy mound with a fan of masked heads above it. Dragon/grass."""
import math
from pathlib import Path

_path = Path(__file__).with_name('amphorin.py')
_base = {'__file__': str(_path)}
exec(compile(_path.read_text(), str(_path), 'exec'), _base)

NORMAL = {**_base['NORMAL'], 'moss': (0.42, 0.56, 0.20), 'mossdark': (0.24, 0.36, 0.14)}
# Shiny: a white hydra, autumn-red reeds, black shards with a red band.
SHINY = {**_base['SHINY'], 'moss': (0.72, 0.36, 0.20), 'mossdark': (0.46, 0.18, 0.12), 'reed': (0.86, 0.50, 0.22)}

# The necks: (where the head ends up, head size). The middle head first.
HEADS = [((0.0, -0.55, 1.3), 0.92), ((-0.95, -0.45, 1.0), 0.72), ((0.97, -0.45, 0.98), 0.72), ((-1.6, -0.3, 0.2), 0.6),
         ((1.62, -0.3, 0.18), 0.6), ((-0.48, 0.3, 1.75), 0.46), ((0.52, 0.3, 1.72), 0.46)]


# Hand-placed pixels (make_art.apply_pixels): the same tragic mask on every head that is big enough to carry
# it: brows up in the middle, hollow eyes, an open mouth with the corners down. No head smiles.
_BROWS = ['...k.k..', '..k...k.']
_MOUTH = ['..kkkk..', '..kffk..']
_FACE = [
    ((28, 9), ['...k..k...', '..k....k..', 'fkkffffkkd', '.kk....kk.']),           # the middle head
    ((28, 15), ['...kkkk...', '..kkkkkk..', '..k...k...']),
    ((14, 14), _BROWS + ['fkkffkkd']), ((14, 18), _MOUTH),                          # the two beside it
    ((43, 14), ['..k.k...', '.k...k..', 'kkfffkkd']), ((43, 18), _MOUTH),
    ((6, 27), ['k..k']), ((6, 29), ['.kk.', 'kffk']),                               # the two outer ones
    ((54, 29), ['.kk.', 'kffk']),
]
# The second frame is squashed wider, so each head has moved by its own amount.
_FACE2 = [
    ((28, 9), ['...k..k...', '..k....k..', 'fkkffffkkd', '.kk....kk.']),
    ((28, 15), ['...kkkk...', '..kkkkkk..', '..k...k...']),
    ((13, 14), _BROWS + ['fkkffkkd']), ((13, 19), _MOUTH),
    ((45, 13), ['..k.k..', '.k...k.', 'kkfffkk', '.f.....']), ((44, 18), ['..kkkk..', '..kffk..', '....f...']),
    ((4, 27), ['k..k']), ((4, 29), ['.kk.', 'kffk']),
    ((55, 29), ['.kk.', 'kffk']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'f': (250, 248, 238), 'd': (176, 174, 167)},
          'front': {'box': (4, 0, 60, 55), 'patches': _FACE},
          'front2': {'box': (2, 0, 62, 56), 'patches': _FACE2}}


def build(k, c):
    clay = k.toon('clay', c['clay'], steps=(0.55, 0.8, 1.0))
    glaze = k.flat('glaze', c['glaze'])
    mask = k.toon('mask', c['mask'], two_tone=True)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    scale = k.toon('scale', c['scale'], two_tone=True)
    scaledark = k.flat('scaledark', c['scaledark'])
    belly = k.toon('belly', c['belly'], two_tone=True)
    reed = k.toon('reed', c['reed'], two_tone=True)
    moss = k.toon('moss', c['moss'], two_tone=True)
    mossdark = k.flat('mossdark', c['mossdark'])
    water = k.flat('water', c['water'])
    k.set_light((-0.7, -0.6, 0.2))

    # The swamp, and the body: a mound grown over with moss, reeds standing on its back.
    k.ellipsoid((0, 0.2, -1.42), (1.7, 1.25, 0.12), water)
    k.ellipsoid((0, 0.25, -0.9), (1.2, 1.0, 0.62), scale)
    k.ellipsoid((0, 0.0, -1.08), (1.02, 0.9, 0.4), belly)
    for x, y, z, s in ((-0.55, -0.45, -0.55, 0.3), (0.6, -0.42, -0.52, 0.32), (0.05, -0.62, -0.62, 0.26), (-1.0, 0.0, -0.75, 0.26),
                       (1.02, 0.0, -0.76, 0.26), (0.0, 0.7, -0.3, 0.4)):
        k.ellipsoid((x, y, z), (s, s * 0.9, s * 0.5), moss if s > 0.27 else mossdark, segments=16)
    for x, y, h, lean in ((-1.3, -0.3, 0.75, -0.2), (-1.12, -0.45, 0.5, -0.05), (1.3, -0.3, 0.8, 0.22), (1.14, -0.48, 0.5, 0.05),
                          (-0.3, 0.8, 1.0, -0.1), (0.3, 0.85, 1.1, 0.1)):
        k.spike((x, y, -1.3), (x + lean, y, -1.3 + h), 0.05, reed)
    # Shards of the jar it burst, still stuck round its base.
    for x, tilt, h in ((-0.72, 0.45, 0.46), (0.0, -0.15, 0.4), (0.74, -0.5, 0.48)):
        p = (x, -0.86, -1.12)
        k.ellipsoid(p, (0.3, 0.08, h), clay, rot=(0, tilt, 0), segments=12)
        k.ellipsoid((p[0], p[1] - 0.02, p[2] + 0.1), (0.31, 0.08, 0.08), glaze, rot=(0, tilt, 0), segments=12)

    # The necks fan up out of the mound; every head wears the tragic mask.
    for (hx, hy, hz), s in HEADS:
        root = k.Vector((hx * 0.4, 0.2, -0.45))
        head = k.Vector((hx, hy + 0.28 * s, hz))
        mid = root.lerp(head, 0.5) + k.Vector((hx * 0.22, -0.05, -0.12))
        n = 9
        for i in range(n):
            t = i / (n - 1)
            p = root.lerp(mid, t * 2) if t < 0.5 else mid.lerp(head, t * 2 - 1)
            r = 0.17 * s + 0.1 * (1 - t)
            k.ellipsoid(p, (r, r, r), scale if i % 2 else scaledark, segments=16)
        k.ellipsoid(head, (0.38 * s, 0.34 * s, 0.36 * s), scale)
        _base['tragic_mask'](k, (hx, hy, hz), s * 0.78, mask, lacquer, hollow)
    # Two tails behind.
    for side in (-1, 1):
        for i in range(5):
            t = i / 4
            k.ellipsoid((side * (0.9 + 0.5 * t), 0.9 + 0.2 * t, -0.9 + 0.5 * t * t), (0.2 - 0.14 * t,) * 3, scale, segments=12)
    return {'kind': 'beast', 'size': 0.96, 'front_az': -8, 'front_el': 8, 'side_az': -70, 'squash': (1.04, 1.04, 0.96)}
