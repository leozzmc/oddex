"""Trekwheel: Trekkeye's second stage (docs/research/friends-designs.md). The wanyudo grows into
an ox-cart: Trekkeye's head, brow camera and burning rear wheel (its build() is reused as is),
plus two big burning cart wheels facing the viewer on either side, a bright brass axle and
spokes, a pair of cart shafts reaching forward, white-hot flame cores, a heavy brass chain
swinging in front and a fourth pair of spider legs. Kept clearly wider and brighter than
Trekkeye so the stages read apart at 64px (the user's review). Head only; fire/steel. The head
layer is replaced by the likeness in tools/oddex/likeness/compose.py."""
import math
from pathlib import Path

_base = {}
exec((Path(__file__).parent / 'trekkeye.py').read_text(), _base)
NORMAL = {**_base['NORMAL'], 'brass': (0.95, 0.78, 0.38), 'hot': (0.80, 0.93, 1.0), 'wood': (0.42, 0.22, 0.12)}
SHINY = {**_base['SHINY'], 'brass': (0.85, 0.88, 0.95), 'hot': (1.0, 0.96, 0.75), 'wood': (0.20, 0.20, 0.30)}


def build(k, c):
    opts = _base['build'](k, c)
    iron = k.toon('iron2', c['iron'], steps=k.HORROR_STEPS, glint=0.4, weathered=0.3)
    brass = k.toon('brass', c['brass'], glint=0.7, two_tone=True)
    wood = k.toon('wood', c['wood'], two_tone=True)
    ember = k.flat('ember2', c['ember'])
    flame = k.flat('flame2', c['flame'])
    hot = k.flat('hot', c['hot'])
    # A bright brass axle across the back, and two big cart wheels facing the viewer at its ends.
    k.rod((-1.4, 0.15, 0.85), (1.4, 0.15, 0.85), 0.09, brass)
    for side in (-1, 1):
        wc = k.Vector((side * 1.4, 0.0, 0.8))
        k.torus(wc, 0.7, 0.1, iron, rot=(math.pi / 2, 0, 0))
        k.torus((wc.x, wc.y - 0.06, wc.z), 0.7, 0.035, brass, rot=(math.pi / 2, 0, 0))
        k.cylinder(wc, 0.2, 0.26, brass, rot=(math.pi / 2, 0, 0))
        for i in range(8):
            a = math.pi / 8 + i * math.pi / 4
            k.rod(wc, wc + k.Vector((math.cos(a), 0, math.sin(a))) * 0.66, 0.045, brass)
        # Big flames round the rim, each with a white-hot core.
        for i in range(12):
            a = i * 2 * math.pi / 12 + 0.25
            out = k.Vector((math.cos(a), 0, math.sin(a)))
            base = wc + out * 0.75
            k.spike(base, base + out * 0.36 + k.Vector((0, 0, 0.16)), 0.15, ember)
            k.spike(base + out * 0.04, base + out * 0.3 + k.Vector((0, -0.02, 0.1)), 0.09, flame)
            k.spike(base + out * 0.05, base + out * 0.18 + k.Vector((0, -0.04, 0.06)), 0.045, hot)
        # The ox-cart shafts reaching forward and down from the axle.
        k.rod((side * 0.9, 0.1, 0.75), (side * 0.7, -1.3, 0.15), 0.06, wood)
        # The fourth pair of legs, from under the side wheels.
        k.spider_leg(wc + k.Vector((0, -0.1, -0.6)), (side * 0.5, -0.85), 0.95, iron, ember, radius=0.055, lift=0.35)
    # A heavy brass chain swinging in front of the cart, from one shaft to the other.
    for i in range(13):
        t = i / 12
        x = -0.72 + 1.44 * t
        p = k.Vector((x, -1.12, 0.2 - 0.4 * math.sin(math.pi * t)))
        k.torus(p, 0.075, 0.025, brass, rot=(math.pi / 2 if i % 2 else 0, 0, math.pi / 2 if i % 2 else 0))
    opts['size'] = 0.92
    opts['front_az'] = -8
    return opts
