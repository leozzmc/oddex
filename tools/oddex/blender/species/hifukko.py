"""Hifukko: the hyottoko mask (the 'fire man' of village kagura, who blows on the hearth through a
bamboo pipe) on a little clay brazier that walks on four stubby legs (Lavaridge segment,
docs/research/mask-designs.md). Fusion: Usobuzz's pursed usobuki mouth pushed out into the
hyottoko's blowing tube, flames at its tip; mismatched eyes; a knotted cloth headband; Mandalumb's
round disc turned into the brazier on its back, burning. Masked quadruped; fire/ground.
face() is shared with Kamadoro, its second stage."""
import math

NORMAL = {'face': (0.88, 0.70, 0.46), 'lacquer': (0.20, 0.10, 0.06), 'hollow': (0.03, 0.02, 0.02),
          'cheek': (0.86, 0.36, 0.26), 'band': (0.20, 0.36, 0.70), 'bandw': (0.95, 0.95, 0.92),
          'clay': (0.62, 0.36, 0.20), 'claydark': (0.36, 0.20, 0.12), 'ember': (1.0, 0.45, 0.08),
          'flame': (1.0, 0.86, 0.32), 'lips': (0.80, 0.10, 0.12), 'bamboo': (0.36, 0.62, 0.22),
          'node': (0.18, 0.36, 0.12)}
SHINY = {**NORMAL, 'bamboo': (0.86, 0.72, 0.30), 'node': (0.56, 0.42, 0.14), 'face': (0.92, 0.88, 0.80), 'band': (0.75, 0.15, 0.15), 'clay': (0.30, 0.30, 0.36),
         'claydark': (0.16, 0.16, 0.22), 'ember': (0.30, 0.55, 1.0), 'flame': (0.80, 0.94, 1.0)}


def face(k, c, s=1.0, bold=False):
    """The hyottoko mask at scale s, facing -Y at the origin; returns the shell. bold (Hifukko
    after the user's 64px review) makes the pursed red lips and a long green bamboo fire tube
    the face's main shape; Kamadoro keeps the original face (bold=False)."""
    face_m = k.toon('face', c['face'], steps=k.HORROR_STEPS, glint=0.3)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    cheek = k.flat('cheek', c['cheek'])
    band = k.toon('band', c['band'], two_tone=True)
    bandw = k.flat('bandw', c['bandw'])
    ember = k.flat('ember', c['ember'])
    flame = k.flat('flame', c['flame'])
    shell = k.mask_shell(face_m, lacquer, width=0.62 * s, depth=0.42 * s, height=0.72 * s)
    # Mismatched eyes: the left one wide open, the right one squeezed small and higher.
    k.hole(shell, -0.24 * s, 0.14 * s, (0.15 * s, 0.12 * s), backing=hollow)
    k.hole(shell, 0.22 * s, 0.2 * s, (0.11 * s, 0.06 * s), backing=hollow)
    for x, z, ang in ((-0.24, 0.32, 15), (0.22, 0.34, -25)):   # startled brows
        k.front_only(k.ellipsoid(k.on_face(shell, x * s, z * s, lift=0.01 * s), (0.13 * s, 0.02 * s, 0.03 * s), hollow,
                                 rot=(0, math.radians(ang), 0)))
    for x in (-0.36, 0.36):
        k.bump(shell, x * s, -0.12 * s, (0.13 * s, 0.06 * s, 0.1 * s), cheek, lift=0.01 * s)
    if bold:
        _bold_mouth(k, c, shell, s, face_m, hollow, ember, flame)
    else:
        _mouth(k, shell, s, face_m, hollow, cheek, ember, flame)
    # A cloth headband knotted at the side.
    for i in range(9):
        x = (-0.48 + i * 0.12) * s
        k.front_only(k.ellipsoid(k.on_face(shell, x, 0.46 * s, lift=0.01 * s), (0.08 * s, 0.03 * s, 0.06 * s), band))
    k.ellipsoid((0.58 * s, -0.05 * s, 0.46 * s), (0.09 * s, 0.07 * s, 0.07 * s), band)
    for dz in (0.08, -0.05):
        k.spike((0.64 * s, -0.05 * s, 0.46 * s), (0.9 * s, 0.0, (0.5 + dz) * s), 0.04 * s, bandw)
    k.cord_holes(shell, lacquer)
    return shell


def _bold_mouth(k, c, shell, s, face_m, hollow, ember, flame):
    """Sharp pursed red lips, and a long green bamboo fire tube sticking out to the viewer's left
    with a jet of flame: the shapes that have to read at 64px."""
    lips = k.toon('lips', c['lips'], two_tone=True)
    bamboo = k.toon('bamboo', c['bamboo'], two_tone=True)
    node = k.flat('node', c['node'])
    m = k.on_face(shell, 0.05 * s, -0.3 * s)
    k.front_only(k.ellipsoid((m.x, m.y - 0.06 * s, m.z), (0.2 * s, 0.16 * s, 0.15 * s), lips))   # pursed lips
    k.front_only(k.spike((m.x, m.y - 0.1 * s, m.z), (m.x - 0.05 * s, m.y - 0.32 * s, m.z), 0.12 * s, lips))
    root = k.Vector((m.x - 0.05 * s, m.y - 0.28 * s, m.z))
    tip = root + k.Vector((-0.95 * s, -0.25 * s, -0.12 * s))
    k.front_only(k.rod(root, tip, 0.1 * s, bamboo))
    for t in (0.35, 0.7):   # bamboo nodes
        k.front_only(k.torus(root.lerp(tip, t), 0.105 * s, 0.03 * s, node, rot=(0, math.radians(90), math.radians(-15))))
    for dx, dz in ((-0.4, 0.18), (-0.55, 0.0), (-0.38, -0.18)):   # a jet of flame out of the tube
        k.front_only(k.spike(tip, tip + k.Vector((dx * s, -0.1 * s, dz * s)), 0.13 * s, ember))
        k.front_only(k.spike(tip, tip + k.Vector((dx * 0.6 * s, -0.08 * s, dz * 0.6 * s)), 0.07 * s, flame))


def _mouth(k, shell, s, face_m, hollow, cheek, ember, flame):
    # Puckered lips pushed out into a blowing tube, a little to one side, flame at the tip.
    m = k.on_face(shell, 0.08 * s, -0.32 * s)
    k.front_only(k.ellipsoid((m.x, m.y - 0.04 * s, m.z), (0.17 * s, 0.14 * s, 0.14 * s), face_m))
    # The tube points at the viewer's left and a little down, so it stands out in 3/4 view.
    tip = k.Vector((m.x - 0.62 * s, m.y - 0.4 * s, m.z - 0.08 * s))
    k.front_only(k.rod(m, tip, 0.12 * s, cheek))
    k.front_only(k.torus(tip, 0.11 * s, 0.05 * s, face_m, rot=(math.radians(90), 0, math.radians(-57))))
    k.front_only(k.ellipsoid(tip, (0.06 * s, 0.03 * s, 0.06 * s), hollow))
    for dx, dz in ((-0.32, 0.12), (-0.42, -0.02), (-0.3, -0.14)):   # a jet of flame out of the tube
        k.front_only(k.spike(tip, tip + k.Vector((dx * s, -0.12 * s, dz * s)), 0.1 * s, ember))
        k.front_only(k.spike(tip, tip + k.Vector((dx * 0.6 * s, -0.08 * s, dz * 0.6 * s)), 0.05 * s, flame))


def brazier(k, c, at, r):
    """A clay brazier bowl burning on its back."""
    clay = k.toon('clay', c['clay'], two_tone=True)
    claydark = k.flat('claydark', c['claydark'])
    ember = k.flat('ember_b', c['ember'])
    flame = k.flat('flame_b', c['flame'])
    k.ellipsoid(at, (r, r, r * 0.6), clay)
    k.torus((at[0], at[1], at[2] + r * 0.5), r * 0.92, r * 0.14, claydark)
    k.flame_halo((at[0], at[1] + 0.02, at[2] + r * 0.35), r * 0.45, ember, flame, licks=9, length=r * 0.9)


def build(k, c):
    k.set_light((-0.75, -0.55, -0.15))
    face(k, c, 1.2, bold=True)
    clay = k.toon('clay_body', c['clay'], two_tone=True)
    k.beast_behind_mask(0.72, clay, length=0.9, girth=0.4, leg=0.28)
    # The brazier rides high on its back, over its right shoulder, so it is a shape of its own.
    brazier(k, c, (0.72, 0.65, 0.78), 0.42)
    return {'kind': 'beast', 'size': 0.88, 'front_az': -10, 'side_az': -75}
