"""Waraningyo: the straw doll of the ushi-no-koku-mairi curse, nailed to a tree at two in the
morning with five-inch nails; the Noh play "Kanawa" tells of the woman who wore an iron trivet
upside down on her head with a candle on each leg to cast it. A cursing tool and a story, not a
deity (no Hashihime: she has a shrine). League segment, replaces Cacturne, the scarecrow, on
Sidney's team (docs/research/mask-designs.md, "Waraningyo 的 Brief", option A). A man-shaped
sheaf of straw with its arms out, a great nail through its chest; its face is a sheet of white
paper nailed on, the features in ink, one eye pierced by the nail; the trivet sits on its head,
three candles burning. Silhouette at 64px: a straw cross with three flames above. The trivet and
candles are not a crown of any kind. Grass/dark."""
import math

NORMAL = {'straw': (0.86, 0.72, 0.36), 'strawdark': (0.56, 0.42, 0.18), 'rope': (0.28, 0.16, 0.09),
          'paper': (0.97, 0.96, 0.92), 'ink': (0.05, 0.05, 0.07), 'iron': (0.40, 0.42, 0.48),
          'irondark': (0.20, 0.21, 0.26), 'candle': (0.95, 0.93, 0.84), 'flame': (1.0, 0.84, 0.25),
          'flamecore': (1.0, 0.48, 0.12)}
# Shiny: old straw gone black, the candles burning blue.
SHINY = {**NORMAL, 'straw': (0.34, 0.30, 0.28), 'strawdark': (0.18, 0.16, 0.16), 'flame': (0.55, 0.85, 1.0),
         'flamecore': (0.20, 0.45, 0.95)}


def bundle(k, a, b, r, straw, rope, frayed=True):
    """A tied sheaf of straw from a to b: the sheaf, a rope band near the far end, frayed tips."""
    a, b = k.Vector(a), k.Vector(b)
    k.rod(a, b, r, straw)
    d = (b - a).normalized()
    band = a.lerp(b, 0.78)
    k.rod(band - d * 0.04, band + d * 0.04, r * 1.12, rope)
    if frayed:
        side = d.cross(k.Vector((0, 1, 0)))
        if side.length < 1e-3:
            side = k.Vector((1, 0, 0))
        side.normalize()
        for j in (-1, 0, 1):
            k.spike(b - d * 0.05, b + d * 0.2 + side * j * r * 0.9, r * 0.45, straw)


# Hand-placed pixels (make_art.apply_pixels): the paper face, in ink. One square dot of an eye; where the
# other eye was, the grey head of the nail driven through it; a short straight line of a mouth (no smile).
_FACE = [
    ((29, 20), ['......iii.',
                'fkkfffikif',
                'fkkfffiiif',
                'ffffffffff',
                'ffffffffff',
                'ffkkkkkfff',
                'ffffffffff']),
]
_ICON = [((14, 12), ['K..K'])]
PIXELS = {'keys': {'f': (252, 251, 246), 'k': (28, 18, 22), 'i': (118, 120, 128), 'K': (65, 65, 65)},
          'front': {'box': (15, 0, 49, 56), 'patches': _FACE},
          'front2': {'box': (13, 0, 50, 56), 'patches': [((x, y - 1), rows) for (x, y), rows in _FACE]},
          'icon': {'box': (7, 2, 24, 30), 'patches': _ICON},
          'icon2': {'box': (7, 1, 24, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    straw = k.toon('straw', c['straw'], steps=(0.5, 0.78, 1.0))
    strawdark = k.toon('strawdark', c['strawdark'], two_tone=True)
    rope = k.flat('rope', c['rope'])
    paper = k.toon('paper', c['paper'], two_tone=True)
    ink = k.flat('ink', c['ink'])
    iron = k.toon('iron', c['iron'], two_tone=True, glint=0.4)
    irondark = k.flat('irondark', c['irondark'])
    candle = k.toon('candle', c['candle'], two_tone=True)
    flame = k.flat('flame', c['flame'])
    flamecore = k.flat('flamecore', c['flamecore'])
    k.set_light((-0.7, -0.6, 0.2))

    # The sheaf: a body, two arms straight out, two legs apart, a round head, tied at every joint.
    k.ellipsoid((0, 0, -0.2), (0.56, 0.44, 0.74), straw)
    for z in (0.3, -0.6):
        k.torus((0, 0, z), 0.46, 0.07, rope)
    for x in (-0.28, 0.0, 0.26):   # the lie of the straw
        k.rod((x, -0.42, 0.22), (x * 1.1, -0.44, -0.55), 0.02, strawdark)
    for side in (-1, 1):
        bundle(k, (side * 0.3, 0, 0.16), (side * 1.02, 0.02, 0.3), 0.24, straw, rope)
        bundle(k, (side * 0.24, 0, -0.75), (side * 0.52, 0, -1.4), 0.25, straw, rope)
    k.ellipsoid((0, 0, 0.82), (0.56, 0.5, 0.54), strawdark)
    for i in range(7):   # loose straw standing up from the top of the head, inside the trivet
        a = math.radians(-70 + i * 23)
        k.spike((0.3 * math.sin(a), 0.05, 1.2), (0.46 * math.sin(a), 0.05, 1.62 + 0.06 * math.cos(a * 3)), 0.06, straw)

    # The paper face, nailed on; its features are ink (redrawn by hand in PIXELS).
    k.ellipsoid((0, -0.46, 0.8), (0.44, 0.06, 0.46), paper)
    for x in (-0.18, 0.18):
        k.ellipsoid((x, -0.52, 0.88), (0.06, 0.02, 0.06), ink)
    k.rod((-0.13, -0.52, 0.62), (0.13, -0.52, 0.62), 0.025, ink)
    k.rod((0.18, -0.5, 0.88), (0.42, -1.0, 1.12), 0.04, iron)        # the nail through one eye
    k.ellipsoid((0.42, -1.02, 1.12), (0.1, 0.05, 0.1), irondark)
    # The great nail through its chest.
    k.rod((0, -0.36, -0.1), (-0.16, -1.1, 0.1), 0.07, iron)
    k.ellipsoid((-0.16, -1.12, 0.1), (0.17, 0.06, 0.17), irondark)

    # The iron trivet upside down on its head, a candle burning on each leg.
    k.torus((0, 0, 1.24), 0.5, 0.06, iron)
    for a_deg in (-150, -30, 90):
        a = math.radians(a_deg)
        foot = k.Vector((0.5 * math.cos(a), 0.5 * math.sin(a), 1.24))
        top = foot + k.Vector((0.14 * math.cos(a), 0.14 * math.sin(a), 0.34))
        k.rod(foot, top, 0.05, iron)
        k.cylinder((top.x, top.y, top.z + 0.16), 0.09, 0.32, candle)
        k.ellipsoid((top.x, top.y, top.z + 0.5), (0.13, 0.13, 0.24), flame)
        k.ellipsoid((top.x, top.y, top.z + 0.45), (0.065, 0.065, 0.12), flamecore)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -12, 'front_el': 6, 'side_az': -70}
