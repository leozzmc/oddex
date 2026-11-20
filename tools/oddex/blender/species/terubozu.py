"""Terubozu: a teru teru bozu, the folk charm children hang under the eaves to ask for fine
weather (not a deity). Winona segment, the Weather Institute's gift, replaces Castform
(docs/research/mask-designs.md, "Terubozu 的 Brief", option A). A round head of white cloth tied
off with a red cord, the cloth hanging below in a rippled skirt, a string loop on top. Its face is
drawn on in ink, a little lopsided (one eye bigger, a crooked smile), and the rain has made the
ink run from both eyes in long streaks. Silhouette at 64px: ball head, pinched neck, flared skirt.
Normal."""
import math

NORMAL = {'cloth': (0.97, 0.97, 0.95), 'clothshade': (0.74, 0.76, 0.80), 'ink': (0.06, 0.06, 0.08),
          'cord': (0.86, 0.14, 0.14), 'corddark': (0.52, 0.06, 0.08), 'string': (0.76, 0.64, 0.46)}
# Shiny: rain-dyed indigo cloth with the face drawn in white chalk.
SHINY = {**NORMAL, 'cloth': (0.42, 0.50, 0.72), 'clothshade': (0.24, 0.28, 0.46), 'ink': (0.96, 0.96, 0.92),
         'cord': (0.95, 0.78, 0.22), 'corddark': (0.66, 0.48, 0.10)}


def build(k, c):
    cloth = k.toon('cloth', c['cloth'], steps=(0.6, 0.82, 1.0))
    shade = k.flat('clothshade', c['clothshade'])
    ink = k.flat('ink', c['ink'])
    cord = k.toon('cord', c['cord'], two_tone=True)
    corddark = k.flat('corddark', c['corddark'])
    string = k.flat('string', c['string'])
    k.set_light((-0.7, -0.6, 0.2))

    head_c, head_r = (0, 0, 0.62), (0.72, 0.66, 0.68)
    k.ellipsoid(head_c, head_r, cloth)
    # The skirt: a flared cone of cloth with a rippled hem and fold shadows.
    k.cone((0, 0, -0.32), 0.18, 0.8, cloth, radius2=0.66, rot=(math.pi, 0, 0), segments=32)
    for i in range(10):
        a = 2 * math.pi * i / 10
        k.ellipsoid((0.66 * math.cos(a), 0.66 * math.sin(a), -0.7), (0.17, 0.17, 0.1), cloth)
    for a in (-2.0, -1.2, -1.95 + math.pi, -1.2 + math.pi, -1.57):
        k.rod((0.2 * math.cos(a), 0.2 * math.sin(a), 0.0), (0.62 * math.cos(a), 0.62 * math.sin(a), -0.7), 0.025, shade)
    # The red cord round the neck, its knot and two tails at the back.
    k.torus((0, 0, -0.02), 0.24, 0.1, cord)
    k.ellipsoid((0.0, 0.24, 0.0), (0.09, 0.07, 0.08), corddark)
    for side in (-1, 1):
        k.rod((0, 0.26, -0.02), (side * 0.12, 0.34, -0.38), 0.035, cord)
    # The string loop it hangs by.
    k.torus((0, 0, 1.44), 0.12, 0.025, string, rot=(math.pi / 2, 0, 0))
    k.rod((0, 0, 1.28), (0, 0, 1.33), 0.03, string)

    def at(x, z, lift=0.0):
        return k.head_point(head_c, head_r, x, z, lift)

    # The ink face: a big round left eye, a smaller right one, a crooked smile.
    k.ellipsoid(at(-0.25, 0.76, 0.02), (0.16, 0.05, 0.17), ink)
    k.ellipsoid(at(0.25, 0.72, 0.02), (0.1, 0.05, 0.1), ink)
    pts = [(-0.32, 0.46), (-0.16, 0.36), (0.02, 0.35), (0.18, 0.4), (0.32, 0.52)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        k.rod(at(x0, z0, 0.02), at(x1, z1, 0.02), 0.045, ink)
    # The ink running from both eyes down over the cheeks and the skirt.
    for x, z0, n in ((-0.24, 0.6, 1), (-0.34, 0.62, 0), (0.25, 0.62, 1)):
        a, b = at(x, z0, 0.02), at(x + 0.02, 0.1, 0.02)
        k.rod(a, b, 0.05, ink)
        if n:
            k.rod(k.Vector((b.x, -0.26, -0.08)), k.Vector((b.x * 1.6 + 0.02, -0.6, -0.6)), 0.045, ink)
    return {'kind': 'beast', 'size': 0.8, 'front_az': -12, 'front_el': 6, 'side_az': -70}
