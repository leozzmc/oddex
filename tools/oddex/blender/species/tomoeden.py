"""Tomoeden: three spark-commas chasing one another round a little shrine drum, the mitsudomoe
crest seen on shrine drums and roof tiles, with a laughing face on the drumhead (Mauville batch,
docs/research/mask-designs.md). Fusion: three magatama bodies (Magatide's part) in red, blue
and yellow, Shojobob's laughing face shrunk onto the drum. Mask (drum); electric/psychic."""
import math

NORMAL = {'drum': (0.80, 0.22, 0.14), 'head': (0.95, 0.90, 0.78), 'rim': (0.20, 0.10, 0.06),
          'gold': (0.95, 0.75, 0.22), 'red': (0.90, 0.18, 0.15), 'blue': (0.18, 0.40, 0.90),
          'yellow': (0.98, 0.82, 0.18), 'line': (0.15, 0.06, 0.05), 'spark': (1.0, 0.98, 0.70)}
SHINY = {**NORMAL, 'drum': (0.20, 0.25, 0.55), 'red': (0.90, 0.50, 0.75), 'blue': (0.40, 0.85, 0.80)}


def build(k, c):
    drum = k.toon('drum', c['drum'], glint=0.4)
    head = k.toon('head', c['head'], two_tone=True)
    rim = k.toon('rim', c['rim'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    commas = [k.toon(n, c[n], glint=0.4) for n in ('red', 'blue', 'yellow')]
    line = k.flat('line', c['line'])
    spark = k.flat('spark', c['spark'])
    k.set_light((-0.7, -0.6, 0.3))

    # The drum, facing the viewer, with studs round the rim.
    k.cylinder((0, 0.1, 0), 0.62, 0.55, drum, rot=(math.pi / 2, 0, 0), segments=32)
    k.cylinder((0, -0.19, 0), 0.6, 0.02, head, rot=(math.pi / 2, 0, 0), segments=32)
    k.torus((0, -0.18, 0), 0.6, 0.04, rim, rot=(math.pi / 2, 0, 0))
    for i in range(14):
        a = 2 * math.pi * i / 14
        k.ellipsoid((0.66 * math.cos(a), -0.15, 0.66 * math.sin(a)), (0.035, 0.035, 0.035), gold)
    # A laughing face painted on the drumhead.
    for side in (-1, 1):
        x0 = side * 0.18
        k.rod((x0 - 0.08, -0.22, 0.1), (x0, -0.22, 0.16), 0.022, line)
        k.rod((x0, -0.22, 0.16), (x0 + 0.08, -0.22, 0.1), 0.022, line)
        k.ellipsoid((side * 0.33, -0.22, -0.05), (0.07, 0.01, 0.04), commas[0])
    k.ellipsoid((0, -0.23, -0.17), (0.16, 0.01, 0.07), line)
    k.ellipsoid((0, -0.235, -0.13), (0.12, 0.01, 0.025), commas[0])
    # Three commas chasing round the drum (the mitsudomoe).
    for i, m in enumerate(commas):
        a = math.radians(90 + 120 * i)
        cx, cz = 0.98 * math.cos(a), 0.98 * math.sin(a)
        hc = k.magatama((cx, -0.05, cz), 0.32, m, rot_z=120 * i + 40)
        k.ellipsoid((hc.x - 0.05, hc.y - 0.17, hc.z + 0.05), (0.05, 0.02, 0.05), spark)
    for x, z in ((-0.4, 1.25), (1.2, -0.4), (-1.15, -0.55)):
        p = k.Vector((x, -0.1, z))
        k.rod(p, p + k.Vector((0.08, 0, 0.16)), 0.022, spark)
        k.rod(p + k.Vector((0.08, 0, 0.16)), p + k.Vector((-0.02, 0, 0.26)), 0.022, spark)
    return {'kind': 'mask', 'size': 0.86, 'front_az': -10}
