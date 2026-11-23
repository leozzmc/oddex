"""Utsuroban: the ship from the sky. After the Edo-period legend of the utsuro-bune, the "hollow
ship" that drifted ashore in Hitachi in 1803 (told in Toen shosetsu, 1825, and other Edo
miscellanies; folklore, public domain): a round vessel like an incense burner, the upper half
glass windows, the lower half plated with iron, unreadable signs inside, and a stranger in it who
let no one touch the box she held. The face at the window is the small grey visitor of
twentieth-century sighting stories (a large head, large black almond eyes, no expression); no
ship or character from any film, show, comic or game. Sootopolis segment, the Rayquaza slot (role
LEGEND_SKY; docs/research/mask-designs.md, "天上:Utsuroban"). The grey face is the mask; a beam
drops from under the hull with the box hanging in it. Silhouette at 64px: a round ship with two
black eyes at its window and a widening beam below. Psychic/flying."""
import math

NORMAL = {'iron': (0.22, 0.17, 0.15), 'plate': (0.40, 0.32, 0.27), 'gold': (0.92, 0.74, 0.26),
          'lacquer': (0.09, 0.08, 0.11), 'glass': (0.42, 0.80, 0.86), 'bar': (0.12, 0.20, 0.26),
          'face': (0.82, 0.84, 0.82), 'eye': (0.02, 0.02, 0.03), 'beam': (1.0, 0.94, 0.56),
          'core': (1.0, 1.0, 0.90), 'box': (0.82, 0.16, 0.12), 'cord': (0.20, 0.10, 0.08)}
# Shiny: rusted red plates, a green beam, amber glass.
SHINY = {**NORMAL, 'iron': (0.42, 0.14, 0.08), 'plate': (0.70, 0.30, 0.16), 'glass': (0.95, 0.70, 0.28),
         'beam': (0.56, 1.0, 0.60), 'core': (0.90, 1.0, 0.90), 'box': (0.20, 0.30, 0.75)}


# Hand-placed pixels (make_art.apply_pixels): the grey visitor's face at the middle window, a large head with two large black almond
# eyes slanting up and out and no mouth at all, and a pair of eyes in the dark behind each side window.
_FACE = [
    ((28, 8), ['...eeeeee...',
               '..eeeeeeee..',
               '.eeeeeeeeee.',
               '.ekkeeeekke.',
               '.ekkkeekkke.',
               '.eekkeekkee.',
               'cceeeeeeee..',
               '.cceeeeeecc.']),
    ((17, 11), ['k.k']),
    ((18, 13), ['c']),
    ((45, 11), ['k.k']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((29, 9), ['...eeeeee...',
               '..eeeeeeee..',
               '.eeeeeeeeee.',
               '.ekkeeeekke.',
               '.ekkkeekkke.',
               '.eekkeekkee.',
               'cceeeeeeee..',
               '..uuuuuuuu..']),
    ((18, 12), ['k.k']),
    ((46, 12), ['k.k']),
]
PIXELS = {'keys': {'k': (28, 18, 22), 'e': (234, 236, 234), 'c': (173, 231, 238), 'u': (129, 115, 108)},
          'front': {'box': (6, 0, 57, 56), 'patches': _FACE},
          'front2': {'box': (5, 0, 59, 56), 'patches': _FACE2}}


def build(k, c):
    iron = k.toon('iron', c['iron'], two_tone=True)
    plate = k.toon('plate', c['plate'], two_tone=True)
    gold = k.toon('gold', c['gold'], two_tone=True, glint=0.4)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True, glint=0.5)
    glass = k.toon('glass', c['glass'], two_tone=True, glint=0.5)
    bar = k.flat('bar', c['bar'])
    face = k.toon('face', c['face'], two_tone=True)
    eye = k.flat('eye', c['eye'])
    beam = k.flat('beam', c['beam'])
    core = k.flat('core', c['core'])
    box = k.toon('box', c['box'], two_tone=True)
    cord = k.flat('cord', c['cord'])
    k.set_light((-0.7, -0.6, 0.3))

    # The beam first (it is behind everything else it touches): a widening cone with a bright core.
    k.cone((0, 0.1, -1.2), 0.8, 1.5, beam, radius2=0.3, segments=24)
    k.cone((0, -0.5, -1.2), 0.36, 1.5, core, radius2=0.12, segments=16)
    # The box no one may touch, hanging in the beam: a plain box wider than it is tall, on one cord. Nothing
    # crosses it: a red box tied crosswise on the pale beam read as a red cross at 32px, a protected emblem.
    k.cylinder((0, -0.9, -1.3), 0.38, 0.3, box, rot=(0, 0, math.pi / 4), segments=4)
    k.rod((0, -0.9, -1.15), (0, -0.9, -0.6), 0.03, cord)   # one cord from its lid up into the hull

    # The lower hull: a deep bowl plated with strips of iron, riveted in gold.
    k.ellipsoid((0, 0, 0.05), (1.3, 1.3, 0.62), iron)
    for i in range(12):
        a = 2 * math.pi * i / 12
        top = k.Vector((1.27 * math.cos(a), 1.27 * math.sin(a), 0.02))
        bottom = k.Vector((0.5 * math.cos(a), 0.5 * math.sin(a), -0.53))
        mid = k.Vector((1.06 * math.cos(a), 1.06 * math.sin(a), -0.32))
        k.rod(top, mid, 0.05, plate)
        k.rod(mid, bottom, 0.05, plate)
        k.ellipsoid(mid, (0.06, 0.06, 0.06), gold)
    k.torus((0, 0, 0.1), 1.34, 0.1, gold)
    # Four signs on the hull that no one can read (plain shapes, not copied from the old drawings).
    k.torus((-0.55, -1.05, -0.18), 0.07, 0.02, gold, rot=(math.radians(70), 0, 0))
    k.rod((-0.22, -1.17, -0.26), (-0.14, -1.2, -0.12), 0.02, gold)
    k.rod((0.14, -1.2, -0.12), (0.22, -1.17, -0.26), 0.02, gold)
    k.rod((0.14, -1.19, -0.26), (0.24, -1.16, -0.12), 0.02, gold)
    k.ellipsoid((0.56, -1.04, -0.18), (0.05, 0.03, 0.07), gold)
    # The upper half: a black dome with a band of latticed windows, a knob on top.
    k.ellipsoid((0, 0, 0.2), (1.12, 1.12, 0.95), lacquer)
    k.ellipsoid((0, 0, 1.15), (0.14, 0.14, 0.1), gold)
    for a_deg, w in ((0, 0.5), (-56, 0.3), (56, 0.3)):
        a = math.radians(a_deg - 90)
        p = (0.98 * math.cos(a), 0.98 * math.sin(a), 0.52)
        k.ellipsoid(p, (w, 0.12, 0.36), glass, rot=(0, 0, math.radians(a_deg)))
    for a_deg in (-31, 31):
        a = math.radians(a_deg - 90)
        k.rod((1.1 * math.cos(a), 1.1 * math.sin(a), 0.16), (0.98 * math.cos(a), 0.98 * math.sin(a), 0.9), 0.035, bar)
    # The face at the middle window, and a pair of eyes in the dark behind each side window.
    k.ellipsoid((0, -1.04, 0.52), (0.36, 0.1, 0.3), face)
    for side in (-1, 1):
        k.ellipsoid((side * 0.15, -1.13, 0.56), (0.11, 0.03, 0.08), eye, rot=(0, math.radians(side * 24), 0))
        a = math.radians(side * 56 - 90)
        for dx in (-0.07, 0.07):
            k.ellipsoid((1.06 * math.cos(a) + dx * math.sin(-a), 1.06 * math.sin(a) + dx * math.cos(a), 0.54), (0.045, 0.04, 0.05), eye)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -8, 'front_el': 2, 'side_az': -70, 'squash': (1.05, 1.05, 0.96)}
