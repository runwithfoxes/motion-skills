"""The Hit Sport 7ft Multi Game Revolver Table, modelled properly (Paul, 25 Oct: "the pool table
still looks like a 3D model"). Built from the shop photos and the manual, at the size Paul gave:
221 x 112 x 81.5 cm. Pool side up: black wood-grain body, blue cloth, cloth-covered cushions,
six pockets, chunky silver corner caps, a silver strip under the apron, tapered end frames with
silver edges, a ball tray with balls at one end, levelling feet and a cross bar.
Use: exec after realistic.py's helpers exist; call build(x0, y0) with the table's corner in cm."""
import bpy, bmesh, math
from mathutils import Vector


def _hull(name, pts, m, bevel=0.0, seg=3):
    """A solid from its corner points (cm), smoothed edges if bevel > 0."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    for p in pts:
        bm.verts.new(Vector(p) * 0.01)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new("soft", "BEVEL"); b.width = bevel * 0.01; b.segments = seg; b.limit_method = "ANGLE"
    return o


def _box(name, x0, y0, z0, x1, y1, z1, m, bevel=0.0, seg=3):
    return _hull(name, [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], m, bevel, seg)


def _cyl(name, x, y, z0, z1, r, m, verts=32, bevel=0.0):
    pts = [(x + r * math.cos(a), y + r * math.sin(a), z) for a in [2 * math.pi * i / verts for i in range(verts)] for z in (z0, z1)]
    return _hull(name, pts, m, bevel)


def _sphere(name, x, y, z, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 0.01, location=(x * 0.01, y * 0.01, z * 0.01), segments=24, ring_count=12)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def build(x0, y0, tex_mat, mat):
    L, W, H = 221.0, 112.0, 81.5
    x1, y1 = x0 + L, y0 + W
    RAIL = 12.0                 # rail width, outer edge to cushion nose
    CLOTH_Z = 76.0              # top of the playing cloth
    APRON_LO = 58.0             # bottom of the body
    BLACK = tex_mat("pt_black", "black_oak_veneer", 0.6, tint=(0.035, 0.033, 0.033), rough_add=0.35, nor=0.35)  # the real table is black
    FELT = tex_mat("pt_felt", "fabric_pattern_07", 0.06, base=(0.0, 0.055, 0.36), rough_add=0.5, nor=0.2, sheen=0.0)  # cloth is matte  # strong blue, as in the shop photos
    SILVER = mat("pt_silver", (0.78, 0.79, 0.8), 0.25)
    SILVER.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
    RUBBER = mat("pt_rubber", (0.015, 0.015, 0.015), 0.6)
    PLASTIC = mat("pt_plastic", (0.015, 0.015, 0.018), 0.6)

    # body (apron), four sides, edges softened
    _box("pt_apron_s", x0, y0, APRON_LO, x1, y0 + 4, CLOTH_Z - 1, BLACK, 0.6)
    _box("pt_apron_n", x0, y1 - 4, APRON_LO, x1, y1, CLOTH_Z - 1, BLACK, 0.6)
    _box("pt_apron_w", x0, y0, APRON_LO, x0 + 4, y1, CLOTH_Z - 1, BLACK, 0.6)
    _box("pt_apron_e", x1 - 4, y0, APRON_LO, x1, y1, CLOTH_Z - 1, BLACK, 0.6)
    # silver strip round the bottom of the apron
    for nm, a in (("s", (x0, y0, x1, y0 + 1)), ("n", (x0, y1 - 1, x1, y1)),
                  ("w", (x0, y0, x0 + 1, y1)), ("e", (x1 - 1, y0, x1, y1))):
        _box("pt_strip_" + nm, a[0], a[1], APRON_LO - 0.5, a[2], a[3], APRON_LO + 2.2, SILVER, 0.3)

    # the bed and its cloth
    _box("pt_bed", x0 + 4, y0 + 4, CLOTH_Z - 6, x1 - 4, y1 - 4, CLOTH_Z, FELT)

    # rails: black wood tops, broken at the six pockets
    P_CORNER, P_SIDE = 13.0, 12.0
    xm = (x0 + x1) / 2
    for side, (ya, yb) in (("s", (y0, y0 + RAIL)), ("n", (y1 - RAIL, y1))):
        for k, (xa, xb) in enumerate(((x0 + P_CORNER, xm - P_SIDE / 2), (xm + P_SIDE / 2, x1 - P_CORNER))):
            _box(f"pt_rail_{side}{k}", xa, ya, CLOTH_Z - 1, xb, yb, H, BLACK, 0.8)
            # cushion: a cloth-covered wedge along the inner edge
            yin, yout = (yb, yb - 3.5) if side == "s" else (ya, ya + 3.5)
            _hull(f"pt_cushion_{side}{k}", [(xa + 2, yout, CLOTH_Z), (xb - 2, yout, CLOTH_Z), (xa + 2, yout, CLOTH_Z + 4.2), (xb - 2, yout, CLOTH_Z + 4.2),
                                            (xa + 3.5, yin + (2.2 if side == "s" else -2.2), CLOTH_Z + 3.4), (xb - 3.5, yin + (2.2 if side == "s" else -2.2), CLOTH_Z + 3.4),
                                            (xa + 3.5, yin + (2.2 if side == "s" else -2.2), CLOTH_Z + 2.0), (xb - 3.5, yin + (2.2 if side == "s" else -2.2), CLOTH_Z + 2.0)], FELT)
    for side, (xa, xb) in (("w", (x0, x0 + RAIL)), ("e", (x1 - RAIL, x1))):
        _box(f"pt_rail_{side}", xa, y0 + P_CORNER, CLOTH_Z - 1, xb, y1 - P_CORNER, H, BLACK, 0.8)
        xin = xb if side == "w" else xa
        sgn = 1 if side == "w" else -1
        _hull(f"pt_cushion_{side}", [(xin - sgn * 3.5, y0 + P_CORNER + 2, CLOTH_Z), (xin - sgn * 3.5, y1 - P_CORNER - 2, CLOTH_Z),
                                     (xin - sgn * 3.5, y0 + P_CORNER + 2, CLOTH_Z + 4.2), (xin - sgn * 3.5, y1 - P_CORNER - 2, CLOTH_Z + 4.2),
                                     (xin + sgn * 2.2, y0 + P_CORNER + 3.5, CLOTH_Z + 3.4), (xin + sgn * 2.2, y1 - P_CORNER - 3.5, CLOTH_Z + 3.4),
                                     (xin + sgn * 2.2, y0 + P_CORNER + 3.5, CLOTH_Z + 2.0), (xin + sgn * 2.2, y1 - P_CORNER - 3.5, CLOTH_Z + 2.0)], FELT)

    # pockets: dark openings with a plastic lip, corners and the middle of each long side
    pockets = [(x0 + 11, y0 + 11), (x1 - 11, y0 + 11), (x0 + 11, y1 - 11), (x1 - 11, y1 - 11), (xm, y0 + 8), (xm, y1 - 8)]
    for i, (px, py) in enumerate(pockets):
        _cyl(f"pt_pocket_{i}", px, py, CLOTH_Z - 8, CLOTH_Z + 0.4, 5.6, RUBBER)
        _cyl(f"pt_pocket_lip_{i}", px, py, H - 0.8, H, 6.6, PLASTIC, bevel=0.4)

    # chunky silver corner caps: rounded blocks over each corner, top and down the side
    for i, (cx, cy) in enumerate(((x0, y0), (x1, y0), (x0, y1), (x1, y1))):
        sx = 1 if cx == x0 else -1; sy = 1 if cy == y0 else -1
        xa, xb = sorted((cx, cx + sx * 8)); ya, yb = sorted((cy, cy + sy * 8))  # flush with the body: overall size stays 221 x 112  # caps stop short of the pocket
        _box(f"pt_cap_{i}", xa, ya, CLOTH_Z - 9, xb, yb, H, SILVER, 2.2, 5)
    # side pocket plates on the long rails
    for i, py in enumerate((y0, y1)):
        ya, yb = (py - 0.5, py + 9) if i == 0 else (py - 9, py + 0.5)
        _box(f"pt_sideplate_{i}", xm - 9, max(ya, y0), CLOTH_Z - 6, xm + 9, min(yb, y1), H, PLASTIC, 1.5, 4)

    # tapered end frames with silver edges, wide at the floor, narrow under the body
    for e, ex in enumerate((x0 + 16, x1 - 20)):
        t = 4.0
        bot = (y0 + 8, y1 - 8); top = (y0 + 20, y1 - 20)
        _hull(f"pt_frame_{e}", [(ex, bot[0], 4), (ex, bot[1], 4), (ex + t, bot[0], 4), (ex + t, bot[1], 4),
                                (ex, top[0], APRON_LO), (ex, top[1], APRON_LO), (ex + t, top[0], APRON_LO), (ex + t, top[1], APRON_LO)], BLACK, 0.5)
        for s, (yb_, yt_) in enumerate(((bot[0], top[0]), (bot[1], top[1]))):
            d = 2.4 if s == 0 else -2.4
            _hull(f"pt_frame_edge_{e}{s}", [(ex - 0.4, yb_, 4), (ex + t + 0.4, yb_, 4), (ex - 0.4, yb_ + d, 4), (ex + t + 0.4, yb_ + d, 4),
                                            (ex - 0.4, yt_, APRON_LO), (ex + t + 0.4, yt_, APRON_LO), (ex - 0.4, yt_ + d, APRON_LO), (ex + t + 0.4, yt_ + d, APRON_LO)], SILVER, 0.3)
        # wide foot under each frame, with two levelling feet
        _box(f"pt_foot_{e}", ex - 6, bot[0] - 4, 2, ex + t + 6, bot[1] + 4, 7, BLACK, 0.8)
        for fy in (bot[0] - 1, bot[1] + 1):
            _cyl(f"pt_leveller_{e}{fy}", ex + t / 2, fy, 0, 2.2, 3.4, RUBBER)
    # low cross bar between the frames, and the side beam
    _box("pt_crossbar", x0 + 20, (y0 + y1) / 2 - 4, 12, x1 - 20, (y0 + y1) / 2 + 4, 20, BLACK, 0.6)

    # ball tray on the outside of the east end frame, with balls in it
    tx = x1 - 20 + 4
    _box("pt_tray", tx, (y0 + y1) / 2 - 16, 26, tx + 9, (y0 + y1) / 2 + 16, 50, PLASTIC, 2.0, 4)
    cols = [(0.9, 0.75, 0.05), (0.05, 0.2, 0.7), (0.75, 0.05, 0.05), (0.35, 0.05, 0.45), (0.95, 0.4, 0.05),
            (0.05, 0.45, 0.15), (0.45, 0.1, 0.05), (0.02, 0.02, 0.02), (0.92, 0.92, 0.88)]
    for i, c in enumerate(cols):
        row, colm = divmod(i, 5)
        _sphere(f"pt_ball_{i}", tx + 6, (y0 + y1) / 2 - 12 + colm * 6 + row * 3, 31 + row * 7.5, 2.8, mat(f"pt_ball_{i}", c, 0.15))
