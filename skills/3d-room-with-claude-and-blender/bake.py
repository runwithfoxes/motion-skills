"""Bake the arcade room: Blender works out how every surface looks under the room's own lights
(texture, light, shadow) and saves it as a picture wrapped onto the model, so the paint travels
with the model to the page Paul turns himself (Paul, 25 Oct: "I want you to bake it. Make sure it's
not too dark."). Uses the games-night lighting, lifted, so the room reads.
Run: blender -b -P bake.py -- out_dir      (writes out_dir/tex/*.jpg and out_dir/baked.gltf + .bin)"""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--") + 1:]
BAKE_OUT = os.path.abspath(argv[0])
here = os.path.dirname(os.path.abspath(__file__))
os.environ["REAL_ONLY"] = "1"
sys.argv = [sys.argv[0], "--", "bright", BAKE_OUT]
exec(open(os.path.join(here, "realistic.py")).read())
os.makedirs(os.path.join(BAKE_OUT, "tex"), exist_ok=True)

# ---- lighting for the bake: games night, lifted so nothing sits in the dark ----
for o in bpy.data.objects:
    if o.type == "LIGHT":
        if o.location.z > 2.4:                      # downlights
            o.data.energy = 70; o.data.size = 0.6
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.6, 0.8, 1)


def is_glow(m):
    if not m or not m.use_nodes:
        return False
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED" and n.inputs["Emission Strength"].default_value > 0.01:
            return True
    return False


SKIP = ("bar_chair", "gamepad", "fridge_glass")
groups = {}
for o in list(bpy.data.objects):
    if o.type not in ("MESH", "FONT") or o.name.startswith(SKIP) or not o.data.materials:
        continue
    if o.parent and o.parent.name.startswith(SKIP):
        continue
    m = o.data.materials[0]
    if is_glow(m) or m.name in ("sky",):
        continue
    groups.setdefault(m.name, []).append(o)

SIZE = {"pt_black": 2048, "pt_felt": 2048, "pt_silver": 1024, "pt_plastic": 512, "wall": 4096, "floor": 2048, "pool_felt": 1024, "table_body": 1024, "velvet_teal": 2048,
        "curtain": 1024, "blind": 1024, "unit": 1024, "rack_dark": 1024, "board": 1024, "trim": 1024}

sc.cycles.samples = 96
sc.render.bake.margin = 6
sc.render.bake.use_clear = True
baked = []
for mname, objs in groups.items():
    # make the group one mesh with its bevels applied
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target="MESH")
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "baked_" + mname
    # one clean UV layout for the light
    while ob.data.uv_layers:
        ob.data.uv_layers.remove(ob.data.uv_layers[0])
    ob.data.uv_layers.new(name="bake")
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
    bpy.ops.object.mode_set(mode="OBJECT")
    size = SIZE.get(mname, 512)
    img = bpy.data.images.new("bake_" + mname, size, size)
    # every material on the joined mesh gets the target image as its active node
    for mat in ob.data.materials:
        if mat and mat.use_nodes:
            n = mat.node_tree.nodes.new("ShaderNodeTexImage"); n.image = img
            mat.node_tree.nodes.active = n
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.bake(type="COMBINED")
    path = os.path.join(BAKE_OUT, "tex", mname + ".jpg")
    img.filepath_raw = path; img.file_format = "JPEG"; img.save()
    baked.append((ob, img, path))
    print("baked", mname, len(objs), "objects", size, flush=True)

# ---- swap each baked mesh onto a plain material that just shows its picture ----
for ob, img, path in baked:
    m = bpy.data.materials.new(ob.name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(b.outputs[0], out.inputs[0])
    ob.data.materials.clear(); ob.data.materials.append(m)

for o in list(bpy.data.objects):
    if o.type == "FONT":
        bpy.ops.object.select_all(action="DESELECT"); o.select_set(True)
        bpy.context.view_layer.objects.active = o; bpy.ops.object.convert(target="MESH")
    elif o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.export_scene.gltf(filepath=os.path.join(BAKE_OUT, "baked.gltf"), export_format="GLTF_SEPARATE",
                          export_apply=True, export_yup=True, export_lights=False, export_cameras=False,
                          export_texture_dir="tex", export_image_format="JPEG", export_jpeg_quality=88)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BAKE_OUT, "baked.blend"))
print("done bake", flush=True)
