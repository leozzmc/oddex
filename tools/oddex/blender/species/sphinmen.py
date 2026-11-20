"""Sphinmen: a sphinx, the user's first idea of a beast wearing a mask (Norman segment, the foreign-
myth theme of 2026-11-21; docs/research/mask-designs.md). Stands in for Baltoy in the Route 111
desert and the Mirage Tower. Brief: a lion's body crouched under a huge mask that fuses the
Egyptian nemes headdress with a Noh face: a broad striped nemes (bold blue and gold bands) framing
a chalk-white Noh mask, its two striped lappets falling over the chest; the eyes are hollow with
a gold glint and long black kohl lines sweeping outward (traditional Japanese horror kept); a thin
archaic smile on blackened teeth. A lion's tail with a dark tuft. Imagery only, not a deity.
Silhouette at 64px: the lion's outline, the big mask face, the striped nemes. Masked quadruped;
ground/psychic."""
import math

NORMAL = {'face': (0.96, 0.93, 0.86), 'lacquer': (0.18, 0.10, 0.06), 'hollow': (0.03, 0.02, 0.02),
          'gold': (0.94, 0.72, 0.22), 'blue': (0.10, 0.20, 0.62), 'kohl': (0.05, 0.04, 0.05),
          'lip': (0.62, 0.10, 0.12), 'body': (0.74, 0.50, 0.26), 'tuft': (0.42, 0.26, 0.12)}
SHINY = {**NORMAL, 'gold': (0.82, 0.84, 0.90), 'blue': (0.66, 0.12, 0.14), 'body': (0.70, 0.70, 0.66),
         'tuft': (0.28, 0.28, 0.32)}


def build(k, c):
    face_m = k.toon('face', c['face'], steps=(0.62, 0.85, 1.0))
    lacquer = k.toon('lacquer', c['lacquer'], two_tone=True)
    hollow = k.flat('hollow', c['hollow'])
    gold = k.toon('gold', c['gold'], glint=0.4, two_tone=True)
    blue = k.toon('blue', c['blue'], two_tone=True)
    kohl = k.flat('kohl', c['kohl'])
    lip = k.flat('lip', c['lip'])
    body = k.toon('body', c['body'], two_tone=True)
    tuft = k.toon('tuft', c['tuft'], two_tone=True)
    k.set_light((-0.75, -0.6, -0.1))
    # The nemes: one solid gold hood behind the face, with blue stripes wrapped round it.
    hc, hr = k.Vector((0, 0.22, 0.38)), (0.74, 0.42, 0.68)
    k.ellipsoid(hc, hr, gold)
    for i in range(5):
        z = hc.z + 0.52 - i * 0.26
        f = max(0.0, 1 - ((z - hc.z) / hr[2]) ** 2) ** 0.5
        k.ellipsoid((hc.x, hc.y, z), (hr[0] * f * 1.03, hr[1] * f * 1.03, 0.11), blue)
    # The two lappets: solid flat flaps falling in front of the shoulders, striped the same way.
    for side in (-1, 1):
        lc = k.Vector((side * 0.55, -0.1, -0.42))
        k.ellipsoid(lc, (0.17, 0.07, 0.52), gold)
        for j in range(3):
            z = lc.z + 0.3 - j * 0.3
            f = max(0.0, 1 - ((z - lc.z) / 0.52) ** 2) ** 0.5
            k.ellipsoid((lc.x, lc.y, z), (0.17 * f * 1.06, 0.07 * f * 1.1, 0.08), blue)
    # The chalk-white Noh face, a gold band across the brow.
    shell = k.mask_shell(face_m, lacquer, width=0.52, depth=0.38, height=0.7)
    for i in range(7):
        x = -0.36 + i * 0.12
        k.front_only(k.ellipsoid(k.on_face(shell, x, 0.6, lift=0.01), (0.08, 0.03, 0.05), gold))
    for x in (-0.19, 0.19):
        side = -1 if x < 0 else 1
        k.hole(shell, x, 0.18, (0.12, 0.06), backing=hollow)
        p = k.on_face(shell, x, 0.18)
        k.front_only(k.ellipsoid((p.x, p.y + 0.04, p.z), (0.04, 0.015, 0.035), gold))
        # Kohl lines: the upper lid, then a long wing sweeping out past the face.
        k.front_only(k.ellipsoid(k.on_face(shell, x, 0.25, lift=0.01), (0.15, 0.02, 0.04), kohl))
        a = k.on_face(shell, x + side * 0.1, 0.22, lift=0.01)
        k.front_only(k.rod(a, a + k.Vector((side * 0.22, 0.05, -0.05)), 0.035, kohl))
    k.bump(shell, 0, -0.04, (0.07, 0.07, 0.14), face_m, lift=0.01)
    # A thin archaic smile over blackened teeth.
    k.hole(shell, 0, -0.38, (0.17, 0.045), backing=kohl)
    for dx in (-0.14, 0.14):
        p = k.on_face(shell, dx, -0.36, lift=0.005)
        k.front_only(k.ellipsoid(p, (0.05, 0.02, 0.02), lip))
    k.cord_holes(shell, lacquer)

    def tail(at, mat):
        pts = [at, at + k.Vector((0.15, 0.35, 0.25)), at + k.Vector((0.25, 0.5, 0.65)), at + k.Vector((0.15, 0.45, 0.95))]
        for a, b in zip(pts, pts[1:]):
            k.rod(a, b, 0.06, mat)
        k.ellipsoid(pts[-1] + k.Vector((0, 0, 0.08)), (0.13, 0.13, 0.17), tuft)

    k.beast_behind_mask(0.7, body, length=1.7, girth=0.58, leg=0.26, tail=tail)   # crouched: short legs
    return {'kind': 'beast', 'size': 0.9, 'front_az': -28, 'side_az': -75}
