"""Blender entry point: build one species model and render its views.

$BLENDER -b --factory-startup -P tools/oddex/blender/render_species.py -- <module> <out_dir> [shiny]

<module> is a file in tools/oddex/blender/species/ defining build(kit, palette) -> dict, where
palette is the species' NORMAL or SHINY colour table and the dict may set:
  kind     "mask" (back view looks into the lacquered inside) or "beast" (rear of the body)
  front_az azimuth of the front view (default -22; negative turns the face to the viewer's left)
  front_el elevation of the front view in degrees (default 8)
  side_az  azimuth of the overworld side view (default -60)
  squash   (sx, sy, sz) scale for the second front animation frame
Writes front.png, front2.png, back.png, ow_front.png, ow_back.png, ow_side.png into out_dir.
"""
import importlib.util
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import maskkit  # noqa: E402

args = sys.argv[sys.argv.index('--') + 1:]
module_name, out = args[0], Path(args[1])
variant = args[2] if len(args) > 2 else 'normal'
out.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location(module_name, HERE / 'species' / f'{module_name}.py')
species = importlib.util.module_from_spec(spec)
spec.loader.exec_module(species)

scene = maskkit.reset()
palette = species.SHINY if variant == 'shiny' else species.NORMAL
opts = species.build(maskkit, palette) or {}

# Parent everything to one root so the animation frame can squash the whole model.
bpy.ops.object.empty_add(location=(0, 0, 0))
root = bpy.context.object
for o in scene.objects:
    if o.type not in ('CAMERA', 'LIGHT') and o is not root and o.parent is None:
        o.parent = root

front_az = opts.get('front_az', -22)
size = opts.get('size', 0.85)
back_az = 180 + 40 if opts.get('kind', 'mask') == 'mask' else 180 - 20
front_el = opts.get('front_el', 8)
maskkit.shoot(scene, str(out / 'front.png'), azimuth=front_az, elevation=front_el, size=size)
root.scale = opts.get('squash', (1.04, 1.04, 0.95))
maskkit.shoot(scene, str(out / 'front2.png'), azimuth=front_az, elevation=front_el, keep_frame=True)
root.scale = (1, 1, 1)
is_mask = opts.get('kind', 'mask') == 'mask'
maskkit.show_front_only(scene, not is_mask)
maskkit.shoot(scene, str(out / 'back.png'), azimuth=back_az, elevation=14, size=size)
maskkit.shoot(scene, str(out / 'ow_back.png'), azimuth=180, elevation=25, res=128, size=0.9)
maskkit.show_front_only(scene, True)
for name, az in (('ow_front', 0), ('ow_side', opts.get('side_az', -60))):
    maskkit.shoot(scene, str(out / f'{name}.png'), azimuth=az, elevation=25, res=128, size=0.9)
