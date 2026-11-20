"""Magatide: a jade magatama that swims like a fish and dreams of becoming a dragon (Rustboro batch,
docs/research/mask-designs.md); the comma-shaped jewel only, not the regalia. Fusion: Usobuzz's
pursed usobuki lips as a fish mouth on the round head, Shojobob's water ring under it and
Kamorai's water drops; two small horn buds for the dragon to come. Mask; water/dragon."""
import math

NORMAL = {'jade': (0.22, 0.62, 0.42), 'shine': (0.85, 0.98, 0.90), 'eye': (0.97, 0.95, 0.85),
          'pupil': (0.03, 0.02, 0.02), 'lip': (0.80, 0.40, 0.35), 'water': (0.25, 0.55, 0.92),
          'foam': (0.90, 0.96, 1.0), 'horn': (0.95, 0.85, 0.55)}
SHINY = {**NORMAL, 'jade': (0.78, 0.25, 0.18), 'shine': (1.0, 0.85, 0.75), 'lip': (0.95, 0.80, 0.40)}


def build(k, c):
    jade = k.toon('jade', c['jade'], steps=k.HORROR_STEPS, glint=0.6)
    shine = k.flat('shine', c['shine'])
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    lip = k.toon('lip', c['lip'], two_tone=True)
    water = k.toon('water', c['water'], two_tone=True)
    foam = k.flat('foam', c['foam'])
    horn = k.toon('horn', c['horn'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.25))

    head = k.magatama((0, 0, 0.1), 0.95, jade, curl=1.35)
    hr = (0.59, 0.475, 0.59)

    def front(x, z, lift=0.0):
        return k.head_point(head, hr, x, head.z + z, lift)

    # The bored hole of the jewel, shown as a ring by one eye.
    k.torus(front(0.2, 0.18, 0.0), 0.11, 0.025, shine, rot=(math.pi / 2, 0, 0))
    for side, sx in ((-1, -0.22), (1, 0.2)):
        e = front(sx, 0.18, 0.03)
        k.ellipsoid(e, (0.12, 0.06, 0.12), eye_m)
        k.ellipsoid((e.x, e.y - 0.06, e.z), (0.055, 0.02, 0.06), pupil)
    # Pursed fish lips.
    m = front(0, -0.12, 0.05)
    k.ellipsoid(m, (0.12, 0.1, 0.09), lip)
    k.ellipsoid((m.x, m.y - 0.09, m.z), (0.05, 0.02, 0.04), pupil)
    k.ellipsoid(front(-0.3, 0.38, 0.0), (0.09, 0.03, 0.05), shine)
    for side in (-1, 1):
        k.spike((head.x + side * 0.2, head.y + 0.05, head.z + 0.5), (head.x + side * 0.32, head.y + 0.1, head.z + 0.82), 0.07, horn)
    # Water ring and drops.
    k.torus((0.05, 0.05, -0.85), 0.75, 0.09, water, rot=(math.radians(-14), 0, 0))
    k.torus((0.05, 0.03, -0.84), 0.75, 0.035, foam, rot=(math.radians(-14), 0, 0))
    for x, z, s in ((-0.75, -0.2, 0.06), (0.85, 0.1, 0.05), (0.7, -0.5, 0.045)):
        k.ellipsoid((x, -0.1, z), (s, s, s * 1.4), water)
        k.spike((x, -0.1, z + s * 1.2), (x, -0.1, z + s * 2.6), s * 0.6, water)
    return {'kind': 'mask', 'size': 0.82, 'front_az': -18}
