"""Ridgefin: Ridgecap's second stage (docs/research/friends-designs.md). The hitouban grows a
second, larger pair of finned ear-wings above the first and trails a long stream of water from
its chin like a neck (a hint of the stage to come); its cap crest rises higher. Ridgecap's
build() is reused as is. Head only; water/flying. The head layer is replaced by the likeness in
compose.py; the taller crest is tagged 'front' so it rises out of either face."""
import math
from pathlib import Path

_base = {}
exec((Path(__file__).parent / 'ridgecap.py').read_text(), _base)
NORMAL = dict(_base['NORMAL'])
SHINY = dict(_base['SHINY'])


def build(k, c):
    opts = _base['build'](k, c)
    fin = k.toon('fin2', c['fin'], two_tone=True)
    rib = k.toon('rib2', c['rib'], two_tone=True)
    water = k.toon('water2', c['water'], two_tone=True)
    foam = k.flat('foam2', (0.92, 0.97, 1.0))
    cap = k.toon('cap2', c['cap'], glint=0.2)
    for side in (-1, 1):
        k.wing((side * 0.5, 0.25, 1.35), side, 1.35, fin, rib, ribs=5, sweep=(15, 80), droop=0.05, depth=0.3)
    # A stream of water trailing down from the chin like a long neck.
    for i in range(10):
        t = i / 9
        p = k.Vector((0.25 * math.sin(t * 3.0), 0.05 + 0.1 * t, 0.25 - 1.35 * t))
        s = 0.16 * (1 - 0.6 * t)
        k.ellipsoid(p, (s, s, s * 1.3), water)
        if i % 3 == 0:
            k.ellipsoid(p + k.Vector((-s * 0.4, -s * 0.6, s * 0.3)), (s * 0.35, s * 0.2, s * 0.35), foam)
    before = k.snapshot()
    for y, h in ((-0.15, 0.55), (0.12, 0.6)):
        k.spike((0, y, 1.85), (0, y + 0.08, 1.85 + h), 0.12, cap)
    k.tag(k.since(before), 'front')
    opts['size'] = 0.86
    return opts
