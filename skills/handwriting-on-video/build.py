"""Handwriting drawn on the wall beside someone as they talk. This writes index.html: the writing alone, white on
black, every letter wiped on in turn and every line and arrow drawn as a stroke. compose.sh lays it on the film with
a screen blend, so the black is clear.

    python build.py [font] [size]      then  ./compose.sh <film.mp4> <name>

NOTES holds what is written and the second each note starts, read off the film's word times. The words written are
the speaker's own spoken words, landing as they say them. The values below are our worked example: the last six
seconds of a course video. Fonts go beside this file as .ttf (./fonts.sh fetches Reenie Beanie)."""
import sys, html, os
here = os.path.dirname(os.path.abspath(__file__))
FONT = sys.argv[1] if len(sys.argv) > 1 else "ReenieBeanie"
SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 92
FPS, DUR = 24, 7
T0 = 66.6                      # the film second this clip starts on (compose.sh takes the same number)
PER = 0.05                     # seconds a letter
# x, y of the line's left end on a 1920 x 1080 frame, the film second it starts, the words
NOTES = [
    (1085, 150, 67.40, "Work your way through it"),
    (1085, 300, 69.40, "questions?"),
    (1560, 300, 70.30, "find me"),
    (1085, 450, 71.60, "practice"),
]
# strokes: the film second it starts, how long it takes, the path. An arrow from "questions?" to "find me", and two lines under "practice".
STROKES = [
    (69.95, 0.30, "M 1400 338 C 1440 330, 1490 344, 1528 336"),
    (70.22, 0.10, "M 1502 316 L 1530 336 L 1500 356"),
    (72.02, 0.22, "M 1082 536 C 1150 528, 1250 540, 1330 530"),
    (72.27, 0.20, "M 1092 554 C 1160 548, 1240 558, 1322 549"),
]
spans = ''
for x, y, t, words in NOTES:
    s = ''.join('<b></b>' if ch == ' ' else f'<i style="animation-delay:{t - T0 + k * PER:.3f}s">{html.escape(ch)}</i>' for k, ch in enumerate(words))
    spans += f'  <div class="note" style="left:{x}px;top:{y}px">{s}</div>\n'
paths = ''.join(f'    <path pathLength="1" d="{d}" style="animation-duration:{dur}s;animation-delay:{t - T0:.3f}s"/>\n' for t, dur, d in STROKES)
page = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<title>Handwriting on video</title>
<!-- Written by build.py. Do not edit by hand. White on black: compose.sh screens it over the film. -->
<style>
@font-face {{ font-family: "Hand"; src: url("{FONT}.ttf"); }}
html, body {{ margin: 0; width: 1920px; height: 1080px; background: #000; }}
#root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
.note {{ position: absolute; font: 400 {SIZE}px/1 "Hand"; color: #fff; white-space: nowrap; transform: rotate(-1.5deg); transform-origin: left center; }}
.note b {{ display: inline-block; width: .3em; }}
.note i {{ display: inline-block; font-style: normal; animation: wr {PER * 1.8:.3f}s linear both; }}
svg {{ position: absolute; left: 0; top: 0; }}
path {{ fill: none; stroke: #fff; stroke-width: 5.5; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 1; animation: dr linear both; }}
@keyframes wr {{ from {{ opacity: 0; clip-path: inset(-40% 110% -40% -40%); }} 1% {{ opacity: 1; }} to {{ clip-path: inset(-40% -40% -40% -40%); }} }}
@keyframes dr {{ from {{ stroke-dashoffset: 1; }} to {{ stroke-dashoffset: 0; }} }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-no-timeline data-start="0" data-width="1920" data-height="1080" data-duration="{DUR}" data-fps="{FPS}">
{spans}  <svg width="1920" height="1080" viewBox="0 0 1920 1080">
{paths}  </svg>
</div>
</body></html>
'''
open(os.path.join(here, 'index.html'), 'w').write(page)
print("written", FONT, SIZE)
