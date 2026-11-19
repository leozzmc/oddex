"""Kyokon: Kitsune (Kyogen "Tsurigitsune", the old fox who disguises itself as a monk). A fox
wearing a white fox mask over its own face: long snout, red-lined hollow eyes, a
thin grin. Masked quadruped; normal/ghost."""
import math

NORMAL = {'mask': (0.95, 0.94, 0.90), 'lacquer': (0.18, 0.08, 0.05), 'red': (0.78, 0.12, 0.10),
          'hollow': (0.02, 0.02, 0.03), 'body': (0.86, 0.52, 0.22), 'tailtip': (0.97, 0.96, 0.92),
          'gold': (0.92, 0.75, 0.25)}
SHINY = {**NORMAL, 'mask': (0.20, 0.20, 0.24), 'red': (0.90, 0.75, 0.25), 'body': (0.70, 0.72, 0.78)}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=(0.5, 0.78, 1.0), weathered=0.15)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    red = k.flat('red', c['red'])
    hollow = k.flat('hollow', c['hollow'])
    body = k.toon('body', c['body'], two_tone=True)
    tailtip = k.toon('tailtip', c['tailtip'], two_tone=True)
    gold = k.flat('gold', c['gold'])
    k.set_light((-0.7, -0.6, 0.0))

    face = k.mask_shell(mask_m, lacquer, width=0.56, depth=0.42, height=0.7)
    for x in (-0.22, 0.22):
        k.hole(face, x, 0.15, (0.12, 0.04), backing=hollow)
        p = k.on_face(face, x, 0.15)
        k.front_only(k.ellipsoid((p.x, p.y + 0.05, p.z), (0.03, 0.02, 0.025), gold))
        q = k.on_face(face, x * 1.15, 0.22, lift=0.01)
        k.front_only(k.ellipsoid(q, (0.2, 0.03, 0.055), red, rot=(0, k.math.radians(-25 if x < 0 else 25), 0)))
    # A long snout with a thin grin.
    s = k.on_face(face, 0, -0.18, lift=0.0)
    k.front_only(k.ellipsoid((s.x, s.y - 0.25, s.z - 0.08), (0.19, 0.42, 0.15), mask_m))
    k.front_only(k.ellipsoid((s.x, s.y - 0.66, s.z - 0.04), (0.07, 0.05, 0.06), hollow))
    k.front_only(k.ellipsoid((s.x, s.y - 0.4, s.z - 0.18), (0.2, 0.04, 0.03), red))
    for side in (-1, 1):
        k.spike((side * 0.3, 0.0, 0.55), (side * 0.48, 0.05, 1.1), 0.13, mask_m)
        k.spike((side * 0.31, -0.03, 0.62), (side * 0.46, 0.0, 0.98), 0.06, red)

    def tail(at, mat):
        k.ellipsoid(at + k.Vector((0, 0.3, 0.2)), (0.18, 0.35, 0.2), mat, rot=(k.math.radians(-40), 0, 0))
        k.ellipsoid(at + k.Vector((0, 0.58, 0.42)), (0.12, 0.14, 0.12), tailtip)

    k.beast_behind_mask(0.7, body, length=1.25, girth=0.4, leg=0.4, tail=tail)
    return {'kind': 'beast', 'size': 0.86, 'front_az': -26, 'side_az': -75}
