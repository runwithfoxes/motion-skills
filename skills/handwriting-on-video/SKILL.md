---
name: handwriting-on-video
description: White pen writing, arrows and underlines drawn on the wall beside someone as they talk to camera, each word landing as they say it. The look of Hector Serrano's videos and the titles in The Gentlemen. Drawn in code and laid on the film, no AI and no cost. Use when someone asks for handwriting on a video, words written on screen as they speak, notes drawn on a talking head, or annotations on the wall.
---

# Handwriting on video

Someone talks to camera, and as they say the words that matter, those words write themselves on the wall beside
them in white pen, letter by letter, with an arrow or an underline drawn in as they make a point.

Read `motion-by-numbers` first for the render set-up.

## How it works

`build.py` writes a web page with the writing alone, white on black. Each letter is wiped on from left to right, one
after another, 0.05 seconds a letter, which reads as a pen writing. Arrows and underlines are real strokes drawn along
their path. `compose.sh` renders the page with HyperFrames at the film's frame rate and lays it on the film with a
screen blend, so the black disappears, with a slight blur so the writing sits on the wall rather than floating over
it.

    ./fonts.sh                                    (once: fetches the handwriting font)
    python build.py ReenieBeanie 100
    ./compose.sh film.mp4 my-take 66.6 6.16       (the second the clip starts on, and its length)

## What to set in build.py

`NOTES` is where each line starts on a 1920 x 1080 frame, the film second it starts on, and the words. `STROKES` are
the arrows and underlines, each a start second, a length in seconds and an SVG path. `T0` is the film second the clip
starts on; `compose.sh` takes the same number.

Take the times from a transcript with word timings of the film (Whisper gives you one). The words written are the
speaker's own spoken words, landing as they say them. Never write something they didn't say.

## Rules

Before a letter is written it is fully hidden, opacity 0. Otherwise bits of ink that hang outside a letter's box show
as specks before the pen gets there.

Word spaces are fixed-width gaps.

Measure where an arrow starts off a still of the rendered writing, because each font sets a different width.

Use the clean take of the film, never one with titles or cards already on it, and pick a take with empty wall beside
the speaker. The writing needs somewhere to go.

Read every frame.

## Colour

White is the colour that works. A screen blend only works cleanly for white: it lightens any colour towards the wall,
so an orange comes out peach. For a true colour, use the writing as a mask over a flat colour and lay that on top:

    [1:v]gblur=sigma=1.1,format=gray[m];[2:v][m]alphamerge[o];[f][o]overlay

with `color=c=0xF47521` (your colour) as the third input.

## The hand

Reenie Beanie, a thin pen. It is free under the SIL Open Font Licence. Any handwriting font works; it is one word in
the build command. We also tried Caveat, Covered By Your Grace, Just Another Hand, Nothing You Could Do and Rock Salt.

## Credit

Inspired by Hector Serrano's videos, where he writes on screen as he talks, and by the hand-drawn titles in Guy
Ritchie's The Gentlemen series on Netflix (theirs are yellow). Rendered with HyperFrames by HeyGen, laid on the film
with ffmpeg. Font: Reenie Beanie by James Grieshaber, SIL Open Font Licence.
