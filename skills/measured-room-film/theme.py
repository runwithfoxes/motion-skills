"""Two looks for Alex and Max's games room, both on layout E (Paul's pick, 25 Oct).
Run: blender -b -P theme.py -- clubhouse out_dir      or      -- arcade out_dir
clubhouse = deep green walls, timber slats, locker doors over the shelves, chalk scoreboard.
arcade    = inky navy room, light strip round the ceiling, glow behind the TV, neon over the
            scoreboard, one long pool light so the table is the bright thing in a dark room.
Both: the far wall (where the gym kit was) is the scoreboard wall, all on the wall and nothing
on the floor, because that end is where the boys stand to take shots."""
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
THEME, OUT = argv[0], argv[1]
LEVEL = argv[2] if len(argv) > 2 else "dim"
here = os.path.dirname(os.path.abspath(__file__))
os.environ["LAYOUT_ONLY"] = "1"
sys.argv = [sys.argv[0], "--", "E", OUT]
exec(open(os.path.join(here, "layout.py")).read())  # room + layout E, no renders

# the planning marks go: no cue zone, no rug from the layout
for o in list(bpy.data.objects):
    if o.name.startswith(("cue48", "rug")):
        bpy.data.objects.remove(o, do_unlink=True)


def recolour(name, rgb, rough=None):
    m = bpy.data.materials[name]; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    if rough is not None:
        b.inputs["Roughness"].default_value = rough


def glow(name, rgb, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = strength
    return m


def words(text, x, y, z, size, m, facing="-x", extrude=0.6):
    """Raised letters on a wall. facing -x = on the far wall, -y = on the door wall."""
    bpy.ops.object.text_add(location=(x * S, y * S, z * S))
    t = bpy.context.object; t.data.body = text; t.data.size = size * S
    t.data.extrude = extrude * S; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
    t.rotation_euler = (math.radians(90), 0, math.radians(-90) if facing == "-x" else 0)
    t.data.materials.append(m)
    return t


def cylinder(name, x0, y0, z0, x1, y1, z1, r, m):
    a, b = Vector((x0, y0, z0)) * S, Vector((x1, y1, z1)) * S
    bpy.ops.mesh.primitive_cylinder_add(radius=r * S, depth=(b - a).length, location=(a + b) / 2, vertices=16)
    o = bpy.context.object; o.name = name
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler(); o.data.materials.append(m)
    return o


L, W, H = D["L"], D["W"], D["H"]
TX = L - 111 - 221 / 2          # table centre along the room
CY = W / 2
CHALK = mat("chalk", (0.92, 0.92, 0.88), 0.9)

# ---- the scoreboard wall (far wall, x = L), the same plan in both looks ----
def scoreboard_wall(board_rgb, frame_m, rack_m, header_m):
    """Far wall (Paul, 25 Oct): a drinks ledge at bar height with two stools for people watching,
    the two league boards above it. The cue rack moves to the window wall pier by this wall."""
    BOARD = mat("board", board_rgb, 0.85)
    for side, (y0, y1), name in ((0, (28, 128), "ALEX"), (1, (217, 317), "MAX")):
        box("board_frame", L - 3, y0 - 3, 116, L, y1 + 3, 210, frame_m)
        box("board", L - 3.5, y0, 119, L - 3, y1, 207, BOARD)
        words(name, L - 4, (y0 + y1) / 2, 196, 12, header_m)
        for k, label in enumerate(("POOL", "HOCKEY", "PING PONG", "PS5")):
            z = 178 - k * 17
            words(label, L - 4, y0 + 30, z, 5, CHALK, extrude=0.2)
            for t in range(k + 2 + side):  # a few tally marks so it reads as a live league
                box("tally", L - 4, y0 + 62 + t * 5, z - 4, L - 3.6, y0 + 63.2 + t * 5, z + 4, CHALK)
    # drinks ledge, 104 cm high, 25 deep, with two bar stools tucked under it
    box("ledge", L - 25, 30, 101, L, D["W"] - 30, 105, rack_m)
    for sy in (95, 250):
        cylinder("stool_seat", L - 30, sy, 73, L - 30, sy, 77, 18, mat("stool_seat", (0.95, 0.35, 0.08), 0.6))
        cylinder("stool_post", L - 30, sy, 2, L - 30, sy, 73, 2.5, mat("stool_metal", (0.1, 0.1, 0.12), 0.3))
        cylinder("stool_ring", L - 30, sy, 25, L - 30, sy, 27, 13, mat("stool_metal", (0.1, 0.1, 0.12), 0.3))
        cylinder("stool_base", L - 30, sy, 0, L - 30, sy, 2, 20, mat("stool_metal", (0.1, 0.1, 0.12), 0.3))
    # cue rack on the window wall pier between the second window and the far wall
    rx = 470
    box("rack_back", rx, 0, 40, rx + 64, 4, 200, rack_m)
    for i, dx in enumerate((10, 23, 36)):
        # 48 inch (122 cm) cues, the length the cue room is drawn for (Cato, dray-33)
        cylinder("cue", rx + dx, 9, 68, rx + dx, 9, 190, 1.4, mat("cue_wood", (0.6, 0.38, 0.18), 0.4))
    cylinder("short_cue", rx + 50, 9, 100, rx + 50, 9, 190, 1.4, mat("cue_wood2", (0.5, 0.3, 0.14), 0.4))
    box("rack_shelf", rx, 0, 40, rx + 64, 12, 43, rack_m)


# ---- the TV unit gets deeper, with a glass-door mini fridge in its right end ----
def tv_unit_with_fridge(unit_m):
    for o in list(bpy.data.objects):
        if o.name.startswith(("tv_unit", "ps5")):
            bpy.data.objects.remove(o, do_unlink=True)
    cx = 150
    box("tv_unit", cx - 90, W - 52, 0, cx + 90, W, 55, unit_m)
    box("ps5", cx - 85, W - 34, 55, cx - 75, W - 8, 94, mat("ps5", (0.92, 0.92, 0.94), 0.3))
    fx0 = cx + 36   # fridge 48 wide, 50 tall, inside the unit's right end
    box("fridge_glass", fx0, W - 52.5, 3, fx0 + 48, W - 52, 52, mat("fridge_glass", (0.6, 0.75, 0.9), 0.05))
    box("fridge_light", fx0 + 3, W - 50, 6, fx0 + 45, W - 49, 49, glow("fridge_lamp", (0.75, 0.88, 1.0), 2))
    for k in range(6):  # beer bottles on two shelves
        for row, zb in enumerate((8, 30)):
            cylinder("bottle", fx0 + 7 + k * 7, W - 45, zb, fx0 + 7 + k * 7, W - 45, zb + 18, 2.6, mat("bottle", (0.25, 0.12, 0.03), 0.2))


# ---- one long pool light over the table ----
def pool_light(shade_m, lamp_rgb, power):
    z = 175
    box("pool_light", TX - 60, CY - 9, z, TX + 60, CY + 9, z + 10, shade_m)
    box("pool_light_glow", TX - 57, CY - 7, z - 0.4, TX + 57, CY + 7, z, glow("pool_lamp", lamp_rgb, 4))
    for dx in (-45, 45):
        cylinder("cord", TX + dx, CY, z + 10, TX + dx, CY, H, 0.4, mat("cord", (0.05, 0.05, 0.05)))
    bpy.ops.object.light_add(type="AREA", location=(TX * S, CY * S, (z - 2) * S))
    l = bpy.context.object; l.data.shape = "RECTANGLE"; l.data.size = 1.1; l.data.size_y = 0.14
    l.data.energy = power; l.data.color = lamp_rgb


# ---- doors over the two shelf alcoves ----
def shelf_doors(door_m, handle_m, labels=None, label_m=None):
    by0 = (W - D["breast_w"]) / 2; by1 = by0 + D["breast_w"]
    for (y0, y1), lab in zip(((0, by0), (by1, W)), labels or (None, None)):
        n = 2
        for k in range(n):
            a, b = y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n
            box("door", 32, a + 0.6, 0, 35, b - 0.6, D["shelf_h"] + 6, door_m)
            box("handle", 35, (a + b) / 2 - 1, 100, 37, (a + b) / 2 + 1, 120, handle_m)
            for v in range(4):  # locker vents near the top
                box("vent", 35, a + 8, 190 - v * 4, 35.4, b - 8, 191.5 - v * 4, handle_m)
        if lab and label_m is not None:
            t = words(lab, 36, (y0 + y1) / 2, 160, 18, label_m)
            t.rotation_euler = (math.radians(90), 0, math.radians(90))  # on the doors, facing +x


# daylight down to an evening level in both looks, so the lamps do the work
for o in bpy.data.objects:
    if o.type == "LIGHT" and o.data.type == "AREA" and abs(o.location.y - 0.05) < 0.01:
        o.data.energy = 15
recolour("sky", (0.25, 0.3, 0.45))

if THEME == "clubhouse":
    recolour("wall", (0.05, 0.16, 0.11), 0.7)        # deep green
    recolour("floor", (0.36, 0.22, 0.12), 0.4)
    recolour("sofa", (0.42, 0.22, 0.10), 0.45)       # tan leather
    recolour("cushion", (0.85, 0.75, 0.55), 0.8)     # cream
    recolour("unit", (0.32, 0.19, 0.10), 0.5)
    recolour("curtain", (0.82, 0.78, 0.68), 0.9)
    bpy.data.objects["ceiling"].data.materials[0] = mat("ceiling_cream", (0.88, 0.85, 0.78))
    TIMBER = mat("timber", (0.55, 0.34, 0.17), 0.5)
    BRASS = mat("brass", (0.75, 0.55, 0.2), 0.3)
    # timber slats across the whole far wall, the boards sit on them
    for k in range(int(W / 7)):
        box("slat", L - 1.5, k * 7 + 1, 0, L, k * 7 + 5, H, TIMBER)
    scoreboard_wall((0.06, 0.07, 0.07), TIMBER, TIMBER, BRASS)
    shelf_doors(mat("locker", (0.80, 0.62, 0.20), 0.45), BRASS, ("A", "M"), mat("locker_num", (0.05, 0.16, 0.11)))
    # timber slat panel behind the TV
    for k in range(int(220 / 7)):
        box("tv_slat", 40 + k * 7, W - 1.5, 30, 44 + k * 7, W, 200, TIMBER)
    # a row of pennants along the door wall above the TV and door
    for i, x in enumerate(range(30, 520, 32)):
        col = ((0.80, 0.62, 0.20), (0.85, 0.80, 0.70))[i % 2]
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=11 * S, depth=0.4 * S, location=(x * S, (W - 1) * S, 225 * S))
        o = bpy.context.object; o.rotation_euler = (math.radians(90), 0, math.radians(180)); o.scale = (1, 1.6, 1)
        o.data.materials.append(mat(f"pennant{i}", col, 0.9))
    box("bunting", 20, W - 1, 230, 530, W - 0.5, 231, BRASS)
    pool_light(mat("green_shade", (0.04, 0.18, 0.1), 0.4), (1.0, 0.85, 0.65), 250)
    sc.view_settings.exposure = -1.0
    box("rug", 30, 100, 0.05, 200, 290, 0.4, mat("rug_stripe", (0.8, 0.62, 0.22), 1.0))
    for k in range(5):
        box("rug_band", 30, 110 + k * 36, 0.4, 200, 120 + k * 36, 0.6, mat("rug_band", (0.05, 0.16, 0.11), 1.0))
    for o in bpy.data.objects:  # warm downlights
        if o.type == "LIGHT" and o.location.z > 2.4:
            o.data.energy = 18; o.data.color = (1.0, 0.85, 0.65)

else:  # arcade
    recolour("wall", (0.015, 0.02, 0.05), 0.85)      # inky navy, ceiling too
    recolour("floor", (0.25, 0.15, 0.09), 0.35)
    recolour("sofa", (0.03, 0.10, 0.12), 0.9)        # deep teal velvet
    recolour("cushion", (0.95, 0.35, 0.08), 0.9)     # orange
    recolour("unit", (0.02, 0.02, 0.03), 0.4)
    recolour("curtain", (0.03, 0.04, 0.08), 0.9)
    recolour("trim", (0.04, 0.04, 0.06), 0.5)
    recolour("shelf", (0.03, 0.03, 0.05), 0.6)
    recolour("rad", (0.05, 0.05, 0.08), 0.4)
    CYAN = glow("cove", (0.15, 0.6, 1.0), 6)
    PINK = glow("neon", (1.0, 0.15, 0.55), 25)
    WARM = glow("tv_glow", (1.0, 0.45, 0.15), 8)
    # light strip round the top of all four walls
    for x0, y0, x1, y1 in ((0, 1, L, 2.5), (0, W - 2.5, L, W - 1), (1, 0, 2.5, W), (L - 2.5, 0, L - 1, W)):
        box("cove_strip", x0, y0, H - 8, x1, y1, H - 6, CYAN)
    # glow behind the TV: a panel the TV stands off, lit at its edges
    box("tv_glow", 150 - 90, W - 1.2, 55, 150 + 90, W - 0.8, 165, WARM)
    bpy.ops.object.light_add(type="AREA", location=(1.5, (W - 10) * S, 1.1))
    l = bpy.context.object; l.data.size = 1.8; l.data.energy = 60; l.data.color = (1.0, 0.45, 0.15)
    l.rotation_euler = (math.radians(90), 0, 0)
    scoreboard_wall((0.02, 0.02, 0.03), mat("frame_dark", (0.06, 0.06, 0.08), 0.4), mat("rack_dark", (0.08, 0.08, 0.1), 0.4), PINK)
    words("GAME ON", L - 4, CY, 228, 16, PINK, extrude=1.0)
    bpy.ops.object.light_add(type="AREA", location=((L - 25) * S, CY * S, 2.2))
    l = bpy.context.object; l.data.size = 1.2; l.data.energy = 50; l.data.color = (1.0, 0.15, 0.55)
    l.rotation_euler = (0, math.radians(-90), 0)
    shelf_doors(mat("panel_dark", (0.02, 0.02, 0.035), 0.6), glow("door_line", (0.15, 0.6, 1.0), 3))
    pool_light(mat("black_shade", (0.02, 0.02, 0.02), 0.3), (1.0, 0.92, 0.8), 300)
    sc.view_settings.exposure = -2.2
    recolour("screen", (0.01, 0.015, 0.03))
    box("rug", 30, 100, 0.05, 200, 290, 0.4, mat("rug_dark", (0.05, 0.05, 0.08), 1.0))
    for o in bpy.data.objects:  # downlights low
        if o.type == "LIGHT" and o.location.z > 2.4:
            o.data.energy = 4
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.05
    if LEVEL == "bright":  # every light on a dimmer: downlights up, the room readable, still navy
        for o in bpy.data.objects:
            if o.type == "LIGHT" and o.location.z > 2.4:
                o.data.energy = 45; o.data.color = (1.0, 0.92, 0.82)
        sc.view_settings.exposure = -1.0

tv_unit_with_fridge(bpy.data.materials["unit"])

# softer edges on everything built from boxes
for o in bpy.data.objects:
    if o.type == "MESH" and o.name not in ("floor", "ceiling") and not o.name.startswith(("wall_", "ww_", "dw_")):
        mod = o.modifiers.new("bevel", "BEVEL"); mod.width = 0.004; mod.segments = 2

sc.cycles.samples = 128
CAMS = {
    "sofa-to-tv": ((120, 40, 110), (150, 345, 115), 16),
    "to-scoreboard": ((90, 70, 150), (560, 172, 130), 18),
    "overview": ((540, 20, 230), (120, 250, 40), 15),
}
if os.environ.get("THEME_ONLY") == "1":
    CAMS = {}
for name, (pos, look, lens) in CAMS.items():
    bpy.ops.object.camera_add(location=Vector(pos) * S)
    cam = bpy.context.object; cam.data.lens = lens
    cam.rotation_euler = ((Vector(look) - Vector(pos)) * S).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = os.path.join(OUT, f"{THEME}-{LEVEL}-{name}.png")
    bpy.ops.render.render(write_still=True)
if CAMS:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{THEME}.blend"))
    print("done", THEME)
