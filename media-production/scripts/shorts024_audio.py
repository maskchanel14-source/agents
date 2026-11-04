#!/usr/bin/env python3
"""
SHORTS-2026-024-Binance-63B — audio engine.

Builds the full 67.000 s (2010 frames @ 30fps) soundtrack for the short:

  1. Timeline   - measures every VO clip, applies `atempo`, lays clips out with
                  lead-in + inter-clip gaps, and emits audio/timing.json.
  2. Score      - original 100 BPM military march (kick / snare / hats / timpani
                  + low-brass chord stabs), arranged in 5 sections.
  3. SFX        - 5 designed effects (riser, vault slam + coin pour, freeze hit,
                  glitch, sub boom) triggered off the VO timeline.
  4. Mix        - music ducked -6 dB under voice (50 ms attack / 250 ms release),
                  SFX peaking at -12 dBFS, then ffmpeg loudnorm to -14 LUFS.

No external audio assets: everything is synthesised with numpy.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import wave

import numpy as np

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
SR = 44100
FPS = 30
TOTAL_FRAMES = 2010                 # 67.0 s — same length as the reference short
TOTAL_SECONDS = TOTAL_FRAMES / FPS  # 67.0
ATEMPO = 1.07                       # VO pace: snappy but not chipmunk
LEAD_IN = 0.50                      # silence before the hook lands
GAP = 0.18                          # breath between VO lines

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                    "projects", "SHORTS-2026-024-Binance-63B"))
AUDIO = os.path.join(ROOT, "audio")
TMP = os.path.join(AUDIO, "_tmp")
FFMPEG = subprocess.run(
    ["node", "-e",
     "console.log(require('/home/user/agents/media-production/node_modules/"
     "@ffmpeg-installer/ffmpeg').path)"],
    capture_output=True, text=True, check=True).stdout.strip()

# VO clips in script order. `sfx` entries fire at the clip's start.
CLIPS = [
    {"id": "L1",  "file": "vo_l1_hook.wav",       "sfx": ["riser"]},
    {"id": "B1",  "file": "vo_b1_setup.wav",      "sfx": ["vault_slam"]},
    {"id": "B2a", "file": "vo_b2a_chains.wav",    "sfx": ["coin_pour"]},
    {"id": "B2b", "file": "vo_b2b_bitcoin.wav",   "sfx": []},
    {"id": "B2c", "file": "vo_b2c_frozen.wav",    "sfx": ["freeze"]},
    {"id": "B3a", "file": "vo_b3a_door.wav",      "sfx": []},
    {"id": "B3b", "file": "vo_b3b_interview.wav", "sfx": ["glitch"]},
    {"id": "B3c", "file": "vo_b3c_laptop.wav",    "sfx": []},
    {"id": "P1",  "file": "vo_p1_paid.wav",       "sfx": []},
    {"id": "P2",  "file": "vo_p2_blame.wav",      "sfx": ["boom"]},
]

# ----------------------------------------------------------------------------
# Small DSP helpers
# ----------------------------------------------------------------------------


def adsr(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    """Linear ADSR envelope, lengths in seconds."""
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n)
    env = np.concatenate([
        np.linspace(0.0, 1.0, a_n, endpoint=False) if a_n else np.zeros(0),
        np.linspace(1.0, s, d_n, endpoint=False) if d_n else np.zeros(0),
        np.full(s_n, s),
        np.linspace(s, 0.0, r_n) if r_n else np.zeros(0),
    ])
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def exp_decay(n: int, tau: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.exp(-t / tau)


def _box(x: np.ndarray, length: int) -> np.ndarray:
    """Length-N moving average via cumulative sum — O(n), fully vectorised."""
    if length <= 1:
        return x
    c = np.cumsum(np.concatenate([np.zeros(length), x]))
    return (c[length:] - c[:-length]) / float(length)


def onepole_lp(x: np.ndarray, cutoff: float) -> np.ndarray:
    """Box-filter lowpass. For a moving average of length L the -3 dB point is
    ~0.44*SR/L, so L = 0.44*SR/cutoff. Cheap stand-in for a one-pole IIR."""
    length = max(1, int(round(0.44 * SR / max(50.0, float(cutoff)))))
    return _box(x, length)


def band(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return onepole_lp(x, hi) - onepole_lp(x, lo)


def place(buf: np.ndarray, sig: np.ndarray, at: float) -> None:
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i >= len(buf) or j <= i:
        return
    buf[i:j] += sig[: j - i]


def norm_peak(x: np.ndarray, peak_db: float) -> np.ndarray:
    p = float(np.max(np.abs(x))) or 1.0
    return x * (10 ** (peak_db / 20.0)) / p


def norm_rms(x: np.ndarray, rms_db: float) -> np.ndarray:
    r = float(np.sqrt(np.mean(x ** 2))) or 1.0
    return x * (10 ** (rms_db / 20.0)) / r


# ----------------------------------------------------------------------------
# Instruments
# ----------------------------------------------------------------------------


def kick(dur: float = 0.35) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 45.0 + 95.0 * np.exp(-t / 0.035)          # 140 Hz -> 45 Hz body
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-t / 0.16)
    click = np.random.default_rng(1).normal(0, 1, n) * np.exp(-t / 0.004) * 0.25
    return (body + click) * 0.9


def snare(dur: float = 0.22) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(2)
    noise = band(rng.normal(0, 1, n), 900, 6500)
    noise *= np.exp(-t / 0.055)
    tone = (np.sin(2 * np.pi * 190 * t) + np.sin(2 * np.pi * 278 * t) * 0.6)
    tone *= np.exp(-t / 0.035) * 0.35
    return (noise * 0.8 + tone) * 0.8


def snare_roll(dur: float = 0.30, hits: int = 6) -> np.ndarray:
    """Military rudiment: accelerating 16ths."""
    out = np.zeros(int(dur * SR))
    step = dur / hits
    for i in range(hits):
        g = 0.35 + 0.65 * (i / max(1, hits - 1))
        place(out, snare(0.16) * g, i * step)
    return out


def hat(dur: float = 0.06) -> np.ndarray:
    n = int(dur * SR)
    rng = np.random.default_rng(3)
    x = band(rng.normal(0, 1, n), 7000, 16000)
    t = np.arange(n) / SR
    return x * np.exp(-t / 0.018) * 0.5


def timpani(freq: float = 62.0, dur: float = 0.9) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1.0 + 0.35 * np.exp(-t / 0.09))
    body = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.42)
    harm = np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t / 0.22) * 0.3
    return (body + harm) * 0.8


def brass(freq: float, dur: float, gain: float = 1.0) -> np.ndarray:
    """Low-brass stab: 6 harmonics, bright attack, warm sustain, vibrato."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1.0 + 0.004 * np.sin(2 * np.pi * 5.2 * t)
    sig = np.zeros(n)
    amps = [1.0, 0.52, 0.34, 0.22, 0.13, 0.08]
    for h, a in enumerate(amps, start=1):
        sig += a * np.sin(2 * np.pi * freq * h * vib * t)
    sig /= sum(amps)
    env = adsr(n, 0.035, 0.10, 0.72, 0.09)
    # Bright attack, darker tail: blend a filtered (warm) version with the raw
    # (buzzy) harmonics using a decaying "brightness" curve.
    warm = onepole_lp(sig, 2600.0)
    bright = np.exp(-t / 0.22)
    sig = warm + (sig - warm) * bright * 0.75
    return sig * env * gain


NOTE = {"D2": 73.42, "A2": 110.0, "Bb2": 116.54, "C3": 130.81, "D3": 146.83,
        "E3": 164.81, "F3": 174.61, "G3": 196.0, "A3": 220.0, "Bb3": 233.08,
        "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0,
        "A4": 440.0, "Bb4": 466.16, "C5": 523.25, "D5": 587.33}

# D minor march: i - VI - III - VII
PROGRESSION = [
    ("Dm", ["D2", "D3", "F3", "A3"]),
    ("Bb", ["Bb2", "D3", "F3", "Bb3"]),
    ("F",  ["C3", "F3", "A3", "C4"]),
    ("C",  ["C3", "E3", "G3", "C4"]),
]
MELODY = ["D4", "F4", "A4", "F4", "D4", "C4", "D4", None,
          "Bb3", "D4", "F4", "D4", "C4", "A3", "Bb3", None,
          "C4", "E4", "G4", "E4", "F4", "E4", "D4", None,
          "E4", "G4", "C5", "G4", "E4", "D4", "C4", "D4"]


def build_score() -> np.ndarray:
    """100 BPM march, 5 sections matching the story beats."""
    bpm = 100.0
    beat = 60.0 / bpm          # 0.60 s
    bar = beat * 4             # 2.40 s
    out = np.zeros(int(TOTAL_SECONDS * SR))
    rng = np.random.default_rng(7)

    kick_s, snare_s, hat_s = kick(), snare(), hat()
    n_bars = int(TOTAL_SECONDS / bar) + 1

    # section map -> (full drums, melody, timpani, brass stabs)
    def section(bar_i: int) -> tuple[bool, bool, bool, bool]:
        t = bar_i * bar
        if t < 8.0:
            return (False, False, False, True)     # sparse drone under hook
        if t < 24.0:
            return (True, True, False, True)       # march enters
        if t < 42.0:
            return (True, True, True, True)        # full band
        if t < 57.0:
            return (True, False, True, False)      # tense: no melody
        return (True, True, True, True)            # payoff

    for b in range(n_bars):
        t0 = b * bar
        drums, melody, timp, stabs = section(b)
        if t0 >= TOTAL_SECONDS:
            break

        if drums:
            for k in range(4):
                place(out, kick_s * (1.0 if k in (0, 2) else 0.72), t0 + k * beat)
                if k in (1, 3):
                    place(out, snare_s * 0.9, t0 + k * beat)
            for e in range(8):                      # hats on 8ths
                place(out, hat_s * (0.7 if e % 2 == 0 else 0.45), t0 + e * beat / 2)
            if b % 4 == 3:                          # rudiment fill every 4 bars
                place(out, snare_roll(beat * 1.0, 8) * 0.55, t0 + beat * 3)
        else:
            for k in (0, 2):
                place(out, kick_s * 0.55, t0 + k * beat)

        if stabs:
            name, chord = PROGRESSION[b % 4]
            for f in (chord[0], chord[1]):          # bass + low voice
                place(out, brass(NOTE[f], beat * 0.9, 0.42), t0)
            place(out, brass(NOTE[chord[2]], beat * 1.8, 0.30), t0 + beat * 2)

        if melody:
            for s in range(8):
                idx = (b * 8 + s) % len(MELODY)
                nname = MELODY[idx]
                if nname:
                    place(out, brass(NOTE[nname], beat * 0.52, 0.34),
                          t0 + s * beat / 2)

        if timp and b % 2 == 0:
            place(out, timpani(58.0, 0.85) * 0.5, t0)
            place(out, timpani(58.0, 0.60) * 0.35, t0 + beat * 2.5)

    # final bar: unison hit then decay
    end = int((TOTAL_SECONDS - 2.2) * SR / SR)
    place(out, brass(NOTE["D2"], 2.0, 0.55), end)
    place(out, brass(NOTE["A2"], 2.0, 0.40), end)
    place(out, brass(NOTE["D3"], 2.0, 0.45), end)
    place(out, timpani(48.0, 1.6) * 0.7, end)

    out = np.tanh(out * 1.05) * 0.9                 # soft-clip glue
    return out


# ----------------------------------------------------------------------------
# SFX
# ----------------------------------------------------------------------------


def sweep_band(x: np.ndarray, lo: float, hi_start: float, hi_end: float,
               steps: int = 12) -> np.ndarray:
    """Band-pass whose top edge sweeps upward. Implemented as `steps` fixed
    bands crossfaded with 50 %-overlap Hann windows (fully vectorised)."""
    n = len(x)
    out = np.zeros(n)
    for k in range(steps):
        c0, c1 = k / steps, (k + 1) / steps
        hi = hi_start + (hi_end - hi_start) * (0.5 * (c0 + c1))
        seg = band(x, lo, hi)
        a = max(0.0, c0 - 0.5 / steps)
        b = min(1.0, c1 + 0.5 / steps)
        i0, i1 = int(a * n), int(b * n)
        w = np.zeros(n)
        if i1 - i0 >= 3:
            w[i0:i1] = np.hanning(i1 - i0)
        out += seg * w
    return out


def sfx_riser(dur: float = 1.1) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    rng = np.random.default_rng(11)
    x = sweep_band(rng.normal(0, 1, n), 200.0, 400.0, 7600.0) * 1.6
    x *= u ** 2.2
    sweep = np.sin(2 * np.pi * (120 + 900 * u ** 2) * t) * 0.30 * u
    return (x * 0.6 + sweep) * 0.9


def sfx_vault_slam(dur: float = 1.5) -> np.ndarray:
    """Steel door slam: metallic ring + low thud."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    metal = np.zeros(n)
    for f, a, tau in ((186, 1.0, 0.55), (404, 0.6, 0.38), (733, 0.35, 0.26),
                      (1181, 0.22, 0.18)):
        metal += a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
    thud = np.sin(2 * np.pi * (70 * np.exp(-t / 0.09) + 34) * t) * np.exp(-t / 0.20)
    scrape = band(np.random.default_rng(12).normal(0, 1, n), 1500, 9000) * \
        np.exp(-t / 0.09) * 0.35
    return (metal * 0.55 + thud * 0.8 + scrape) * 0.85


def sfx_coin_pour(dur: float = 2.2) -> np.ndarray:
    """Hundreds of tiny metallic impacts, then a settling shimmer."""
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(13)
    k = 260
    for i in range(k):
        u = (i / k) ** 0.75
        at = u * dur * 0.72 + rng.uniform(0, 0.02)
        f = rng.uniform(1800, 5200)
        d = rng.uniform(0.02, 0.07)
        m = int(d * SR)
        t = np.arange(m) / SR
        ping = (np.sin(2 * np.pi * f * t) +
                np.sin(2 * np.pi * f * 1.61 * t) * 0.5) * np.exp(-t / (d / 3))
        amp = 0.30 * (1.0 - 0.55 * u)
        place(out, ping * amp, at)
    tail = band(rng.normal(0, 1, n), 2500, 11000) * np.exp(-t_dummy(n) / 0.6) * 0.10
    return (out + tail) * 0.9


def t_dummy(n: int) -> np.ndarray:
    return np.arange(n) / SR


def sfx_freeze(dur: float = 1.6) -> np.ndarray:
    """Ice forming: crystalline shimmer + a hardening low tone."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(14)
    x = band(rng.normal(0, 1, n), 3000, 15000) * np.exp(-t / 0.35) * 0.55
    grow = np.zeros(n)
    for f in (1560, 2340, 3510, 4680):
        grow += np.sin(2 * np.pi * f * t) * np.minimum(1.0, t / 0.22) * 0.16
    sub = np.sin(2 * np.pi * (110 - 46 * np.minimum(1.0, t / 0.5)) * t) * \
        np.exp(-t / 0.45) * 0.45
    return (x + grow * np.exp(-t / 0.9) + sub) * 0.85


def sfx_glitch(dur: float = 1.3) -> np.ndarray:
    """Terminal glitch: gated noise bursts + bit-crushed tone."""
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(15)
    t = np.arange(n) / SR
    cursor = 0.0
    while cursor < dur * 0.8:
        seg = int(rng.uniform(0.02, 0.09) * SR)
        m = min(seg, n - int(cursor * SR))
        if m <= 0:
            break
        tt = np.arange(m) / SR
        f = rng.choice([220, 330, 440, 660, 880, 1320])
        crushed = np.round(np.sin(2 * np.pi * f * tt) * 3) / 3
        g = rng.uniform(0.35, 1.0) * np.exp(-tt / 0.05)
        place(out, (crushed * 0.5 + rng.normal(0, 1, m) * 0.4) * g, cursor)
        cursor += rng.uniform(0.05, 0.16)
    key = band(rng.normal(0, 1, n), 1200, 6000) * np.exp(-t / 0.5) * 0.12
    return (out + key) * 0.8


def sfx_boom(dur: float = 2.4) -> np.ndarray:
    """Sub impact for the final reveal."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (90 * np.exp(-t / 0.12) + 32) * t) * np.exp(-t / 0.65)
    airy = band(np.random.default_rng(16).normal(0, 1, n), 400, 6000) * \
        np.exp(-t / 0.20) * 0.4
    ring = np.sin(2 * np.pi * 62 * t) * np.exp(-t / 1.4) * 0.35
    return (body * 1.0 + airy + ring) * 0.9


SFX_MAKERS = {
    "riser": (sfx_riser, 1.1),
    "vault_slam": (sfx_vault_slam, 1.5),
    "coin_pour": (sfx_coin_pour, 2.2),
    "freeze": (sfx_freeze, 1.6),
    "glitch": (sfx_glitch, 1.3),
    "boom": (sfx_boom, 2.4),
}


# ----------------------------------------------------------------------------
# Timeline
# ----------------------------------------------------------------------------


def wav_duration(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def time_stretch(src: str, dst: str, factor: float) -> None:
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src,
                    "-filter:a", f"atempo={factor}", "-ar", str(SR), "-ac", "1",
                    dst], check=True)


def load_mono(path: str) -> np.ndarray:
    with wave.open(path, "rb") as w:
        frames = w.readframes(w.getnframes())
    x = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    return x


def write_wav(path: str, x: np.ndarray, sr: int = SR) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = np.clip(x, -1.0, 1.0)
    pcm = (x * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def build_timeline() -> list[dict]:
    os.makedirs(TMP, exist_ok=True)
    t = LEAD_IN
    timeline = []
    for c in CLIPS:
        src = os.path.join(AUDIO, c["file"])
        raw = wav_duration(src)
        dst = os.path.join(TMP, c["file"])
        time_stretch(src, dst, ATEMPO)
        dur = raw / ATEMPO
        timeline.append({
            "id": c["id"], "file": c["file"], "sfx": c["sfx"],
            "start": round(t, 4), "end": round(t + dur, 4),
            "duration": round(dur, 4), "raw_duration": round(raw, 4),
            "start_frame": int(round(t * FPS)), "end_frame": int(round((t + dur) * FPS)),
        })
        t += dur + GAP
    return timeline


def build_vo(timeline: list[dict]) -> np.ndarray:
    vo = np.zeros(int(TOTAL_SECONDS * SR))
    for c in timeline:
        x = load_mono(os.path.join(TMP, c["file"]))
        place(vo, x, c["start"])
        # 8 ms fades so splices never click
        fi = int(0.008 * SR)
        i = int(c["start"] * SR)
        if i + fi < len(vo):
            vo[i:i + fi] *= np.linspace(0, 1, fi)
            j = i + len(x)
            if j - fi > 0 and j <= len(vo):
                vo[j - fi:j] *= np.linspace(1, 0, fi)
    return vo


def build_sfx(timeline: list[dict]) -> tuple[np.ndarray, list[dict]]:
    bed = np.zeros(int(TOTAL_SECONDS * SR))
    log = []
    for c in timeline:
        for name in c["sfx"]:
            maker, dur = SFX_MAKERS[name]
            sig = norm_peak(maker(dur), -12.0)
            at = max(0.0, c["start"] - (0.18 if name == "riser" else 0.02))
            place(bed, sig, at)
            log.append({"name": name, "at": round(at, 3), "dur": dur,
                        "clip": c["id"]})
    return bed, log


def duck_envelope(timeline: list[dict]) -> np.ndarray:
    """1.0 where voice is active, smoothed: 50 ms attack, 250 ms release."""
    n = int(TOTAL_SECONDS * SR)
    env = np.zeros(n)
    for c in timeline:
        a = int((c["start"] - 0.06) * SR)
        b = int((c["end"] + 0.10) * SR)
        env[max(0, a):min(n, b)] = 1.0
    out = np.zeros(n)
    atk = 1.0 - math.exp(-1.0 / (0.050 * SR))
    rel = 1.0 - math.exp(-1.0 / (0.250 * SR))
    val = 0.0
    for i in range(n):                    # one-pole smoother, attack/release split
        target = env[i]
        k = atk if target > val else rel
        val += k * (target - val)
        out[i] = val
    return out


def loudnorm(src: str, dst: str) -> None:
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", src,
         "-filter:a", "loudnorm=I=-14:LRA=11:TP=-1.5",
         "-ar", str(SR), "-ac", "1", dst], check=True)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    os.makedirs(AUDIO, exist_ok=True)
    print(f"[1/6] timeline  (atempo={ATEMPO}, lead={LEAD_IN}s, gap={GAP}s)")
    timeline = build_timeline()
    for c in timeline:
        print(f"      {c['id']:>4}  {c['start']:6.2f}s -> {c['end']:6.2f}s "
              f"({c['start_frame']:4d}-{c['end_frame']:4d}f)  {c['file']}")
    vo_end = timeline[-1]["end"]
    print(f"      VO ends at {vo_end:.2f}s / {TOTAL_SECONDS:.2f}s")

    print("[2/6] score (100 BPM march)")
    music = norm_rms(build_score(), -18.0)
    write_wav(os.path.join(AUDIO, "music.wav"), music)

    print("[3/6] sfx")
    sfx_bed, sfx_log = build_sfx(timeline)
    write_wav(os.path.join(AUDIO, "sfx.wav"), sfx_bed)

    print("[4/6] vo")
    vo = build_vo(timeline)
    write_wav(os.path.join(AUDIO, "vo.wav"), vo)

    print("[5/6] mix (ducking -6 dB under voice)")
    env = duck_envelope(timeline)
    gain = 10 ** ((-6.0 / 20.0) * env)          # 1.0 -> 0.501 while voice is up
    music_ducked = music * gain
    mix = vo + music_ducked + sfx_bed
    mix = np.tanh(mix * 0.85) / math.tanh(0.85) * 0.92
    write_wav(os.path.join(AUDIO, "mix.wav"), mix)

    print("[6/6] loudnorm -> -14 LUFS")
    loudnorm(os.path.join(AUDIO, "mix.wav"), os.path.join(AUDIO, "final.wav"))

    with open(os.path.join(AUDIO, "timing.json"), "w") as f:
        json.dump({
            "fps": FPS, "total_frames": TOTAL_FRAMES, "total_seconds": TOTAL_SECONDS,
            "atempo": ATEMPO, "lead_in": LEAD_IN, "gap": GAP,
            "vo_end": round(vo_end, 3),
            "clips": timeline,
            "sfx": sfx_log,
        }, f, indent=2)
    print("      wrote audio/timing.json, music.wav, sfx.wav, vo.wav, mix.wav, final.wav")
    return 0


if __name__ == "__main__":
    sys.exit(main())
