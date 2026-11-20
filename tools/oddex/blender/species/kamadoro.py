"""Kamadoro: Hifukko's second stage (Lavaridge segment, docs/research/mask-designs.md). The brazier
has grown into a whole clay cooking stove (kamado, the object only, never a hearth god): a broad
rounded stove body on short legs, two fire holes on its back roaring like volcanoes, the stoke
hole glowing in front, and the hyottoko face (Hifukko's face(), larger) set into its front,
blackened with soot. Masked quadruped; fire/ground."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'hifukko.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'face': (0.46, 0.36, 0.30), 'clay': (0.56, 0.48, 0.42), 'claydark': (0.26, 0.22, 0.22),
          'soot': (0.12, 0.10, 0.10)}
SHINY = {**_base['SHINY'], 'face': (0.70, 0.66, 0.62), 'clay': (0.36, 0.40, 0.52), 'claydark': (0.16, 0.18, 0.26),
         'soot': (0.10, 0.10, 0.16)}


def build(k, c):
    k.set_light((-0.75, -0.55, -0.15))
    clay = k.toon('stove', c['clay'], steps=k.HORROR_STEPS, weathered=0.3)
    claydark = k.flat('stovedark', c['claydark'])
    soot = k.flat('soot', c['soot'])
    ember = k.flat('ember_s', c['ember'])
    flame = k.flat('flame_s', c['flame'])
    # The stove body behind the face, on four short legs.
    k.ellipsoid((0, 0.85, -0.05), (1.05, 0.95, 0.72), clay)
    for x in (-0.7, 0.7):
        for y in (0.25, 1.45):
            k.cylinder((x, y, -0.78), 0.17, 0.3, claydark)
    # Two fire holes on its back, roaring.
    for x, h in ((-0.45, 1.0), (0.45, 0.8)):
        top = k.Vector((x, 1.0, 0.62))
        k.cylinder(top, 0.28, 0.3, clay)
        k.torus((top.x, top.y, top.z + 0.15), 0.26, 0.07, claydark)
        k.flame_halo((top.x, top.y, top.z + 0.15), 0.12, ember, flame, licks=8, length=0.55 * h)
        k.spike((top.x, top.y, top.z + 0.15), (top.x - 0.1, top.y, top.z + 0.15 + h), 0.2, ember)
        k.spike((top.x, top.y - 0.02, top.z + 0.15), (top.x - 0.06, top.y - 0.02, top.z + 0.15 + h * 0.65), 0.1, flame)
    # The stoke hole glowing low in front, below the face.
    k.ellipsoid((0.0, -0.12, -0.55), (0.32, 0.06, 0.18), soot)
    k.ellipsoid((0.0, -0.15, -0.58), (0.22, 0.04, 0.1), ember)
    # The face set into the stove's front, larger and blackened with soot.
    before = k.snapshot()
    _base['face'](k, c, 1.15)
    k.transform(k.since(before), offset=(0, -0.05, 0.12))
    return {'kind': 'beast', 'size': 0.9, 'front_az': -24, 'side_az': -75}
