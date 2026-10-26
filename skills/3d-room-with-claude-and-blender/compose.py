"""Cut the games room film from the Blender frames (BRIEF.md). Draws the orange dimension lines, the size labels
that ride on their objects, the light-line wipe into the lit room, the render-to-photo wipe and the end title.
Writes frames to out/final/. Usage: python3 compose.py"""
import os, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
G = HERE
W, H = 1920, 1080
L = json.load(open(os.path.join(OUT, "labels.json")))
FR, LAND = L["frames"], L["land"]
LAB = {k: (name, size, grp) for k, name, size, grp in L["labels"]}
ORANGE, NAVY, WHITE, GREY = (255, 106, 0), (10, 14, 32), (255, 255, 255), (196, 204, 226)
AV = "/System/Library/Fonts/Avenir Next.ttc"
F_NAME = ImageFont.truetype(AV, 30, index=2); F_SIZE = ImageFont.truetype(AV, 26, index=0)
F_DIM = ImageFont.truetype(AV, 40, index=2); F_TITLE = ImageFont.truetype(AV, 74, index=2); F_SUB = ImageFont.truetype(AV, 32, index=0)
F_TAG = ImageFont.truetype(AV, 26, index=2); F_END = ImageFont.truetype(AV, 82, index=2)

def ease_out(t): return 1 - (1 - max(0, min(1, t))) ** 5
def ease_io(t):
    t = max(0, min(1, t)); return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def clay(f): return Image.open(os.path.join(OUT, "clay", f"{f:04d}.png")).convert("RGB")
def arc(f): return Image.open(os.path.join(OUT, "arcade", f"{f:04d}.png")).convert("RGB")
def cover(im, z=1.0):
    s = max(W / im.width, H / im.height) * z
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))
# The render-to-photo shot (frames 690-809) needs a still render and its repainted photo in photos/. Without them the
# shot holds the lit room instead.
_r, _p = os.path.join(G, "photos", "render.png"), os.path.join(G, "photos", "photo.png")
RENDER, PHOTO = (Image.open(_r), Image.open(_p)) if os.path.exists(_r) and os.path.exists(_p) else (None, None)

def pill(d, x, y, name, size, a):
    """A label like the live page's: navy pill, name in demi bold, size under it, a dot on the object."""
    if a <= 0: return
    w = max(d.textlength(name, font=F_NAME), d.textlength(size, font=F_SIZE)) + 36
    yy = y - 96 + 10 * (1 - a)
    d.line((x, y, x, yy + 76), fill=WHITE + (int(170 * a),), width=2)
    d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=ORANGE + (int(255 * a),))
    bx = min(max(x - 24, 30), W - w - 30)
    d.rounded_rectangle((bx, yy, bx + w, yy + 76), 12, fill=NAVY + (int(225 * a),))
    d.text((bx + 18, yy + 8), name, font=F_NAME, fill=WHITE + (int(255 * a),))
    d.text((bx + 18, yy + 42), size, font=F_SIZE, fill=GREY + (int(255 * a),))

def dims(d, row, a, draw):
    """Orange dimension lines along two walls, drawn on by 'draw' (0..1), with their sizes."""
    if a <= 0: return
    for (p, q, text) in (("c00", "cL0", "560 cm"), ("c00", "c0W", "345 cm")):
        (x0, y0, v0), (x1, y1, v1) = row[p], row[q]
        if not (v0 and v1): continue
        dx, dy = x1 - x0, y1 - y0; n = math.hypot(dx, dy) or 1
        ox, oy = -dy / n * 34, dx / n * 34                     # stand off the wall
        if p == "c00" and q == "c0W": ox, oy = -ox, -oy
        ex, ey = x0 + ox + dx * draw, y0 + oy + dy * draw
        col = ORANGE + (int(255 * a),)
        d.line((x0 + ox, y0 + oy, ex, ey), fill=col, width=4)
        for tx, ty in ((x0 + ox, y0 + oy), (ex, ey)):
            d.line((tx - oy * 0.35, ty + ox * 0.35, tx + oy * 0.35, ty - ox * 0.35), fill=col, width=4)
        if draw > 0.6:
            ta = a * min(1, (draw - 0.6) / 0.3)
            mx, my = x0 + ox * 2.4 + dx / 2, y0 + oy * 2.4 + dy / 2
            tw = d.textlength(text, font=F_DIM)
            d.rounded_rectangle((mx - tw / 2 - 14, my - 28, mx + tw / 2 + 14, my + 28), 10, fill=NAVY + (int(220 * ta),))
            d.text((mx, my), text, font=F_DIM, fill=WHITE + (int(255 * ta),), anchor="mm")

def tag(d, text, a):
    if a <= 0: return
    w = d.textlength(text, font=F_TAG) + 40
    d.rounded_rectangle((60, 56, 60 + w, 110), 27, fill=NAVY + (int(215 * a),))
    d.ellipse((76, 76, 90, 90), fill=ORANGE + (int(255 * a),))
    d.text((102, 83), text, font=F_TAG, fill=WHITE + (int(255 * a),), anchor="lm")

def light_wipe(a_img, b_img, u):
    """b comes in from the left behind a thin line of light."""
    x = int(W * ease_io(u))
    out = a_img.copy(); out.paste(b_img.crop((0, 0, x, H)), (0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    g.rectangle((x - 3, 0, x + 3, H), fill=(255, 236, 214, 255))
    glow = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)), glow)
    return Image.alpha_composite(out.convert("RGBA"), glow).convert("RGB")

os.makedirs(os.path.join(OUT, "final"), exist_ok=True)
for f in range(900):
    row = FR[str(f)]
    if f < 270:
        im = clay(f)
    elif f < 330:
        im = light_wipe(clay(f), arc(f), (f - 272) / 54)
    elif f < 690:
        im = arc(f)
    elif f < 810:
        k = (f - 690) / 119; z = 1.0 + 0.025 * k
        if RENDER is None:                        # no photo pair: hold the last lit frame, still drifting in
            im = cover(arc(689), z)
        else:
            r, p = cover(RENDER, z), cover(PHOTO, z)
            im = r if f < 728 else (light_wipe(r, p, (f - 728) / 40) if f < 770 else p)
    else:
        im = arc(f)
    im = im.convert("RGBA"); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if f < 300:                                   # the plan: dimension lines draw on, then fade as we crane down
        dims(d, row, 1 - max(0, (f - 150) / 40), ease_out((f - 24) / 40))
    if 90 <= f < 330:                             # each label 4 frames after its piece lands, off before the wipe
        for key, (name, size, grp) in LAB.items():
            t0 = LAND[grp] + 4
            a = min(1, max(0, (f - t0) / 6)) * (1 - max(0, (f - 262) / 10))
            x, y, vis = row[key]
            if vis: pill(d, x, y, name, size, a)
    if 690 <= f < 810 and RENDER is not None:
        tag(d, "The Blender render", min(1, (f - 692) / 8) * (1 - max(0, (f - 726) / 6)))
        tag(d, "Repainted as a photo · every object back within 1 cm", min(1, (f - 772) / 8))
    if f >= 810:                                  # the end: the room as a model on black, the type in the space beside it
        dims(d, row, ease_out((f - 816) / 14), ease_out((f - 816) / 34))
        x0 = 120
        ra = ease_out((f - 826) / 16)
        if ra > 0:
            d.rectangle((x0, 168, x0 + 64 * ra, 174), fill=ORANGE + (255,))
        for i, (txt, fnt, col, y, start) in enumerate((("Built to", F_END, WHITE, 200, 832), ("the centimetre.", F_END, WHITE, 290, 838),
                                                      ("A real room in Blender,", F_SUB, GREY, 428, 852), ("every size from the tape measure.", F_SUB, GREY, 472, 856))):
            a = ease_out((f - start) / 14)
            if a > 0:
                d.text((x0, y + 18 * (1 - a)), txt, font=fnt, fill=col + (int(255 * a),))
    Image.alpha_composite(im, ov).convert("RGB").save(os.path.join(OUT, "final", f"{f:04d}.png"))
print("composed 900 frames")
