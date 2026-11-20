"""Dogoggle: a goggle-eyed Jomon clay figure (shakoki-dogu) dug out of the Route 111 desert and
revived at Devon, standing in for Anorith (the Claw Fossil; role FOSSIL_CLAW; Norman segment,
docs/research/mask-designs.md). Brief: revived, the figure turned out to be an ancient arthropod.
A squat clay body ringed with red cord-pattern bands; a wide head with a crown; two huge
horizontal snow-goggle eyes, each with a dark slit (its compound eyes); two big open pincers
held up at the sides; a segmented tail curling up behind; short legs. An excavated artefact,
not a deity. Silhouette at 64px: the goggles, the pincers, the tail. Rock/bug."""
import math

NORMAL = {'clay': (0.68, 0.62, 0.54), 'pattern': (0.60, 0.26, 0.18), 'goggle': (0.88, 0.84, 0.74),
          'slit': (0.04, 0.03, 0.03), 'claw': (0.46, 0.33, 0.25), 'tip': (0.72, 0.22, 0.16)}
SHINY = {**NORMAL, 'clay': (0.36, 0.46, 0.58), 'pattern': (0.92, 0.74, 0.28), 'goggle': (0.80, 0.90, 0.96),
         'claw': (0.24, 0.30, 0.42), 'tip': (0.95, 0.80, 0.30)}


def build(k, c):
    clay = k.toon('clay', c['clay'], steps=k.HORROR_STEPS, glint=0.15)
    pattern = k.toon('pattern', c['pattern'], two_tone=True)
    goggle = k.toon('goggle', c['goggle'], glint=0.3, two_tone=True)
    slit = k.flat('slit', c['slit'])
    claw = k.toon('claw', c['claw'], two_tone=True)
    tip = k.toon('tip', c['tip'], two_tone=True)
    k.set_light((-0.75, -0.6, -0.1))
    # The segmented tail trailing out low to its left and curling up, clear of the pincer.
    pts = [(0.4, 0.55, -0.78), (0.9, 0.68, -0.85), (1.38, 0.72, -0.76), (1.72, 0.68, -0.52), (1.86, 0.58, -0.18), (1.8, 0.48, 0.14)]
    for i, p in enumerate(pts):
        r = 0.3 - 0.035 * i
        k.ellipsoid(p, (r, r * 0.85, r * 0.8), clay)
        k.torus(p, r * 0.92, r * 0.16, pattern, rot=(math.radians(40 + 10 * i), 0, 0))
    k.spike(pts[-1], (1.6, 0.4, 0.42), 0.1, tip)
    # The squat body ringed with cord-pattern bands, on short legs.
    k.ellipsoid((0, 0.15, -0.42), (0.58, 0.48, 0.56), clay)
    for z in (-0.25, -0.55):
        k.torus((0, 0.15, z), 0.56 - 0.1 * abs(z + 0.4), 0.05, pattern)
    for x in (-0.3, 0.3):
        for y in (-0.1, 0.4):
            k.cylinder((x, y, -0.98), 0.12, 0.2, clay)
    # The wide head, its crown, and the two huge goggle eyes with slits.
    k.ellipsoid((0, -0.02, 0.42), (0.66, 0.46, 0.42), clay)
    k.torus((0, 0.0, 0.78), 0.3, 0.07, pattern)
    for x in (-0.18, 0.0, 0.18):
        k.ellipsoid((x, 0.0, 0.88), (0.08, 0.08, 0.1), clay)
    for side in (-1, 1):
        g = k.Vector((side * 0.29, -0.4, 0.42))
        k.front_only(k.ellipsoid(g + k.Vector((0, 0.03, 0)), (0.3, 0.08, 0.2), pattern))   # rim
        k.front_only(k.ellipsoid(g, (0.26, 0.08, 0.16), goggle))
        k.front_only(k.ellipsoid(g + k.Vector((0, -0.07, 0)), (0.22, 0.02, 0.03), slit))
    k.front_only(k.ellipsoid((0, -0.42, 0.16), (0.08, 0.04, 0.05), slit))   # a small mouth
    # Two big open pincers held up at the sides.
    for side in (-1, 1):
        sh = k.Vector((side * 0.55, 0.0, -0.2))
        el = k.Vector((side * 0.95, -0.2, -0.15))
        k.rod(sh, el, 0.12, claw)
        k.ellipsoid(el, (0.14, 0.14, 0.14), claw)
        # A broad palm and two thick fingers held wide open in a V, tipped red.
        palm = k.Vector((side * 1.12, -0.42, 0.1))
        k.ellipsoid(palm, (0.26, 0.2, 0.28), claw)
        for (dx, dz), r in (((0.12, 0.62), 0.15), ((0.42, 0.12), 0.13)):
            base = palm + k.Vector((side * 0.04, -0.06, 0.1 if dz > 0.3 else -0.05))
            end = palm + k.Vector((side * dx, -0.3, dz))
            k.spike(base, end, r, claw)
            k.spike(base.lerp(end, 0.7), end + (end - base).normalized() * 0.05, r * 0.45, tip)
    return {'kind': 'beast', 'size': 0.88, 'front_az': -20, 'side_az': -70}
