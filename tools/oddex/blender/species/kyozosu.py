"""Kyozosu: Kyokon's second stage (docs/research/mask-designs.md). In Kyogen
"Tsurigitsune" the old fox disguises itself as a priest to talk the hunter out of his traps:
Kyokon (its build() is reused as is) now goes about in that disguise, a long low fox in a
brown priest's robe with a gold-bordered stole, a dark hood round its tilted white fox mask, a
bamboo staff, and a second tail it cannot quite hide. Masked quadruped; normal/ghost."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'kyokon.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'robe': (0.36, 0.22, 0.14), 'stole': (0.80, 0.62, 0.22),
          'hood': (0.28, 0.24, 0.42), 'bamboo': (0.62, 0.58, 0.30)}
SHINY = {**NORMAL, **_base['SHINY'], 'robe': (0.20, 0.22, 0.30), 'stole': (0.75, 0.75, 0.80), 'hood': (0.62, 0.20, 0.25)}


class _Longer:
    """maskkit, but with a longer, lower fox behind the mask and a second tail."""
    def __init__(self, k):
        self._k = k

    def __getattr__(self, name):
        return getattr(self._k, name)

    def beast_behind_mask(self, mask_height, body_mat, **kw):
        tail = kw.get('tail')

        def two_tails(at, mat):
            tail(at, mat)
            tail(at + self._k.Vector((0.25, -0.05, -0.05)), mat)
        kw.update(length=1.75, girth=0.42, leg=0.32, tail=two_tails)
        return self._k.beast_behind_mask(mask_height, body_mat, **kw)


def build(k, c):
    opts = _base['build'](_Longer(k), c)
    robe = k.toon('robe', c['robe'], two_tone=True)
    stole = k.toon('stole', c['stole'], glint=0.4, two_tone=True)
    hood = k.toon('hood', c['hood'], steps=(0.5, 0.78, 1.0))
    bamboo = k.toon('bamboo', c['bamboo'], two_tone=True)
    # The priest's robe draped over the back, a gold stole across it.
    k.ellipsoid((0, 0.95, 0.72), (0.52, 0.95, 0.42), robe)
    k.rod((-0.5, 0.5, 0.6), (0.45, 1.3, 1.1), 0.07, stole)   # the stole across the robe
    for side in (-1, 1):
        k.ellipsoid((side * 0.47, 0.95, 0.45), (0.06, 0.85, 0.3), robe)
    # A white hood wrapped round the mask (behind it, so the tilted mask still shows).
    k.ellipsoid((0, 0.25, 0.15), (0.56, 0.4, 0.62), hood)
    for side in (-1, 1):
        k.ellipsoid((side * 0.42, 0.05, -0.4), (0.15, 0.18, 0.3), hood)
    # A bamboo staff leaning against its shoulder.
    k.rod((0.75, -0.3, -0.15), (0.55, 0.3, 1.45), 0.045, bamboo)
    for z in (0.2, 0.7, 1.15):
        t = (z + 0.15) / 1.6
        k.torus((0.75 - 0.2 * t, -0.3 + 0.6 * t, z), 0.05, 0.015, bamboo)
    opts['size'] = 0.88
    return opts
