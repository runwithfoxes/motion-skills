"""Paul's living room as it is now, built in Blender from his photos and his measurements.
Run: blender -b -P room.py -- out_dir
Every size is in centimetres in DIM below. MEASURED = Paul gave it (25 Oct). Everything else is
GUESSED from the photos and gets replaced when he measures.

Axes: x runs the length, 0 = fireplace wall, 560 = gym wall. y runs the width, 0 = window wall,
345 = door wall. z is up from the floor."""
import bpy, sys, os, math
from mathutils import Vector

DIM = dict(
    L=560, W=345, H=253,                       # MEASURED
    breast_w=125, breast_d=38,                 # chimney breast, centred on the fireplace wall (GUESSED)
    shelf_w=95, shelf_d=32, shelf_h=215,       # the two built-in shelf units in the alcoves (GUESSED)
    win_sill=45, win_h=170, win_w=150,         # both big windows (GUESSED)
    win1_x=60, win2_x=60 + 150 + 75,           # left edge of each window from the fireplace wall (GUESSED)
    rad_v_w=55, rad_v_h=180,                   # tall radiator between the windows (GUESSED)
    door_x=300, door_w=82, door_h=204,         # door on the door wall (GUESSED)
    rad_h_x=400, rad_h_w=110, rad_h_h=60,      # low radiator past the door (GUESSED)
)
D = DIM
S = 0.01  # Blender works in metres

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "renders"
os.makedirs(out, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, rgb, rough=0.6, emit=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    return m


WALL = mat("wall", (0.86, 0.87, 0.88))
WOOD = mat("floor", (0.42, 0.26, 0.15), 0.45)
TRIM = mat("trim", (0.55, 0.33, 0.18), 0.4)
CREAM = mat("shelf", (0.88, 0.86, 0.80))
BLACK = mat("black", (0.03, 0.03, 0.03))
GLASS = mat("sky", (0.85, 0.9, 1.0), emit=1.5)
BLIND = mat("blind", (0.92, 0.92, 0.92))
CURTAIN = mat("curtain", (0.78, 0.78, 0.78), 0.9)
RAD = mat("rad", (0.95, 0.95, 0.95), 0.3)


def box(name, x0, y0, z0, x1, y1, z1, m):
    """Axis-aligned box from two corners, in cm."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object; o.name = name
    o.location = ((x0 + x1) / 2 * S, (y0 + y1) / 2 * S, (z0 + z1) / 2 * S)
    o.scale = (abs(x1 - x0) * S, abs(y1 - y0) * S, abs(z1 - z0) * S)
    o.data.materials.append(m)
    return o


T = 10  # wall thickness
# floor, ceiling, the two end walls
box("floor", 0, 0, -2, D["L"], D["W"], 0, WOOD)
box("ceiling", 0, 0, D["H"], D["L"], D["W"], D["H"] + 2, WALL)
box("wall_fireplace", -T, -T, 0, 0, D["W"] + T, D["H"], WALL)
box("wall_gym", D["L"], -T, 0, D["L"] + T, D["W"] + T, D["H"], WALL)

# window wall (y=0), built in pieces around the two windows
s0, s1 = D["win_sill"], D["win_sill"] + D["win_h"]
x = 0
for i, wx in enumerate((D["win1_x"], D["win2_x"])):
    box(f"ww_pier{i}", x, -T, 0, wx, 0, D["H"], WALL)
    box(f"ww_below{i}", wx, -T, 0, wx + D["win_w"], 0, s0, WALL)
    box(f"ww_above{i}", wx, -T, s1, wx + D["win_w"], 0, D["H"], WALL)
    box(f"sky{i}", wx, -T - 2, s0, wx + D["win_w"], -T, s1, GLASS)
    for k in range(int(D["win_h"] / 6)):  # blind slats
        z = s0 + 3 + k * 6
        box(f"slat{i}_{k}", wx + 2, -4, z, wx + D["win_w"] - 2, -1, z + 0.6, BLIND)
    # curtains each side, floor length, on a rod near the ceiling
    box(f"curtL{i}", wx - 25, 1, 2, wx + 15, 6, D["H"] - 25, CURTAIN)
    box(f"curtR{i}", wx + D["win_w"] - 15, 1, 2, wx + D["win_w"] + 25, 6, D["H"] - 25, CURTAIN)
    box(f"rod{i}", wx - 35, 3, D["H"] - 26, wx + D["win_w"] + 35, 5, D["H"] - 24, BLACK)
    x = wx + D["win_w"]
box("ww_pier_end", x, -T, 0, D["L"], 0, D["H"], WALL)
rx = D["win1_x"] + D["win_w"] + (D["win2_x"] - D["win1_x"] - D["win_w"] - D["rad_v_w"]) / 2
box("rad_tall", rx, 0, 15, rx + D["rad_v_w"], 6, 15 + D["rad_v_h"], RAD)

# door wall (y=W), with the door opening
dx0, dx1 = D["door_x"], D["door_x"] + D["door_w"]
box("dw_a", 0, D["W"], 0, dx0, D["W"] + T, D["H"], WALL)
box("dw_above", dx0, D["W"], D["door_h"], dx1, D["W"] + T, D["H"], WALL)
box("dw_b", dx1, D["W"], 0, D["L"], D["W"] + T, D["H"], WALL)
box("hall", dx0, D["W"] + T, 0, dx1, D["W"] + 120, D["door_h"], mat("hall", (0.7, 0.68, 0.64)))
for side in (dx0 - 7, dx1):  # door frame
    box("frame", side, D["W"] - 2, 0, side + 7, D["W"] + 1, D["door_h"] + 7, TRIM)
box("frame_top", dx0 - 7, D["W"] - 2, D["door_h"], dx1 + 7, D["W"] + 1, D["door_h"] + 7, TRIM)
# door leaf, open about 70 degrees into the room, hinged on the gym side
a = math.radians(70)
leaf = box("door_leaf", -D["door_w"] / 2, -2, 0, D["door_w"] / 2, 2, D["door_h"] - 1, TRIM)
leaf.location = ((dx1 - D["door_w"] / 2 * math.cos(a)) * S, (D["W"] - D["door_w"] / 2 * math.sin(a)) * S, leaf.location.z)
leaf.rotation_euler.z = -a
box("rad_low", D["rad_h_x"], D["W"] - 8, 12, D["rad_h_x"] + D["rad_h_w"], D["W"], 12 + D["rad_h_h"], RAD)

# skirting all round
for x0, y0, x1, y1 in ((0, 0, D["L"], 2), (0, D["W"] - 2, D["L"], D["W"]), (0, 0, 2, D["W"]), (D["L"] - 2, 0, D["L"], D["W"])):
    box("skirting", x0, y0, 0, x1, y1, 10, TRIM)

# chimney breast, fireplace, mantel, hearth, and the two shelf units
by0 = (D["W"] - D["breast_w"]) / 2; by1 = by0 + D["breast_w"]
box("breast", 0, by0, 0, D["breast_d"], by1, D["H"], WALL)
box("fire_surround", D["breast_d"], by0 + 12, 0, D["breast_d"] + 2, by1 - 12, 112, CREAM)
box("fire_opening", D["breast_d"] + 0.5, by0 + 28, 18, D["breast_d"] + 2.5, by1 - 28, 95, BLACK)
box("mantel", D["breast_d"], by0 + 5, 112, D["breast_d"] + 14, by1 - 5, 117, TRIM)
box("hearth", D["breast_d"], by0 + 8, 0, D["breast_d"] + 45, by1 - 8, 12, BLACK)
for name, y0 in (("shelf_left", (by0 - D["shelf_w"]) / 2), ("shelf_right", by1 + (D["W"] - by1 - D["shelf_w"]) / 2)):
    y1 = y0 + D["shelf_w"]
    box(name + "_back", 0, y0, 0, 2, y1, D["shelf_h"], CREAM)
    box(name + "_sideA", 0, y0, 0, D["shelf_d"], y0 + 2, D["shelf_h"], CREAM)
    box(name + "_sideB", 0, y1 - 2, 0, D["shelf_d"], y1, D["shelf_h"], CREAM)
    for k in range(8):
        z = 8 + k * (D["shelf_h"] - 10) / 7
        box(name + f"_board{k}", 0, y0, z, D["shelf_d"], y1, z + 2, CREAM)
    box(name + "_top", 0, y0 - 3, D["shelf_h"], D["shelf_d"] + 3, y1 + 3, D["shelf_h"] + 6, CREAM)

# ceiling downlights
LAMP = mat("lamp", (1, 0.95, 0.85), emit=3)
for lx in (150, 410):
    for ly in (110, 235):
        box("downlight", lx - 5, ly - 5, D["H"] - 0.5, lx + 5, ly + 5, D["H"], LAMP)
        bpy.ops.object.light_add(type="AREA", location=(lx * S, ly * S, (D["H"] - 3) * S))
        l = bpy.context.object; l.data.energy = 25; l.data.size = 0.3

# daylight in through the windows, pointing into the room (+y)
for wx in (D["win1_x"], D["win2_x"]):
    bpy.ops.object.light_add(type="AREA", location=((wx + D["win_w"] / 2) * S, 0.05, (s0 + D["win_h"] / 2) * S))
    l = bpy.context.object; l.data.energy = 90; l.data.shape = "RECTANGLE"
    l.data.size = D["win_w"] * S; l.data.size_y = D["win_h"] * S; l.rotation_euler = (-math.pi / 2, 0, 0)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

# Cycles, so light bounces off the walls onto the ceiling the way it does in the real room
sc.render.engine = "CYCLES"; sc.cycles.samples = 64; sc.cycles.use_denoising = True
try:
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "METAL"
    bpy.context.preferences.addons["cycles"].preferences.get_devices(); sc.cycles.device = "GPU"
except Exception:
    pass
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"

# cameras at roughly Paul's photo positions, phone wide lens
CAMS = {
    "01-to-fireplace": ((520, 172, 140), (0, 172, 110)),    # his photos 1 and 4
    "02-to-door-wall": ((150, 30, 150), (330, 345, 120)),   # photo 2
    "03-to-gym-end": ((60, 172, 140), (560, 172, 110)),     # photo 3
    "04-to-windows": ((250, 325, 150), (300, 0, 110)),      # photos 5 and 6
    "05-plan": ((280, 172, 900), (280, 172.1, 0)),          # from above, ceiling off
}
if os.environ.get("ROOM_ONLY") == "1":
    CAMS = {}
for name, (pos, look) in CAMS.items():
    bpy.ops.object.camera_add(location=Vector(pos) * S)
    cam = bpy.context.object; cam.data.lens = 14 if name != "05-plan" else 24
    cam.rotation_euler = ((Vector(look) - Vector(pos)) * S).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    bpy.data.objects["ceiling"].hide_render = name == "05-plan"
    sc.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)

if CAMS:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "room-as-is.blend"))
print("done", out)
