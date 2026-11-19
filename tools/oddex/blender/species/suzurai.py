"""Suzurai: a shrine bell (suzu) that hums with static, its slit the mouth of a small glaring
face, hung from a red-and-white bell rope with paper streamers (Mauville batch,
docs/research/mask-designs.md). Fusion: Okinoir's bells blown up into the body, Kamorai's gold
eyes shrunk, the shared rope and shide. Mask (bell); steel/electric. Evolves into Kagurai."""
import math

NORMAL = {'bronze': (0.78, 0.58, 0.22), 'dark': (0.18, 0.10, 0.05), 'eye': (0.98, 0.88, 0.40),
          'pupil': (0.03, 0.02, 0.02), 'red': (0.85, 0.15, 0.12), 'white': (0.96, 0.96, 0.94),
          'paper': (0.98, 0.98, 0.96), 'spark': (1.0, 0.95, 0.40)}
SHINY = {**NORMAL, 'bronze': (0.78, 0.80, 0.86), 'red': (0.20, 0.35, 0.80), 'spark': (0.60, 0.90, 1.0)}


def build(k, c):
    bronze = k.toon('bronze', c['bronze'], steps=k.HORROR_STEPS, glint=0.7, weathered=0.2)
    dark = k.flat('dark', c['dark'])
    eye = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    red = k.toon('red', c['red'], two_tone=True)
    white = k.toon('white', c['white'], two_tone=True)
    paper = k.flat('paper', c['paper'])
    spark = k.flat('spark', c['spark'])
    k.set_light((-0.7, -0.6, 0.2))

    hc, hr = (0, 0, 0.0), (0.72, 0.68, 0.7)
    k.ellipsoid(hc, hr, bronze)
    k.torus((0, 0, 0.0), 0.71, 0.04, bronze, rot=(0, 0, 0))   # the bell's waist band
    # The slit of the bell is the mouth; small staring eyes above it.
    m = k.head_point(hc, hr, 0, -0.3, 0.0)
    k.ellipsoid(m, (0.42, 0.05, 0.06), dark)
    k.ellipsoid(k.head_point(hc, hr, 0, -0.55, 0.0), (0.12, 0.05, 0.12), dark)
    for side in (-1, 1):
        e = k.head_point(hc, hr, side * 0.24, 0.18, 0.02)
        k.ellipsoid(e, (0.13, 0.06, 0.11), eye)
        k.ellipsoid((e.x, e.y - 0.05, e.z), (0.045, 0.02, 0.06), pupil)
        k.ellipsoid(k.head_point(hc, hr, side * 0.24, 0.34, 0.02), (0.15, 0.04, 0.035), dark,
                    rot=(0, math.radians(side * 22), 0))
    # Top loop, the bell rope (red and white twist) and streamers.
    k.torus((0, 0, 0.78), 0.12, 0.04, bronze, rot=(math.pi / 2, 0, 0))
    k.rope([(0, 0, 0.88), (0.02, 0, 1.6)], 0.09, red, white)
    for side in (-1, 1):
        k.shide((side * 0.14 - (0.12 if side < 0 else 0), -0.05, 1.45), 0.42, 0.11, paper, side=side)
    # Static crackling round it.
    for x, z, a in ((-0.95, 0.3, 30), (0.98, 0.1, -25), (0.85, -0.6, 40), (-0.9, -0.5, -35)):
        p = k.Vector((x, -0.1, z))
        q = p + k.Vector((0.12 * math.cos(math.radians(a)), 0, 0.2))
        k.rod(p, q, 0.025, spark)
        k.rod(q, q + k.Vector((-0.1, 0, 0.12)), 0.025, spark)
    return {'kind': 'mask', 'size': 0.84, 'front_az': -14}
