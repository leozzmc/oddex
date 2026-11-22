"""Shojoran: the shojo dancing 'midare', the wild tiptoe dance on the waves in the Noh play Shojo.
Mossdeep segment, Shojomai's evolution by Water Stone, replaces Ludicolo (the Lilycove rival;
docs/research/mask-designs.md, "Shojoran", option A). The red laughing youth's face of the line,
but the long red hair has been whipped out into a great wheel round it as it spins; it stands in
a huge vermilion sake cup floating on the waves, in a gold robe, one arm flung up with the
long-handled sake ladle. Silhouette at 64px: the wheel of hair, the wide cup under it, the ladle
raised at an angle (Shojomai has a leaf hat and hair only behind it). Water/fairy."""
import math

NORMAL = {'face': (0.92, 0.32, 0.24), 'lacquer': (0.25, 0.06, 0.05), 'hair': (0.70, 0.06, 0.08),
          'hairdark': (0.42, 0.03, 0.06), 'ink': (0.12, 0.05, 0.05), 'lip': (0.55, 0.06, 0.08),
          'robe': (0.94, 0.74, 0.24), 'cup': (0.78, 0.16, 0.10), 'cupin': (0.16, 0.06, 0.06),
          'sake': (0.98, 0.94, 0.80), 'water': (0.25, 0.55, 0.92), 'foam': (0.92, 0.97, 1.0),
          'wood': (0.55, 0.38, 0.20), 'arm': (0.88, 0.38, 0.28)}
# Shiny: golden hair and a blue cup.
SHINY = {**NORMAL, 'hair': (0.96, 0.78, 0.26), 'hairdark': (0.70, 0.48, 0.10), 'robe': (0.90, 0.92, 0.96),
         'cup': (0.16, 0.30, 0.74), 'face': (0.98, 0.62, 0.66), 'arm': (0.96, 0.66, 0.70)}


def build(k, c):
    face_m = k.toon('face', c['face'], glint=0.6)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hair = k.toon('hair', c['hair'], two_tone=True)
    hairdark = k.flat('hairdark', c['hairdark'])
    ink = k.flat('ink', c['ink'])
    lip = k.flat('lip', c['lip'])
    robe = k.toon('robe', c['robe'], two_tone=True)
    cup = k.toon('cup', c['cup'], two_tone=True)
    cupin = k.flat('cupin', c['cupin'])
    sake = k.flat('sake', c['sake'])
    water = k.toon('water', c['water'])
    foam = k.toon('foam', c['foam'], two_tone=True)
    wood = k.toon('wood', c['wood'], two_tone=True)
    arm = k.toon('arm', c['arm'], two_tone=True)
    k.set_light((-0.7, -0.6, 0.3))

    # The wheel of hair: locks thrown out all round the face and swept one way by the spin.
    hz = 0.35
    for i in range(11):
        a = math.radians(-130 + i * 26)   # open at the bottom, where the body is
        d = k.Vector((math.sin(a), 0, math.cos(a)))
        b = a + math.radians(32)          # each lock bends the way it spins
        tip = k.Vector((0, 0.3, hz)) + d * 0.6 + k.Vector((math.sin(b), 0, math.cos(b))) * 0.95
        k.spike(k.Vector((0, 0.3, hz)) + d * 0.5, tip, 0.26, hair if i % 2 else hairdark)
    k.ellipsoid((0, 0.32, hz), (0.74, 0.2, 0.76), hair)
    # The laughing red face of the Shojobob line (same proportions as Shojomai's).
    before = k.snapshot()
    face = k.mask_shell(face_m, lacquer, width=0.6, depth=0.38, height=0.7)
    for x in (-0.3, 0.3):
        k.bump(face, x, -0.18, (0.17, 0.09, 0.14), face_m)
        p = k.on_face(face, x * 0.8, 0.14, lift=0.01)
        k.front_only(k.ellipsoid(p, (0.15, 0.04, 0.06), ink, rot=(0, math.radians(18 if x < 0 else -18), 0)))
    k.hole(face, 0, -0.36, (0.25, 0.11), backing=lip)
    k.cord_holes(face, lacquer)
    k.transform(k.since(before), offset=(0, 0, hz))
    # The gold robe, standing in the cup.
    k.cone((0, 0.12, -0.72), 0.3, 0.9, robe, radius2=0.46, rot=(math.pi, 0, 0), segments=24)
    for side, hand in ((-1, k.Vector((-0.95, -0.15, 0.2))), (1, k.Vector((0.8, -0.2, -0.75)))):
        sh = k.Vector((side * 0.34, 0.05, -0.4))
        k.rod(sh, hand, 0.09, robe)
        k.ellipsoid(hand, (0.1, 0.1, 0.1), arm)
    # The long-handled ladle flung up in its left hand.
    k.rod((-0.95, -0.15, 0.2), (-1.55, -0.25, 1.0), 0.045, wood)
    k.cylinder((-1.62, -0.25, 1.1), 0.24, 0.24, wood, rot=(0, math.radians(30), 0))
    # The great sake cup: a wide shallow bowl on a foot, sake inside, waves round it.
    k.cone((0, 0.1, -1.28), 0.5, 0.42, cup, radius2=1.25, segments=32)
    k.cylinder((0, 0.1, -1.08), 1.2, 0.03, sake, segments=32)
    k.torus((0, 0.1, -1.07), 1.24, 0.05, cupin)
    k.cylinder((0, 0.1, -1.55), 0.4, 0.14, cup, segments=24)
    k.torus((0, 0.1, -1.62), 1.0, 0.1, water)
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.3
        k.ellipsoid((1.15 * math.cos(a), 0.1 + 1.15 * math.sin(a), -1.6), (0.2, 0.2, 0.1), foam)
    return {'kind': 'mask', 'size': 0.92, 'front_az': -16, 'front_el': 10}
