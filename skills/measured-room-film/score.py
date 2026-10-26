"""The film's sound, made in code from the same frame numbers as the picture. Each hit lands one frame after its picture.
Writes score.wav (48 kHz stereo, 30 s). Usage: python3 score.py"""
import numpy as np, wave, os
SR, FPS, DUR = 48000, 30, 30.0
N = int(SR * DUR); t = np.arange(N) / SR
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)
def at(frame): return int((frame + 1) / FPS * SR)          # one frame after the picture
def add(sig, start, pan=0.0, gain=1.0):
    s = at(start); e = min(N, s + len(sig)); sig = sig[: e - s] * gain
    mix[s:e, 0] += sig * (1 - pan) ; mix[s:e, 1] += sig * (1 + pan)
def env(n, a=0.005, r=0.4):
    x = np.arange(n) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
def tone(freq, secs, r=0.6, harm=(1, 0.35, 0.12)):
    n = int(secs * SR); x = np.arange(n) / SR
    return sum(h * np.sin(2 * np.pi * freq * (k + 1) * x) for k, h in enumerate(harm)) * env(n, 0.004, r)
def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y
def noise_swell(secs, up=True):
    n = int(secs * SR); nz = rng.standard_normal(n); x = np.linspace(0, 1, n)
    shape = (x ** 2.2) if up else (1 - x) ** 2
    return lowpass(nz, 0.06) * shape
def thud(secs=0.5, f0=70):
    n = int(secs * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * (f0 + 60 * np.exp(-x * 30)) * x) * np.exp(-x * 9)

# a warm pad under everything: A, E, C# (A major), soft, slowly swelling
pad = sum(np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.11 * t * (i + 1))) for i, f in enumerate((110, 164.8, 277.2, 220)))
pad *= np.minimum(1, t / 2.5) * np.minimum(1, (DUR - t) / 1.5) * 0.05
mix[:, 0] += pad; mix[:, 1] += pad
# walls rise (frames 14-54): a soft swell, then a tick as the dimension lines finish (64)
add(noise_swell(1.4), 12, gain=0.25)
add(tone(1760, 0.25, 0.08, (1, 0.2)), 64, gain=0.18)
# each piece lands: a thud and a rising note
for fr, note, pan in ((132, 440, -0.3), (156, 494, 0.3), (178, 554, -0.2), (200, 659, 0.2), (218, 740, 0)):
    add(thud(), fr, pan, 0.55); add(tone(note, 0.9, 0.35), fr, pan, 0.22)
# the light line: a riser into the lit room, then the lights-on hit at the cut (330)
add(noise_swell(2.0), 270, gain=0.35)
add(thud(1.2, 45), 330, gain=0.9)
for f in (220, 277.2, 330, 440): add(tone(f, 2.4, 1.1), 330, gain=0.14)
# the hero glide: a slow heartbeat pulse at 100 bpm under it (frames 330-689)
for k in range(0, 18):
    fr = 330 + k * 18
    if fr < 690: add(thud(0.35, 55), fr, gain=0.32)
# the close-up: two clicks of balls touching
for fr, pan in ((600, -0.2), (612, 0.2)):
    add(tone(2400, 0.06, 0.02, (1, 0.5, 0.3)) + rng.standard_normal(int(0.06 * SR)) * 0.2 * env(int(0.06 * SR), 0.001, 0.01), fr, pan, 0.35)
# render to photo: a whoosh with the wipe (728-768), a chime as the photo lands
add(noise_swell(1.3), 728, gain=0.3); add(tone(880, 1.6, 0.8), 770, gain=0.2); add(tone(1318.5, 1.6, 0.8), 772, gain=0.12)
# the end: a resolving chord under the title (838)
for f in (110, 220, 277.2, 330, 440, 554.4): add(tone(f, 2.2, 1.2), 838, gain=0.12)
mix = np.tanh(mix * 1.2) * 0.8
out = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("score.wav", DUR, "s")
