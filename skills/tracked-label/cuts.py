"""Find the cuts in a film and write one gridded still per shot, so you can mark the object once in each.

    python cuts.py film.mp4 work/

Writes work/shots.json and work/shot-<n>.jpg. Open each still, read the grid, and fill in "box" for every shot
you want tracked as [x, y, width, height] in the film's own pixels. Leave "box" as null to skip a shot.
"""
import sys, os, json
import cv2, numpy as np

src, out = sys.argv[1], sys.argv[2]
CUT = float(sys.argv[3]) if len(sys.argv) > 3 else 18.0   # mean grey difference on a small copy that counts as a cut
os.makedirs(out, exist_ok=True)

cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS)
frames, prev, cuts = [], None, [0]
while True:
    ok, f = cap.read()
    if not ok:
        break
    small = cv2.cvtColor(cv2.resize(f, (90, 160) if f.shape[0] > f.shape[1] else (160, 90)), cv2.COLOR_BGR2GRAY)
    if prev is not None and np.abs(small.astype(int) - prev.astype(int)).mean() > CUT:
        cuts.append(len(frames))
    prev = small
    frames.append(f)
cuts.append(len(frames))

shots = []
for n, (a, b) in enumerate(zip(cuts, cuts[1:])):
    shots.append({"shot": n, "start": a, "end": b - 1, "box": None})
    im = frames[a].copy()
    h, w = im.shape[:2]
    step = 50 if max(h, w) <= 1280 else 100
    for x in range(0, w, step):
        cv2.line(im, (x, 0), (x, h), (255, 255, 255) if x % (step * 2) == 0 else (120, 120, 120), 1)
        cv2.putText(im, str(x), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    for y in range(0, h, step):
        cv2.line(im, (0, y), (w, y), (255, 255, 255) if y % (step * 2) == 0 else (120, 120, 120), 1)
        cv2.putText(im, str(y), (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    cv2.imwrite(os.path.join(out, f"shot-{n}.jpg"), im)

json.dump({"film": os.path.abspath(src), "fps": fps, "frames": len(frames), "shots": shots},
          open(os.path.join(out, "shots.json"), "w"), indent=1)
for s in shots:
    print(f"shot {s['shot']}: frames {s['start']} to {s['end']} ({(s['end'] - s['start'] + 1) / fps:.1f} s)")
print("now mark a box in", os.path.join(out, "shots.json"), "for each shot you want tracked")
