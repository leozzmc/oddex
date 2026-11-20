"""Haniwort: a haniwa (Kofun-period terracotta tomb figure) dug out of the Route 111 desert and
revived at Devon, standing in for Lileep (the Root Fossil; role FOSSIL_ROOT; Norman segment,
docs/research/mask-designs.md). Brief: the dancing-haniwa pose, one arm raised high; a hollow
cylinder body flaring at the base; a round head with side hair loops; the haniwa's three black
holes for eyes and mouth, roots crawling out of them and down the face so it always seems to
weep; a sprout on its crown and roots spreading from its base. An excavated artefact, not a
deity. Silhouette at 64px: the raised arm, the three holes, the roots. Rock/grass."""
import math

NORMAL = {'clay': (0.80, 0.46, 0.28), 'claydark': (0.52, 0.26, 0.16), 'hollow': (0.03, 0.02, 0.02),
          'root': (0.40, 0.56, 0.20), 'leaf': (0.45, 0.78, 0.28)}
SHINY = {**NORMAL, 'clay': (0.40, 0.44, 0.52), 'claydark': (0.22, 0.24, 0.30), 'root': (0.86, 0.70, 0.24),
         'leaf': (0.95, 0.85, 0.35)}


def build(k, c):
    clay = k.toon('clay', c['clay'], steps=k.HORROR_STEPS, glint=0.15)
    claydark = k.toon('claydark', c['claydark'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    root = k.toon('root', c['root'], two_tone=True)
    leaf = k.toon('leaf', c['leaf'], two_tone=True)
    k.set_light((-0.75, -0.6, -0.1))
    # The hollow cylinder body, a raised band, the flared base.
    k.cylinder((0, 0.1, -0.55), 0.4, 1.0, clay)
    k.torus((0, 0.1, -0.35), 0.41, 0.04, claydark)
    k.cone((0, 0.1, -1.12), 0.56, 0.24, claydark, radius2=0.4)
    # The round head with hair loops (mizura) at the sides.
    k.cylinder((0, 0.05, 0.02), 0.18, 0.2, clay)
    k.ellipsoid((0, 0.0, 0.42), (0.44, 0.38, 0.46), clay)
    for side in (-1, 1):
        k.torus((side * 0.48, 0.05, 0.3), 0.13, 0.05, claydark, rot=(math.pi / 2, 0, 0))
    # The three holes: wide black eyes and mouth.
    for x, z, sx, sz in ((-0.18, 0.5, 0.14, 0.11), (0.18, 0.5, 0.14, 0.11), (0.0, 0.22, 0.14, 0.12)):
        k.front_only(k.ellipsoid((x, -0.35, z), (sx, 0.06, sz), hollow))
    # Roots crawling out of each hole and down the face and body, like tears.
    for x, z, side in ((-0.18, 0.46, -1), (0.18, 0.46, 1), (0.0, 0.18, 1)):
        pts = [k.Vector((x, -0.4, z - 0.04)), k.Vector((x + side * 0.05, -0.42, z - 0.25)),
               k.Vector((x + side * 0.16, -0.38, z - 0.5)), k.Vector((x + side * 0.22, -0.4, z - 0.85))]
        for a, b, r in zip(pts, pts[1:], (0.055, 0.05, 0.04)):
            k.front_only(k.rod(a, b, r, root))
    # The dancing pose: one arm raised high, the other bent forward.
    up = [k.Vector((-0.38, 0.05, -0.15)), k.Vector((-0.78, 0.0, 0.2)), k.Vector((-0.72, -0.05, 0.78))]
    for a, b in zip(up, up[1:]):
        k.rod(a, b, 0.12, clay)
    k.ellipsoid(up[-1] + k.Vector((0, 0, 0.08)), (0.13, 0.11, 0.13), clay)
    down = [k.Vector((0.38, 0.05, -0.2)), k.Vector((0.72, -0.1, -0.42)), k.Vector((0.6, -0.3, -0.62))]
    for a, b in zip(down, down[1:]):
        k.rod(a, b, 0.11, clay)
    k.ellipsoid(down[-1], (0.12, 0.1, 0.12), clay)
    # A sprout on the crown.
    for ang, tilt in ((0.5, 35), (2.6, 40)):
        k.ellipsoid((0.18 * math.cos(ang), 0.05, 0.93), (0.2, 0.06, 0.08), leaf, rot=(0, math.radians(tilt), ang))
    k.rod((0, 0.05, 0.86), (0.02, 0.05, 1.02), 0.03, root)
    # Roots spreading from the base over the sand.
    for i in range(6):
        a = math.radians(200 + i * 28)
        base = k.Vector((0.45 * math.cos(a), 0.1 + 0.45 * math.sin(a), -1.15))
        tip = k.Vector((1.0 * math.cos(a), 0.1 + 0.85 * math.sin(a), -1.25))
        k.spike(base, tip, 0.08, root)
    return {'kind': 'beast', 'size': 0.88, 'front_az': -12, 'side_az': -70}
