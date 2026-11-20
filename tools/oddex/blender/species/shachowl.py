"""Shachowl: Shachound's second stage (docs/research/mask-designs.md). The hound of
the Cham dance of the stag and the hounds, grown into a big hound; in the story the hunter's
dogs are calmed by a song and turn to the dharma. Shachound's mask (its build() is reused as is)
now has a gold third eye on the brow (the calmed mind) and a shaggy dark ruff tipped in red, and the hound
under it is bigger, with a line of five-coloured prayer flags strung along its back on the rope
of the story. Masked quadruped; dark/psychic. Imagery only: no deity, no skull crown."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'shachound.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'ruff': (0.12, 0.11, 0.14), 'rufftip': (0.80, 0.18, 0.10), 'third': (0.95, 0.78, 0.25),
          'flag1': (0.20, 0.45, 0.85), 'flag2': (0.95, 0.95, 0.92), 'flag3': (0.85, 0.15, 0.12),
          'flag4': (0.20, 0.62, 0.30), 'flag5': (0.95, 0.80, 0.20), 'rope': (0.70, 0.55, 0.30)}
SHINY = {**NORMAL, **_base['SHINY'], 'ruff': (0.62, 0.52, 0.36), 'rufftip': (0.95, 0.85, 0.40), 'third': (0.75, 0.90, 1.0)}


class _Bigger:
    """maskkit, but with a bigger hound behind the mask."""
    def __init__(self, k):
        self._k = k

    def __getattr__(self, name):
        return getattr(self._k, name)

    def beast_behind_mask(self, mask_height, body_mat, **kw):
        kw.update(length=1.7, girth=0.56, leg=0.55)
        return self._k.beast_behind_mask(mask_height, body_mat, **kw)


def build(k, c):
    opts = _base['build'](_Bigger(k), c)
    ruff = k.toon('ruff', c['ruff'], two_tone=True)
    third = k.toon('third', c['third'], glint=0.6, two_tone=True)
    pupil = k.flat('pupil2', c['pupil'])
    rope = k.toon('rope', c['rope'], two_tone=True)
    flags = [k.toon(f'flag{i}', c[f'flag{i}'], two_tone=True) for i in range(1, 6)]
    # A shaggy ruff round the back of the mask.
    tip = k.toon('rufftip', c['rufftip'], two_tone=True)
    for i in range(16):
        a = 2 * math.pi * i / 16
        base = k.Vector((0.55 * math.cos(a), 0.3, 0.0 + 0.5 * math.sin(a)))
        out = k.Vector((math.cos(a), 0.1, math.sin(a)))
        k.spike(base, base + out * 0.7, 0.16, ruff)
        k.spike(base + out * 0.45, base + out * 0.75, 0.07, tip)
    # The third eye, upright, on the brow above the cloth band.
    k.ellipsoid((0, -0.6, 0.36), (0.09, 0.04, 0.16), third)
    k.ellipsoid((0, -0.64, 0.36), (0.04, 0.02, 0.09), pupil)
    # Prayer flags on the rope strung across its back, in the five colours.
    pts = [k.Vector((-1.0, 0.9, 1.0)), k.Vector((0, 0.9, 1.25)), k.Vector((1.0, 0.9, 1.0))]
    for a, b in zip(pts, pts[1:]):
        k.rod(a, b, 0.02, rope)
    for i in range(10):
        t = (i + 0.5) / 10
        a, b = (pts[0], pts[1]) if t < 0.5 else (pts[1], pts[2])
        p = a.lerp(b, (t % 0.5) * 2)
        k.ellipsoid(p + k.Vector((0, 0, -0.12)), (0.09, 0.03, 0.12), flags[i % 5], rot=(0, 0, 0))
    opts['size'] = 0.9
    return opts
