"""Karabeki: Bekurama's second stage (docs/research/mask-designs.md). The
o-beshimi tengu mask turning into a karasu-tengu, the crow tengu of the same mountain: Bekurama's
mask, cap, fan and sword (its build() is reused as is) now with a crow's beak jutting from the
nose over the clamped lips, black crow wings behind, the yamabushi's coloured pompoms (bonten)
on the cap. The wings stay inside Bekurama's outline so the mask is no smaller (the user's
review), and the beak is long and bright yellow so it reads against the red face. Mask body; grass/steel."""
from pathlib import Path

_path = Path(__file__).parent / 'bekurama.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'beak': (0.98, 0.80, 0.15), 'beaktip': (0.10, 0.08, 0.08), 'feather': (0.08, 0.08, 0.12),
          'rib': (0.20, 0.22, 0.32), 'bonten': (0.92, 0.92, 0.88)}
SHINY = {**_base['SHINY'], 'beak': (0.20, 0.20, 0.24), 'beaktip': (0.90, 0.90, 0.85), 'feather': (0.30, 0.30, 0.36),
         'rib': (0.55, 0.55, 0.62), 'bonten': (0.95, 0.75, 0.30)}


def build(k, c):
    opts = _base['build'](k, c)
    beak = k.toon('beak', c['beak'], glint=0.5, two_tone=True)
    tip = k.toon('beaktip', c['beaktip'], two_tone=True)
    feather = k.toon('feather', c['feather'], two_tone=True)
    rib = k.toon('rib', c['rib'], two_tone=True)
    bonten = k.toon('bonten', c['bonten'], two_tone=True)
    # A long bright crow's beak in place of the nose, hooked down over the clamped lips.
    k.ellipsoid((0, -0.45, 0.04), (0.2, 0.16, 0.16), beak)
    k.spike((0, -0.52, 0.06), (0, -1.15, -0.4), 0.2, beak)
    k.spike((0, -1.0, -0.3), (0, -1.18, -0.52), 0.08, tip)
    k.spike((0, -0.5, -0.12), (0, -0.9, -0.34), 0.11, beak)
    # Crow wings kept inside Bekurama's own outline (fan and sword), so the mask stays as large.
    for side in (-1, 1):
        k.wing((side * 0.45, 0.35, 0.3), side, 0.62, feather, rib, ribs=5, sweep=(-30, 40), droop=0.1, depth=0.2)
    # Bonten pompoms down the front of the tokin cap.
    for i, z in enumerate((0.98, 0.84, 0.7)):
        k.ellipsoid((0, -0.2 - 0.03 * i, z + 0.05), (0.08, 0.07, 0.07), bonten)
    opts['size'] = 0.98   # the beak and wings widen the frame; keep the mask at least Bekurama's size
    return opts
