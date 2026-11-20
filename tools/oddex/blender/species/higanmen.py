"""Higanmen: a red spider lily (higanbana) whose heart is a serene zo-onna mask (Lavaridge
segment, docs/research/mask-designs.md). It grows by graves and paddy ridges, blooms only around
the equinox with no leaves at all, and its bulb is poisonous. A ring of long, curled red
petals and threadlike stamens radiates round the pale face like a crown; a bare green stem,
with a smaller lily on each side for hands; the bulb below. Fusion: Omotelle's still, chalk-white
face with painted high brows (as zo-onna, slightly older); Shishiblaze's mane spikes turned
into petals. After the user's 64px review the face is 2.2x larger and the petals ring it like a
halo. Masked flower; grass/poison."""
import math

NORMAL = {'face': (0.97, 0.95, 0.92), 'lacquer': (0.16, 0.06, 0.05), 'hollow': (0.03, 0.02, 0.03),
          'ink': (0.08, 0.06, 0.08), 'lip': (0.72, 0.10, 0.14), 'gold': (0.92, 0.75, 0.25),
          'petal': (0.86, 0.10, 0.12), 'petaldark': (0.52, 0.04, 0.08), 'stem': (0.30, 0.55, 0.22),
          'bulb': (0.86, 0.80, 0.66)}
# Shiny: violet lilies (all-white petals lost the outline against the white face).
SHINY = {**NORMAL, 'petal': (0.70, 0.42, 0.92), 'petaldark': (0.34, 0.16, 0.55), 'lip': (0.55, 0.20, 0.60)}


def lily(k, at, r, petal, n=6):
    """A small spider lily head: n long petals curling back (no stamens: they break into noise at 64px)."""
    at = k.Vector(at)
    for i in range(n):
        a = 2 * math.pi * i / n + 0.3
        out = k.Vector((math.cos(a), -0.15, math.sin(a)))
        mid = at + out * r * 0.6
        tip = at + out * r + k.Vector((0, 0.25 * r, 0))
        k.spike(at, mid, r * 0.16, petal)
        k.spike(mid, tip, r * 0.1, petal)


def build(k, c):
    face_m = k.toon('face', c['face'], steps=(0.62, 0.85, 1.0))
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
    F = 2.2   # the face, 2.2x its first size (the user's 64px review): the petals are now its halo
    # The halo: thick red petals curling back, with stamens, all round the face's rim.
    for i in range(14):
        a = 2 * math.pi * i / 14 + 0.15
        out = k.Vector((math.cos(a) * 1.0, 0, math.sin(a) * 1.25))
        d = out.normalized()
        up = k.Vector((0, 0, 1))
        base = out * 1.02 + k.Vector((0, 0.25, 0.0))
        p1 = base + d * 0.38
        p2 = p1 + d * 0.22 + up * 0.1 + k.Vector((0, 0.18, 0))
        p3 = p2 - d * 0.08 + up * 0.08 + k.Vector((0, 0.15, 0))
        k.rod(base, p1, 0.17, petal)
        k.rod(p1, p2, 0.13, petal)
        k.spike(p2, p3, 0.1, petaldark)
        if i % 2 == 0:   # every other petal has a stamen tip showing past it
            s1 = base + d * 0.66 + k.Vector((0, -0.1, 0.04))
            k.rod(base, s1, 0.04, petal)
            k.ellipsoid(s1, (0.07, 0.07, 0.07), petaldark)
    # The serene zo-onna mask: hollow eyes under heavy lids with a gold glint, high painted
    # brows, a faint closed smile.
    shell = k.mask_shell(face_m, lacquer, width=0.5 * F, depth=0.36 * F, height=0.62 * F)
    for x in (-0.18, 0.18):
        k.hole(shell, x * F, 0.1 * F, (0.08 * F, 0.03 * F), backing=hollow)
        p = k.on_face(shell, x * F, 0.1 * F)
        k.front_only(k.ellipsoid((p.x, p.y + 0.04 * F, p.z), (0.03 * F, 0.015 * F, 0.022 * F), gold))
        k.front_only(k.ellipsoid(k.on_face(shell, x * F, 0.36 * F, lift=0.005 * F), (0.07 * F, 0.02 * F, 0.04 * F), ink))
        k.front_only(k.ellipsoid(k.on_face(shell, x * F, 0.11 * F, lift=0.005 * F), (0.11 * F, 0.02 * F, 0.025 * F), ink))
    k.bump(shell, 0, -0.05 * F, (0.06 * F, 0.06 * F, 0.12 * F), face_m, lift=0.01 * F)
    for z, sx in ((-0.3, 0.12), (-0.35, 0.1)):
        p = k.on_face(shell, 0, z * F)
        k.front_only(k.ellipsoid((p.x, p.y - 0.01 * F, p.z), (sx * F, 0.03 * F, 0.022 * F), lip))
    # A short bare stem, a small lily on each side for hands, and the bulb below.
    k.rod((0, 0.2, -1.2), (0, 0.2, -1.95), 0.09, stem)
    for side in (-1, 1):
        k.rod((0, 0.2, -1.6), (side * 0.95, 0.05, -1.45), 0.05, stem)
        lily(k, (side * 1.05, 0.0, -1.42), 0.36, petal)
    k.ellipsoid((0, 0.2, -2.05), (0.32, 0.3, 0.22), bulb)
    for side in (-1, 0, 1):
        k.spike((side * 0.12, 0.2, -2.2), (side * 0.3, 0.2, -2.42), 0.035, bulb)
    k.cord_holes(shell, lacquer)
    return {'kind': 'beast', 'size': 0.9, 'front_az': -12, 'side_az': -70}
