"""Kagurai: Suzurai grown into a kagura-suzu, the tiered bell cluster shrine dancers carry: three
tiers of bells on a handle, five-coloured streamers flowing from it, the glaring face on the top
bell (Mauville batch, docs/research/mask-designs.md). Imagery only; no deity. Fusion: Suzurai's
bell face, Okinoir's bells for the tiers, the five colours of Mandalumb.
Mask (bell cluster); steel/electric."""
import math

NORMAL = {'bronze': (0.80, 0.60, 0.22), 'dark': (0.18, 0.10, 0.05), 'eye': (0.98, 0.88, 0.40),
          'pupil': (0.03, 0.02, 0.02), 'wood': (0.55, 0.25, 0.12), 'blue': (0.15, 0.35, 0.80),
          'white': (0.96, 0.96, 0.94), 'red': (0.82, 0.16, 0.14), 'green': (0.18, 0.58, 0.28),
          'yellow': (0.95, 0.80, 0.18), 'spark': (1.0, 0.95, 0.40)}
SHINY = {**NORMAL, 'bronze': (0.78, 0.80, 0.86), 'wood': (0.20, 0.18, 0.30), 'spark': (0.60, 0.90, 1.0)}


def build(k, c):
    bronze = k.toon('bronze', c['bronze'], steps=k.HORROR_STEPS, glint=0.7, weathered=0.2)
    dark = k.flat('dark', c['dark'])
    eye = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    wood = k.toon('wood', c['wood'], two_tone=True)
    cloth = [k.toon(n, c[n], two_tone=True) for n in ('blue', 'white', 'red', 'green', 'yellow')]
    spark = k.flat('spark', c['spark'])
    k.set_light((-0.7, -0.6, 0.2))

    # The handle and the five-coloured streamers flowing down from its end.
    k.rod((0, 0.05, -0.2), (0, 0.05, -1.25), 0.07, wood)
    for i, m in enumerate(cloth):
        x = (i - 2) * 0.12
        k.ellipsoid((x, 0.0, -0.95 - 0.06 * abs(i - 2)), (0.05, 0.02, 0.38), m, rot=(0, math.radians((i - 2) * 9), 0))
    # Two tiers of large bells (five, three) round the shaft; the face bell crowns it (simplified from
    # the real seven/five/three so it still reads at 64px).
    for tier, (z, r, n, s) in enumerate(((-0.15, 0.72, 5, 0.27), (0.38, 0.5, 3, 0.25), (0.82, 0.0, 0, 0.0))):
        if not n:
            continue
        for i in range(n):
            a = 2 * math.pi * i / n + tier * 0.3
            p = k.Vector((r * math.cos(a), 0.05 + r * math.sin(a) * 0.6, z))
            k.ellipsoid(p, (s, s, s), bronze)
            k.ellipsoid(p + k.Vector((0, -s * 0.9, -s * 0.2)), (s * 0.6, 0.02, s * 0.12), dark)
    # The top bell keeps Suzurai's face.
    hc, hr = (0, 0.05, 1.0), (0.42, 0.4, 0.42)
    k.ellipsoid(hc, hr, bronze)
    k.ellipsoid(k.head_point(hc, hr, 0, 0.84, 0.0), (0.24, 0.04, 0.04), dark)
    for side in (-1, 1):
        e = k.head_point(hc, hr, side * 0.15, 1.06, 0.02)
        k.ellipsoid(e, (0.1, 0.05, 0.09), eye)
        k.ellipsoid((e.x, e.y - 0.03, e.z), (0.03, 0.015, 0.04), pupil)
    k.torus((0, 0.05, 1.48), 0.09, 0.035, bronze, rot=(math.pi / 2, 0, 0))
    for x, z in ((-1.0, 0.6), (1.0, 0.3), (-0.95, -0.4), (0.9, -0.7)):
        p = k.Vector((x, -0.1, z))
        k.rod(p, p + k.Vector((0.1, 0, 0.2)), 0.025, spark)
        k.rod(p + k.Vector((0.1, 0, 0.2)), p + k.Vector((0.0, 0, 0.32)), 0.025, spark)
    return {'kind': 'mask', 'size': 0.88, 'front_az': -14, 'front_el': 10}
