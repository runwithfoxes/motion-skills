# Games room film v2 (Paul, 25 Oct: "no art to the editing... approach this artistically... make it wow. It can be 30 seconds")

GOAL: a marketer sees a real room built to the centimetre, then lit and dressed, then turned into a photo, and thinks "we could sell that".
OUTPUT: Blender 5 EEVEE renders, composited in Python, 1920x1080 for the site and a 1080x1350 (4:5) cut framed for LinkedIn (rendered, not cropped).
TIME: 30 s x 30 fps = 900 frames. No loop. Frame 0 is the thumbnail, frame 899 the poster.
LOOK: clay white #EDEBE6 on deep navy #0B1026 for the build; the arcade room for the reveal. One accent, RWF orange #FF6A00, only for
  dimension lines and step dots. Avenir Next Demi Bold for labels, Regular for sizes, white on navy pills like the live page.
MOTION: camera on bezier ease-in-out, never parks. Walls rise from the floor over 40 frames (quint ease-out). Furniture drops from
  above on a spring (zeta 0.6, 2.2 Hz), one piece every 18 to 25 frames. Labels arrive 4 frames after their object lands.
SHOTS:
  0-89     PLAN. Top down, clay. Room lines draw on, walls rise, "560 cm" and "345 cm" draw along the walls. Why: the tape measure is the start.
  90-239   CRANE DOWN to eye level as the furniture drops in: table, sofa, TV unit, ledge and boards, stools. Each lands with its size.
  240-329  HOLD AND TURN. The finished clay room, slow drift. A light line sweeps across and the room turns into the lit arcade (wipe 270-329).
  330-569  HERO. Low dolly from the sofa end along the table to the neon and the boards, rising at the end. No labels. Why: show the detail.
  570-689  MACRO. 50 mm slider across the table's corner cap and pocket, shallow focus. Why: this is what a model can't usually do.
  690-809  RENDER TO PHOTO. The Blender view, then a wipe to the repainted photo, same frame, sizes held. Why: the point of it.
  810-899  END. Top-down of the lit room, every size on it, then the title "Built to the centimetre in Blender". Poster frame.
BANNED: fades on everything, zoom-in Ken Burns on stills, labels that move while being read, purple gradients, lens flares,
  particles, captions over the hero shot, text centred over the subject.
QA: contact sheet per format, first and last frame, stills at 89, 239, 300, 450, 620, 760, 899; measure label positions against the model.
MODEL: build/realistic.py (the measured room, Hit Sport table 221 x 112 x 81.5). CAMERA: keyed in film/v2/film.py.
