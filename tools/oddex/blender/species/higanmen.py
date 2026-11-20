"""Higanmen: a red spider lily (higanbana) whose heart is a serene zo-onna mask (Lavaridge
segment, docs/research/mask-designs.md). It grows by graves and paddy ridges, blooms only around
the equinox with no leaves at all, and its bulb is poisonous. A ring of long, curled red
petals and threadlike stamens radiates round the pale face like a crown; a bare green stem,
with a smaller lily on each side for hands; the bulb below. Fusion: Omotelle's still, chalk-white
face with painted high brows (as zo-onna, slightly older); Shishiblaze's mane spikes turned
into petals. Masked flower; grass/poison."""
import math

NORMAL = {'face': (0.97, 0.95, 0.92), 'lacquer': (0.16, 0.06, 0.05), 'hollow': (0.03, 0.02, 0.03),
          'ink': (0.08, 0.06, 0.08), 'lip': (0.72, 0.10, 0.14), 'gold': (0.92, 0.75, 0.25),
          'petal': (0.86, 0.10, 0.12), 'petaldark': (0.52, 0.04, 0.08), 'stem': (0.30, 0.55, 0.22),
          'bulb': (0.86, 0.80, 0.66)}
SHINY = {**NORMAL, 'petal': (0.96, 0.94, 0.96), 'petaldark': (0.70, 0.68, 0.80), 'lip': (0.55, 0.20, 0.60)}


def lily(k, at, r, petal, petaldark, n=6):
    """A spider lily head: n long petals curling back, with longer threadlike stamens."""
    at = k.Vector(at)
    for i in range(n):
        a = 2 * math.pi * i / n + 0.3
        out = k.Vector((math.cos(a), -0.15, math.sin(a)))
        mid = at + out * r * 0.6
        tip = at + out * r + k.Vector((0, 0.25 * r, 0))
        k.spike(at, mid, r * 0.16, petal)
        k.spike(mid, tip, r * 0.1, petal)
        k.rod(at, at + out * r * 1.4 + k.Vector((0, -0.2 * r, 0.2 * r)), r * 0.025, petaldark)


def build(k, c):
    face_m = k.toon('face', c['face'], steps=(0.62, 0.85, 1.0), weathered=0.1)
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    ink = k.flat('ink', c['ink'])
    lip = k.flat('lip', c['lip'])
    gold = k.flat('gold', c['gold'])
    petal = k.toon('petal', c['petal'], two_tone=True)
    petaldark = k.flat('petaldark', c['petaldark'])
    stem = k.toon('stem', c['stem'], two_tone=True)
    bulb = k.toon('bulb', c['bulb'], two_tone=True)
    k.set_light((-0.6, -0.75, 0.1))
    # The crown: long curled petals and stamens radiating behind the face.
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.15
        out = k.Vector((math.cos(a), 0, math.sin(a)))
        up = k.Vector((0, 0, 1))
        base = out * 0.45 + k.Vector((0, 0.2, 0.05))
        # A thick petal that curls back on itself at the tip.
        p1 = base + out * 0.35
        p2 = p1 + out * 0.22 + up * 0.12 + k.Vector((0, 0.18, 0))
        p3 = p2 - out * 0.08 + up * 0.1 + k.Vector((0, 0.15, 0))
        k.rod(base, p1, 0.11, petal)
        k.rod(p1, p2, 0.08, petal)
        k.spike(p2, p3, 0.06, petaldark)
        # A long stamen curving out past it.
        s1 = base + out * 0.75 + k.Vector((0, -0.12, 0.05))
        s2 = s1 + out * 0.35 + up * 0.18
        k.rod(base, s1, 0.02, petal)
        k.rod(s1, s2, 0.02, petal)
        k.ellipsoid(s2, (0.04, 0.04, 0.04), petaldark)
    # The serene zo-onna mask: small hollow eyes with a gold glint, high painted brows,
    # a faint closed smile.
    shell = k.mask_shell(face_m, lacquer, width=0.5, depth=0.36, height=0.66)
    for x in (-0.18, 0.18):
        k.hole(shell, x, 0.1, (0.08, 0.03), backing=hollow)
        p = k.on_face(shell, x, 0.1)
        k.front_only(k.ellipsoid((p.x, p.y + 0.04, p.z), (0.025, 0.015, 0.02), gold))
        k.front_only(k.ellipsoid(k.on_face(shell, x, 0.38, lift=0.005), (0.07, 0.02, 0.04), ink))
        k.front_only(k.ellipsoid(k.on_face(shell, x, 0.1, lift=0.005), (0.11, 0.02, 0.025), ink))   # heavy upper lid
    k.bump(shell, 0, -0.05, (0.06, 0.06, 0.12), face_m, lift=0.01)
    for z, sx in ((-0.32, 0.12), (-0.37, 0.1)):
        p = k.on_face(shell, 0, z)
        k.front_only(k.ellipsoid((p.x, p.y - 0.01, p.z), (sx, 0.03, 0.02), lip))
    # The bare stem, a lily on each side for hands, and the bulb below.
    k.rod((0, 0.15, -0.6), (0, 0.15, -1.45), 0.07, stem)
    for side in (-1, 1):
        k.rod((0, 0.15, -0.95), (side * 0.75, 0.05, -0.55), 0.04, stem)
        lily(k, (side * 0.8, 0.0, -0.5), 0.3, petal, petaldark)
    k.ellipsoid((0, 0.15, -1.55), (0.3, 0.28, 0.22), bulb)
    for side in (-1, 0, 1):
        k.spike((side * 0.12, 0.15, -1.7), (side * 0.3, 0.15, -1.95), 0.03, bulb)
    k.cord_holes(shell, lacquer)
    return {'kind': 'beast', 'size': 0.86, 'front_az': -16, 'side_az': -70}
