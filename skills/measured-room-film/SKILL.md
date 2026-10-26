---
name: measured-room-film
description: A real room built in Blender to the centimetre from phone photos and a tape measure, laid out with furniture at its true size, then shot as a 30 second film. The walls rise, each piece drops in with its size, a line of light turns the white model into the lit room, and the camera moves through it like a real one. Sound is made in code from the same frame numbers. Free, runs on a Mac mini. Use when someone wants a room, a shop, a stand or a space planned to real sizes and shown as a film, a "will it fit" check before buying furniture, or a product shown in a real room without a photo shoot.
---

# Measured room film

A room built in Blender from real measurements, with the furniture at its real size, filmed from the model. Our
example is a living room turned into a games room for two ten year olds: 560 by 345 cm, 253 cm to the ceiling, with a
7ft pool table that has to leave room to swing a cue.

Everything is Python. No AI pictures go into the model, so every size you see is the size you typed.

## What you need

Blender 5 (it runs headless with `blender -b`), Python 3 with `pillow` and `numpy`, and ffmpeg. The textures and two
models come free from Poly Haven, with no key:

    python3 fetch_assets.py

The labels use Avenir Next, which ships with macOS. On another system, point the `AV` line in `compose.py` at any
font you like.

## How it works

The scripts build on each other in a chain: `room.py`, then `layout.py`, `theme.py` and `realistic.py` (which pulls in
`pooltable.py`), then `film.py`. Each one runs the one before it, so a change to a size in `room.py` carries all the
way to the film.

1. Measure the room and put the sizes in the `DIM` list at the top of `room.py`, in centimetres. Mark each one
   MEASURED or GUESSED. The length, width and height must be measured. The windows, door and fireplace can start as
   guesses from the photos and be corrected later. Render the empty room from the same angles as the photos and lay
   them side by side to check it:

        blender -b -P room.py -- renders

2. Lay it out. `layout.py` places the furniture at its real size and paints the space each thing needs on the floor:
   orange for room to swing a pool cue (120 cm round the cloth), blue for room to stand at the ends. Move things until
   nothing sits in a coloured area. Take the big item's size from the maker's listing, never from a picture. Ours
   took five layouts, A to E, and E is the one the film uses.

        blender -b -P layout.py -- E renders

3. Dress it. `theme.py` gives it a look (ours has two, `clubhouse` and `arcade`), and `realistic.py` adds real
   materials, a proper sofa and stools, and the table from `pooltable.py`, modelled from the shop photos at
   221 x 112 x 81.5 cm. Every size stays as measured.

        blender -b -P realistic.py -- bright renders

4. Shoot it. `BRIEF.md` is the shot list, in frame numbers. `film.py` loads the room, keys the camera, drops the
   furniture in on a spring and renders two passes: the white clay build and the lit room. A third pass renders
   nothing and writes where every size label sits on screen, frame by frame.

        blender -b -P film.py -- labels 0 899 out
        blender -b -P film.py -- clay 0 329 out
        blender -b -P film.py -- arcade 270 689 out
        blender -b -P film.py -- arcade 810 899 out

   EEVEE renders a frame in about four seconds on a Mac mini, so the 840 frames take about forty minutes. A pass can
   be stopped and started again: frames already on disk are skipped.

5. Cut it. `compose.py` draws the orange dimension lines, the size labels that ride on their objects, the line of light
   that switches the room on and the end title, and writes `out/final/`. `score.py` writes the sound from the same frame
   numbers, so every landing has its own hit. Then put them together:

        python3 compose.py
        python3 score.py
        ffmpeg -framerate 30 -i out/final/%04d.png -i score.wav -c:v libx264 -crf 18 -pix_fmt yuv420p \
          -c:a aac -b:a 192k -af loudnorm=I=-14:TP=-1 -shortest room-film.mp4

6. Look at it. Make a contact sheet, then check the first and last frames and every moment a piece lands, full size.

        ffmpeg -i room-film.mp4 -vf "fps=1,scale=480:-1,tile=6x5" -frames:v 1 sheet.jpg

`bake.py` and `export_web.py` take the same room to a web page you can turn with a finger: `bake.py` saves the room's
own lighting onto the model as pictures, so it looks the same from every angle on a phone.

## The render-to-photo shot

Frames 690 to 809 are made for a still Blender render and the same view repainted by an AI model to look like a
photograph, with a wipe between them. Put the pair in `photos/render.png` and `photos/photo.png`. Without them, the
shot holds the lit room and the film still works.

Be warned about the repaint. AI moves things while it paints: a board shifts, a black rail turns to wood, the words
come out as nonsense. Most of it is too small to see by eye, so measure it. Render a mask of every object, let the AI
repaint only the surfaces, measure how far each object drifted and push it back inside its mask, and put words and
signs back from the render rather than through the AI. Ours got every object back within a centimetre. The surfaces
were close to a photograph but not all the way.

## Rules

Measure first. A room built from guesses looks right and is wrong, and the whole point is that the sizes are true.

Every size label is read straight from the model. Have something other than the person who built it check the labels
against the model before anyone sees them. Ours caught a sofa sitting through a shelf unit.

Shoot the model, never a slideshow of stills. The camera always moves on an ease, and nothing parks.

End on a frame someone art directed. Ours takes the near wall away so the lit room sits on black like an architect's
model, with the title in the empty space beside it. A plan view with a caption bar across it is not an ending.

No words over the hero shot. Let the detail carry it.

## Credit

Built and rendered in Blender. The textures and the stool and gamepad models are from Poly Haven (CC0). The sound is
made with numpy, and the film is put together with Pillow and ffmpeg.
