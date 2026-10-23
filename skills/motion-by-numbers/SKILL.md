---
name: motion-by-numbers
description: The working method for any short film drawn in code, a chart that builds, a number that counts, a diagram that moves. Brief in eight lines with numbers instead of adjectives, every frame a pure function of time, easing and springs as values, fixes named by frame number, sound made in code from the same timings. Rendered with HyperFrames. Use before building any motion graphic, animated chart, or code-drawn video, and when someone says an animation "feels off" and wants it fixed.
---

# Motion by numbers

A film drawn in code is a web page whose every animation can be set to any moment in time. An engine opens it in a
headless browser, steps through it one frame at a time, and ffmpeg joins the frames. No video model, no key, no
cost, and the same file comes out every time, so a brand colour or a number on a chart cannot drift.

The method is simple to say. Every adjective left in a brief is a decision handed to the default look, so replace
each one with a number. Then judge the film by its frames, and fix it by frame number.

## 1. The brief, in eight lines, before any code

    GOAL: what the viewer should feel or do, in one sentence
    OUTPUT: one page, the engine and its version, W x H
    TIME: seconds x fps = total frames. Loop: yes or no
    LOOK: palette in hex, one accent, typeface + weight + size + tracking
    MOTION: easing as cubic-bezier, springs as damping ratio, durations in frames
    SHOTS: frame ranges, one hero move per shot, how each shot hands off
    BANNED: the defaults never to be seen, by name
    QA: stills at named frames, a contact sheet, fix, then the full render

For a character add WHAT MAY NOT CHANGE (proportions, colours, the face). For 3D add MODEL and CAMERA.

The SHOTS line becomes a list where every beat has a start state, an end state and a reason: what the viewer knows
after it that they did not know before. A beat with no reason is cut before anything is built. "Zoom in, then morph"
is a list of moves, not a shot list.

If the job comes with a reference (a film, a frame, past work), write `reference.md` before the brief is settled. It
records what the reference does: palette as hex, type as family, width, weight and size, where the eye goes first,
pacing as the average seconds between real changes, motion as snap, glide, overshoot, cut or hold, and texture. It
ends with a DO NOT COPY list: the reference's subjects, logos, words and product pictures. Take the way it works,
never the things in it.

If the brief needs a real logo, screen, product picture or number and you don't have the file, stop and ask for it.
Never draw a convincing stand-in.

## 2. The render rule

Every frame is a pure function of time. No clock, no timers, no unseeded random, no fetching, no CSS transitions, no
`requestAnimationFrame`. Use CSS keyframes with `animation-fill-mode: both` and a fixed length, or the Web Animations
API with fill "both". A loop renders frames 0 to N-1 and is driven from phase = frame / N in whole cycles, with frame
0 a finished picture. Fonts and scripts are local files beside the page, pinned to a version.

The safest way we have found: work every value out in Python for every frame and write it into the page as stepped
CSS keyframes, one step per frame where a value changes. Then the engine only has to seek. Place each step half a
frame early, `(f - 0.5) / N`: a step placed exactly on a frame's time is sometimes missed when the engine seeks
there, and the frame before shows twice. The `beat-reel` skill's `build.py` does all of this and is the template.

A number that counts up: register it with `@property --n { syntax: "<integer>"; inherits: true }`, animate `--n`, and
print it with `counter-reset: n var(--n)` on a `::before`. With `inherits: false` the `::before` reads 0 for the
whole film.

## 3. The numbers

Easing. Enter with ease-out (expo 0.16, 1, 0.3, 1; quint 0.22, 1, 0.36, 1). Move with ease-in-out (quart 0.76, 0,
0.24, 1). Exit with ease-in (expo 0.7, 0, 0.84, 0), and make exits 40 to 50 percent shorter than entrances. A pop is
back 0.34, 1.56, 0.64, 1. Linear only for rotation, progress and loop phase.

Springs, by damping ratio: 1.0 no bounce, 0.7 to 0.85 premium, 0.4 to 0.6 playful, under 0.3 a cartoon. Position and
size may bounce; opacity and colour never. As a pure function of time, so any frame renders on its own (zeta the
ratio, f in Hz):

    w = 2*pi*f
    zeta >= 1:  1 - exp(-w*t) * (1 + w*t)
    zeta < 1:   wd = w*sqrt(1 - zeta^2);  1 - exp(-zeta*w*t) * (cos(wd*t) + (zeta*w/wd)*sin(wd*t))

A spring takes about 3 frames to look full. Start it 3 frames before the moment it should land, or it lands late.

Durations. Feedback 100 to 200 ms, moves 200 to 500, hero reveals 600 to 900. Letters 1 frame apart, words 60 to 120
ms, list items 40 to 80. Start the next thing when the last is 30 to 50 percent done.

Rank. One hero move at a time. Secondary moves travel 50 to 70 percent as far and start 100 to 200 ms later. Ambient
motion stays under 5 percent of the hero's travel, on a slow sine.

Holds. Text stays 0.3 seconds a word plus 0.5. A 2 percent push keeps a hold alive.

Beat grid. Frames per beat = fps x 60 / BPM. Work each beat out from time and round it; never add up rounded counts.

A character drawn in code: anticipation as a crouch (11 frames, 1.2 wide by 0.75 tall), stretch at take-off (0.85 by
1.28), squash on landing (1.25 by 0.7), spring back at 0.55, limbs lag by frames (arms 4, legs 6), follow-through as a
looser spring (2.2 Hz at 0.22), paths as arcs. Push key poses 10 to 30 percent further than feels right for a phone
screen.

The camera gets the softest curves and never parks. Text keeps 4.5 to 1 contrast on every frame.

## 4. Look, then fix by frame number

Render stills around every hit before the full render. Notes name a frame: "frame 84 peaks late". When a fix does not
hold, render the frames either side and list the differences. When timing is in doubt, two more views: an onion skin
of a move (spacing should tighten near the key poses) and a plot of position per frame (a straight line is linear
motion).

Translate a feeling into a number before acting on it. "Pop" is scale 1.0 to 1.08 to 1.0 over 6 frames. "It drags"
is each hold cut by a beat. "Busy" is one hero at a time.

After the first full render, find the three worst faults, no more. Each gets the frame it happens on, the proof (the
still, the crop or the measured number) and a fix limited to that spot. Fix those three, re-render only the frames
they touch, look at those frames, and go again. Three at a time stops a long list of small notes turning into a
rebuild.

## 5. Check the numbers on the real frames

Read the rendered frames and check them against the brief: a landing on its frame, a label lit on its frame, nothing
outside the frame. Dump frames to PNG and measure them with Pillow; ffmpeg from Homebrew has no text filter and no
need for one. A passing check proves the film matches its numbers. It does not prove the numbers make a good move,
so look at every frame of every move yourself, at a size you can read.

## 6. Keep a ban list

After each first render, name what came back that you didn't want, and add it. Start from: purple or blue gradients,
glow, lens flares, particles as decoration, everything fading in at once, fade and slide up on every element,
everything centred, text that moves while it is being read.

## 7. Sound last, in code

Generate it from the same timings as the picture, with no samples, so the two cannot drift. Each hit lands one frame
after its picture, never before. About -14 LUFS, peak -1 dBTP, hits 3 to 6 dB over the bed, and nothing that only
lives under 60 Hz, because phones play nothing there. Check it by decoding the finished file and measuring, never by
ear. The picture must work muted.

## 8. Every format is its own composition

16:9, 9:16 and 1:1 are separate compositions from one timeline, never a crop of the wide film. The vertical one
usually needs bigger type, fewer things on screen and a tighter story. Look at each format's own contact sheet.

The first frame is the thumbnail and the last frame has to work as a poster. Look at both full size. A chart film put
on a page plays once and stops on the finished chart, so the reader can study it.

## 9. Keep the receipts

Save the first prompt and every follow-up beside the film, and count the rounds.

## The engine

We render with HyperFrames, HeyGen's open source engine (Apache 2.0, version 0.8.143 when we wrote this). Install it
in your project folder, not globally:

    npm i hyperframes@0.8.143 --ignore-scripts

The page's root element needs `data-composition-id`, `data-width`, `data-height`, `data-duration`, and
`data-no-timeline` if it uses CSS keyframes. Render through `render.sh` here, which turns off the engine's usage
reporting and update checks, lints the page, renders to the next free version number (it never overwrites a render
someone may already have), and cuts a contact sheet, the first frame and the last frame. Don't run `hyperframes
init`: it installs its own skills into your Claude setup.

    ./render.sh my-film

## Credit

The eight-line brief, the render rule, the easing, spring and duration numbers, fixing by frame number, the ban
list, sound in code and keeping the receipts came from Florence's (@flxrnc) X article on motion design with Claude,
which publishes every prompt and follow-up behind each animation. The reference file, the start-end-reason shot
list, the three-worst-faults critic, the separate compositions per format, the last frame as poster and the stop on a
missing asset came from rari's (@0xwhrrari) "Motion Engineering" article. The stepped keyframes worked out in Python
and placed half a frame early, the counter fix, the spring started 3 frames early and the chart film that plays once
are ours, learned making our own films. Rendered with HyperFrames
by HeyGen.
