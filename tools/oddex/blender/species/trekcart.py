"""Trekcart: Trekkeye's third stage (docs/research/friends-designs.md). After the
katawaguruma (a burning cart that rolls through the night with a face aboard): Trekwheel's head,
wheels, chain and legs (its build() is reused as is) now carry a whole ox-cart cabin. A black
lacquered roof with a raised curved gable and a gold ridge sits over the head, its eaves turned
up at the corners and hung with red tassels; dark pillars and a bamboo blind close the cabin
behind; will-o'-wisps circle it. Head only; fire/steel. The head layer is
replaced by the likeness in tools/oddex/likeness/compose.py."""
import math
from pathlib import Path

_path = Path(__file__).parent / 'trekwheel.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'lacquer': (0.08, 0.06, 0.07), 'gold': (0.98, 0.80, 0.30),
          'tassel': (0.80, 0.10, 0.14), 'blind': (0.80, 0.68, 0.40)}
SHINY = {**_base['SHINY'], 'lacquer': (0.85, 0.84, 0.80), 'gold': (0.40, 0.45, 0.60),
         'tassel': (0.30, 0.30, 0.70), 'blind': (0.55, 0.55, 0.62)}


def build(k, c):
    opts = _base['build'](k, c)
    lacquer = k.toon('lacquer', c['lacquer'], glint=0.5, two_tone=True)
    gold = k.toon('gold', c['gold'], glint=0.7, two_tone=True)
    tassel = k.toon('tassel', c['tassel'], two_tone=True)
    blind = k.toon('blind', c['blind'], two_tone=True)
    wood = k.toon('wood3', c['wood'], two_tone=True)
    ember = k.flat('ember3', c['ember'])
    flame = k.flat('flame3', c['flame'])
    hot = k.flat('hot3', c['hot'])
    # The cabin behind the wheel: four pillars, a bamboo blind between the back pair.
    for x in (-1.05, 1.05):
        for y in (0.6, 1.2):
            k.rod((x, y, 0.85), (x, y, 2.45), 0.07, wood)
    k.ellipsoid((0, 1.2, 1.65), (1.0, 0.03, 0.8), blind)
    for i in range(7):
        z = 1.0 + i * 0.22
        k.rod((-1.0, 1.15, z), (1.0, 1.15, z), 0.018, wood)
    # The roof: a broad lacquered slab with a raised, curved gable over the head and a gold ridge.
    k.ellipsoid((0, 0.85, 2.55), (1.6, 1.0, 0.16), lacquer)
    k.ellipsoid((0, 0.55, 2.7), (0.75, 0.6, 0.26), lacquer)
    k.ellipsoid((0, -0.05, 2.62), (0.7, 0.05, 0.12), gold)   # the gable's gold bargeboard
    k.rod((-1.5, -0.12, 2.5), (1.5, -0.12, 2.5), 0.04, gold)   # gold trim along the front eave
    k.rod((-1.25, 0.85, 2.74), (1.25, 0.85, 2.74), 0.06, gold)
    k.ellipsoid((0, 0.55, 2.97), (0.16, 0.16, 0.08), gold)
    for side in (-1, 1):
        for y in (-0.1, 1.75):
            eave = k.Vector((side * 1.5, y, 2.55))
            tip = eave + k.Vector((side * 0.3, -0.1 if y < 0.5 else 0.1, 0.3))
            k.spike(eave, tip, 0.1, lacquer)
            k.ellipsoid(tip, (0.06, 0.06, 0.06), gold)
        # Red tassels hanging from the front eaves.
        top = k.Vector((side * 1.55, -0.05, 2.45))
        k.rod(top, top + k.Vector((0, 0, -0.45)), 0.02, gold)
        k.ellipsoid(top + k.Vector((0, 0, -0.5)), (0.06, 0.06, 0.06), gold)
        k.cone(top + k.Vector((0, 0, -0.72)), 0.1, 0.36, tassel)
    # Will-o'-wisps circling the cart.
    for x, y, z, s in ((-2.05, -0.3, 1.9, 0.17), (2.1, -0.2, 2.25, 0.15), (-1.7, -0.5, 0.25, 0.13), (1.0, -0.6, 3.15, 0.12)):
        p = k.Vector((x, y, z))
        k.ellipsoid(p, (s, s, s), ember)
        k.spike(p + k.Vector((0, 0, s * 0.3)), p + k.Vector((-0.15 if x > 0 else 0.15, 0, s * 3)), s * 0.7, ember)
        k.ellipsoid(p + k.Vector((0, -s * 0.4, 0)), (s * 0.6,) * 3, flame)
        k.ellipsoid(p + k.Vector((0, -s * 0.8, -s * 0.1)), (s * 0.3,) * 3, hot)
    opts['size'] = 0.95
    return opts
