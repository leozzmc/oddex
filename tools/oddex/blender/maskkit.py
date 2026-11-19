"""Shared modelling and toon-rendering kit for oddex mask species. Runs inside Blender.

Species modules (tools/oddex/blender/species/<id>.py) call these helpers from build(kit).
Colours are flat on purpose: every material is a 3-step toon ramp (plus an optional glint)
emitted through the Standard view transform, so a 4x render collapses to a handful of exact
colours that survive the GBA's 15-colour palette.
"""
import math

import bpy
from mathutils import Euler, Vector  # noqa: F401  (Euler for species modules: k.Euler)

SUN_DIR = Vector((-0.85, -0.5, 0.55)).normalized()  # light from the upper left, raking across the face
TOON_STEPS = (0.45, 0.72, 1.0)
TOON_EDGES = (0.3, 0.68)
HORROR_STEPS = (0.3, 0.6, 1.0)  # deeper shadows, harder contrast


# --- scene -----------------------------------------------------------------------------

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    # One sample: no anti-aliasing blends, so the 4x render holds only exact toon colours and
    # the majority downscale in make_art.py stays crisp.
    scene.eevee.taa_render_samples = 1
    scene.render.filter_size = 0.0
    world = bpy.data.worlds.new('void')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
    scene.world = world
    bpy.ops.object.light_add(type='SUN')
    sun = bpy.context.object
    sun.name = 'sun'
    sun.data.energy = math.pi
    sun.rotation_euler = (-SUN_DIR).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.type = 'ORTHO'
    scene.camera = cam
    return scene


def toon(name, rgb, steps=TOON_STEPS, glint=0.0, two_tone=False, weathered=0.0):
    """Flat 3-step toon material (2 steps with two_tone, for small parts that should not spend
    palette slots). glint > 0 adds a lacquer highlight that strength. weathered > 0 darkens
    blotches (chipped gofun, tarnished gold) by pushing the light value down a step, so the
    wear costs no extra palette colours."""
    if two_tone:
        steps = (steps[0], steps[2], steps[2])
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    to_rgb = nodes.new('ShaderNodeShaderToRGB')
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    els = ramp.color_ramp.elements
    els[0].position, els[1].position = 0.0, TOON_EDGES[0]
    els.new(TOON_EDGES[1])
    for el, k in zip(els, steps):
        el.color = (rgb[0] * k, rgb[1] * k, rgb[2] * k, 1.0)
    links.new(diffuse.outputs['BSDF'], to_rgb.inputs['Shader'])
    if weathered:
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 7.0
        noise.inputs['Detail'].default_value = 6.0
        blot = nodes.new('ShaderNodeValToRGB')
        blot.color_ramp.interpolation = 'CONSTANT'
        blot.color_ramp.elements[0].color = (0, 0, 0, 1)
        blot.color_ramp.elements[1].position = 0.6
        blot.color_ramp.elements[1].color = (weathered, weathered, weathered, 1)
        bw = nodes.new('ShaderNodeRGBToBW')
        sub = nodes.new('ShaderNodeMath')
        sub.operation = 'SUBTRACT'
        links.new(noise.outputs['Fac'], blot.inputs['Fac'])
        links.new(to_rgb.outputs['Color'], bw.inputs['Color'])
        links.new(bw.outputs['Val'], sub.inputs[0])
        links.new(blot.outputs['Color'], sub.inputs[1])
        links.new(sub.outputs['Value'], ramp.inputs['Fac'])
    else:
        links.new(to_rgb.outputs['Color'], ramp.inputs['Fac'])
    color = ramp.outputs['Color']
    if glint:
        gloss = nodes.new('ShaderNodeBsdfGlossy')
        gloss.inputs['Roughness'].default_value = 0.12
        g_rgb = nodes.new('ShaderNodeShaderToRGB')
        g_ramp = nodes.new('ShaderNodeValToRGB')
        g_ramp.color_ramp.interpolation = 'CONSTANT'
        g_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        g_ramp.color_ramp.elements[1].position = 0.55
        hi = [min(1.0, c + (1 - c) * 0.75) for c in rgb]
        g_ramp.color_ramp.elements[1].color = (*hi, 1.0)
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'LIGHTEN'
        mix.inputs['Factor'].default_value = glint
        links.new(gloss.outputs['BSDF'], g_rgb.inputs['Shader'])
        links.new(g_rgb.outputs['Color'], g_ramp.inputs['Fac'])
        links.new(color, mix.inputs['A'])
        links.new(g_ramp.outputs['Color'], mix.inputs['B'])
        color = mix.outputs['Result']
    emit = nodes.new('ShaderNodeEmission')
    links.new(color, emit.inputs['Color'])
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return m


def set_light(direction):
    """Move the sun: `direction` points from the model towards the light (like SUN_DIR).
    A low raking light from below gives the kaidan (ghost story) look."""
    sun = bpy.data.objects['sun']
    sun.rotation_euler = (-Vector(direction).normalized()).to_track_quat('-Z', 'Y').to_euler()


def flat(name, rgb):
    """Unshaded colour (painted details such as pupils, lips, lines)."""
    return toon(name, rgb, steps=(1.0, 1.0, 1.0))


# --- primitives ------------------------------------------------------------------------

def _finish(obj, mat, smooth=True, name=None):
    if name:
        obj.name = name
    obj.data.materials.append(mat)
    if smooth:
        bpy.ops.object.shade_smooth()
    return obj


def ellipsoid(loc, scale, mat, rot=(0, 0, 0), segments=32, name=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(8, segments // 2),
                                         location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    return _finish(o, mat, name=name)


def cone(loc, radius, depth, mat, rot=(0, 0, 0), radius2=0.0, segments=16, name=None):
    bpy.ops.mesh.primitive_cone_add(vertices=segments, radius1=radius, radius2=radius2, depth=depth,
                                    location=loc, rotation=rot)
    return _finish(bpy.context.object, mat, name=name)


def cylinder(loc, radius, depth, mat, rot=(0, 0, 0), segments=16, name=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth, location=loc, rotation=rot)
    return _finish(bpy.context.object, mat, name=name)


def torus(loc, major, minor, mat, rot=(0, 0, 0), name=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=24, minor_segments=8)
    return _finish(bpy.context.object, mat, name=name)


def cut(target, cutter):
    mod = target.modifiers.new('cut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    cutter.hide_render = True
    return target


def point_from(obj, a, b):
    """Orient obj's local +Z along the segment a->b and place it at the midpoint."""
    a, b = Vector(a), Vector(b)
    obj.location = (a + b) / 2
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj


def spike(base, tip, radius, mat, name=None):
    """A cone from base to tip (horns, fangs, mane locks, ears)."""
    base, tip = Vector(base), Vector(tip)
    o = cone((0, 0, 0), radius, (tip - base).length, mat, name=name)
    return point_from(o, base, tip)


def rod(a, b, radius, mat, name=None):
    a, b = Vector(a), Vector(b)
    o = cylinder((0, 0, 0), radius, (b - a).length, mat, segments=10, name=name)
    return point_from(o, a, b)


# --- masks -----------------------------------------------------------------------------

def mask_shell(face_mat, inner_mat, width=0.8, depth=0.42, height=1.0, thickness=0.07, cut_y=0.02):
    """Front half of an ellipsoid with real thickness: the outside is face_mat (gofun or
    pigment), the inside and the cut rim are inner_mat (lacquer). The face looks along -Y."""
    face = ellipsoid((0, 0, 0), (width, depth, height), face_mat, segments=64, name='face')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in face.data.vertices:
        v.select = v.co.y > cut_y
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    solid = face.modifiers.new('thick', 'SOLIDIFY')
    solid.thickness = thickness
    solid.offset = 1.0
    solid.material_offset = 1
    solid.material_offset_rim = 1
    face.data.materials.append(inner_mat)
    face['oddex_shell'] = (width, depth, height)
    return face


def on_face(face, x, z, lift=0.0):
    """Point on the outer surface of mask_shell at (x, z), pushed `lift` outward (-Y)."""
    w, d, h = face['oddex_shell']
    t = 1 - (x / w) ** 2 - (z / h) ** 2
    y = -d * math.sqrt(max(0.0, t))
    return Vector((x, y - lift, z))


def front_only(obj):
    """Hide obj in the back view: a mask's inside is plain lacquer, so features sitting on the
    face (which would poke through the shell) must not show there."""
    obj['oddex_front_only'] = True
    return obj


def bump(face, x, z, scale, mat, lift=0.0, name=None):
    """A raised feature (nose, cheek, brow ridge) sitting on the face at (x, z)."""
    return front_only(ellipsoid(on_face(face, x, z, lift), scale, mat, name=name))


def hole(face, x, z, scale, backing=None, name=None):
    """Cut an eye or mouth opening through the shell at (x, z). With a backing material the
    opening is closed from behind (a dark mouth) in the front view; the back view sees through."""
    p = on_face(face, x, z)
    c = ellipsoid((p.x, p.y + 0.05, p.z), (scale[0], 0.4, scale[1]), face.data.materials[0], name=name)
    cut(face, c)
    if backing is not None:
        front_only(ellipsoid((p.x, p.y + 0.08, p.z), (scale[0] * 1.1, 0.03, scale[1] * 1.1), backing))
    return face


def glare_eyes(face, sep, z, size, gold, pupil, socket, tilt=18):
    """Staring kishin-men eyes: a dark socket and under-eye shadow, a large gold eyeball and a
    small black pupil. size is the eyeball radius (about a quarter of the face width each)."""
    for side in (-1, 1):
        x = side * sep
        s = on_face(face, x, z - size * 0.15, lift=0.0)
        front_only(ellipsoid(s, (size * 1.5, 0.06, size * 1.35), socket,
                             rot=(0, math.radians(-side * tilt), 0)))
        e = on_face(face, x, z, lift=size * 0.35)
        front_only(ellipsoid(e, (size, size * 0.8, size * 0.85), gold))
        front_only(ellipsoid((e.x, e.y - size * 0.78, e.z), (size * 0.36, 0.03, size * 0.42), pupil))


def brows(face, sep, z, length, mat, frown=28, thick=0.11):
    """Heavy brow ridges whose inner ends dip toward the nose: the knitted, glaring frown."""
    for side in (-1, 1):
        p = on_face(face, side * sep, z, lift=0.02)
        front_only(ellipsoid(p, (length, thick * 1.2, thick), mat,
                             rot=(0, math.radians(side * frown), 0)))


def fanged_mouth(face, z, width, height, backing, gum, tooth, fang=None, upper=6, lower=6, fang_len=0.22):
    """A gaping mouth: dark throat, dark-red gums along both jaws and two rows of separate teeth
    with dark gaps between them (each tooth is ~60% of its slot), plus optional long fangs at
    the corners. width/height are the opening's half-sizes on the face."""
    hole(face, 0, z, (width, height), backing=backing)
    for row, n, sgn in (('upper', upper, 1), ('lower', lower, -1)):
        edge = z + sgn * height * 0.62
        g = on_face(face, 0, edge, lift=0.0)
        front_only(ellipsoid((g.x, g.y + 0.02, g.z), (width * 0.95, 0.05, height * 0.42), gum))
        slot = (width * 1.5) / n
        for i in range(n):
            x = -width * 0.75 + slot * (i + 0.5)
            t = on_face(face, x, edge - sgn * height * 0.3, lift=0.0)
            front_only(ellipsoid((t.x, t.y - 0.025, t.z), (slot * 0.27, 0.04, height * 0.3), tooth))
    if fang is not None:
        for side in (-1, 1):
            for sgn in (1, -1):
                base = on_face(face, side * width * 0.82, z + sgn * height * 0.5, lift=0.0)
                front_only(spike((base.x, base.y - 0.02, base.z),
                                 (base.x - side * 0.03, base.y - 0.07, base.z - sgn * fang_len), 0.06, fang))


def wrinkles(face, mat, folds):
    """Raised folds (nasolabial lines, flared nostrils, cheek muscles): list of (x, z, sx, sz, deg)."""
    for x, z, sx, sz, deg in folds:
        p = on_face(face, x, z, lift=0.01)
        front_only(ellipsoid(p, (sx, 0.06, sz), mat, rot=(0, math.radians(deg), 0)))


def show_front_only(scene, visible):
    for o in scene.objects:
        if o.get('oddex_front_only'):
            o.hide_render = not visible


def cord_holes(face, inner_mat, z=0.25):
    """The two side holes masks are tied through; visible from the back."""
    w, d, h = face['oddex_shell']
    for side in (-1, 1):
        x = side * w * 0.93
        c = ellipsoid((x, -0.02, z), (0.045, 0.3, 0.045), inner_mat)
        cut(face, c)


def cord(face, mat, z=0.25, drop=0.45):
    """A tying cord trailing from both side holes."""
    w, d, h = face['oddex_shell']
    for side in (-1, 1):
        x = side * w * 0.95
        rod((x, 0.02, z), (x + side * 0.12, 0.2, z - drop), 0.025, mat)


# --- groups ----------------------------------------------------------------------------

def snapshot():
    """Names of the objects that exist now; pass to since() to get what was built after."""
    return {o.name for o in bpy.context.scene.objects}


def since(before):
    return [o for o in bpy.context.scene.objects if o.name not in before and o.type == 'MESH']


def transform(objs, offset=(0, 0, 0), rot_x=0.0, scale=1.0):
    """Rotate (degrees, about X through the origin), scale and move a group of objects together,
    keeping booleans and parented helpers consistent by going through a temporary parent."""
    bpy.ops.object.empty_add(location=(0, 0, 0))
    pivot = bpy.context.object
    for o in objs:
        if o.parent is None:
            o.parent = pivot
    pivot.rotation_euler = (math.radians(rot_x), 0, 0)
    pivot.scale = (scale, scale, scale)
    pivot.location = offset
    return pivot


# --- quadrupeds -------------------------------------------------------------------------

def quadruped(body_mat, leg_mat=None, length=1.2, girth=0.42, leg=0.45, tail=None, tail_mat=None):
    """Body along +Y (rear) from the head end at y=0, standing on z=0. Returns the point
    where a mask should be hung (in front of the head)."""
    leg_mat = leg_mat or body_mat
    top = leg + girth * 0.8
    ellipsoid((0, length * 0.45, top), (girth * 0.9, length * 0.55, girth * 0.8), body_mat, name='body')
    ellipsoid((0, -0.05, top + girth * 0.55), (girth * 0.75, girth * 0.7, girth * 0.7), body_mat, name='head')
    for side in (-1, 1):
        for y in (0.1, length * 0.8):
            rod((side * girth * 0.5, y, top - girth * 0.3), (side * girth * 0.5, y, 0.06), girth * 0.18, leg_mat)
            ellipsoid((side * girth * 0.5, y - 0.03, 0.05), (girth * 0.22, girth * 0.28, 0.07), leg_mat)
    if tail:
        tail(Vector((0, length * 0.98, top + girth * 0.2)), tail_mat or body_mat)
    return Vector((0, -0.05 - girth * 0.75, top + girth * 0.6))


def beast_behind_mask(mask_height, body_mat, **kw):
    """Build a quadruped whose face sits just behind a mask modelled at the origin."""
    before = snapshot()
    anchor = quadruped(body_mat, **kw)
    parts = since(before)
    transform(parts, offset=(-anchor.x, -anchor.y + 0.12, -anchor.z - mask_height * 0.15))
    return parts


# --- heads (unmasked characters whose whole body is one big head) ---------------------------

def head_point(center, radii, x, z, lift=0.0):
    """Point on the front (-Y) of an ellipsoid head at offset x (right) and height z (absolute),
    pushed lift outward. Features are placed relative to the head instead of a mask shell."""
    cx, cy, cz = center
    rx, ry, rz = radii
    u = min(0.999, (x / rx) ** 2 + ((z - cz) / rz) ** 2)
    return Vector((cx + x, cy - ry * math.sqrt(1 - u) - lift, z))


def limb(a, b, radius, mat, hand_mat=None, hand=0.0):
    """A straight limb from a to b, with a round hand (or foot) of radius hand at b."""
    rod(a, b, radius, mat)
    if hand:
        ellipsoid(b, (hand, hand, hand), hand_mat or mat)


def tag(objs, layer):
    """Mark objects for layered renders (render_species with ODDEX_LAYERS): 'head' is the face
    and everything painted on it, which a likeness overlay replaces; 'front' sits in front of
    the head. Untagged parts are drawn behind the head."""
    for o in objs:
        o['oddex_layer'] = layer
    return objs


# --- appendages shared by the starters and the Rustboro batch ------------------------------

def spider_leg(root, direction, length, mat, tip_mat=None, radius=0.045, lift=0.55, ground=0.0):
    """One jointed spider leg: a femur rising from root to a high knee, then a long shin down to
    a pointed tip on the ground. direction is the horizontal heading (x, y) of the leg."""
    root = Vector(root)
    d = Vector((direction[0], direction[1], 0)).normalized()
    knee = root + d * length * 0.45 + Vector((0, 0, length * lift))
    foot = Vector((root.x + d.x * length, root.y + d.y * length, ground + radius))
    rod(root, knee, radius, mat)
    ellipsoid(knee, (radius * 1.5,) * 3, mat)
    rod(knee, foot.lerp(knee, 0.18), radius * 0.85, mat)
    spike(foot.lerp(knee, 0.2), foot, radius * 0.8, tip_mat or mat)
    return knee, foot


def spider_legs(center, pairs, length, mat, tip_mat=None, radius=0.045, spread=(-60, 60), lift=0.55,
                ground=0.0, ring=0.0):
    """pairs legs on each side, fanned between spread degrees (0 = straight out to the side,
    negative = toward the viewer). ring offsets each root from center along its heading."""
    center = Vector(center)
    for side in (-1, 1):
        for i in range(pairs):
            t = 0.5 if pairs == 1 else i / (pairs - 1)
            ang = math.radians(spread[0] + (spread[1] - spread[0]) * t)
            d = (side * math.cos(ang), math.sin(ang))
            root = center + Vector((d[0], d[1], 0)) * ring
            spider_leg(root, d, length, mat, tip_mat, radius, lift, ground)


def membrane(points, mat, name=None):
    """A flat polygon fan (wing or fin membrane) from points[0] through the rest, in order."""
    mesh = bpy.data.meshes.new(name or 'membrane')
    verts = [tuple(p) for p in points]
    faces = [(0, i, i + 1) for i in range(1, len(verts) - 1)]
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name or 'membrane', mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('thick', 'SOLIDIFY')
    mod.thickness = 0.02
    return obj


def wing(root, side, span, mat, rib_mat=None, ribs=4, sweep=(-35, 50), droop=0.25, depth=0.15, scallop=0.3):
    """A ribbed wing or fin on one side (side = -1 left, 1 right): ribs fan out from root between
    sweep degrees (0 = straight out, positive = up); the membrane between rib tips is scalloped
    inward by scallop, so it reads as bat wing or fish fin depending on the colours."""
    root = Vector(root)
    tips = []
    for i in range(ribs):
        t = i / (ribs - 1)
        ang = math.radians(sweep[0] + (sweep[1] - sweep[0]) * t)
        tip = root + Vector((side * span * math.cos(ang), depth * t, span * math.sin(ang) - droop * (1 - t)))
        tips.append(tip)
        rod(root, tip, 0.03, rib_mat or mat)
    outline = [root]
    for a, b in zip(tips, tips[1:]):
        outline.append(a)
        outline.append(root.lerp((a + b) / 2, 1 - scallop))
    outline.append(tips[-1])
    return membrane(outline, mat)


# --- Shinto and esoteric Buddhist motifs (Rustboro batch) ----------------------------------
# Only symbols and imagery: none of these makes a deity catchable (docs/research/mask-designs.md).

def rope(points, thick, mat, dark=None, twists_per_unit=6.0):
    """A twisted straw rope (shimenawa) along a polyline: two strands of beads spiralling round
    each other, the second strand in dark (or mat) so the twist reads at 64px."""
    pts = [Vector(p) for p in points]
    beads = []
    for a, b in zip(pts, pts[1:]):
        seg = b - a
        n = max(2, int(seg.length * twists_per_unit * 3))
        axis = seg.normalized()
        side = axis.cross(Vector((0, 0, 1)))
        if side.length < 1e-3:
            side = axis.cross(Vector((1, 0, 0)))
        side.normalize()
        up = axis.cross(side)
        for i in range(n):
            t = i / n
            ang = t * seg.length * twists_per_unit * 2 * math.pi
            for strand, m in ((0, mat), (math.pi, dark or mat)):
                off = (side * math.cos(ang + strand) + up * math.sin(ang + strand)) * thick * 0.45
                beads.append(ellipsoid(a + seg * t + off, (thick * 0.62,) * 3, m, segments=12))
    return beads


def ring_rope(center, radius, thick, mat, dark=None, rot=(0, 0, 0), segments=24):
    """A closed shimenawa loop in the XZ plane (facing -Y) before rotation rot (degrees)."""
    from mathutils import Euler
    e = Euler(tuple(math.radians(r) for r in rot))
    pts = []
    for i in range(segments + 1):
        a = i * 2 * math.pi / segments
        v = Vector((radius * math.cos(a), 0, radius * math.sin(a)))
        v.rotate(e)
        pts.append(Vector(center) + v)
    return rope(pts, thick, mat, dark)


def shide(top, length, width, mat, side=1, steps=3):
    """A zigzag paper streamer (shide/gohei) hanging from top, facing -Y."""
    top = Vector(top)
    step = length / steps
    pts = []
    for i in range(steps):
        x0 = top.x + (side * width * 0.5 if i % 2 else 0)
        z0 = top.z - i * step
        pts += [(x0, top.y, z0), (x0 + width, top.y, z0), (x0 + width, top.y, z0 - step), (x0, top.y, z0 - step)]
    objs = []
    for i in range(steps):
        quad = [Vector(p) for p in pts[i * 4:i * 4 + 4]]
        objs.append(membrane([quad[0], quad[1], quad[2], quad[3]], mat, name='shide'))
    return objs


def magatama(center, size, mat, curl=1.0, rot_z=0.0):
    """A comma-shaped jewel body: a round head and a tail curling round beneath it, in the XZ
    plane. Returns the head centre (for a face) as a Vector."""
    c = Vector(center)
    head = c + Vector((-size * 0.25, 0, size * 0.25))
    ellipsoid(head, (size * 0.62, size * 0.5, size * 0.62), mat)
    n = 9
    for i in range(1, n + 1):
        t = i / n
        ang = math.radians(150 - 220 * t * curl + rot_z)
        r = size * (0.55 + 0.15 * t)
        p = head + Vector((r * math.cos(ang), 0, r * math.sin(ang) - size * 0.3 * t))
        s = size * 0.5 * (1 - 0.8 * t)
        ellipsoid(p, (s, s * 0.85, s), mat, segments=16)
    return head


def mandala_disc(center, radius, ring_mats, petal_mat, gate_mats, tilt=60, petals=8, spin=0.0):
    """A flat round mandala lying tilted toward the viewer: concentric rings (ring_mats from the
    outside in), petals round the centre, and four square gates at the cardinal points, each in
    its own colour (gate_mats). Returns the disc's centre and its normal."""
    from mathutils import Euler
    c = Vector(center)
    e = Euler((math.radians(tilt), 0, math.radians(spin)))
    normal = Vector((0, 0, 1))
    normal.rotate(e)
    n = len(ring_mats)
    for i, m in enumerate(ring_mats):
        r = radius * (1 - i / (n + 1))
        cylinder(c + normal * (0.02 * i), r, 0.04, m, rot=tuple(e), segments=48)
    for i in range(petals):
        a = 2 * math.pi * i / petals
        v = Vector((radius * 0.32 * math.cos(a), radius * 0.32 * math.sin(a), 0))
        v.rotate(e)
        ellipsoid(c + v + normal * 0.1, (radius * 0.16, radius * 0.08, 0.03), petal_mat,
                  rot=(e.x, e.y, e.z + a))
    for i, m in enumerate(gate_mats[:4]):
        a = math.pi / 2 * i
        v = Vector((radius * 1.02 * math.cos(a), radius * 1.02 * math.sin(a), 0))
        v.rotate(e)
        cylinder(c + v, radius * 0.16, 0.12, m, rot=(e.x, e.y, e.z + a + math.pi / 4), segments=4)
    return c, normal


def vajra(center, length, mat, axis=(1, 0, 0), prongs=4):
    """A vajra: a central knob, a lotus ring each side, and prongs bowing out and closing onto a
    central spike at each end. axis is the direction the vajra lies along."""
    c, ax = Vector(center), Vector(axis).normalized()
    side = ax.cross(Vector((0, -1, 0)))
    if side.length < 1e-3:
        side = ax.cross(Vector((0, 0, 1)))
    side.normalize()
    up = ax.cross(side)
    ellipsoid(c, (length * 0.12,) * 3, mat)
    half = length / 2
    for sgn in (-1, 1):
        ring = c + ax * sgn * length * 0.14
        ellipsoid(ring, (length * 0.1,) * 3, mat, segments=16)
        tip = c + ax * sgn * half
        spike(ring, tip, length * 0.05, mat)
        for i in range(prongs):
            a = 2 * math.pi * i / prongs
            out = (side * math.cos(a) + up * math.sin(a)) * length * 0.16
            mid = c + ax * sgn * length * 0.32 + out
            rod(ring, mid, length * 0.025, mat)
            rod(mid, tip - ax * sgn * length * 0.03, length * 0.022, mat)


def flame_halo(center, radius, mat, inner=None, licks=16, length=0.35, bird=None, depth=0.0):
    """A ring of flame tongues round center in the XZ plane (a flame mandorla), leaning upward.
    bird, if given, is a material for a garuda-head flame at the top (karura-en)."""
    c = Vector(center) + Vector((0, depth, 0))
    for i in range(licks):
        a = 2 * math.pi * i / licks + math.pi / licks
        out = Vector((math.cos(a), 0, math.sin(a)))
        base = c + out * radius
        tip = base + (out + Vector((0, 0, 0.6))).normalized() * length
        spike(base, tip, length * 0.4, mat)
        if inner is not None:
            spike(base + out * 0.03, base.lerp(tip, 0.55), length * 0.2, inner)
    if bird is not None:
        top = c + Vector((0, -0.02, radius + length * 0.6))
        ellipsoid(top, (length * 0.45, length * 0.3, length * 0.4), bird)
        spike(top + Vector((0, -0.05, 0)), top + Vector((length * 0.55, -0.1, -length * 0.15)), length * 0.15, bird)
        for side in (-1, 1):
            spike(top, top + Vector((side * length * 0.9, 0, length * 0.5)), length * 0.22, bird)


# --- rendering --------------------------------------------------------------------------

def frame_all(scene, margin=1.08):
    """Fit the orthographic camera to every renderable object for the current view."""
    cam = scene.camera
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    for o in scene.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        for corner in o.bound_box:
            p = inv @ (o.matrix_world @ Vector(corner))
            xs.append(p.x)
            ys.append(p.y)
    span = max(max(xs) - min(xs), max(ys) - min(ys)) * margin
    cam.data.ortho_scale = span
    cam.data.shift_x = ((max(xs) + min(xs)) / 2) / span
    cam.data.shift_y = ((max(ys) + min(ys)) / 2) / span


def shoot(scene, path, azimuth=0.0, elevation=10.0, res=256, distance=12.0, size=0.9, keep_frame=False):
    """Orthographic render from azimuth degrees around Z (0 = looking at the face from -Y).
    size: fraction of the frame the model's larger side fills (smaller for early stages).
    keep_frame: reuse the previous framing (animation frames must not be re-fitted)."""
    cam = scene.camera
    az, el = math.radians(azimuth), math.radians(elevation)
    cam.location = (distance * math.sin(az) * math.cos(el), -distance * math.cos(az) * math.cos(el),
                    distance * math.sin(el))
    cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x = scene.render.resolution_y = res
    if not keep_frame:
        cam.data.shift_x = cam.data.shift_y = 0
        frame_all(scene, margin=1.0 / size)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
