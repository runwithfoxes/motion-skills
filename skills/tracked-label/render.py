"""Draw a label pinned to the tracked object: a dot on it, a leader line, and a two-line card. Sound is carried over.

    python render.py work/ out.mp4 "First line" "Second line" [--font path/to/font.ttf] [--side right|left] [--keep-out Y0 Y1]

The centre and size are smoothed over 5 frames, centred, which is fine because this runs offline. The card fades
in over 6 frames at the start of each shot. --keep-out keeps the card out of a horizontal band, such as the ad's own
caption. All text is drawn with Pillow, so ffmpeg needs no text filter.
"""
import sys, os, json, argparse, subprocess, shutil
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("out"); ap.add_argument("line1"); ap.add_argument("line2")
ap.add_argument("--font"); ap.add_argument("--side", default="right")
ap.add_argument("--keep-out", nargs=2, type=int)
o = ap.parse_args()

S = json.load(open(os.path.join(o.work, "shots.json")))
T = {int(k): v for k, v in json.load(open(os.path.join(o.work, "track.json")))["track"].items()}
cap = cv2.VideoCapture(S["film"])
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)
H, W = frames[0].shape[:2]
K = 2 if max(W, H) < 1000 else 1            # draw small films at twice the size, so the type is sharp
u = max(W, H) * K / 1280                    # one unit of type and spacing, scaled to the frame

def font(size, bold):
    if o.font:
        return ImageFont.truetype(o.font, size)
    return ImageFont.load_default(size=size)
fb, fr = font(int(30 * u), True), font(int(24 * u), False)

# smooth centre and size inside each shot
sm = {}
for s in S["shots"]:
    idx = [i for i in range(s["start"], s["end"] + 1) if T.get(i)]
    if not idx:
        continue
    arr = np.array([T[i] for i in idx], float)
    k = 5
    smooth = lambda v: np.convolve(np.pad(v, (k // 2, k // 2), mode="edge"), np.ones(k) / k, "valid")
    cx, cy = smooth(arr[:, 0] + arr[:, 2] / 2), smooth(arr[:, 1] + arr[:, 3] / 2)
    w, h = smooth(arr[:, 2]), smooth(arr[:, 3])
    for j, i in enumerate(idx):
        sm[i] = (cx[j] * K, cy[j] * K, w[j] * K, h[j] * K, i - s["start"])

tmp = os.path.join(o.work, "_frames")
shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
pad, line_w = int(18 * u), max(2, int(2 * u))
for i, f in enumerate(frames):
    im = Image.fromarray(cv2.cvtColor(cv2.resize(f, (W * K, H * K), interpolation=cv2.INTER_LANCZOS4), cv2.COLOR_BGR2RGB)).convert("RGBA")
    if i in sm:
        cx, cy, w, h, n = sm[i]
        a = min(1.0, n / 6)
        A = int(255 * a)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        tw = max(d.textlength(o.line1, font=fb), d.textlength(o.line2, font=fr)) + 2 * pad
        th = int(30 * u) + int(24 * u) + 3 * int(10 * u)
        ax = cx + w / 2 if o.side == "right" else cx - w / 2          # anchor on the object's edge, half way up
        ay = cy
        bx = ax + 40 * u if o.side == "right" else ax - 40 * u - tw
        bx = min(max(bx, 20 * u), W * K - tw - 20 * u)
        by = min(max(ay - th / 2, 20 * u), H * K - th - 20 * u)
        if o.keep_out:
            y0, y1 = o.keep_out[0] * K, o.keep_out[1] * K
            if by < y1 and by + th > y0:
                by = y1 + 10 * u if ay > (y0 + y1) / 2 else y0 - th - 10 * u
        ex, ey = (bx if o.side == "right" else bx + tw), by + th / 2
        d.line([(ax, ay), (ax + (ex - ax) * a, ay + (ey - ay) * a)], fill=(255, 255, 255, A), width=line_w)
        r = 5 * u
        d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=(255, 255, 255, A))
        d.rectangle([bx, by, bx + tw, by + th], fill=(22, 22, 22, int(215 * a)))
        d.text((bx + pad, by + 10 * u), o.line1, font=fb, fill=(255, 255, 255, A))
        d.text((bx + pad, by + 20 * u + 30 * u), o.line2, font=fr, fill=(235, 200, 150, A))
        im = Image.alpha_composite(im, ov)
    im.convert("RGB").save(os.path.join(tmp, f"{i:05d}.png"))

subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(S["fps"]), "-i", os.path.join(tmp, "%05d.png"), "-i", S["film"],
                "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-shortest", o.out], check=True)
shutil.rmtree(tmp)
print(o.out)
