"""Yokozunat: Tsunacoon's third stage (Lavaridge segment, docs/research/mask-designs.md). The
mosquito spirit of Kyogen 'Ka-zumo' that trained in its rope-bound cocoon has burst out as a
grand champion: Usobuzz's usobuki face, proboscis, six legs and belt (its build() is reused as
is), now with Tsunacoon's rope turned into a yokozuna's thick white tsuna with zigzag shide
hanging in front, and two pairs of clear mosquito wings. Mask; bug/fighting."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'usobuzz.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'tsuna': (0.97, 0.96, 0.92), 'tsunadark': (0.74, 0.72, 0.66),
          'paper': (1.0, 1.0, 1.0), 'wing': (0.72, 0.86, 0.96), 'vein': (0.30, 0.40, 0.55)}
SHINY = {**_base['SHINY'], 'tsuna': (0.96, 0.82, 0.36), 'tsunadark': (0.70, 0.52, 0.16),
         'paper': (1.0, 1.0, 1.0), 'wing': (0.86, 0.96, 0.80), 'vein': (0.35, 0.50, 0.30)}


def build(k, c):
    opts = _base['build'](k, c)
    tsuna = k.toon('tsuna', c['tsuna'], two_tone=True)
    tsunadark = k.flat('tsunadark', c['tsunadark'])
    paper = k.flat('paper', c['paper'])
    wing = k.toon('wingm', c['wing'], two_tone=True)
    vein = k.toon('vein', c['vein'], two_tone=True)
    # Two pairs of clear mosquito wings, rising behind.
    for side in (-1, 1):
        k.wing((side * 0.3, 0.3, 0.35), side, 1.15, wing, vein, ribs=3, sweep=(30, 65), droop=0.05, depth=0.25, scallop=0.1)
        k.wing((side * 0.3, 0.35, 0.15), side, 0.85, wing, vein, ribs=3, sweep=(0, 30), droop=0.05, depth=0.2, scallop=0.1)
    # The yokozuna's tsuna round the belt, and shide hanging in front.
    k.ring_rope((0, 0.0, -0.62), 0.5, 0.13, tsuna, tsunadark, rot=(90, 0, 0), segments=18)
    for x, side in ((-0.28, 1), (0.0, -1), (0.28, 1)):
        k.shide((x, -0.52, -0.66), 0.45, 0.1, paper, side=side)
    opts['size'] = 0.88
    return opts
