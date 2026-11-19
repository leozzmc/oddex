# Prototype: model a Ko-omote-style Noh mask and render GBA-ready front/back views.
# Usage: $BLENDER -b --factory-startup -P tools/oddex/blender/proto_mask.py -- OUT_DIR
import math
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
RES = 256


def material(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    return m


def ellipsoid(name, loc, scale, mat, segments=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=segments // 2, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def boolean_cut(target, cutter):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    cutter.hide_render = True


bpy.ops.wm.read_factory_settings(use_empty=True)
ivory = material("gofun", (0.93, 0.88, 0.78))
lacquer = material("lacquer", (0.18, 0.07, 0.05))
ink = material("ink", (0.05, 0.05, 0.06))
lip = material("lip", (0.70, 0.08, 0.10))

# Face shell: front half of an ellipsoid, given thickness so the rim reads as an object.
face = ellipsoid("face", (0, 0, 0), (0.78, 0.42, 1.0), ivory, 64)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="DESELECT")
bpy.ops.object.mode_set(mode="OBJECT")
for v in face.data.vertices:
    v.select = v.co.y > 0.02
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.delete(type="VERT")
bpy.ops.object.mode_set(mode="OBJECT")
solid = face.modifiers.new("thick", "SOLIDIFY")
solid.thickness = 0.06
solid.material_offset = 1
face.data.materials.append(lacquer)

# Nose, cheeks and brow ridge as soft bumps.
ellipsoid("nose", (0, -0.40, -0.05), (0.09, 0.08, 0.22), ivory)
ellipsoid("cheekL", (-0.32, -0.30, -0.25), (0.18, 0.1, 0.16), ivory)
ellipsoid("cheekR", (0.32, -0.30, -0.25), (0.18, 0.1, 0.16), ivory)

# Narrow eye slits and mouth opening cut through the shell.
for x in (-0.27, 0.27):
    c = ellipsoid(f"eyecut{x}", (x, -0.4, 0.15), (0.13, 0.4, 0.035), ink, 16)
    boolean_cut(face, c)
mouth = ellipsoid("mouthcut", (0, -0.4, -0.48), (0.12, 0.4, 0.03), ink, 16)
boolean_cut(face, mouth)

# Painted details: high court eyebrows and red lips.
for x in (-0.27, 0.27):
    ellipsoid(f"brow{x}", (x, -0.36, 0.55), (0.1, 0.03, 0.06), ink)
ellipsoid("lipU", (0, -0.385, -0.44), (0.15, 0.03, 0.03), lip)
ellipsoid("lipL", (0, -0.385, -0.52), (0.13, 0.03, 0.035), lip)

# Hair parting painted at the top edge.
ellipsoid("hair", (0, -0.12, 0.92), (0.6, 0.3, 0.12), ink)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
shading = scene.display.shading
shading.light = "STUDIO"
shading.color_type = "MATERIAL"
shading.show_cavity = True
shading.cavity_type = "BOTH"
shading.show_object_outline = True
shading.object_outline_color = (0.05, 0.03, 0.03)
shading.show_specular_highlight = True
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = RES
scene.render.filter_size = 0.5

bpy.ops.object.camera_add()
cam = bpy.context.object
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.6
scene.camera = cam


def shoot(name, azimuth_deg, elevation_deg):
    r = 10
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    cam.location = (r * math.sin(az) * math.cos(el), -r * math.cos(az) * math.cos(el), r * math.sin(el))
    direction = Vector((0, 0, 0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = f"{OUT}/{name}.png"
    bpy.ops.render.render(write_still=True)


shoot("front", -25, 8)
shoot("back", 160, 15)
