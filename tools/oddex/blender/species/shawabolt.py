"""Shawabolt: the stag from the Cham dance of the stag and the hounds (Shawa Shachi, Bhutan), the
animal Milarepa sheltered; a story animal, not a deity. A young stag wearing a carved stag mask:
wide staring eyes, an open mouth, tall antlers hung with streamers. Masked quadruped;
electric/fairy."""
import math

NORMAL = {'mask': (0.80, 0.62, 0.30), 'lacquer': (0.16, 0.07, 0.04), 'trim': (0.15, 0.50, 0.30),
          'eye': (0.98, 0.95, 0.75), 'pupil': (0.03, 0.02, 0.02), 'socket': (0.45, 0.20, 0.08),
          'gum': (0.48, 0.06, 0.10), 'tooth': (0.96, 0.94, 0.86), 'antler': (0.95, 0.88, 0.40),
          'body': (0.62, 0.42, 0.24), 'streamer': (0.95, 0.40, 0.60)}
SHINY = {**NORMAL, 'mask': (0.92, 0.92, 0.88), 'antler': (0.55, 0.85, 1.0), 'body': (0.90, 0.78, 0.40)}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=k.HORROR_STEPS, glint=0.3, weathered=0.25)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    trim = k.toon('trim', c['trim'], two_tone=True)
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    antler = k.toon('antler', c['antler'], two_tone=True)
    body = k.toon('body', c['body'], two_tone=True)
    streamer = k.toon('streamer', c['streamer'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.1))

    face = k.mask_shell(mask_m, lacquer, width=0.56, depth=0.5, height=0.74)
    k.brows(face, 0.24, 0.4, 0.2, trim, frown=20, thick=0.08)
    k.glare_eyes(face, 0.25, 0.18, 0.16, eye_m, pupil, socket)
    s = k.on_face(face, 0, -0.2, lift=0.0)
    k.front_only(k.ellipsoid((s.x, s.y - 0.12, s.z - 0.05), (0.2, 0.2, 0.2), mask_m))
    k.fanged_mouth(face, -0.48, 0.24, 0.13, pupil, gum, tooth, upper=3, lower=3)
    # Tall branching antlers with streamers, and ears.
    for side in (-1, 1):
        a0 = k.Vector((side * 0.25, 0.05, 0.6))
        a1 = k.Vector((side * 0.55, 0.05, 1.25))
        a2 = k.Vector((side * 0.45, 0.05, 1.7))
        k.rod(a0, a1, 0.05, antler)
        k.rod(a1, a2, 0.045, antler)
        k.rod(a1, a1 + k.Vector((side * 0.35, 0, 0.2)), 0.04, antler)
        k.rod((a0 + a1) / 2, (a0 + a1) / 2 + k.Vector((side * 0.3, 0, 0.12)), 0.04, antler)
        k.ellipsoid(a1 + k.Vector((side * 0.05, -0.05, -0.2)), (0.05, 0.03, 0.22), streamer)
        k.spike((side * 0.45, 0.05, 0.3), (side * 0.8, 0.1, 0.45), 0.1, mask_m)

    def tail(at, mat):
        k.ellipsoid(at + k.Vector((0, 0.1, 0.1)), (0.1, 0.1, 0.12), mat)

    k.beast_behind_mask(0.74, body, length=1.3, girth=0.4, leg=0.55, tail=tail)
    return {'kind': 'beast', 'size': 0.9, 'front_az': -24, 'side_az': -75}
