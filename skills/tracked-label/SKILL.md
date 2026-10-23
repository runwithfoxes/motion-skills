---
name: tracked-label
description: The After Effects tracking job done in code. A label pinned to something moving in real video, a product in an ad, a character walking, followed frame by frame through every shot, with a dot, a leader line and a two-line card. OpenCV, free, about twenty minutes. Use when someone wants a graphic stuck to a moving object, a product callout that follows the product, motion tracking without After Effects, or a label on a person or thing in footage.
---

# Tracked label

A label that follows something moving in a film. A dot sits on the object, a thin line runs out to a small card with
two lines of words, and as the object moves through the shot the label moves with it. Across a cut, it picks the
object up again in the next shot.

Our example follows the fox's head through three shots of one of our films: a corridor, a kitchen and a stage.

## What you need

Python 3 with `opencv-contrib-python-headless`, `numpy` and `pillow` (the contrib build has the CSRT tracker), and
ffmpeg. All the text is drawn with Pillow, so ffmpeg needs no text filter.

    python -m venv .venv && .venv/bin/pip install opencv-contrib-python-headless numpy pillow

## How it works

1. Find the cuts. `cuts.py` compares each frame with the last on a small grey copy; a mean difference over 18 is a
   cut. It writes `shots.json` and one still per shot with a numbered grid on it.

        python cuts.py film.mp4 work

2. Mark the object once per shot. Open each `shot-N.jpg`, read the grid, and type the box round the object into
   `shots.json` as `[x, y, width, height]`. Leave a shot's box as null to skip it. Mark something with its own colour
   and texture, such as a face, a label or a head, rather than something plain.

3. Track. `track.py` runs OpenCV's CSRT tracker from your box to the end of each shot, then checks the track: it
   compares the colours inside every tracked box with the first one and prints the worst frame.

        python track.py work

   Below about 0.8, look at that frame full size before you trust it. In our example the two worst were 0.73 and
   0.74, where the head turned and the light changed, and the dot was still on the head in both.

4. Draw. `render.py` smooths the centre over 5 frames (fine, because this runs offline), puts a dot on the object's
   edge, draws the line and the card, fades them in over 6 frames at the start of each shot, and carries the sound
   over.

        python render.py work out.mp4 "First line" "Second line" --font YourFont.ttf --keep-out 560 640

## Rules

The words come from the brand: the product's own name off the pack, a line from the ad's own copy. Never invent a
claim, and no price unless the ad gives one.

No brackets round the corners of the object. The box size drifts a little while the centre holds steady, and corner
brackets show the drift. A dot and a leader line hide it.

Keep the card clear of the film's own captions or titles. `--keep-out` takes a band of the frame the card must not
enter.

Work from the best copy of the film you can get. A video saved off an ad library is small and soft, and the label
will look sharper than the film under it.

Look at the worst-scoring frame of every shot full size before anyone sees it.

## Credit

The tracking is OpenCV's CSRT tracker (the discriminative correlation filter with channel and spatial reliability by
Lukežič and others, 2017). The job it replaces is After Effects' tracker. Drawn with Pillow, put together with ffmpeg.
