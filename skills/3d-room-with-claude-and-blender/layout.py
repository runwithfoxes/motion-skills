"""Games room layouts for Alex and Max, built on top of room.py.
Run: blender -b -P layout.py -- A out_dir   (A = table down the room, B = table across the gym end)
Sizes in cm. Table: Hit Sport 7ft Revolver, 221 x 112 x 81.5 (Paul, 25 Oct). TV: 75 inch, 166 x 96.
The coloured floor marks the space each game needs: orange = room to swing a pool cue (120 cm),
blue = room to stand at the ends for air hockey and table tennis (100 cm)."""
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
VARIANT, OUT = argv[0], argv[1]
here = os.path.dirname(os.path.abspath(__file__))
os.environ["ROOM_ONLY"] = "1"
sys.argv = [sys.argv[0], "--", OUT]
exec(open(os.path.join(here, "room.py")).read())  # builds the room, defines box(), mat(), D, S, sc

TL, TW, TH = 221, 112, 81.5
FELT = mat("felt", (0.05, 0.25, 0.45), 0.8)
BODY = mat("table_body", (0.08, 0.08, 0.09), 0.5)
SOFA = mat("sofa", (0.35, 0.40, 0.48), 0.9)
CUSH = mat("cushion", (0.85, 0.45, 0.15), 0.9)
SCREEN = mat("screen", (0.02, 0.05, 0.12), 0.2, emit=0.4)
UNIT = mat("unit", (0.25, 0.22, 0.20), 0.5)
CUE = mat("cue_zone", (1.0, 0.55, 0.1), 0.9)
END = mat("end_zone", (0.2, 0.55, 1.0), 0.9)
RUG = mat("rug", (0.55, 0.50, 0.42), 1.0)


def zone(name, x0, y0, x1, y1, m):
    """A thin coloured patch on the floor, clipped to the room."""
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, D["L"]), min(y1, D["W"])
    if x1 > x0 and y1 > y0:
        box(name, x0, y0, 0.1, x1, y1, 0.4, m)


def table(x0, y0, along_x):
    """The Hit Sport revolver table in pool mode, from the shop photos: black body, silver corner
    caps, blue felt with six pockets, tapered end frames with the ball tray, a cross bar low down."""
    lx, ly = (TL, TW) if along_x else (TW, TL)
    SILVER = mat("silver", (0.75, 0.76, 0.78), 0.25)
    POOLFELT = mat("pool_felt", (0.05, 0.42, 0.75), 0.85)
    HOLE = mat("pocket", (0.01, 0.01, 0.01), 0.9)
    box("table_body", x0, y0, TH - 28, x0 + lx, y0 + ly, TH - 6, BODY)
    box("table_rail", x0, y0, TH - 6, x0 + lx, y0 + ly, TH, BODY)
    box("table_felt", x0 + 9, y0 + 9, TH - 6, x0 + lx - 9, y0 + ly - 9, TH + 0.3, POOLFELT)
    box("trim_low", x0 - 0.5, y0 - 0.5, TH - 29, x0 + lx + 0.5, y0 + ly + 0.5, TH - 27, SILVER)
    for cx, cy in ((x0, y0), (x0 + lx - 12, y0), (x0, y0 + ly - 12), (x0 + lx - 12, y0 + ly - 12)):
        box("corner_cap", cx - 0.5, cy - 0.5, TH - 7, cx + 12.5, cy + 12.5, TH + 0.5, SILVER)
    long_ax = lx if along_x else ly
    for t in (0.04, 0.5, 0.96):
        for side in (0, 1):
            if along_x:
                px, py = x0 + lx * t, (y0 + 9) if side == 0 else (y0 + ly - 9)
            else:
                px, py = (x0 + 9) if side == 0 else (x0 + lx - 9), y0 + ly * t
            box("pocket", px - 5, py - 5, TH, px + 5, py + 5, TH + 0.6, HOLE)
    # tapered end frames: wide at the floor, narrower at the top, silver edges, a ball tray
    for e in (0, 1):
        if along_x:
            ex = x0 + 18 if e == 0 else x0 + lx - 22
            box("end_frame", ex, y0 + 22, 6, ex + 4, y0 + ly - 22, TH - 28, BODY)
            box("end_foot", ex - 6, y0 + 10, 0, ex + 10, y0 + ly - 10, 6, BODY)
            for fy in (y0 + 18, y0 + ly - 22):
                box("end_edge", ex - 0.5, fy, 6, ex + 4.5, fy + 4, TH - 28, SILVER)
            tx = ex - 8 if e == 0 else ex + 4
            box("ball_tray", tx, y0 + ly / 2 - 18, 20, tx + 8, y0 + ly / 2 + 18, 45, BODY)
        else:
            ey = y0 + 18 if e == 0 else y0 + ly - 22
            box("end_frame", x0 + 22, ey, 6, x0 + lx - 22, ey + 4, TH - 28, BODY)
            box("end_foot", x0 + 10, ey - 6, 0, x0 + lx - 10, ey + 10, 6, BODY)
    if along_x:
        box("cross_bar", x0 + 22, y0 + ly / 2 - 4, 8, x0 + lx - 22, y0 + ly / 2 + 4, 16, BODY)
    else:
        box("cross_bar", x0 + lx / 2 - 4, y0 + 22, 8, x0 + lx / 2 + 4, y0 + ly - 22, 16, BODY)
    return lx, ly


def beanbag(cx, cy, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * S, location=(cx * S, cy * S, r * 0.55 * S))
    o = bpy.context.object; o.scale = (1, 1, 0.6); o.data.materials.append(m)
    bpy.ops.object.shade_smooth()


def sofa(x0, y0, w, d, facing):
    """A simple sofa: seat, back on the wall side, arms, two cushions. facing = +y or -y or +x."""
    box("sofa_seat", x0, y0, 0, x0 + w, y0 + d, 45, SOFA)
    if facing == "+y":
        box("sofa_back", x0, y0, 45, x0 + w, y0 + 22, 85, SOFA)
        for ax in (x0, x0 + w - 18):
            box("sofa_arm", ax, y0, 45, ax + 18, y0 + d, 62, SOFA)
        for cx in (x0 + 30, x0 + w - 70):
            box("cushion", cx, y0 + 22, 45, cx + 40, y0 + 34, 80, CUSH)
    elif facing == "+x":
        box("sofa_back", x0, y0, 45, x0 + 22, y0 + w if False else y0 + d, 85, SOFA)
        for ay in (y0, y0 + d - 18):
            box("sofa_arm", x0, ay, 45, x0 + w, ay + 18, 62, SOFA)


def tv_on_door_wall(cx):
    """75 inch TV on the door wall, low unit under it with the PS5 standing on it."""
    box("tv_unit", cx - 90, D["W"] - 40, 0, cx + 90, D["W"], 45, UNIT)
    box("ps5", cx + 50, D["W"] - 30, 45, cx + 60, D["W"] - 4, 84, mat("ps5", (0.92, 0.92, 0.94), 0.3))
    box("tv_frame", cx - 83, D["W"] - 6, 62, cx + 83, D["W"] - 2, 158, BODY)
    box("tv_screen", cx - 81, D["W"] - 6.5, 64, cx + 81, D["W"] - 6, 156, SCREEN)


# TV on the door wall near the fireplace, except in D where it moves to the gym wall
if VARIANT not in ("D", "E"):
    tv_on_door_wall(150)
if VARIANT in ("A", "B"):
    sofa(45, 0, 220, 95, "+y")
    box("rug", 50, 110, 0.05, 250, 290, 0.3, RUG)

if VARIANT == "E":
    # Paul, 25 Oct: TV back on the door wall by the fireplace (D's gym-wall TV was too far away),
    # an L-shaped sofa in the window and fireplace corner, which may cover the left shelves.
    FELT_IN, CUE48 = 11, 122
    x0 = D["L"] - (CUE48 - FELT_IN) - TL; y0 = (D["W"] - TW) / 2
    table(x0, y0, True)
    zone("cue48", x0 + FELT_IN - CUE48, y0 + FELT_IN - CUE48, x0 + TL - FELT_IN + CUE48, y0 + TW - FELT_IN + CUE48, CUE)
    tv_on_door_wall(150)
    # L sofa: long side under the first window facing the TV, short side along the left shelves
    LONG_X1, DEPTH, SHORT_Y1 = 200, 88, 112
    box("Lsofa_long_seat", 0, 0, 0, LONG_X1, DEPTH, 42, SOFA)
    box("Lsofa_long_back", 0, 0, 42, LONG_X1, 20, 82, SOFA)
    box("Lsofa_short_seat", 0, DEPTH, 0, DEPTH, SHORT_Y1, 42, SOFA)
    box("Lsofa_short_back", 0, 0, 42, 20, SHORT_Y1, 82, SOFA)
    box("Lsofa_arm_end", LONG_X1 - 16, 0, 42, LONG_X1, DEPTH, 60, SOFA)
    for cx in (40, 95, 150):
        box("cushion", cx, 20, 42, cx + 38, 32, 76, CUSH)
    box("rug", 30, 100, 0.05, 200, 290, 0.3, RUG)
    print("L sofa ends at x", LONG_X1, "| cue room starts at x", x0 + FELT_IN - CUE48,
          "| felt corner at", x0 + FELT_IN, y0 + FELT_IN, "| sofa front to TV", D["W"] - 6 - DEPTH)
elif VARIANT == "D":
    # Paul, 25 Oct: a sofa in the corner by the right-hand shelves, out of the table's way.
    # Same table and cue room as C. Loveseat 118 x 80, backed onto the shelf unit, facing up the
    # room. The 75 inch TV moves to the gym wall so the sofa looks at it over the table.
    FELT_IN, CUE48 = 11, 122
    x0 = D["L"] - (CUE48 - FELT_IN) - TL; y0 = (D["W"] - TW) / 2
    table(x0, y0, True)
    zone("cue48", x0 + FELT_IN - CUE48, y0 + FELT_IN - CUE48, x0 + TL - FELT_IN + CUE48, y0 + TW - FELT_IN + CUE48, CUE)
    sx0, sy0, sw, sd = 32, D["W"] - 120, 80, 118   # x depth 32..112, y 225..343
    box("loveseat_seat", sx0, sy0, 0, sx0 + sw, sy0 + sd, 45, SOFA)
    box("loveseat_back", sx0, sy0, 45, sx0 + 20, sy0 + sd, 85, SOFA)
    box("loveseat_arm1", sx0, sy0, 45, sx0 + sw, sy0 + 15, 62, SOFA)
    box("loveseat_arm2", sx0, sy0 + sd - 15, 45, sx0 + sw, sy0 + sd, 62, SOFA)
    box("cushion", sx0 + 20, sy0 + 25, 45, sx0 + 32, sy0 + 60, 78, CUSH)
    print("loveseat front at x", sx0 + sw, "cue room starts at x", x0 + FELT_IN - CUE48)
    # TV on the gym wall, centred, with a slim unit under it for the PS5
    cy = D["W"] / 2
    box("tv_unit", D["L"] - 35, cy - 90, 0, D["L"], cy + 90, 40, UNIT)
    box("ps5", D["L"] - 30, cy + 55, 40, D["L"] - 4, cy + 65, 79, mat("ps5", (0.92, 0.92, 0.94), 0.3))
    box("tv_frame", D["L"] - 6, cy - 83, 75, D["L"] - 2, cy + 83, 171, BODY)
    box("tv_screen", D["L"] - 6.5, cy - 81, 77, D["L"] - 6, cy + 81, 169, SCREEN)
    beanbag(75, 120, 36, CUSH)
elif VARIANT == "C":
    # Paul, 25 Oct: "way too tight", table nearer the door, room for cues all round.
    # Table at the gym and door end. Orange = room for a 48 inch (122 cm) cue measured from the
    # playing surface, which is about 11 cm in from the table's edge. No sofa: two beanbags
    # in front of the fireplace that get moved for shots from that end.
    FELT_IN, CUE48 = 11, 122
    x0 = D["L"] - (CUE48 - FELT_IN) - TL; y0 = (D["W"] - TW) / 2
    table(x0, y0, True)
    zone("cue48", x0 + FELT_IN - CUE48, y0 + FELT_IN - CUE48, x0 + TL - FELT_IN + CUE48, y0 + TW - FELT_IN + CUE48, CUE)
    beanbag(75, 120, 38, CUSH)
    beanbag(75, 225, 38, mat("bean2", (0.15, 0.35, 0.6), 0.9))
elif VARIANT == "A":
    # table down the room, 105 cm clear of the gym wall
    x0 = D["L"] - 105 - TL; y0 = (D["W"] - TW) / 2
    table(x0, y0, True)
    zone("cue_side1", x0, y0 - 120, x0 + TL, y0, CUE)
    zone("cue_side2", x0, y0 + TW, x0 + TL, y0 + TW + 120, CUE)
    zone("end1", x0 - 100, y0, x0, y0 + TW, END)
    zone("end2", x0 + TL, y0, x0 + TL + 100, y0 + TW, END)
    # two beanbags in the gym-end corners, clear of where the boys stand at the end of the table
    beanbag(D["L"] - 45, 50, 40, CUSH)
    beanbag(D["L"] - 45, D["W"] - 50, 40, mat("bean2", (0.15, 0.35, 0.6), 0.9))
else:
    # table across the room in the gym half
    x0 = 300; y0 = (D["W"] - TL) / 2
    table(x0, y0, False)
    zone("cue_side1", x0 - 120, y0, x0, y0 + TL, CUE)
    zone("cue_side2", x0 + TW, y0, x0 + TW + 120, y0 + TL, CUE)
    zone("end1", x0, y0 - 100, x0 + TW, y0, END)
    zone("end2", x0, y0 + TL, x0 + TW, y0 + TL + 100, END)

CAMS = {
    "plan": ((280, 172, 900), (280, 172.1, 0), 24),
    "from-gym-corner": ((545, 330, 175), (100, 120, 60), 16),
    "table-close": ((520, 60, 150), (330, 172, 70), 20),
    "from-sofa": ((150, 60, 105), (150, 345, 110), 16) if VARIANT != "D" else ((75, 285, 110), (560, 172, 110), 18),
    **({"sofa-to-tv": ((120, 45, 110), (150, 345, 115), 16), "overview": ((540, 20, 230), (120, 250, 40), 16)} if VARIANT == "E" else {}),
    "from-fireplace": ((70, 172, 170), (560, 172, 40), 16),
}
if os.environ.get("LAYOUT_ONLY") == "1":
    CAMS = {}
for name, (pos, look, lens) in CAMS.items():
    bpy.ops.object.camera_add(location=Vector(pos) * S)
    cam = bpy.context.object; cam.data.lens = lens
    cam.rotation_euler = ((Vector(look) - Vector(pos)) * S).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    bpy.data.objects["ceiling"].hide_render = name == "plan"
    sc.render.filepath = os.path.join(OUT, f"{VARIANT}-{name}.png")
    bpy.ops.render.render(write_still=True)

if CAMS:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"layout-{VARIANT}.blend"))
    print("done", VARIANT)
