"""Grinarbor: Grinpack's third stage (docs/research/friends-designs.md). After the
jinmenju (a tree whose fruit are human heads that laugh): Grinvine's head, bough, gourd heads and
spider legs (its build() is reused as is) have become a whole tree. A thick trunk rises behind
the head into a broad crown of leaves; more boughs reach out, and grinning fruit faces hang all
round it. The spider legs are its roots. Head only; grass/dark. The head
layer is replaced by the likeness in compose.py."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'grinvine.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'leaf2': (0.24, 0.50, 0.18), 'fruit': (0.96, 0.78, 0.52), 'cheek': (0.90, 0.36, 0.30)}
SHINY = {**_base['SHINY'], 'leaf2': (0.70, 0.22, 0.10), 'fruit': (0.85, 0.70, 0.95), 'cheek': (0.60, 0.25, 0.60)}


def build(k, c):
    opts = _base['build'](k, c)
    bark = k.toon('bark3', c['bark'], two_tone=True)
    leaf = k.toon('leaf3', c['leaf'], two_tone=True)
    leaf2 = k.toon('leaf4', c['leaf2'], two_tone=True)
    fruit = k.toon('fruit', c['fruit'], steps=k.HORROR_STEPS, glint=0.3)
    cheek = k.flat('cheek', c['cheek'])
    carve = k.flat('carve3', c['carve'])
    tooth = k.toon('tooth3', c['tooth'], two_tone=True)
    vine = k.toon('vine3', c['vine'], two_tone=True)
    # The trunk behind the head, and boughs reaching out from it.
    k.cone((0, 0.5, 1.2), 0.42, 2.9, bark, radius2=0.22)
    for side in (-1, 1):
        k.rod((0, 0.5, 2.3), (side * 1.5, 0.45, 2.85), 0.1, bark)
        k.rod((side * 0.2, 0.5, 1.7), (side * 1.7, 0.4, 1.9), 0.08, bark)
    # A broad crown of leaves in two greens.
    for x, y, z, s, m in ((0, 0.75, 3.15, (0.9, 0.6, 0.5), leaf2), (-1.05, 0.7, 2.9, (0.7, 0.55, 0.45), leaf2),
                          (1.05, 0.7, 2.9, (0.7, 0.55, 0.45), leaf2), (-0.5, 0.45, 3.3, (0.55, 0.45, 0.4), leaf),
                          (0.55, 0.45, 3.32, (0.55, 0.45, 0.38), leaf), (-1.65, 0.55, 2.4, (0.45, 0.4, 0.38), leaf),
                          (1.65, 0.55, 2.45, (0.45, 0.4, 0.38), leaf), (0, 0.4, 3.6, (0.4, 0.35, 0.28), leaf)):
        k.ellipsoid((x, y, z), s, m)
    # Grinning fruit faces hanging from the crown and boughs.
    for x, top, drop, s in ((-1.6, 2.2, 1.45, 0.27), (1.65, 2.25, 1.35, 0.27), (-0.75, 2.6, 2.2, 0.21),
                            (0.8, 2.6, 2.25, 0.21)):
        k.rod((x, 0.1, top), (x, 0.0, drop + s), 0.03, vine)
        p = k.Vector((x, -0.05, drop))
        k.ellipsoid(p, (s, s * 0.9, s * 1.05), fruit)
        for ex in (-0.4, 0.4):   # eyes squeezed into arcs
            k.ellipsoid(p + k.Vector((ex * s, -s * 0.85, s * 0.3)), (s * 0.22, s * 0.05, s * 0.08), carve)
            k.ellipsoid(p + k.Vector((ex * s * 1.4, -s * 0.75, -s * 0.05)), (s * 0.2, s * 0.05, s * 0.13), cheek)
        k.ellipsoid(p + k.Vector((0, -s * 0.88, -s * 0.35)), (s * 0.6, s * 0.06, s * 0.25), carve)
        k.ellipsoid(p + k.Vector((0, -s * 0.92, -s * 0.24)), (s * 0.48, s * 0.04, s * 0.08), tooth)
    opts['size'] = 0.95
    return opts
