---
name: beat-reel
description: A 15 second square video, all graphics, no camera and no AI pictures, where every change lands on a drum beat and the music is made in code from the same list of beats, so picture and sound cannot drift. The worked example explains the 95:5 rule with 100 dots. Use when someone asks for a reel cut to a beat, a short graphic video for social, an animated stat with music, or a motion graphic that feels rhythmic.
---

# Beat reel

Fifteen seconds, square, all graphics. A drum beat runs underneath, and every change in the picture lands on a beat
or a half beat. The music is generated in code from the same table of beats as the picture, so the two cannot drift
apart.

The worked example is here: the 95:5 rule shown with a field of 100 dots. Read `motion-by-numbers` first; this skill
is that method applied to a beat.

## How to make one

1. Write `brief.md` in the eight lines (`brief.md` here is the example). The goal is one idea someone gets in fifteen
   seconds. The words come from something real you or your client wrote, never invented for the reel.
2. Pick the tempo. At 120 BPM one beat is half a second, 15 frames at 30 fps, so 15 seconds is 30 beats.
3. Write the shots as beat numbers in `build.py`, never seconds: `b(6.5)`, `b(11)`. Captions, cuts and sound hits
   all use `b()`.
4. Build, render, mix:

        ./fonts.sh                                (once: copies the two fonts in)
        python build.py                           (writes index.html and score.wav)
        ../motion-by-numbers/render.sh .
        ./mix.sh                                  (lays the music under the newest render)

5. Measure, then look. The checks are below. Share the `-sound.mp4`.

## The rules that make it work

Time the picture to the beat, never to the words. A caption needs about two seconds to read, and the temptation is to
hold the picture still while it is read. Our second version held the dots still for four beats under each caption,
and it was dull: the timing was going against the words. So while a line is read, something small keeps moving on
every beat. In the example the five lit dots pulse on each beat with a soft pop, and the 95 grey dots stay still, so
only the point of the reel moves.

Something changes on every beat or half beat. No stretch of more than two beats where nothing moves, except the end
card.

Bring things in one at a time on the half beat. Never everything at once.

A spring takes about 3 frames to look full, so start it 3 frames before its beat (`tl - 3 / FPS`) or it lands late.
Rows of dots start 4.5 frames early. Measure, never guess.

Each sound hits one frame after its picture (`LAG` in `build.py`). It reads as locked.

One idea, one accent colour, your brand's ground colour. The source of any number on screen goes on screen too, in
small type.

Don't drop a soft 3D character picture onto flat graphics at the end. We tried it and it looked like a sticker. A
character goes in only if it is drawn in the same flat style, or properly animated.

Loudness: `mix.sh` aims at -14 LUFS. On a 15 second file the leveller undershoots, so it adds a fixed 3.6 dB before
the limiter. It lands near -15.

Most feeds play muted. The words and the picture have to carry it without the beat.

## Checks before anyone sees it

Measure the frame each arrival reaches full size against its beat (beat n is frame 15n at 30 fps and 120 BPM). Every
one within 2 frames. Dump frames to PNG and count pixels with Pillow.

Read the contact sheet, the first and last frames, and the end card full size.

## Credit

The method came from Sunwood AI Labs' hyperframes-motion-reel-skill
(github.com/Sunwood-ai-labs/hyperframes-motion-reel-skill), released under the MIT licence, Copyright (c) 2026
Sunwood AI Labs. We kept its idea of a beat grid that every cut is written against, every frame a pure function of
time, and sound generated from the same beat table, and replaced its GSAP layer with a frame-by-frame build in
Python. Rendered with HyperFrames by HeyGen. The 95:5 rule is John Dawes' work at the Ehrenberg-Bass Institute.
Fonts: Space Grotesk and JetBrains Mono, both under the SIL Open Font Licence.
