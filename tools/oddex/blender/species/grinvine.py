"""Grinvine: Grinpack's second stage (docs/research/friends-designs.md). The tsurube-otoshi's
branch has grown into a leafy bough: Grinpack's grinning head, vine and spider legs (its build()
is reused as is), plus a longer branch thick with leaves, two grinning gourd heads hanging on
vines of their own (a hint of the jinmenju to come) and another pair of spider legs.
Head only; grass/dark. The head layer is replaced by the likeness in compose.py."""
import math
from pathlib import Path

_base = {}
exec((Path(__file__).parent / 'grinpack.py').read_text(), _base)
NORMAL = {**_base['NORMAL'], 'gourd': (0.80, 0.62, 0.28), 'carve': (0.20, 0.08, 0.04)}
SHINY = {**_base['SHINY'], 'gourd': (0.62, 0.30, 0.55), 'carve': (0.10, 0.04, 0.10)}


def build(k, c):
    opts = _base['build'](k, c)
    bark = k.toon('bark2', c['bark'], two_tone=True)
    vine = k.toon('vine2', c['vine'], two_tone=True)
    leaf = k.toon('leaf2', c['leaf'], two_tone=True)
    leg = k.toon('leg2', c['leg'], steps=k.HORROR_STEPS)
    gourd = k.toon('gourd', c['gourd'], steps=k.HORROR_STEPS, glint=0.3)
    carve = k.flat('carve', c['carve'])
    # A longer bough with leaves along it.
    k.rod((-1.5, 0.25, 2.4), (1.5, 0.3, 2.62), 0.1, bark)
    for i in range(9):
        x = -1.4 + i * 0.35
        k.ellipsoid((x, 0.15 + 0.05 * (i % 2), 2.62 + 0.04 * (i % 3)), (0.2, 0.07, 0.09), leaf,
                    rot=(0, math.radians(20 + 10 * (i % 3)), 0.6 * i))
    # Two grinning gourd heads on their own vines.
    for side, drop in ((-1, 1.05), (1, 0.85)):
        x = side * 1.15
        k.rod((x, 0.2, 2.45), (x, 0.15, drop + 0.55), 0.035, vine)
        k.ellipsoid((x, 0.1, drop + 0.4), (0.16, 0.15, 0.16), gourd)
        k.ellipsoid((x, 0.1, drop), (0.26, 0.24, 0.28), gourd)
        for ex in (-0.09, 0.09):
            k.ellipsoid((x + ex, -0.13, drop + 0.07), (0.045, 0.02, 0.04), carve)
        k.ellipsoid((x, -0.14, drop - 0.1), (0.15, 0.02, 0.04), carve)
        for tx in (-0.08, 0.0, 0.08):
            k.ellipsoid((x + tx, -0.155, drop - 0.08), (0.025, 0.01, 0.02), gourd)
    # A third pair of spider legs, reaching out sideways.
    k.spider_legs((0, 0.25, 1.0), 1, 1.3, leg, radius=0.04, spread=(5, 5), lift=0.3, ground=-0.1, ring=0.5)
    opts['size'] = 0.86
    return opts
