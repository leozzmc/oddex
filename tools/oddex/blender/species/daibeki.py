"""Daibeki: Bekurama's third stage, after Karabeki (docs/research/mask-designs.md). The crow tengu
grown into a great tengu (daitengu) of the mountain, the kind the Noh "Kurama Tengu" is about:
Bekurama's o-beshimi mask, cap, leaf fan and sword (its build() is reused as is) with the beak
become a long red nose, a mane and beard of white hair, gold bonten on the cap, a feathered fan
(hauchiwa) and broad dark wings. A generic great tengu, not any named one. Mask body; grass/steel;
evolves from Karabeki with a Leaf Stone."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'bekurama.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'nose': (0.88, 0.22, 0.10), 'hair': (0.95, 0.94, 0.90), 'feather': (0.08, 0.08, 0.12), 'rib': (0.20, 0.22, 0.32),
          'plume': (0.92, 0.90, 0.85), 'plume2': (0.45, 0.30, 0.20), 'bonten': (0.95, 0.75, 0.25)}
SHINY = {**_base['SHINY'], 'nose': (0.30, 0.50, 0.28), 'hair': (0.85, 0.62, 0.30), 'feather': (0.30, 0.30, 0.36), 'rib': (0.55, 0.55, 0.62),
         'plume': (0.90, 0.85, 0.60), 'plume2': (0.30, 0.45, 0.25), 'bonten': (0.85, 0.85, 0.95)}


def build(k, c):
    opts = _base['build'](k, c)
    nose = k.toon('nose', c['nose'], glint=0.5, two_tone=True)
    hair = k.toon('hair', c['hair'], two_tone=True)
    feather = k.toon('feather', c['feather'], two_tone=True)
    rib = k.toon('rib', c['rib'], two_tone=True)
    plume = k.toon('plume', c['plume'], two_tone=True)
    plume2 = k.toon('plume2', c['plume2'], two_tone=True)
    bonten = k.toon('bonten', c['bonten'], glint=0.4, two_tone=True)
    cap = k.toon('cap3', c['cap'], two_tone=True)
    # The long red nose of a great tengu, jutting out and a little up.
    # A brighter red than the face, and the view turned further, so it reads at 64px.
    k.ellipsoid((0, -0.45, 0.04), (0.18, 0.16, 0.16), nose)
    k.spike((0, -0.5, 0.04), (0, -1.45, 0.3), 0.17, nose)
    # A white mane round the mask and a long beard below it.
    for i in range(13):
        a = math.radians(200 + i * 11.5)   # round the sides and top, behind the mask
        base = k.Vector((0.7 * math.cos(a), 0.25, 0.05 + 0.8 * -math.sin(a)))
        out = k.Vector((math.cos(a), 0.1, -math.sin(a)))
        k.spike(base, base + out * 0.6 + k.Vector((0, 0, -0.2)), 0.15, hair)
    for x in (-0.36, -0.24, -0.12, 0.0, 0.12, 0.24, 0.36):
        k.spike((x, -0.1, -0.7), (x * 1.5, -0.2, -1.55 + 0.4 * abs(x)), 0.1, hair)
    # Gold bonten on the cap.
    for i, z in enumerate((0.98, 0.84, 0.7)):
        k.ellipsoid((0, -0.2 - 0.03 * i, z + 0.05), (0.09, 0.08, 0.08), bonten)
    # Broad dark wings.
    for side in (-1, 1):
        k.wing((side * 0.5, 0.4, 0.35), side, 1.15, feather, rib, ribs=6, sweep=(-30, 45), droop=0.1, depth=0.25)
    # A feathered fan (hauchiwa) on a black handle, on the sword side.
    for i in range(9):
        a = math.radians(-60 + i * 15)
        m = plume if i % 2 else plume2
        k.ellipsoid((-1.0 + 0.42 * math.sin(a), -0.05, 0.35 + 0.42 * math.cos(a)), (0.09, 0.03, 0.3), m, rot=(0, -a, 0))
    k.rod((-1.0, -0.05, 0.3), (-0.95, -0.05, -0.35), 0.045, cap)
    opts['size'] = 0.9
    opts['front_az'] = -35
    return opts
