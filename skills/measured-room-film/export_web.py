"""Export the realistic arcade room as one GLB for the page Paul can turn with his finger or mouse.
Run: blender -b -P export_web.py -- out_dir
The Poly Haven textures are box-projected in world space, which a GLB cannot carry, so each
textured material goes out as its flat colour. The page adds its own lights; the LED strip, neon,
fridge and TV glow travel as glowing materials."""
import bpy, sys, os

argv = sys.argv[sys.argv.index("--") + 1:]
WEB_OUT = argv[0]
here = os.path.dirname(os.path.abspath(__file__))
os.environ["REAL_ONLY"] = "1"
sys.argv = [sys.argv[0], "--", "dim", WEB_OUT]
exec(open(os.path.join(here, "realistic.py")).read())

FLAT = {
    "wall": (0.05, 0.06, 0.13), "floor": (0.36, 0.22, 0.12), "unit": (0.045, 0.04, 0.035),
    "rack_dark": (0.06, 0.045, 0.035), "frame_dark": (0.06, 0.045, 0.035),
    "pool_felt": (0.02, 0.22, 0.65), "velvet_teal": (0.03, 0.22, 0.24), "velvet_orange": (0.8, 0.22, 0.05),
}
for name, rgb in FLAT.items():
    m = bpy.data.materials.get(name)
    if not m:
        continue
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = 0.8
    nt.links.new(b.outputs[0], out.inputs[0])

# text becomes mesh so the names and the neon travel; cameras and lights stay behind
for o in list(bpy.data.objects):
    if o.type == "FONT":
        bpy.ops.object.select_all(action="DESELECT"); o.select_set(True)
        bpy.context.view_layer.objects.active = o; bpy.ops.object.convert(target="MESH")
    elif o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)

path = os.path.join(WEB_OUT, "games-room.glb")
bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_apply=True, export_yup=True,
                          export_lights=False, export_cameras=False)
print("exported", path, round(os.path.getsize(path) / 1e6, 2), "MB")
