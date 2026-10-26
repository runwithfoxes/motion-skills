"""Games room film v2: the measured room animated and shot in Blender (see BRIEF.md).
Run: blender -b -P film.py -- clay|arcade|labels START END out_dir
  clay   = the build in white clay on navy (walls rise, furniture drops), frames 0-329
  arcade = the lit room, same animation finished, for the wipe, hero, macro and end shots
  labels = no render; writes labels.json with where each size label sits on screen, every frame"""
import bpy, sys, os, math, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
PASS, F0, F1, FOUT = argv[0], int(argv[1]), int(argv[2]), os.path.abspath(argv[3])
BUILD = os.path.dirname(os.path.abspath(__file__))
os.environ["REAL_ONLY"] = "1"
sys.argv = [sys.argv[0], "--", "bright", FOUT]
here = BUILD
__file__ = os.path.join(BUILD, "realistic.py")   # the build scripts find each other by __file__
exec(open(__file__).read())
os.makedirs(FOUT, exist_ok=True)
CM = 0.01

leaf = bpy.data.objects.get("door_leaf")
if leaf:
    dx0 = D["door_x"]; leaf.rotation_euler.z = 0
    leaf.location = ((dx0 + D["door_w"] / 2) * S, (D["W"] - 2) * S, leaf.location.z)
TX0, TY0 = D["L"] - 111 - 221, (D["W"] - 112) / 2
R = 2.54; apex = TX0 + 12 + 197 * 0.72; cy = TY0 + 56
bcols = [(0.9, 0.75, 0.05), (0.05, 0.2, 0.7), (0.75, 0.05, 0.05), (0.35, 0.05, 0.45), (0.95, 0.4, 0.05), (0.05, 0.45, 0.15), (0.45, 0.1, 0.05), (0.02, 0.02, 0.02)]
k = 0
for row in range(5):
    for j in range(row + 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=R * S, location=((apex + row * R * 1.74) * S, (cy + (j - row / 2) * R * 2.02) * S, (76 + R) * S), segments=32, ring_count=16)
        b = bpy.context.object; b.name = "pt_rackball"; bpy.ops.object.shade_smooth(); b.data.materials.append(mat(f"rb{k}", bcols[k % 8], 0.06)); k += 1
bpy.ops.mesh.primitive_uv_sphere_add(radius=R * S, location=((TX0 + 70) * S, (cy + 9) * S, (76 + R) * S), segments=32, ring_count=16)
bpy.context.object.name = "pt_cueball"; bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(mat("cueball", (0.92, 0.9, 0.85), 0.06))
pm = bpy.data.materials.get("pt_plastic")
if pm:
    pm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.006, 0.006, 0.007, 1)
    pm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35

# ---------- groups: what rises, what drops, and when ----------
def start(*p):
    return lambda o: o.name.startswith(p)
GROUPS = [  # name, test, land frame
    ("table", start("pt_"), 132),
    ("sofa", lambda o: o.name.startswith(("sofa_", "seat", "back_cushion", "scatter", "gamepad")), 156),
    ("tv", start("tv_", "ps5", "fridge", "bottle"), 178),
    ("wallset", lambda o: o.type == "FONT" or o.name.startswith(("ledge", "board", "tally", "rack_", "cue", "short_cue", "pool_light", "cord", "can")), 200),
    ("stools", lambda o: "bar_chair" in o.name, 218),
]
ROOM = start("wall_", "ww_", "dw_", "skirting", "breast", "fire_", "mantel", "hearth", "shelf_", "door", "frame", "rad_",
             "slat", "curt", "rod", "sky", "hall", "cove", "panel", "handle", "vent", "downlight", "rug")

def roots():
    return [o for o in bpy.data.objects if o.parent is None and o.type in ("MESH", "FONT", "EMPTY")]

def make_empty(name):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); return e

def parent_to(o, e):
    mw = o.matrix_world.copy(); o.parent = e; o.matrix_parent_inverse = e.matrix_world.inverted(); o.matrix_world = mw

assigned = set()
for name, test, land in GROUPS:
    e = make_empty("grp_" + name)
    for o in roots():
        if o.name in assigned or o.name.startswith("grp_"):
            continue
        if test(o):
            parent_to(o, e); assigned.add(o.name)
    # drop from 2.4 m above on a spring (zeta 0.6, 2.2 Hz), starting 16 frames before it lands
    def spring(t, zeta=0.6, f=2.2):
        w = 2 * math.pi * f; wd = w * math.sqrt(1 - zeta * zeta)
        return 1 - math.exp(-zeta * w * t) * (math.cos(wd * t) + (zeta * w / wd) * math.sin(wd * t))
    s = land - 16
    e.location.z = 2.4; e.keyframe_insert("location", index=2, frame=0); e.keyframe_insert("location", index=2, frame=s)
    for k in range(0, 46):
        e.location.z = 2.4 * (1 - spring(k / 30)); e.keyframe_insert("location", index=2, frame=s + k)
    e["land"] = land
    for o in [c for c in e.children_recursive]:
        o.hide_render = True; o.keyframe_insert("hide_render", frame=0)
        o.hide_render = False; o.keyframe_insert("hide_render", frame=s)

walls = make_empty("grp_room")
for o in roots():
    if o.name not in assigned and not o.name.startswith("grp_") and ROOM(o):
        parent_to(o, walls); assigned.add(o.name)
walls.location.z = -2.6; walls.keyframe_insert("location", index=2, frame=12)
for k in range(0, 41):   # quint ease-out over 40 frames
    t = k / 40; walls.location.z = -2.6 * (1 - (1 - (1 - t) ** 5)); walls.keyframe_insert("location", index=2, frame=14 + k)

# the end shot is a cutaway: the two near walls and what hangs on them come away
CUT = ("ww_", "slat", "curt", "rod", "sky", "rad_tall", "rack_", "cue", "short_cue")
for o in bpy.data.objects:
    near_strip = o.name.startswith(("cove", "skirting")) and o.location.y < 0.1
    if o.name.startswith(CUT) or near_strip:
        o.hide_render = False; o.keyframe_insert("hide_render", frame=0)
        o.hide_render = True; o.keyframe_insert("hide_render", frame=810)
# the ceiling is off for every shot from above and for the build
ceil = bpy.data.objects["ceiling"]
for f, v in ((0, True), (329, True), (330, False), (809, False), (810, True)):
    ceil.hide_render = v; ceil.keyframe_insert("hide_render", frame=f)

# ---------- camera ----------
cam_data = bpy.data.cameras.new("film"); cam = bpy.data.objects.new("film", cam_data); bpy.context.collection.objects.link(cam)
tgt = make_empty("cam_target")
con = cam.constraints.new("TRACK_TO"); con.target = tgt; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
sc.camera = cam
for f, ex in ((809, 0.0), (810, 0.55)):   # the end shot gets more light: the room is seen from outside
    sc.view_settings.exposure = ex; sc.view_settings.keyframe_insert("exposure", frame=f)
KEYS = [  # frame, camera (cm), target (cm), lens
    (0, (282, 60, 1000), (282, 172, 0), 28), (89, (300, 70, 930), (282, 172, 0), 28),
    (239, (515, 25, 150), (300, 205, 75), 18), (329, (500, 52, 142), (290, 215, 80), 18),
    (330, (78, 250, 108), (560, 168, 118), 20), (569, (372, 238, 148), (560, 150, 150), 24),
    (570, (296, 140, 87), (392, 166, 79), 50), (689, (300, 200, 88), (392, 176, 79), 50),
    (690, (150, 42, 124), (560, 165, 124), 24), (809, (150, 42, 124), (560, 165, 124), 24),
    (810, (90, -540, 540), (75, 178, 55), 25), (899, (200, -575, 525), (88, 178, 55), 25),
]
CUTS = {330, 570, 690, 810}
for f, c, t, lens in KEYS:
    cam.location = Vector(c) * CM; tgt.location = Vector(t) * CM; cam_data.lens = lens
    cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f); cam_data.keyframe_insert("lens", frame=f)
for ob in (cam, tgt, cam_data):
    ad = ob.animation_data
    def curves(act):   # Blender 5 keeps curves in layers > strips > channelbags
        if hasattr(act, "fcurves") and len(act.fcurves):
            return list(act.fcurves)
        return [fc for L in act.layers for st in L.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in curves(ad.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT" if int(kp.co.x) + 1 in CUTS else "BEZIER"
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
cam_data.dof.use_dof = True
for f, fs, dist in ((0, 22.0, 6.0), (569, 22.0, 6.0), (570, 2.2, 0.95), (689, 2.2, 0.92), (690, 22.0, 6.0)):
    cam_data.dof.aperture_fstop = fs; cam_data.dof.focus_distance = dist
    cam_data.keyframe_insert("dof.aperture_fstop", frame=f); cam_data.keyframe_insert("dof.focus_distance", frame=f)
cam_data.clip_start = 0.02

# ---------- labels: where each size sits on screen, every frame ----------
LABELS = [  # key, text, size, anchor (cm), group whose landing shows it
    ("table", "Pool table, Hit Sport 7ft", "221 × 112 cm, 81.5 high", (338, 172, 86), "table"),
    ("sofa", "L-shaped sofa", "200 × 108 cm", (140, 50, 92), "sofa"),
    ("tv", "TV, 75 inch, PS5 and beer fridge", "166 × 96 cm · unit 180 × 52", (150, 330, 168), "tv"),
    ("ledge", "Drinks ledge and scoreboards", "285 cm long, top 105 high", (550, 172, 200), "wallset"),
    ("stools", "Bar stools", "seat 75 high", (528, 95, 82), "stools"),
]
if PASS == "labels":
    out = {}
    W, H = 1920, 1080
    for f in range(0, 900):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
        row = {}
        for key, _, _, at, _ in LABELS:
            p = world_to_camera_view(sc, cam, Vector(at) * CM)
            row[key] = [round(p.x * W, 1), round((1 - p.y) * H, 1), p.z > 0]
        for k, c in (("c00", (0, 0, 0)), ("cL0", (560, 0, 0)), ("c0W", (0, 345, 0)), ("cLW", (560, 345, 0))):
            p = world_to_camera_view(sc, cam, Vector(c) * CM); row[k] = [round(p.x * W, 1), round((1 - p.y) * H, 1), p.z > 0]
        out[f] = row
    json.dump({"labels": [[k, a, b, g] for k, a, b, _, g in LABELS], "land": {n: l for n, _, l in GROUPS}, "frames": out},
              open(os.path.join(FOUT, "labels.json"), "w"))
    print("done labels"); sys.exit(0)

# ---------- look ----------
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
ee = sc.eevee
for attr, val in (("taa_render_samples", 64), ("use_raytracing", True), ("use_shadows", True), ("use_gtao", True)):
    if hasattr(ee, attr):
        setattr(ee, attr, val)
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = 30
sc.render.image_settings.file_format = "PNG"
if PASS == "clay":
    clay = bpy.data.materials.new("clay"); clay.use_nodes = True
    b = clay.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.84, 0.82, 0.78, 1); b.inputs["Roughness"].default_value = 0.7
    bpy.context.view_layer.material_override = clay
    wn = sc.world.node_tree; wn.nodes.clear()
    bg = wn.nodes.new("ShaderNodeBackground"); bg.inputs[0].default_value = (0.006, 0.009, 0.03, 1); bg.inputs[1].default_value = 1.0
    o = wn.nodes.new("ShaderNodeOutputWorld"); wn.links.new(bg.outputs[0], o.inputs[0])
    for ob in bpy.data.objects:
        if ob.type == "LIGHT":
            ob.hide_render = True
    bpy.ops.object.light_add(type="SUN", location=(3, 1, 6)); s = bpy.context.object
    s.data.energy = 3.2; s.rotation_euler = (math.radians(38), math.radians(-12), math.radians(-35)); s.data.angle = math.radians(6)
    bpy.ops.object.light_add(type="AREA", location=(2.8, 1.72, 4.5)); a = bpy.context.object; a.data.size = 6; a.data.energy = 900
    sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = 0.3
else:
    for ob in bpy.data.objects:   # the pool lamp hangs 93 cm over the cloth: at the room's level it bleaches the blue
        if ob.type == "LIGHT" and ob.data.type == "AREA" and abs(ob.data.size - 1.1) < 0.01:
            ob.data.energy = 38
    sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = 0.0
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
FRAMES = [int(x) for x in os.environ["FILM_FRAMES"].split(",")] if os.environ.get("FILM_FRAMES") else range(F0, F1 + 1)
for f in FRAMES:
    sc.frame_set(f)
    sc.render.filepath = os.path.join(FOUT, PASS, f"{f:04d}.png")
    if not os.path.exists(sc.render.filepath):
        bpy.ops.render.render(write_still=True)
print("done", PASS, F0, F1)
