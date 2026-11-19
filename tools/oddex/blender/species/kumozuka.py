"""Kumozuka: the earth-spider spirit of the Noh play Tsuchigumo, which throws white threads across
the stage (Rustboro batch, docs/research/mask-designs.md); only the play's spider, not the old
ethnic slur. Its face is a shikami grimace with Fudo's heaven-and-earth eyes (one looking up,
one down) and its threads are knotted into a binding lasso; venom drips from its fangs.
Fusion: Kamorai/Hannyagon's clenched fangs and knitted brows, the shared spider legs, and
Yamambrr's wild hair turned into threads. Masked spider; bug/poison."""
import math

NORMAL = {'mask': (0.55, 0.14, 0.10), 'lacquer': (0.14, 0.05, 0.04), 'gold': (0.90, 0.70, 0.22),
          'pupil': (0.03, 0.02, 0.02), 'socket': (0.18, 0.04, 0.04), 'gum': (0.38, 0.05, 0.12),
          'tooth': (0.93, 0.88, 0.72), 'body': (0.30, 0.22, 0.15), 'leg': (0.20, 0.15, 0.10),
          'thread': (0.95, 0.95, 0.92), 'venom': (0.65, 0.30, 0.85)}
SHINY = {**NORMAL, 'body': (0.10, 0.10, 0.12), 'leg': (0.06, 0.06, 0.08), 'thread': (0.80, 0.84, 0.95),
         'mask': (0.25, 0.30, 0.55)}


def build(k, c):
    mask_m = k.toon('mask', c['mask'], steps=k.HORROR_STEPS, glint=0.3, weathered=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True)
    pupil = k.flat('pupil', c['pupil'])
    socket = k.flat('socket', c['socket'])
    gum = k.toon('gum', c['gum'], two_tone=True)
    tooth = k.toon('tooth', c['tooth'], two_tone=True)
    body = k.toon('body', c['body'], steps=k.HORROR_STEPS)
    leg = k.toon('leg', c['leg'], two_tone=True)
    thread = k.flat('thread', c['thread'])
    venom = k.flat('venom', c['venom'])
    k.set_light((-0.75, -0.55, -0.15))

    # Spider body behind the mask, eight legs.
    k.ellipsoid((0, 0.55, -0.1), (0.55, 0.6, 0.42), body)
    k.ellipsoid((0, 0.15, -0.25), (0.4, 0.3, 0.3), body)
    k.spider_legs((0, 0.35, -0.2), 4, 1.25, leg, radius=0.045, spread=(-55, 60), lift=0.5, ground=-0.95, ring=0.3)

    face = k.mask_shell(mask_m, lacquer, width=0.66, depth=0.45, height=0.66)
    k.brows(face, 0.27, 0.36, 0.25, mask_m, frown=36, thick=0.12)
    # Heaven-and-earth eyes: the left looks up, the right looks down.
    for side, z, dz in ((-1, 0.2, 0.06), (1, 0.08, -0.06)):
        s = k.on_face(face, side * 0.27, z, lift=0.0)
        k.front_only(k.ellipsoid(s, (0.2, 0.05, 0.17), socket))
        e = k.on_face(face, side * 0.27, z, lift=0.06)
        k.front_only(k.ellipsoid(e, (0.15, 0.12, 0.13), gold))
        k.front_only(k.ellipsoid((e.x, e.y - 0.12, e.z + dz), (0.05, 0.02, 0.06), pupil))
    # Clenched shikami grimace: two rows of teeth pressed together, venom at the fangs.
    k.fanged_mouth(face, -0.38, 0.38, 0.13, pupil, gum, tooth, fang=tooth, upper=6, lower=6, fang_len=0.14)
    for side in (-1, 1):
        f = k.on_face(face, side * 0.31, -0.55, lift=0.05)
        k.front_only(k.ellipsoid((f.x, f.y, f.z - 0.08), (0.035, 0.03, 0.05), venom))
    # Threads streaming from behind the mask, one knotted into a lasso.
    for x, z, dx, dz in ((-0.5, 0.5, -0.9, 0.5), (0.45, 0.55, 0.85, 0.65), (-0.2, 0.62, -0.4, 0.95),
                         (0.25, 0.6, 0.55, 1.0)):
        k.rod((x, 0.1, z), (x + dx, 0.15, z + dz * 0.6), 0.02, thread)
    k.torus((0.95, 0.0, 0.85), 0.16, 0.022, thread, rot=(math.radians(70), 0, 0))
    k.rod((0.45, 0.1, 0.55), (0.85, 0.02, 0.75), 0.02, thread)
    return {'kind': 'beast', 'size': 0.86, 'front_az': -20, 'side_az': -70}
