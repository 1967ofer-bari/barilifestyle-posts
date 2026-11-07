"""Original ambient background music, generated from scratch (no third-party audio, no rights issues).
Usage: python3 music.py OUT.wav SECONDS VARIANT(0-2)"""
import sys, numpy as np, wave

SR = 44100
out, dur, var = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
n = int(SR * dur); t = np.arange(n) / SR

def hz(m): return 440 * 2 ** ((m - 69) / 12)
PROGS = [  # (chord midi notes), one chord per bar
    [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],   # Am F C G
    [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]],   # C G Am F
    [[50, 53, 57], [55, 59, 62], [48, 52, 55], [57, 60, 64]],   # Dm G C Am
]
prog = PROGS[var % 3]
bpm = [72, 76, 70][var % 3]
beat = 60 / bpm; bar = beat * 4

def env(x, a, r, length):
    e = np.clip(x / a, 0, 1) * np.clip((length - x) / r, 0, 1)
    return e

mix = np.zeros(n)
nbars = int(np.ceil(dur / bar)) + 1
for b in range(nbars):
    ch = prog[b % 4]; s0 = int(b * bar * SR); L = int(bar * 1.15 * SR)
    seg = slice(s0, min(n, s0 + L)); x = t[seg] - b * bar
    if x.size == 0: break
    e = env(x, 0.9, 0.9, bar * 1.15)
    for m in ch:  # warm pad: detuned sines + soft 2nd harmonic
        for d in (-0.15, 0.15):
            f = hz(m) * 2 ** (d / 12)
            mix[seg] += 0.05 * e * (np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x))
    bf = hz(ch[0] - 12)  # bass
    mix[seg] += 0.09 * e * np.sin(2 * np.pi * bf * x)
    # gentle plucked arpeggio
    pattern = [0, 1, 2, 1, 2, 0, 1, 2]
    for k, idx in enumerate(pattern):
        st = b * bar + k * beat / 2
        if st >= dur: break
        i0 = int(st * SR); i1 = min(n, i0 + int(1.6 * SR)); xx = t[i0:i1] - st
        f = hz(ch[idx] + 12)
        pl = np.exp(-xx * 3.2) * (np.sin(2 * np.pi * f * xx) + 0.3 * np.sin(4 * np.pi * f * xx) + 0.1 * np.sin(6 * np.pi * f * xx))
        mix[i0:i1] += 0.06 * np.minimum(1, xx / 0.005) * pl

# simple stereo delay "space"
L = mix.copy(); R = mix.copy()
for dly, g in ((0.23, 0.35), (0.41, 0.22), (0.67, 0.12)):
    k = int(dly * SR)
    L[k:] += g * mix[:-k]; R[int(k * 1.13):] += g * mix[:-int(k * 1.13)]
st = np.stack([L, R], 1)
fade = np.minimum(1, np.minimum(t / 1.0, (dur - t) / 1.5))[:, None]
st *= fade
st = st / np.max(np.abs(st)) * 0.8
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("ok", out)
