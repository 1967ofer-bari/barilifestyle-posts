"""Original background music for BariLifestyle posts, synthesised from scratch.
No samples, no third-party audio: every note is generated here, so there are no rights issues.

Every post gets its OWN track: the seed (default: derived from the output file name, e.g. the
post date) picks the key, chord progression, melody, rhythm and instrument mix, so no two posts
sound the same. The mood sets the character so the music fits the content.

Usage:  python3 music.py OUT.wav SECONDS [MOOD] [SEED]
MOOD:   calm       – slow, soft pad + piano; reflective tips, mindset, personal story
        warm       – gentle guitar-like plucks + piano; story, community, products/services
        uplifting  – brighter piano + light percussion; motivation, achievements, teasers
        energetic  – beat, bass and plucks; fitness, workouts, challenges
        (legacy: 0/1/2 map to calm/warm/uplifting)
SEED:   any integer or text; omitted = derived from OUT's file name
"""
import hashlib, sys, wave
import numpy as np
from scipy.signal import fftconvolve, butter, lfilter

SR = 44100
MOODS = {
    "calm":      dict(bpm=(64, 74),   bright=0.35, drums=0.0,  pluck=0.25, keys=0.8,  pad=1.0, bass=0.6),
    "warm":      dict(bpm=(76, 88),   bright=0.5,  drums=0.0,  pluck=0.9,  keys=0.6,  pad=0.6, bass=0.7),
    "uplifting": dict(bpm=(92, 104),  bright=0.75, drums=0.45, pluck=0.6,  keys=1.0,  pad=0.6, bass=0.8),
    "energetic": dict(bpm=(112, 124), bright=0.9,  drums=1.0,  pluck=0.8,  keys=0.5,  pad=0.4, bass=1.0),
}
LEGACY = {"0": "calm", "1": "warm", "2": "uplifting"}
# progressions as scale degrees (0-based, major scale), one chord per bar
PROGS = {
    "major": [[0, 4, 5, 3], [0, 5, 3, 4], [3, 0, 4, 5], [0, 3, 4, 3], [5, 3, 0, 4], [0, 4, 3, 4], [0, 2, 3, 4]],
    "minor": [[5, 3, 0, 4], [5, 1, 4, 0], [5, 4, 3, 4], [5, 3, 4, 4]],  # relative-minor flavoured
}
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=float)
    a = min(a, n); e[:a] = np.linspace(0, 1, a, endpoint=False)
    d2 = min(d, n - a); e[a:a + d2] = np.linspace(1, s, d2, endpoint=False)
    r = min(r, n); e[n - r:] *= np.linspace(1, 0, r)
    return e


def lowpass(x, cutoff):
    b, a = butter(2, min(cutoff, SR / 2 - 100) / (SR / 2), "low")
    return lfilter(b, a, x)


def pluck(f, dur, rng, bright):
    """Karplus-Strong string (guitar-like)."""
    n = int(dur * SR); N = max(2, int(SR / f))
    out = np.zeros(n + N)
    out[:N] = lowpass(rng.uniform(-1, 1, N), 2000 + 6000 * bright)
    decay = 0.996
    for s in range(N, n + N, N):
        prev = out[s - N:s]
        blk = 0.5 * (prev + np.roll(prev, 1)) * decay
        out[s:s + N] = blk[:len(out[s:s + N])]
    y = out[:n]
    return y * adsr(n, 0.002, 0.05, 1.0, 0.05)


def epiano(f, dur, bright):
    """Soft FM electric-piano tone."""
    n = int(dur * SR); t = np.arange(n) / SR
    idx = (1.2 + 2.0 * bright) * np.exp(-t * 3.5)
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    y += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
    return y * np.exp(-t * 1.6) * adsr(n, 0.004, 0.1, 1.0, 0.08)


def pad(freqs, dur, bright, rng):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            saw = 2 * ((ff * t + ph / (2 * np.pi)) % 1.0) - 1
            y += saw
    y = lowpass(y, 700 + 1600 * bright)
    return y / (3 * len(freqs)) * adsr(n, dur * 0.35, 0.2, 0.9, dur * 0.35)


def kick(n):
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(n, rng):
    t = np.arange(n) / SR
    x = rng.uniform(-1, 1, n)
    b, a = butter(2, 7000 / (SR / 2), "high")
    return lfilter(b, a, x) * np.exp(-t * 45)


def clap(n, rng):
    t = np.arange(n) / SR
    x = rng.uniform(-1, 1, n)
    b, a = butter(2, [900 / (SR / 2), 3500 / (SR / 2)], "band")
    return lfilter(b, a, x) * np.exp(-t * 22)


def add(buf, sig, start, gain=1.0):
    i = int(start * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[:j - i]


def reverb(x, rng, size=1.8, mix=0.25):
    n = int(size * SR); t = np.arange(n) / SR
    ir = rng.uniform(-1, 1, n) * np.exp(-t * 3.2 / size)
    ir = lowpass(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(x, ir)[:len(x)]
    return (1 - mix) * x + mix * wet


def make(dur, mood, seed):
    P = MOODS[mood]
    h = int(hashlib.sha256(str(seed).encode()).hexdigest()[:12], 16)
    rng = np.random.default_rng(h)
    bpm = rng.uniform(*P["bpm"]); beat = 60 / bpm; bar = 4 * beat
    root = 57 + int(rng.integers(-4, 6))          # key centre around A3
    flavour = "minor" if (mood in ("calm", "warm") and rng.random() < 0.35) else "major"
    prog = PROGS[flavour][int(rng.integers(len(PROGS[flavour])))]
    scale = [root + s for s in MAJOR]

    def chord(deg, octv=0):
        return [scale[(deg + k) % 7] + 12 * ((deg + k) // 7) + 12 * octv for k in (0, 2, 4)]

    n = int((dur + 2.5) * SR)
    L = np.zeros(n); R = np.zeros(n)
    nbars = int(np.ceil(dur / bar))
    # melody motif (repeated with variation)
    motif_len = 8
    motif = list(rng.choice([0, 1, 2, 2, 3, 4, 4, 5, 6, 7], motif_len))
    rhythm = rng.choice([0.5, 0.5, 1.0, 1.0, 1.5], motif_len)
    arp_pat = [list(p) for p in ([0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3], [2, 1, 0, 1])][int(rng.integers(4))]

    for b in range(nbars):
        deg = prog[b % len(prog)]; t0 = b * bar
        ch = chord(deg)
        # pad
        if P["pad"]:
            p = pad([hz(m) for m in ch], bar * 1.25, P["bright"], rng)
            add(L, p, t0, 0.16 * P["pad"]); add(R, p, t0, 0.16 * P["pad"])
        # bass
        bf = hz(ch[0] - 24)
        if mood == "energetic":
            for k in range(8):
                nb = int(beat / 2 * SR * 0.9); tt = np.arange(nb) / SR
                s = (np.sin(2 * np.pi * bf * tt) + 0.3 * np.sin(4 * np.pi * bf * tt)) * adsr(nb, 0.005, 0.05, 0.8, 0.03)
                add(L, s, t0 + k * beat / 2, 0.22 * P["bass"]); add(R, s, t0 + k * beat / 2, 0.22 * P["bass"])
        else:
            nb = int(bar * SR); tt = np.arange(nb) / SR
            s = np.sin(2 * np.pi * bf * tt) * adsr(nb, 0.05, 0.3, 0.7, 0.4)
            add(L, s, t0, 0.2 * P["bass"]); add(R, s, t0, 0.2 * P["bass"])
        # keys: chord stabs / arpeggio
        if P["keys"]:
            if mood in ("calm", "warm"):
                for k, idx in enumerate(arp_pat * 2):
                    m = (ch + [ch[0] + 12])[idx] + 12
                    s = epiano(hz(m), beat * 1.5, P["bright"])
                    pan = 0.5 + 0.25 * np.sin(k)
                    add(L, s, t0 + k * beat / 2, 0.09 * P["keys"] * (1.2 - pan)); add(R, s, t0 + k * beat / 2, 0.09 * P["keys"] * (0.2 + pan))
            else:
                for k in (0, 1.5, 2.5) if rng.random() < 0.5 else (0, 2):
                    for m in ch:
                        s = epiano(hz(m + 12), beat * 1.2, P["bright"])
                        add(L, s, t0 + k * beat, 0.05 * P["keys"]); add(R, s, t0 + k * beat, 0.05 * P["keys"])
        # plucks: melody motif (skip first bar for an intro feel, some variation per bar)
        if P["pluck"] and b >= 1:
            tt = t0
            shift = int(rng.integers(-1, 2)) if b % 2 else 0
            for k in range(motif_len):
                if tt >= t0 + bar: break
                deg_m = motif[k] + shift + deg % 3
                m = scale[deg_m % 7] + 12 * (deg_m // 7) + 12
                if rng.random() > 0.15:
                    s = pluck(hz(m), 1.4, rng, P["bright"])
                    pan = rng.uniform(0.3, 0.7)
                    add(L, s, tt, 0.13 * P["pluck"] * (1 - pan) * 2); add(R, s, tt, 0.13 * P["pluck"] * pan * 2)
                tt += rhythm[k] * beat
        # drums
        if P["drums"] and b >= 1:
            g = P["drums"]
            for k in range(4):
                if mood == "energetic" or k in (0, 2):
                    s = kick(int(0.35 * SR)); add(L, s, t0 + k * beat, 0.35 * g); add(R, s, t0 + k * beat, 0.35 * g)
                if k in (1, 3):
                    s = clap(int(0.25 * SR), rng); add(L, s, t0 + k * beat, 0.12 * g); add(R, s, t0 + k * beat, 0.12 * g)
            for k in range(8):
                s = hat(int(0.08 * SR), rng); gg = 0.05 * g * (1.0 if k % 2 else 0.6)
                add(L, s, t0 + k * beat / 2, gg * 0.8); add(R, s, t0 + k * beat / 2, gg * 1.2)

    L = reverb(L, np.random.default_rng(h + 1), mix=0.28 if mood == "calm" else 0.2)
    R = reverb(R, np.random.default_rng(h + 2), mix=0.28 if mood == "calm" else 0.2)
    st = np.stack([L, R], 1)[: int(dur * SR)]
    t = np.arange(len(st)) / SR
    st *= np.minimum(1, np.minimum(t / 0.8, (dur - t) / 1.8))[:, None]
    rms = np.sqrt(np.mean(st ** 2)) + 1e-9
    st = np.tanh(st * (0.16 / rms)) * 0.9
    return st


if __name__ == "__main__":
    out, dur = sys.argv[1], float(sys.argv[2])
    mood = sys.argv[3] if len(sys.argv) > 3 else "calm"
    mood = LEGACY.get(mood, mood)
    if mood not in MOODS:
        sys.exit(f"unknown mood {mood}; use one of {list(MOODS)}")
    import os
    seed = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(out)
    st = make(dur, mood, seed)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    print("ok", out, mood, seed)
