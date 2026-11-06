#!/usr/bin/env python3
"""
audio_kit.py -- score + SFX + master for the Palmer mango spot.

No API keys, no licensed music: the score is generated as MIDI and rendered
through a GM soundfont, SFX are synthesised from noise/sine maths, and the
whole thing is mastered to -14 LUFS.

Structure (45.5 s):
  0.0 - 5.0    pad swell + single low piano note          (establishing)
  5.0 - 10.0   piano motif enters, soft pulse             (hero)
  10.0- 15.0   motif climbs, strings counter-line         (texture)
  15.0- 22.0   pulse + ticking data hits on each number   (the numbers)
  22.0- 28.0   fuller chord (IV - V - vi), gentle lift    (varieties)
  28.0- 34.0   rhythmic bed, industrial ticks             (supply chain)
  34.0- 39.0   motif returns, highest point               (brix)
  39.0- 42.0   strip back to pad + one note               (ready)
  42.0- 45.5   resolve on tonic, tail                     (sign-off)

Usage: audio_kit.py --shots shots.json --build build
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 44100
ROOT = Path(__file__).resolve().parent


def ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


# --------------------------------------------------------------- midi writing
def vlq(n: int) -> bytes:
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def write_midi(path: Path, events: list[tuple[float, str, int, int, int]], bpm: float = 76.0) -> None:
    """events: (time_s, 'on'|'off', channel, pitch, velocity)."""
    ppq = 480
    ticks_per_s = ppq * bpm / 60.0

    by_ch: dict[int, list[tuple[int, bytes]]] = {}
    for t, kind, ch, pitch, vel in events:
        tick = int(round(t * ticks_per_s))
        status = (0x90 if kind == "on" else 0x80) | ch
        by_ch.setdefault(ch, []).append((tick, bytes([status, pitch, vel])))

    out = bytearray()
    out += b"MThd" + (6).to_bytes(4, "big") + (1).to_bytes(2, "big") + len(by_ch).to_bytes(2, "big") + ppq.to_bytes(2, "big")

    # track 0: tempo + name
    trk = bytearray()
    trk += b"\x00\xff\x51\x03" + int(60_000_000 / bpm).to_bytes(3, "big")
    trk += b"\x00\xff\x2f\x00"
    out += b"MTrk" + len(trk).to_bytes(4, "big") + trk

    for ch, evs in sorted(by_ch.items()):
        evs.sort(key=lambda x: x[0])
        trk = bytearray()
        last = 0
        for tick, msg in evs:
            trk += vlq(max(0, tick - last)) + msg
            last = tick
        trk += b"\x00\xff\x2f\x00"
        out += b"MTrk" + len(trk).to_bytes(4, "big") + trk

    path.write_bytes(bytes(out))


# --------------------------------------------------------------- the score
NOTE = {n: i for i, n in enumerate(
    ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def hz(name: str) -> int:
    """'A4' -> midi number."""
    pitch, octave = name[:-1], int(name[-1])
    return 12 * (octave + 1) + NOTE[pitch]


def compose(total: float) -> list[tuple[float, str, int, int, int]]:
    """A-minor / C-major palette. Channels: 0 piano, 1 strings, 2 bass, 3 marimba."""
    ev: list[tuple[float, str, int, int, int]] = []

    def note(ch: int, name: str, start: float, dur: float, vel: int = 80) -> None:
        if start >= total:
            return
        p = hz(name)
        ev.append((start, "on", ch, p, vel))
        ev.append((min(total, start + dur), "off", ch, p, 0))

    # --- pads (strings, ch1): Am - F - C - G, long and quiet
    pads = [
        (0.0, 5.2, ["A3", "C4", "E4"]),
        (5.0, 10.2, ["F3", "A3", "C4"]),
        (10.0, 15.2, ["C4", "E4", "G4"]),
        (15.0, 22.2, ["G3", "B3", "D4"]),
        (22.0, 28.2, ["A3", "C4", "E4"]),
        (28.0, 34.2, ["F3", "A3", "C4"]),
        (34.0, 39.2, ["C4", "E4", "G4"]),
        (39.0, 42.2, ["G3", "B3", "D4"]),
        (42.0, 45.5, ["A3", "C4", "E4"]),
    ]
    for start, end, chord in pads:
        for i, n in enumerate(chord):
            note(1, n, start, end - start, 34 + i * 3)
        note(1, n_oct(chord[0], 1), start, end - start, 40)

    # --- bass: root on the bar, sustained
    for start, end, chord in pads:
        note(2, n_oct(chord[0], -1), start, min(1.9, end - start), 62)

    # --- piano motif (ch0): the hook, A C E D | C A G
    motif = [("A4", 0.0, 1.2), ("C5", 1.2, 1.0), ("E5", 2.2, 1.4), ("D5", 3.6, 1.0), ("C5", 4.6, 1.6)]
    # statement 1 (5.0) and statement 2 (10.0), then the lift at 22.0
    for base in (5.0, 10.0, 22.0, 34.0):
        for n, off, dur in motif:
            note(0, n, base + off, dur, 66 if base == 22.0 else 58)
    # quiet opening statement — just the first two notes, alone
    note(0, "A4", 1.2, 1.8, 46)
    note(0, "E5", 3.0, 1.6, 40)

    # --- marimba ticks (ch3): one per data row, then per supply step
    for t in (15.7, 17.0, 18.3):
        note(3, "E6", t, 0.22, 54)
        note(3, "A6", t + 0.11, 0.18, 40)
    for t in (28.9, 29.7, 30.5, 31.3, 32.1):
        note(3, "C6", t, 0.14, 44)

    # --- pulse bed: a soft sub on every beat from the data act to the sign-off.
    # Without this the 28-34s supply-chain section sags ~7 dB against the rest.
    beat = 60.0 / 76.0
    roots = {"F3": "F2", "G3": "G2", "A3": "A2", "C4": "C3"}
    pad_lookup = [(s, e, c) for s, e, c in pads]
    for start, end, chord in pad_lookup:
        if start < 15.0 or start >= 42.0:
            continue
        root = chord[0]
        bass_name = roots.get(root, n_oct(root, -1))
        k = 0
        tt = start
        while tt < min(end, 42.0) - 0.05:
            # accent the downbeat, lighten the off-beats
            vel = 54 if k % 4 == 0 else 34
            note(2, bass_name, tt, 0.30, vel)
            tt += beat
            k += 1

    # --- a very quiet high shimmer sustained through the middle acts
    for start, end, _ in pad_lookup:
        if 10.0 <= start < 39.0:
            note(1, "E6", start, end - start, 18)

    # --- climb into the brix beat
    climb = ["E5", "F5", "G5", "A5"]
    for i, n in enumerate(climb):
        note(0, n, 34.0 + i * 0.5, 0.5, 62)

    # --- resolve: tonic chord, one high note left ringing
    note(0, "A5", 42.4, 2.4, 62)
    note(0, "E5", 43.2, 2.0, 48)

    ev.sort(key=lambda x: x[0])
    return ev


def n_oct(name: str, delta: int) -> str:
    return f"{name[:-1]}{int(name[-1]) + delta}"


# --------------------------------------------------------------- sfx
def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def whoosh(dur=1.1, sr=SR, seed=3) -> np.ndarray:
    n = int(dur * sr)
    t = np.linspace(0, 1, n)
    noise = rng(seed).normal(0, 1, n)
    # simple one-pole lowpass whose cutoff sweeps up
    out = np.zeros(n)
    a = 0.02 + 0.5 * t**2
    for i in range(1, n):
        out[i] = out[i - 1] + a[i] * (noise[i] - out[i - 1])
    env = np.sin(np.pi * t) ** 2
    return (out * env).astype(np.float32)


def boom(dur=1.6, sr=SR, seed=2, f0=90, f1=34) -> np.ndarray:
    n = int(dur * sr)
    t = np.linspace(0, dur, n)
    f = f1 + (f0 - f1) * np.exp(-t * 5)
    ph = 2 * np.pi * np.cumsum(f) / sr
    body = np.sin(ph) * np.exp(-t * 2.4)
    click = rng(seed).normal(0, 1, n) * np.exp(-t * 55)
    return (body * 0.9 + click * 0.22).astype(np.float32)


def tick(dur=0.05, sr=SR, f=2600) -> np.ndarray:
    n = int(dur * sr)
    t = np.linspace(0, dur, n)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 90)).astype(np.float32)


def riser(dur=2.2, sr=SR, seed=7) -> np.ndarray:
    n = int(dur * sr)
    t = np.linspace(0, 1, n)
    noise = rng(seed).normal(0, 1, n)
    out = np.zeros(n)
    a = 0.005 + 0.55 * t**3
    for i in range(1, n):
        out[i] = out[i - 1] + a[i] * (noise[i] - out[i - 1])
    return (out * (t**2.2)).astype(np.float32)


def shimmer(dur=2.6, sr=SR, seed=11) -> np.ndarray:
    n = int(dur * sr)
    t = np.linspace(0, dur, n)
    acc = np.zeros(n)
    for k, f in enumerate((1480, 1975, 2637, 3136)):
        acc += np.sin(2 * np.pi * f * t + k) * np.exp(-t * (1.6 + k * 0.5))
    return (acc / 4 * np.minimum(1, t * 8)).astype(np.float32)


# --------------------------------------------------------------- build
def resample(x: np.ndarray, sr_in: int, sr_out: int = SR) -> np.ndarray:
    if sr_in == sr_out:
        return x
    n_out = int(round(len(x) * sr_out / sr_in))
    xs = np.linspace(0, len(x) - 1, n_out)
    return np.interp(xs, np.arange(len(x)), x).astype(np.float32)


def highpass(x: np.ndarray, cutoff: float = 90.0, sr: int = SR) -> np.ndarray:
    """One-pole highpass, applied twice for a 12 dB/oct slope."""
    a = np.exp(-2 * np.pi * cutoff / sr)
    y = x.astype(np.float32).copy()
    for _ in range(2):
        prev_x = 0.0
        prev_y = 0.0
        for i in range(len(y)):
            xi = float(y[i])
            yi = a * (prev_y + xi - prev_x)
            y[i] = yi
            prev_x = xi
            prev_y = yi
    return y


def compress(x: np.ndarray, thresh_db: float = -20.0, ratio: float = 3.0,
             attack: float = 0.008, release: float = 0.18, sr: int = SR) -> np.ndarray:
    """Feed-forward compressor with a smoothed envelope follower."""
    env = np.abs(x)
    a_att = np.exp(-1 / (attack * sr))
    a_rel = np.exp(-1 / (release * sr))
    sm = np.zeros_like(env)
    e = 0.0
    for i in range(len(env)):
        c = a_att if env[i] > e else a_rel
        e = c * e + (1 - c) * env[i]
        sm[i] = e
    lvl = 20 * np.log10(np.maximum(sm, 1e-6))
    over = np.maximum(0.0, lvl - thresh_db)
    gain_db = -over * (1 - 1 / ratio)
    return (x * (10 ** (gain_db / 20))).astype(np.float32)


def reverb(x: np.ndarray, wet: float = 0.10, dur: float = 0.55, sr: int = SR, seed: int = 21) -> np.ndarray:
    """Short synthetic plate: exponentially decaying noise IR, FFT convolution."""
    n_ir = int(dur * sr)
    t = np.linspace(0, dur, n_ir)
    ir = rng(seed).normal(0, 1, n_ir) * np.exp(-t * 6.5)
    ir[: int(0.012 * sr)] *= np.linspace(0, 1, int(0.012 * sr))  # soften the onset
    ir /= np.max(np.abs(ir)) or 1
    n = len(x) + n_ir
    size = 1 << (n - 1).bit_length()
    wet_sig = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    wet_sig /= (np.max(np.abs(wet_sig)) or 1) / (np.max(np.abs(x)) or 1)
    return ((1 - wet) * x + wet * wet_sig).astype(np.float32)


def load_vo(path: Path) -> np.ndarray:
    x, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = resample(x, sr)
    x = highpass(x, 95.0)
    x = compress(x, thresh_db=-21.0, ratio=3.2)
    x = reverb(x, wet=0.085)
    # normalise each line to a consistent level so the read feels even
    rms = float(np.sqrt(np.mean(x ** 2))) or 1e-6
    x *= 0.13 / rms
    x = np.tanh(x * 1.25) / 1.25  # gentle saturation to sit it in the mix
    return x.astype(np.float32)


def place(buf: np.ndarray, sig: np.ndarray, at: float, gain: float, sr: int = SR) -> None:
    i = int(at * sr)
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i : i + n] += sig[:n] * gain


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True)
    ap.add_argument("--build", required=True)
    ap.add_argument("--sf2", default="/home/user/agents/dark-science-studio/assets/TimGM6mb.sf2")
    ap.add_argument("--total", type=float, default=45.5)
    args = ap.parse_args()

    build = Path(args.build)
    build.mkdir(parents=True, exist_ok=True)
    total = args.total
    n = int(total * SR)

    # 1. compose + render the score
    events = compose(total)
    mid = build / "score.mid"
    write_midi(mid, events, bpm=76.0)
    score_wav = build / "score.wav"
    subprocess.run(
        ["node", str(ROOT / "render-midi.mjs"), str(mid), str(score_wav), args.sf2, str(total)],
        check=True,
    )

    score, _ = sf.read(score_wav, dtype="float32", always_2d=True)
    if score.shape[1] == 1:
        score = np.repeat(score, 2, axis=1)
    score = score[:n] if len(score) >= n else np.pad(score, ((0, n - len(score)), (0, 0)))

    # 2. sfx bed
    sfx = np.zeros((n, 2), dtype=np.float32)

    def put(sig: np.ndarray, at: float, gain: float, pan: float = 0.0) -> None:
        m = np.zeros(n, dtype=np.float32)
        place(m, sig, at, gain)
        sfx[:, 0] += m * (1 - max(0, pan))
        sfx[:, 1] += m * (1 + min(0, pan))

    # transitions land on the shot list -- kept deliberately understated:
    # the voice is the focus, the design sounds just mark the cuts.
    shots = json.loads(Path(args.shots).read_text())
    for s in shots:
        t = s["from"] / s["fps"]
        if t == 0:
            continue
        if s["name"] in ("hero", "lineup", "water"):
            put(boom(), max(0, t - 0.02), 0.26)
            put(whoosh(1.2), t - 0.55, 0.12, -0.2)
        elif s["name"] in ("numbers", "pack"):
            put(boom(), max(0, t - 0.02), 0.22)
            put(riser(1.8), t - 1.7, 0.075, 0.15)
        else:
            put(whoosh(0.9), t - 0.45, 0.085, 0.25)

    # data ticks, exactly where the copy lands
    for t in (15.7, 17.0, 18.3):
        put(tick(), t, 0.055, 0.3)
    for t in (28.9, 29.7, 30.5, 31.3, 32.1):
        put(tick(f=2100), t, 0.035, -0.25)

    # a felt-kick pulse carrying the mid-section energy (half level, no thump)
    beat = 60.0 / 76.0
    tt = 15.0
    k = 0
    while tt < 42.0:
        g = 0.095 if k % 4 == 0 else 0.045
        put(boom(dur=0.42, f0=110, f1=52), tt, g)
        tt += beat
        k += 1

    put(shimmer(), 41.6, 0.13, 0.1)
    put(boom(dur=2.4, f0=70, f1=30), 42.0, 0.26)

    # 3. voice-over: one line per shot, sitting on the bed
    vo = np.zeros(n, dtype=np.float32)
    vo_cues: list[tuple[float, float]] = []
    # let the opening pad breathe before the first word; every other line
    # comes in just after its cut so the picture and the voice stay married
    VO_OFFSET = {"orchard": 0.55, "end": 0.20}
    vo_dir = ROOT / "public" / "audio" / "vo"
    for s in shots:
        name = s["name"]
        f = vo_dir / f"vo_{name}.wav"
        if not f.exists():
            print(f"[vo] missing {f.name}")
            continue
        x = load_vo(f)
        shot_start = s["from"] / s["fps"]
        shot_len = (s["to"] - s["from"]) / s["fps"]
        # start a hair after the cut, and never let a line overrun its shot
        at = shot_start + VO_OFFSET.get(name, 0.15)
        if len(x) / SR > shot_len - 0.30:
            print(f"[vo] WARNING {name}: {len(x)/SR:.2f}s does not fit {shot_len:.2f}s")
        place(vo, x, at, 1.0)
        vo_cues.append((at, at + len(x) / SR))

    # duck the music + design under the voice (soft, 5 dB, smooth edges)
    duck = np.ones(n, dtype=np.float32)
    fade = int(0.25 * SR)
    for a, b in vo_cues:
        i0 = max(0, int(a * SR) - fade)
        i1 = min(n, int(b * SR) + fade)
        seg = np.ones(i1 - i0, dtype=np.float32)
        ramp = np.linspace(0, 1, fade) if fade else np.array([1.0])
        n_in = min(fade, len(seg))
        n_out = min(fade, len(seg))
        seg[:n_in] = 1 - ramp[:n_in] * 0.44
        seg[-n_out:] = np.minimum(seg[-n_out:], 1 - ramp[:n_out][::-1] * 0.44)
        seg[:n_in] = np.minimum(seg[:n_in], np.linspace(1, 0.56, n_in))
        duck[i0:i1] = np.minimum(duck[i0:i1], seg)

    score *= 0.60
    mix = score * duck[:, None] + sfx * 0.85 * duck[:, None] + vo[:, None] * 1.0

    # 4. two-pass loudnorm to -14 LUFS
    pre = build / "mix_pre.wav"
    sf.write(pre, np.clip(mix, -1, 1), SR, subtype="PCM_24")

    def measure(p: Path) -> dict:
        cp = subprocess.run(
            [ffmpeg(), "-hide_banner", "-nostats", "-i", str(p), "-af",
             "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        txt = cp.stderr
        j = txt[txt.rindex("{") : txt.rindex("}") + 1]
        return json.loads(j)

    m = measure(pre)
    print(f"[mix] measured I={m['input_i']} TP={m['input_tp']} LRA={m['input_lra']}")
    out = build / "mix.wav"
    subprocess.run(
        [ffmpeg(), "-y", "-hide_banner", "-i", str(pre), "-af",
         f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
         "-ar", str(SR), str(out)],
        check=True, capture_output=True,
    )
    m2 = measure(out)
    print(f"[qa] {float(m2['input_i']):.2f} LUFS / {float(m2['input_tp']):.2f} dBTP")
    print(f"[out] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
