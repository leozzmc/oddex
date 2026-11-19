"""Shachound: a hound from the Cham dance of the stag and the hounds (Shawa Shachi, Bhutan), a
story animal rather than a deity. A dark dog wearing a carved, brightly painted hound mask:
bulging eyes, bared fangs, pricked ears, a cloth band on the brow. Masked quadruped; dark/psychic."""
import math

NORMAL = {'mask': (0.82, 0.55, 0.20), 'lacquer': (0.16, 0.07, 0.04), 'trim': (0.12, 0.45, 0.32),
          'eye': (0.97, 0.92, 0.70), 'pupil': (0.03, 0.02, 0.02), 'socket': (0.55, 0.10, 0.06),
          'gum': (0.50, 0.05, 0.10), 'tooth': (0.97, 0.95, 0.85), 'body': (0.22, 0.20, 0.24),
          'cloth': (0.20, 0.55, 0.75)}
SHINY = {**NORMAL, 'mask': (0.90, 0.88, 0.80), 'trim': (0.75, 0.20, 0.15), 'body': (0.80, 0.70, 0.50)}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=k.HORROR_STEPS, glint=0.3, weathered=0.25)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    trim = k.toon('trim', c['trim'], two_tone=True)
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    body = k.toon('body', c['body'], two_tone=True)
    cloth = k.toon('cloth', c['cloth'], two_tone=True)
    k.set_light((-0.75, -0.55, -0.15))

    face = k.mask_shell(mask_m, lacquer, width=0.66, depth=0.55, height=0.7)
    k.brows(face, 0.27, 0.36, 0.24, trim, frown=32, thick=0.1)
    k.glare_eyes(face, 0.28, 0.16, 0.18, eye_m, pupil, socket)
    k.bump(face, 0, -0.12, (0.2, 0.2, 0.15), mask_m, lift=0.05)
    k.front_only(k.ellipsoid(k.on_face(face, 0, -0.04, lift=0.2), (0.09, 0.06, 0.06), pupil))
    k.fanged_mouth(face, -0.38, 0.36, 0.18, pupil, gum, tooth, fang=tooth, upper=4, lower=4, fang_len=0.18)
    for side in (-1, 1):
        k.spike((side * 0.48, 0.05, 0.5), (side * 0.8, 0.15, 1.05), 0.14, mask_m)
    p = k.on_face(face, 0, 0.55, lift=0.02)
    k.ellipsoid((p.x, p.y, p.z), (0.62, 0.1, 0.07), cloth)
    k.spike((0.6, 0.05, 0.55), (0.95, 0.4, 0.3), 0.05, cloth)

    def tail(at, mat):
        k.spike(at, at + k.Vector((0, 0.35, 0.35)), 0.08, mat)

    k.beast_behind_mask(0.7, body, length=1.3, girth=0.44, leg=0.42, tail=tail)
    return {'kind': 'beast', 'size': 0.88, 'front_az': -24, 'side_az': -75}
