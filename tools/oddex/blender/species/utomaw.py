"""Utomaw: Utoghast's second stage (docs/research/mask-designs.md). In Noh "Uto"
the hunter's ghost is chased in hell by the seabird he killed, grown monstrous: here that bird
has caught him. A huge pale seabird head with red eyes holds Utoghast's gaunt mask (its build()
is reused as is) in its great pouched beak, the upper bill arching over the mask's brow and the
pouch sagging below it; wide black-and-white wings. Mask body; flying/ghost."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'utoghast.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'bird': (0.92, 0.92, 0.90), 'bill': (0.90, 0.70, 0.22), 'pouch': (0.92, 0.80, 0.45),
          'eye': (0.85, 0.10, 0.08), 'rib': (0.25, 0.25, 0.28)}
SHINY = {**_base['SHINY'], 'bird': (0.30, 0.30, 0.34), 'bill': (0.55, 0.75, 0.85), 'pouch': (0.70, 0.85, 0.92),
         'eye': (0.95, 0.85, 0.20), 'rib': (0.70, 0.75, 0.80)}


def build(k, c):
    opts = _base['build'](k, c)
    bird = k.toon('bird', c['bird'], two_tone=True)
    bill = k.toon('bill', c['bill'], glint=0.3, two_tone=True)
    pouch = k.toon('pouch', c['pouch'], steps=k.HORROR_STEPS)
    eye = k.flat('eye', c['eye'])
    pupil = k.flat('bpupil', (0.02, 0.02, 0.02))
    wing = k.toon('wing2', c['wing'], two_tone=True)
    wingw = k.toon('wingw2', c['wingw'], two_tone=True)
    rib = k.toon('rib2', c['rib'], two_tone=True)
    # The bird's head above and behind the mask, with red eyes.
    k.ellipsoid((0, 0.55, 1.25), (0.6, 0.55, 0.5), bird)
    for side in (-1, 1):
        k.ellipsoid((side * 0.38, 0.12, 1.38), (0.11, 0.06, 0.1), eye)
        k.ellipsoid((side * 0.38, 0.07, 1.38), (0.045, 0.03, 0.06), pupil)
    # The upper bill arching from the head over the mask's brow, hooked at the tip.
    pts = [k.Vector((0, 0.2, 1.15)), k.Vector((0, -0.3, 1.12)), k.Vector((0, -0.7, 1.0)), k.Vector((0, -0.95, 0.8))]
    for a, b, r in zip(pts, pts[1:], (0.22, 0.18, 0.14)):
        k.rod(a, b, r, bill)
    k.spike(pts[-1], (0, -1.0, 0.55), 0.1, bill)
    # The pouch sagging under the mask, its rim of lower bill on either side.
    k.ellipsoid((0, 0.05, -0.75), (0.85, 0.6, 0.65), pouch)
    for side in (-1, 1):
        k.rod((side * 0.15, 0.3, 1.0), (side * 0.75, -0.3, -0.45), 0.07, bill)
    # Wide wings.
    for side in (-1, 1):
        k.wing((side * 0.6, 0.45, 0.8), side, 1.7, wing, rib, ribs=6, sweep=(-15, 45), droop=0.2, depth=0.2)
        k.wing((side * 0.6, 0.4, 0.6), side, 1.2, wingw, rib, ribs=4, sweep=(-25, 15), droop=0.1, depth=0.15)
    opts['size'] = 0.92
    return opts
