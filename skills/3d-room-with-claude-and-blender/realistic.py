"""The arcade games room made to look like a photograph, painted in Blender only (Paul, 25 Oct:
"keep with the blender because otherwise nothing will be real"). Every size stays as measured.
Real materials from Poly Haven (run fetch_assets.py first), a proper L sofa, real bar stools.
Run: blender -b -P realistic.py -- dim out_dir      or      -- bright out_dir"""
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
LEVEL_ARG, OUT_ARG = argv[0], argv[1]
here = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(here, "assets")
os.environ["THEME_ONLY"] = "1"
sys.argv = [sys.argv[0], "--", "arcade", OUT_ARG, LEVEL_ARG]
exec(open(os.path.join(here, "theme.py")).read())  # room + layout E + arcade look, no renders
OUT, LEVEL = OUT_ARG, LEVEL_ARG


def tex_mat(matname, folder, tile_m, tint=(1, 1, 1), rough_add=0.0, nor=0.4, sheen=0.0, base=None):
    """Rebuild a material with Poly Haven maps, box-projected in world space so scaled boxes
    never stretch the grain. tile_m = how many metres one copy of the texture covers."""
    m = bpy.data.materials.get(matname) or bpy.data.materials.new(matname)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / tile_m,) * 3
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    def img(name, colour):
        p = os.path.join(ASSETS, folder, name + ".jpg")
        if not os.path.exists(p):
            return None
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(p, check_existing=True)
        n.projection = "BOX"; n.projection_blend = 0.25
        if not colour:
            n.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs[0], n.inputs["Vector"]); return n
    d = img("diff", True)
    if d and base is None:
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0; mix.inputs[7].default_value = (*tint, 1)
        nt.links.new(d.outputs["Color"], mix.inputs[6]); nt.links.new(mix.outputs[2], bs.inputs["Base Color"])
    else:
        bs.inputs["Base Color"].default_value = (*(base or tint), 1)
    r = img("rough", False)
    if r:
        add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"; add.inputs[1].default_value = rough_add
        nt.links.new(r.outputs["Color"], add.inputs[0]); nt.links.new(add.outputs[0], bs.inputs["Roughness"])
    n = img("nor", False)
    if n:
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nor
        nt.links.new(n.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], bs.inputs["Normal"])
    if sheen:
        for key in ("Sheen Weight", "Sheen"):
            if key in bs.inputs:
                bs.inputs[key].default_value = sheen; break
    return m


# ---- real materials ----
tex_mat("wall", "plastered_wall_02", 2.0, tint=(0.05, 0.07, 0.16), rough_add=0.15, nor=0.25)   # navy matt paint
tex_mat("floor", "laminate_floor_02", 1.6, tint=(0.95, 0.85, 0.75), nor=0.3)                   # oak boards
tex_mat("unit", "black_oak_veneer", 1.0, nor=0.3)
for name in ("rack_dark", "frame_dark"):
    if name in bpy.data.materials:
        tex_mat(name, "black_oak_veneer", 1.0, nor=0.3)
tex_mat("pool_felt", "fabric_pattern_07", 0.08, base=(0.02, 0.18, 0.55), nor=0.15, sheen=0.4)  # blue cloth
VELVET = tex_mat("velvet_teal", "velour_velvet", 0.5, base=(0.02, 0.16, 0.17), nor=0.3, sheen=0.8)  # the texture is red underneath, so colour comes from base only
ORANGE = tex_mat("velvet_orange", "velour_velvet", 0.5, base=(0.75, 0.18, 0.03), nor=0.3, sheen=0.8)

# ---- a proper L sofa in the same footprint: plinth, seat cushions, back cushions, one arm ----
for o in list(bpy.data.objects):
    if o.name.startswith(("Lsofa_", "cushion")):
        bpy.data.objects.remove(o, do_unlink=True)


def soft(name, x0, y0, z0, x1, y1, z1, m, r=4):
    o = box(name, x0, y0, z0, x1, y1, z1, m)
    b = o.modifiers.new("soft", "BEVEL"); b.width = r * S; b.segments = 6; b.limit_method = "NONE"
    bpy.context.view_layer.objects.active = o; bpy.ops.object.shade_smooth()
    return o


LEG = mat("sofa_leg", (0.03, 0.03, 0.03), 0.4)
LONG_X1, DEPTH, SHORT_Y1 = 200, 88, 108   # short side stops 2 cm short of the chimney breast (Cato, dray-32)
box("sofa_plinth_long", 2, 2, 0, LONG_X1 - 2, DEPTH - 4, 10, LEG)
box("sofa_plinth_short", 2, DEPTH - 4, 0, DEPTH - 4, SHORT_Y1 - 2, 10, LEG)
soft("sofa_base_long", 0, 0, 10, LONG_X1, DEPTH, 26, VELVET, 3)
soft("sofa_base_short", 0, DEPTH - 2, 10, DEPTH, SHORT_Y1, 26, VELVET, 3)
soft("sofa_back_rail", 0, 0, 26, LONG_X1, 18, 72, VELVET, 5)
soft("sofa_back_rail2", 0, 0, 26, 18, SHORT_Y1, 72, VELVET, 5)
soft("sofa_arm", LONG_X1 - 18, 0, 26, LONG_X1, DEPTH, 60, VELVET, 6)
for x0, x1 in ((18, 70), (72, 124), (126, LONG_X1 - 18)):          # seat cushions, long side
    soft("seat", x0, 18, 26, x1, DEPTH, 44, VELVET, 6)
soft("seat", 18, DEPTH, 26, DEPTH, SHORT_Y1, 44, VELVET, 6)          # corner piece to the hearth
for x0, x1 in ((20, 70), (72, 124), (126, LONG_X1 - 20)):          # back cushions
    soft("back_cushion", x0, 16, 44, x1, 32, 82, VELVET, 7)
soft("back_cushion", 16, 34, 44, 32, SHORT_Y1 - 2, 82, VELVET, 7)
for x0, rot in ((40, 8), (140, -6)):                                 # two orange scatter cushions
    c = soft("scatter", x0, 30, 44, x0 + 42, 42, 84, ORANGE, 9)
    c.rotation_euler.y = math.radians(rot)

# the sofa stands in front of the left shelf unit, never through it (Cato, dray-32; Paul: the shelves
# can be covered). The shelf front is at x 35, so the whole sofa moves 35 cm out from the wall.
SOFA_SHIFT = 35
for o in bpy.data.objects:
    if o.name.startswith(("sofa_", "seat", "back_cushion", "scatter")):
        o.location.x += SOFA_SHIFT * S

# ---- real bar stools from Poly Haven in place of the drawn ones ----
for o in list(bpy.data.objects):
    if o.name.startswith("stool_"):
        bpy.data.objects.remove(o, do_unlink=True)


def import_gltf(folder, fname):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, folder, fname))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(folder + "_root", None); bpy.context.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    return root, new


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), \
           Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))


for sy in (95, 250):
    root, objs = import_gltf("bar_chair_round_01", "bar_chair_round_01_1k.gltf")
    bpy.context.view_layer.update(); lo, hi = bbox(objs)
    root.location = (Vector(((L - 32) * S, sy * S, 0)) - Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)))
    root.rotation_euler.z = math.radians(90)
    print("bar stool height cm", round((hi.z - lo.z) * 100, 1))

# a PS5 controller left on the sofa
root, objs = import_gltf("gamepad", "gamepad_1k.gltf")
root.location = (1.35, 0.55, 0.445); root.rotation_euler.z = math.radians(25)

# ---- the real Hit Sport table in place of the box version (Paul, 25 Oct) ----
for o in list(bpy.data.objects):
    if o.name.startswith(("table_", "trim_low", "corner_cap", "pocket", "end_frame", "end_foot", "end_edge", "ball_tray", "cross_bar")):
        bpy.data.objects.remove(o, do_unlink=True)
exec(open(os.path.join(here, "pooltable.py")).read())
build(D["L"] - 111 - 221, (D["W"] - 112) / 2, tex_mat, mat)

# ---- the pool light was bleaching the blue cloth: turn it down, keep the colour ----
for o in bpy.data.objects:
    if o.type == "LIGHT" and o.data.type == "AREA" and abs(o.data.size - 1.1) < 0.01:
        o.data.energy = 110 if LEVEL == "dim" else 150
bpy.data.materials["pool_lamp"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass

# ---- render ----
sc.cycles.samples = 256
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
CAMS = {
    "hero": ((90, 70, 150), (560, 172, 125), 18),
    "tv-wall": ((470, 110, 160), (90, 345, 95), 18),
    "sofa-corner": ((430, 300, 165), (60, 50, 55), 18),
    "overview": ((545, 15, 238), (150, 250, 20), 15),
}
if os.environ.get("REAL_ONLY") == "1":
    CAMS = {}
for name, (pos, look, lens) in CAMS.items():
    bpy.ops.object.camera_add(location=Vector(pos) * S)
    cam = bpy.context.object; cam.data.lens = lens
    cam.rotation_euler = ((Vector(look) - Vector(pos)) * S).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = os.path.join(OUT, f"real-{LEVEL}-{name}.png")
    bpy.ops.render.render(write_still=True)
if CAMS:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"real-{LEVEL}.blend"))
    print("done real", LEVEL)
