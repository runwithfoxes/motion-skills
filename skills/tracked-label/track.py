"""Follow the marked object through each shot with OpenCV's CSRT tracker, and check the track.

    python track.py work/

Reads work/shots.json (with a box filled in per shot), writes work/track.json. For each shot it prints how many
frames were lost and the colour likeness of every tracked box to the first one. Below about 0.8, look at that
frame yourself before trusting the track.
"""
import sys, os, json
import cv2, numpy as np

work = sys.argv[1]
S = json.load(open(os.path.join(work, "shots.json")))
cap = cv2.VideoCapture(S["film"])
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)

def hist(img):
    h = cv2.calcHist([cv2.cvtColor(img, cv2.COLOR_BGR2HSV)], [0, 1], None, [30, 32], [0, 180, 0, 256])
    return cv2.normalize(h, h)

track, report = {}, []
for s in S["shots"]:
    if not s.get("box"):
        continue
    a, b, box = s["start"], s["end"], tuple(int(v) for v in s["box"])
    t = cv2.TrackerCSRT_create()
    t.init(frames[a], box)
    track[a] = list(box)
    for i in range(a + 1, b + 1):
        ok, bb = t.update(frames[i])
        track[i] = [int(v) for v in bb] if ok else None
    x, y, w, h = box
    h0 = hist(frames[a][y:y + h, x:x + w])
    sims = []
    for i in range(a, b + 1):
        if track[i] is None:
            sims.append(0.0)
            continue
        x, y, w, h = track[i]
        crop = frames[i][max(y, 0):y + h, max(x, 0):x + w]
        sims.append(cv2.compareHist(h0, hist(crop), cv2.HISTCMP_CORREL) if crop.size else 0.0)
    lost = sum(track[i] is None for i in range(a, b + 1))
    worst = a + int(np.argmin(sims))
    report.append(dict(shot=s["shot"], lost=lost, worst=round(min(sims), 2), mean=round(float(np.mean(sims)), 2), worst_frame=worst))
    print(f"shot {s['shot']} frames {a}-{b}: lost {lost}, likeness worst {min(sims):.2f} (frame {worst}), mean {np.mean(sims):.2f}")

json.dump({"track": {str(k): v for k, v in track.items()}, "report": report}, open(os.path.join(work, "track.json"), "w"))
print("look at the worst frame of every shot full size before you render")
