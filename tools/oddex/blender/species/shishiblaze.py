"""Shishiblaze: Shishiguchi (Noh, the lion of "Shakkyo") worn by a lion cub, played as
traditional Japanese horror: tarnished gilt face under a knitted brow, huge staring eyes, a
gaping maw with dark gums, two rows of teeth and fangs, a flame-red mane. The cub's body stays
small behind the mask. Masked quadruped; fire/fighting."""
import math

NORMAL = {'mask': (0.60, 0.40, 0.12), 'lacquer': (0.20, 0.07, 0.05), 'mane': (0.78, 0.10, 0.06),
          'body': (0.62, 0.34, 0.14), 'throat': (0.04, 0.02, 0.02), 'gum': (0.44, 0.04, 0.10),
          'tooth': (0.95, 0.92, 0.80), 'eye': (1.0, 0.93, 0.42), 'socket': (0.10, 0.04, 0.02),
          'peony': (0.92, 0.42, 0.58)}
# The white lion of Shakkyo: tarnished silver mask, white mane.
SHINY = {**NORMAL, 'mask': (0.72, 0.74, 0.78), 'mane': (0.94, 0.93, 0.88), 'body': (0.80, 0.74, 0.64),
         'eye': (0.92, 0.30, 0.20), 'socket': (0.10, 0.10, 0.14)}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=k.HORROR_STEPS, glint=0.45, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    mane = k.toon('mane', c['mane'], steps=k.HORROR_STEPS)
    body = k.toon('body', c['body'], two_tone=True)
    throat = k.flat('throat', c['throat'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    eye_m = k.toon('eye', c['eye'], two_tone=True)
    socket = k.flat('socket', c['socket'])
    peony = k.toon('peony', c['peony'], two_tone=True)
    k.set_light((-0.7, -0.6, -0.15))

    face = k.mask_shell(mask_m, lacquer, width=0.76, depth=0.5, height=0.78)
    k.brows(face, 0.3, 0.42, 0.3, mask_m, frown=34, thick=0.13)
    k.glare_eyes(face, 0.32, 0.2, 0.2, eye_m, throat, socket)
    k.bump(face, 0, -0.02, (0.24, 0.16, 0.15), mask_m, lift=0.03)
    k.wrinkles(face, mask_m, [(-0.2, -0.08, 0.09, 0.06, 0), (0.2, -0.08, 0.09, 0.06, 0),
                              (-0.42, -0.2, 0.05, 0.18, -25), (0.42, -0.2, 0.05, 0.18, 25)])
    k.fanged_mouth(face, -0.42, 0.42, 0.24, throat, gum, tooth, fang=tooth, upper=5, lower=4, fang_len=0.22)
    # A ring of flame-red mane locks swept back from the rim of the mask.
    for i in range(20):
        a = i * 2 * math.pi / 20
        base = (0.78 * math.cos(a), 0.12, 0.8 * math.sin(a))
        tip = (1.2 * math.cos(a), 0.45, 1.15 * math.sin(a) - 0.1)
        k.spike(base, tip, 0.17, mane)

    def tail(at, mat):
        k.rod(at, at + k.Vector((0, 0.35, 0.3)), 0.05, mat)
        for i in range(5):
            a = i * 2 * math.pi / 5
            k.ellipsoid(at + k.Vector((0.09 * math.cos(a), 0.38, 0.38 + 0.09 * math.sin(a))), (0.1, 0.07, 0.1), peony)

    k.beast_behind_mask(0.78, body, length=1.5, girth=0.48, leg=0.45, tail=tail)
    return {'kind': 'beast', 'size': 0.9, 'front_az': -20, 'side_az': -75}
