"""Ridgeloom: Ridgecap's third stage (docs/research/friends-designs.md). After the ookubi (a giant
head that looms in the sky) and the hitouban's long neck: Ridgefin's head, both pairs of finned
ear-wings and its water neck (its build() is reused as is), with the head itself grown larger,
borne on a low bank of storm cloud. The water neck winds into a coil through the cloud, the crest
rises into a crown of fins, and small lightning bolts flicker below (its ability is Lightning
Rod). Head only; water/flying. The head layer is replaced by the likeness in compose.py; the
crown is tagged 'front'. The user asked for the head to read as giant: it is at least as large
in the frame as Ridgefin's, so the cloud stays inside Ridgefin's outline."""
import math
from pathlib import Path

import bpy

_path = Path(__file__).parent / 'ridgefin.py'
_base = {'__file__': str(_path)}
exec(_path.read_text(), _base)
NORMAL = {**_base['NORMAL'], 'cloud': (0.86, 0.88, 0.92), 'cloud2': (0.48, 0.52, 0.62), 'bolt': (1.0, 0.90, 0.30)}
SHINY = {**_base['SHINY'], 'cloud': (0.95, 0.85, 0.70), 'cloud2': (0.62, 0.45, 0.35), 'bolt': (0.60, 1.0, 0.85)}

HEAD_Z = 1.0      # Ridgecap's head centre (local to the pivot its build() scales the head with)
GROW = 1.4        # how much larger the head grows on top of Ridgecap's own scaling


def build(k, c):
    opts = _base['build'](k, c)
    # Grow the head (and the parts riding on it) about its own centre.
    pivots = {o.parent for o in bpy.context.scene.objects if o.get('oddex_layer') == 'head' and o.parent}
    for p in pivots:
        p.scale = p.scale * GROW
        p.location.z = HEAD_Z - HEAD_Z * p.scale.z
    top = HEAD_Z + 0.64 * 1.25 * GROW   # the grown crown of the head
    water = k.toon('water3', c['water'], two_tone=True)
    cloud = k.toon('cloud', c['cloud'], two_tone=True)
    cloud2 = k.toon('cloud2', c['cloud2'], two_tone=True)
    bolt = k.flat('bolt', c['bolt'])
    cap = k.toon('cap3', c['cap'], glint=0.2)
    # The water neck winds into a coil through the cloud.
    for i in range(18):
        t = i / 17
        a = t * 2.4 * math.pi
        p = k.Vector((0.65 * math.sin(a) * (1 - 0.3 * t), -0.45 + 0.3 * math.cos(a), -0.75 - 0.25 * t))
        s = 0.13 * (1 - 0.5 * t) + 0.04
        k.ellipsoid(p, (s, s, s * 1.2), water)
    # A low bank of storm cloud: dark underneath, light on top.
    for x, y, z, r in ((-0.75, 0.3, -0.8, 0.36), (0.0, 0.5, -0.9, 0.42), (0.75, 0.3, -0.78, 0.36),
                       (-1.2, 0.4, -0.62, 0.26), (1.2, 0.4, -0.6, 0.27), (-0.35, 0.1, -0.66, 0.3), (0.42, 0.1, -0.62, 0.31)):
        k.ellipsoid((x, y + 0.05, z - r * 0.25), (r * 1.2, r * 0.8, r * 0.7), cloud2)
        k.ellipsoid((x, y - 0.08, z + r * 0.1), (r * 1.05, r * 0.7, r * 0.65), cloud)
    # Lightning flickering under the cloud.
    for x0, z0, side in ((-0.9, -1.0, 1), (1.0, -0.98, -1)):
        pts = [k.Vector((x0, -0.45, z0)), k.Vector((x0 + side * 0.15, -0.48, z0 - 0.22)),
               k.Vector((x0 - side * 0.04, -0.5, z0 - 0.28)), k.Vector((x0 + side * 0.12, -0.52, z0 - 0.5))]
        for a, b in zip(pts, pts[1:]):
            k.rod(a, b, 0.04, bolt)
    # The crest rises into a crown of fins.
    before = k.snapshot()
    for x, h in ((-0.32, 0.45), (0.32, 0.45), (-0.6, 0.3), (0.6, 0.3)):
        k.spike((x, 0.0, top - 0.15), (x * 1.5, 0.05, top - 0.15 + h), 0.1, cap)
    k.tag(k.since(before), 'front')
    opts['size'] = 0.92
    return opts
