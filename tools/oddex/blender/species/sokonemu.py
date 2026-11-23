"""Sokonemu: the sleeper under the sea. After the small stone idol described in H. P. Lovecraft's
"The Call of Cthulhu" (Weird Tales, February 1928; public domain): a vaguely anthropoid thing with
an octopus-like head whose face is a mass of feelers, a scaly rubbery body, great claws on fore
and hind feet and long narrow wings behind, squatting on a block carved with unreadable
characters, in greenish-black stone flecked with gold. A fictional monster with no real worship;
nothing here comes from later writers, artists or games. Sootopolis segment, the Kyogre slot
(role LEGEND_SEA; docs/research/mask-designs.md, "海底:Sokonemu"). The whole face is one stone
mask whose lower half comes apart into feelers; the eyes are two slits that barely open.
Silhouette at 64px: a big domed head with hanging feelers on a squatting body on a square block.
Water/psychic."""
import math

NORMAL = {'stone': (0.20, 0.40, 0.31), 'deep': (0.09, 0.19, 0.16), 'feeler': (0.30, 0.52, 0.40),
          'inner': (0.46, 0.14, 0.22), 'fleck': (0.88, 0.72, 0.30), 'iris': (0.46, 0.34, 0.62),
          'eye': (0.98, 0.84, 0.34), 'block': (0.52, 0.55, 0.52), 'blockdark': (0.24, 0.27, 0.27),
          'growth': (0.14, 0.30, 0.20), 'claw': (0.80, 0.80, 0.66)}
# Shiny: pale stone that has lain in the sea too long, red coral grown on it.
SHINY = {**NORMAL, 'stone': (0.78, 0.82, 0.80), 'deep': (0.46, 0.52, 0.54), 'feeler': (0.90, 0.92, 0.88),
         'growth': (0.90, 0.26, 0.22), 'eye': (0.30, 0.90, 0.90), 'iris': (0.86, 0.40, 0.40)}


# Hand-placed pixels (make_art.apply_pixels): the idol's eyes are two slanting slits in the stone, a gold line under a dark lid, barely
# open; in the second frame they open one pixel more. It has no mouth to see: the feelers hang over it.
_FACE = [
    ((25, 11), ['kk.....',
                'eekkk..',
                'kkeeekk',
                '..kkkee',
                '...hhkk']),
    ((39, 11), ['.....kk',
                '..kkkee',
                'kkeeekk',
                'eekkk..',
                'kkhh...']),
]
# The second frame moves the parts by different amounts, so it has its own patches.
_FACE2 = [
    ((25, 11), ['kk.....',
                'eekkk..',
                'eeeeekk',
                'kkeeeee',
                '..kkkee',
                '...hhkk']),
    ((39, 11), ['.....kk',
                '..kkkee',
                'kkeeeee',
                'eeeeekk',
                'eekkk..',
                'kkhh...']),
]
_ICON = [
    ((11, 10), ['YYK..KYY']),
    ((13, 11), ['HH']),
]
PIXELS = {'keys': {'k': (28, 18, 22),
                   'e': (241, 221, 149),
                   'h': (97, 134, 119),
                   'Y': (246, 246, 41),
                   'K': (65, 65, 65),
                   'H': (123, 123, 123)},
          'front': {'box': (5, 2, 58, 56), 'patches': _FACE},
          'front2': {'box': (5, 2, 58, 56), 'patches': _FACE2},
          'icon': {'box': (3, 5, 28, 30), 'patches': _ICON},
          'icon2': {'box': (3, 4, 28, 29), 'patches': [((x, y - 1), rows) for (x, y), rows in _ICON]}}


def build(k, c):
    stone = k.toon('stone', c['stone'], steps=k.HORROR_STEPS, glint=0.25)
    deep = k.toon('deep', c['deep'], two_tone=True)
    feeler = k.toon('feeler', c['feeler'], two_tone=True)
    inner = k.flat('inner', c['inner'])
    fleck = k.flat('fleck', c['fleck'])
    iris = k.toon('iris', c['iris'], two_tone=True)
    eye = k.flat('eye', c['eye'])
    block = k.toon('block', c['block'], two_tone=True)
    blockdark = k.flat('blockdark', c['blockdark'])
    growth = k.toon('growth', c['growth'], two_tone=True)
    claw = k.toon('claw', c['claw'], two_tone=True)
    k.set_light((-0.75, -0.6, 0.2))

    # The block it squats on, three scored lines on its front (marks, not any real script).
    k.cylinder((0, 0.1, -1.25), 1.25, 0.62, block, rot=(0, 0, math.pi / 4), segments=4)
    for z in (-1.1, -1.25, -1.4):
        k.rod((-0.6, -0.8, z), (0.6, -0.8, z), 0.03, blockdark)
    for x, z, s in ((-0.75, -1.0, 0.14), (0.7, -1.3, 0.12), (0.85, -0.98, 0.1)):
        k.ellipsoid((x, -0.72, z), (s, s * 0.6, s * 0.7), growth)

    # The squatting body: knees drawn up, fore claws clasping them, hind claws over the edge.
    k.ellipsoid((0, 0.15, -0.45), (0.8, 0.66, 0.6), deep)
    for side in (-1, 1):
        k.ellipsoid((side * 0.6, -0.4, -0.55), (0.34, 0.38, 0.42), stone)   # the knee
        k.rod((side * 0.95, 0.05, -0.05), (side * 0.66, -0.72, -0.4), 0.14, stone)   # the fore limb clasping it
        for j in (-1, 0, 1):
            k.spike((side * 0.66 + j * 0.11, -0.76, -0.4), (side * 0.66 + j * 0.13, -0.9, -0.66), 0.06, claw)
            k.spike((side * 0.56 + j * 0.13, -0.74, -0.9), (side * 0.56 + j * 0.15, -0.98, -1.0), 0.06, claw)
    # The long narrow wings folded behind, their tips rising past the head.
    for side in (-1, 1):
        k.ellipsoid((side * 1.12, 0.6, 0.2), (0.14, 0.08, 1.0), deep, rot=(0, math.radians(side * 14), 0))
        k.ellipsoid((side * 1.24, 0.62, 0.22), (0.05, 0.06, 0.92), iris, rot=(0, math.radians(side * 14), 0))

    # The head: a smooth dome, the face one mask that comes apart into feelers below the eyes.
    head_c, head_r = (0, -0.15, 0.72), (0.86, 0.7, 0.66)
    k.ellipsoid(head_c, head_r, stone)

    def at(x, z, lift=0.0):
        return k.head_point(head_c, head_r, x, z, lift)

    for side in (-1, 1):   # the slit eyes (redrawn by hand in PIXELS)
        k.ellipsoid(at(side * 0.36, 0.78, 0.01), (0.24, 0.04, 0.07), deep, rot=(0, math.radians(side * 16), 0))
        k.ellipsoid(at(side * 0.36, 0.775, 0.03), (0.16, 0.03, 0.03), eye, rot=(0, math.radians(side * 16), 0))
    for i, (x, length, curl) in enumerate(((-0.6, 0.4, -1), (-0.4, 0.55, -1), (-0.2, 0.75, 0), (0.0, 0.85, 0), (0.2, 0.75, 0),
                                           (0.4, 0.55, 1), (0.6, 0.4, 1))):
        p = at(x, 0.5, 0.02)
        n = 6
        for j in range(n):
            t = j / (n - 1)
            q = (p.x + curl * 0.22 * t * t, p.y - 0.12 * math.sin(t * math.pi) - 0.04, p.z - length * t)
            r = 0.125 * (1 - 0.5 * t)
            k.ellipsoid(q, (r, r, r * 1.3), inner if (j == n - 1) else feeler, segments=16)
    # Gold flecks in the stone.
    for x, z in ((-0.45, 1.05), (0.3, 1.12), (0.6, 0.92), (-0.1, 1.24)):
        k.ellipsoid(at(x, z, 0.01), (0.04, 0.02, 0.04), fleck)
    for x, z in ((-0.3, -0.1), (0.42, -0.2), (0.05, 0.05)):
        k.ellipsoid((x, -0.56, z), (0.04, 0.03, 0.04), fleck)
    return {'kind': 'beast', 'size': 0.95, 'front_az': -10, 'front_el': 6, 'side_az': -70, 'squash': (1.02, 1.02, 0.98)}
