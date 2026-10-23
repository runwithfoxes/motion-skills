"""Beat reel, worked example: the 95:5 rule in 15 seconds. Writes index.html and score.wav from one beat table.

Every frame is worked out here as a pure function of time and written into CSS keyframes, one step a
frame (a keyframe only where a value changes), so HyperFrames can seek to any frame. The sound is made
from the same beat table, so picture and sound cannot drift. Each hit sounds one frame after its picture.

    python build.py      then   ../motion-by-numbers/render.sh .      then   ./mix.sh

To make your own, keep everything below the shots and change the shots, the captions and the drawing.
Fonts: run ./fonts.sh once to copy Space Grotesk and JetBrains Mono (both SIL Open Font Licence) in beside the page.
"""
import math, random, struct, wave, pathlib

HERE = pathlib.Path(__file__).resolve().parent
FPS, BPM, BEATS = 30, 120, 30
SPB = 60 / BPM                      # seconds a beat
DUR = BEATS * SPB                   # 15 s
N = int(DUR * FPS)                  # 450 frames
b = lambda n: n * SPB               # beat number to seconds: every cut below is written as b(...)

GROUND, WHITE, SKY = (26, 58, 78), (250, 250, 248), (108, 170, 200)

# ---- shots (beats), the brief's SHOTS line --------------------------------------------------------
T_LIGHT, T_FIVE, T_ROLL, T_QUARTERS, T_LAST, T_LOGO = b(4.5), b(6.5), b(11), b(16), b(23), b(24)
Q_TIMES = [b(16), b(17.5), b(19), b(20.5)]
CAPTIONS = [  # from Paul Dervan's essay "The 95:5 rule: the Day One list"
    ("Everyone who could buy from you.", None, b(6)),
    ("Only a small share are in a position to buy.", b(6.5), b(11)),
    ("The rest have no immediate need today.", b(11.5), b(16)),
    ("A different small group each quarter.", b(16), b(23)),
    ("Get your place on the list before they need you.", b(23), None),
]

# ---- the field of 100 -----------------------------------------------------------------------------
DOT, GAP = 32, 18
GX, GY = 1080 - 84 - (DOT * 10 + GAP * 9), 440
rng = random.Random(95)
def pick(avoid):
    s = set()
    while len(s) < 5:
        i = rng.randrange(100)
        if i not in avoid and all(abs(i // 10 - j // 10) + abs(i % 10 - j % 10) > 1 for j in s):
            s.add(i)
    return sorted(s)
SETS = [pick(set())]
for _ in range(3):
    SETS.append(pick(set(SETS[-1])))
# lit events per dot: (time, 1 on / 0 off). Q1 keeps the first five.
LIT = {i: [] for i in range(100)}
LIGHTS = [b(4.5 + 0.5 * k) for k in range(5)]      # the five light one per half beat, the fifth with the 5%
for i, tl in zip(SETS[0], LIGHTS): LIT[i].append((tl - 3 / FPS, 1))   # the spring takes 3 frames to fill
PULSES = [b(n) for n in (7, 8, 9, 10, 12, 13, 14, 15)]  # the five pulse on the beat through the two holds; the 95 sit still
for k in range(1, 4):
    for i in SETS[k - 1]: LIT[i].append((Q_TIMES[k], 0))
    for i in SETS[k]: LIT[i].append((Q_TIMES[k], 1))

# ---- motion helpers (the README's numbers) --------------------------------------------------------
def spring(t, zeta, hz):
    if t <= 0: return 0.0
    w = 2 * math.pi * hz
    if zeta >= 1: return 1 - math.exp(-w * t) * (1 + w * t)
    wd = w * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * w * t) * (math.cos(wd * t) + zeta * w / wd * math.sin(wd * t))
def clamp(x, a=0.0, c=1.0): return max(a, min(c, x))
def bez(x1, y1, x2, y2):
    def f(u):
        u = clamp(u); lo, hi = 0.0, 1.0
        for _ in range(40):
            m = (lo + hi) / 2
            x = 3 * (1 - m) ** 2 * m * x1 + 3 * (1 - m) * m * m * x2 + m ** 3
            lo, hi = (m, hi) if x < u else (lo, m)
        m = (lo + hi) / 2
        return 3 * (1 - m) ** 2 * m * y1 + 3 * (1 - m) * m * m * y2 + m ** 3
    return f
EASE_IN_EXPO_OUT, EASE_IN = bez(0.16, 1, 0.3, 1), bez(0.7, 0, 0.84, 0)
def mix(a, c, u): return tuple(round(a[k] + (c[k] - a[k]) * u) for k in range(3))

def enter_exit(t, tin, tout, lin=12 / FPS, lout=6 / FPS):
    """(opacity, y offset px, clip 0..1 shown) for a line that arrives and leaves."""
    if tin is None: a = 1.0
    else: a = EASE_IN_EXPO_OUT((t - tin) / lin) if t >= tin else 0.0
    if tout is not None and t >= tout:
        e = EASE_IN((t - tout) / lout)
        return (1 - e, -18 * e, 1.0)
    return (1.0 if a > 0 else 0.0, 28 * (1 - a), a)

# ---- per-frame values -----------------------------------------------------------------------------
def dot(i, t):
    r, c = divmod(i, 10)
    t0 = r * (SPB / 2) - 4.5 / FPS + (c - 4.5) / FPS / 2  # a row lands on each beat and off-beat, half a frame between dots
    appear = max(0.0, spring(t - t0, 0.55, 3.0))
    lit = 0.0
    for te, v in LIT[i]:
        lit += (1 if v else -1) * spring(t - te, 0.7, 5.0)
    lit = clamp(lit)
    d = math.hypot(r - 4.5, c - 4.5)                      # the wave runs out from the middle at b11
    wave = math.exp(-(((t - (T_ROLL + d * 0.035)) / 0.09) ** 2))
    hold = clamp((t - T_ROLL - 0.2) / 0.3) * (1 - clamp((t - T_QUARTERS) / 0.2))
    alpha = 0.16 + 0.55 * wave + 0.14 * hold
    grey = mix(GROUND, WHITE, alpha)
    col = mix(grey, SKY, lit)
    beat = sum(math.exp(-(t - p) * 9) for p in PULSES if t >= p) * lit
    s = appear * (1 + 0.28 * lit + 0.3 * wave * (1 - lit) + 0.32 * beat)
    return "transform:scale(%.3f);background:rgb(%d,%d,%d);" % (s, *col)

def number(t):
    if t < T_FIVE or t >= T_QUARTERS + 6 / FPS: return "opacity:0;"
    a = spring(t - T_FIVE, 0.55, 2.4)
    s = 1.22 - 0.22 * a
    o = clamp((t - T_FIVE) * FPS / 3)
    y = 0.0
    if t >= T_QUARTERS:
        e = EASE_IN((t - T_QUARTERS) * FPS / 6); o *= 1 - e; y = -18 * e
    n = 5 if t < T_ROLL else min(95, round(5 + 90 * (t - T_ROLL) / SPB))
    col = SKY if t < T_ROLL else WHITE
    return "opacity:%.3f;transform:translateY(%.1fpx) scale(%.4f);--n:%d;color:rgb(%d,%d,%d);" % (o, y, s, n, *col)

def caption(k, t):
    _, tin, tout = CAPTIONS[k]
    if tin is not None and t < tin: return "opacity:0;"
    o, y, c = enter_exit(t, tin, tout)
    return "opacity:%.3f;transform:translateY(%.1fpx);clip-path:inset(0 0 %.1f%% 0);" % (o, y, 100 * (1 - c))

def quarter(k, t):
    tin = Q_TIMES[k]; tout = Q_TIMES[k + 1] if k < 3 else T_LAST
    if t < tin: return "opacity:0;"
    o, y, c = enter_exit(t, tin, tout, lin=8 / FPS, lout=4 / FPS)
    return "opacity:%.3f;transform:translateY(%.1fpx);clip-path:inset(0 0 %.1f%% 0);" % (o, y, 100 * (1 - c))

def grid(t):
    push = 1 + 0.02 * clamp((t - T_QUARTERS) / (T_LAST - T_QUARTERS))
    return "transform:scale(%.4f);" % push

def late(tin):
    def f(t):
        a = EASE_IN_EXPO_OUT((t - tin) * FPS / 10) if t >= tin else 0.0
        return "opacity:%.3f;transform:translateY(%.1fpx);" % (a, 16 * (1 - a))
    return f

# ---- page -----------------------------------------------------------------------------------------
def keyframes(name, fn):
    rows, last = [], None
    for f in range(N):
        v = fn(f / FPS)
        if v != last:
            # half a frame early: placed exactly on a frame's time, a step is sometimes missed when the engine seeks
            # there and the frame before shows twice.
            rows.append("%.4f%% { %s }" % (100 * max(0, f - 0.5) / N, v)); last = v
    return "@keyframes %s { %s }\n" % (name, " ".join(rows))

def page():
    css, html = [], []
    for i in range(100):
        r, c = divmod(i, 10)
        css.append(keyframes("d%d" % i, lambda t, i=i: dot(i, t)))
        html.append('<i class="dot" style="left:%dpx;top:%dpx;animation-name:d%d"></i>' % (c * (DOT + GAP), r * (DOT + GAP), i))
    css.append(keyframes("grid", grid)); css.append(keyframes("num", number));
    css.append(keyframes("logo", late(T_LOGO))); css.append(keyframes("src", late(T_LOGO + SPB / 2)))
    caps = []
    for k, (words, _, _) in enumerate(CAPTIONS):
        css.append(keyframes("c%d" % k, lambda t, k=k: caption(k, t)))
        caps.append('<p class="cap" style="animation-name:c%d">%s</p>' % (k, words))
    qs = []
    for k in range(4):
        css.append(keyframes("q%d" % k, lambda t, k=k: quarter(k, t)))
        qs.append('<div class="q" style="animation-name:q%d">Q%d</div>' % (k, k + 1))
    W = DOT * 10 + GAP * 9
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1080" />
<title>95:5 reel</title>
<!-- Written by build.py. Do not edit by hand: change a number at the top of build.py and run it again. -->
<style>
@font-face {{ font-family: "Space Grotesk"; font-weight: 500; src: url(space-grotesk-latin-500-normal.woff2) format("woff2"); }}
@font-face {{ font-family: "JetBrains Mono"; font-weight: 400; src: url(jetbrains-mono-latin-400-normal.woff2) format("woff2"); }}
@font-face {{ font-family: "JetBrains Mono"; font-weight: 500; src: url(jetbrains-mono-latin-500-normal.woff2) format("woff2"); }}
@property --n {{ syntax: "<integer>"; inherits: true; initial-value: 5; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 1080px; height: 1080px; background: #1A3A4E; }}
#root {{ position: relative; width: 1080px; height: 1080px; overflow: hidden; background: #1A3A4E; color: #FAFAF8; font-family: "Space Grotesk", sans-serif; }}
#root * {{ animation-duration: {DUR}s; animation-timing-function: step-end; animation-fill-mode: both; animation-delay: 0s; }}
.cap {{ position: absolute; left: 84px; top: 84px; width: 900px; margin: 0; font-weight: 500; font-size: 62px; line-height: 1.1; letter-spacing: -.02em; padding-bottom: 14px; }}
#grid {{ position: absolute; left: {GX}px; top: {GY}px; width: {W}px; height: {W}px; transform-origin: 50% 50%; animation-name: grid; }}
.dot {{ position: absolute; width: {DOT}px; height: {DOT}px; border-radius: 50%; }}
#num {{ position: absolute; left: 84px; top: 470px; font-weight: 500; font-size: 200px; line-height: 1; letter-spacing: -.045em; font-variant-numeric: tabular-nums; transform-origin: 0 100%; animation-name: num; }}
#num::before {{ counter-reset: n var(--n); content: counter(n) "%"; }}
.q {{ position: absolute; left: 84px; top: 470px; font: 500 200px/1 "JetBrains Mono", monospace; letter-spacing: -.06em; color: #6CAAC8; }}
.logo {{ position: absolute; right: 80px; bottom: 74px; font: 400 26px/1 "JetBrains Mono", monospace; letter-spacing: 4px; color: #FAFAF8; white-space: nowrap; animation-name: logo; }}
.src {{ position: absolute; left: 84px; top: 262px; font: 400 20px/1.3 "JetBrains Mono", monospace; letter-spacing: .04em; color: rgba(250,250,248,.62); animation-name: src; }}
{''.join(css)}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-no-timeline data-start="0" data-width="1080" data-height="1080" data-duration="{DUR:g}" data-fps="{FPS}">
{''.join(caps)}
<div id="grid">{''.join(html)}</div>
<div id="num"></div>
{''.join(qs)}
<div class="src">95:5, John Dawes, Ehrenberg-Bass Institute</div>
<div class="logo">/Runwithfoxes</div>
</div>
</body>
</html>
"""

# ---- sound, from the same beat table --------------------------------------------------------------
SR = 44100
def score():
    out = [0.0] * int(SR * (DUR + 1.5))
    rnd = random.Random(5)
    noise = [rnd.uniform(-1, 1) for _ in range(SR)]
    LAG = 1 / FPS                                          # every hit one frame after its picture
    def add(t0, fn, length, gain):
        s0 = int((t0 + LAG) * SR)
        for k in range(int(length * SR)):
            if 0 <= s0 + k < len(out): out[s0 + k] += gain * fn(k / SR, k)
    kick = lambda x, k: math.sin(2 * math.pi * (70 * x + 90 * (1 - math.exp(-x * 28)) / 28)) * math.exp(-x * 11) + 0.25 * noise[k % SR] * math.exp(-x * 120)
    def hat(x, k):
        n = noise[(k * 7) % SR] - noise[(k * 7 + 1) % SR]
        return n * math.exp(-x * 75)
    pop = lambda x, k: math.sin(2 * math.pi * (900 * x + 900 * x * x * 4)) * math.exp(-x * 30)
    tick = lambda f: (lambda x, k: math.sin(2 * math.pi * f * x) * math.exp(-x * 180))
    def rise(x, k, L=SPB):
        return noise[k % SR] * (x / L) ** 2 * (1 - math.exp(-(L - x) * 60))
    chime = lambda x, k: sum(math.sin(2 * math.pi * f * x) / (j + 1) for j, f in enumerate((660, 990, 1320))) * math.exp(-x * 2.6) * min(1, x * 200)
    for n in range(0, 24):                                  # the bed: a soft kick on the beat, hats on the off-beats
        add(b(n), kick, 0.35, 0.35)
        add(b(n + 0.5), hat, 0.08, 0.16)
        add(b(n), hat, 0.05, 0.07)
    for t in (T_LIGHT, T_ROLL, T_QUARTERS, T_LAST):          # the hits
        add(t, kick, 0.45, 0.9)
    add(T_FIVE, kick, 0.4, 0.6); add(T_FIVE, lambda x, k: noise[k % SR] * math.exp(-x * 18), 0.3, 0.35)
    add(T_LIGHT - SPB, rise, SPB, 0.22); add(T_ROLL - SPB, rise, SPB, 0.22); add(T_LAST - SPB, rise, SPB, 0.18)
    for i in range(15):                                     # the count from 5 to 95
        add(T_ROLL + i * 2 / FPS, tick(1400 + 60 * i), 0.03, 0.22)
    for t in Q_TIMES:
        add(t, pop, 0.12, 0.3)
    for t in LIGHTS:
        add(t, pop, 0.12, 0.26)
    for t in PULSES:
        add(t, pop, 0.08, 0.12)
    add(T_LOGO, chime, 1.6, 0.22)
    peak = max(abs(v) for v in out) or 1
    with wave.open(str(HERE / "score.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(32767 * 0.9 * v / peak)) for v in out))

if __name__ == "__main__":
    (HERE / "index.html").write_text(page())
    score()
    print("index.html + score.wav;", N, "frames; sets", SETS)
