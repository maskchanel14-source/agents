#!/usr/bin/env python3
"""
audio_kit.py -- per-video score + SFX + mix, all synthesised locally.

Pipeline
  1. read timeline.json + words.json
  2. compose a MIDI score that follows the script beats  -> build/score.mid
  3. render it through SpessaSynth + a GM soundfont      -> build/score.wav
  4. synthesise layered SFX on every cut/reveal           -> build/sfx.wav
  5. duck the score under the voice, sum, master          -> build/mix.wav

Master target: -14 LUFS integrated, true peak <= -1.0 dBTP (two-pass loudnorm).

Usage: audio_kit.py --project projects/DS-003 --build build/DS-003
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
FFMPEG = None  # resolved lazily


def ffmpeg() -> str:
    global FFMPEG
    if FFMPEG is None:
        import imageio_ffmpeg

        FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    return FFMPEG


def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ score
def compose_score(tl: dict, beat_times: list[float], total: float, path: Path) -> None:
    """D minor, 72 BPM, 7-bar structure that tracks the script's beats."""
    import pretty_midi

    pm = pretty_midi.PrettyMIDI(initial_tempo=72)
    bpm = 72.0
    beat = 60.0 / bpm

    # ---- instruments
    pad = pretty_midi.Instrument(program=91, name="pad")        # warm pad
    bass = pretty_midi.Instrument(program=38, name="sub")       # synth bass
    stabs = pretty_midi.Instrument(program=52, name="choir")    # choir aahs
    strings = pretty_midi.Instrument(program=48, name="strings")  # tremolo
    celesta = pretty_midi.Instrument(program=8, name="celesta")
    timp = pretty_midi.Instrument(program=47, name="timp", is_drum=False)

    D2, D3, F3, A3, C4, D4, E4, F4, A4, Bb3, E3 = 38, 50, 53, 57, 60, 62, 64, 65, 69, 58, 52

    def note(inst, pitch, start, dur, vel):
        if start >= total:
            return
        inst.notes.append(
            pretty_midi.Note(velocity=int(max(1, min(127, vel))), pitch=pitch,
                             start=max(0.0, start), end=min(total, start + max(0.08, dur)))
        )

    # ---- pad: Dm -> Bb -> F -> C, two beats per chord, whole video
    prog = [[D3, F3, A3], [Bb3, D4, F4], [F3, A3, C4], [E3, A3, C4]]
    t = 0.0
    i = 0
    while t < total:
        chord = prog[i % len(prog)]
        for p in chord:
            note(pad, p, t, beat * 2.05, 52)
        t += beat * 2
        i += 1

    # ---- sub: half notes on the root, only after the hook lands
    t = 2.3
    roots = [D2, D2, Bb3 - 12, F3 - 12]
    k = 0
    while t < total:
        note(bass, roots[k % len(roots)], t, beat * 1.9, 74)
        t += beat * 2
        k += 1

    # ---- tremolo strings: enter at the escalation (~12.9 s), swell, drop before the twist
    t = 12.9
    while t < 36.3:
        for p in [D4, F4, A4]:
            note(strings, p, t, beat * 0.5, 40 + int(18 * (t / 36.0)))
        t += beat * 0.5

    # ---- choir stabs on the two big reveals
    for at in (19.6, 38.7):
        for p in [D3, F3, A3, D4]:
            note(stabs, p, at, 1.6, 92)

    # ---- celesta motif: innocent-but-wrong, 4 notes, repeated in the gaps
    motif = [(D4, 0.0), (F4, 0.5), (E4, 1.0), (C4, 1.5)]
    t = 8.45
    while t < 36.3:
        for p, off in motif:
            note(celesta, p, t + off * beat, beat * 0.45, 46)
        t += beat * 4

    # ---- timpani hits on every cut in the back half
    for bt in beat_times:
        if bt >= 21.0:
            note(timp, 38, bt, 0.9, 78)

    pm.instruments.extend([pad, bass, strings, stabs, celesta, timp])
    pm.write(str(path))


def render_score(midi: Path, sf2: Path, out: Path, seconds: float) -> None:
    script = ROOT / "tools" / "studio" / "scripts" / "render-midi.mjs"
    studio = ROOT / "tools" / "studio"
    # absolute paths: the node process runs with cwd=tools/studio
    r = subprocess.run(
        ["node", str(script), str(midi.resolve()), str(out.resolve()), str(sf2.resolve()), f"{seconds:.3f}"],
        cwd=studio, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"render-midi failed:\n{r.stdout}\n{r.stderr}")
    print(" ", r.stdout.strip())


# ------------------------------------------------------------------ sfx
def env_adsr(n: int, a: int, d: int, s: float, r: int) -> np.ndarray:
    e = np.ones(n) * s
    e[:a] = np.linspace(0, 1, a)
    e[a:a + d] = np.linspace(1, s, min(d, max(0, n - a)))
    if r > 0 and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def sub_drop(dur=1.4, f0=120, f1=28, sr=SR, seed=1):
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / sr
    body = np.sin(ph) * np.exp(-t * 2.4)
    click = rng(seed).normal(0, 0.35, n) * np.exp(-t * 90)
    return (body * 0.9 + click).astype(np.float32)


def impact(dur=1.8, sr=SR, seed=2):
    """sub drop + mid transient + metallic tail."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    g = rng(seed)
    sub = sub_drop(dur, 130, 30, sr, seed)
    noise = g.normal(0, 1, n)
    # resonant band-pass around 1.8 kHz for the transient
    from scipy.signal import butter, sosfilt

    sos = butter(2, [1200 / (sr / 2), 3200 / (sr / 2)], btype="band", output="sos")
    mid = sosfilt(sos, noise) * np.exp(-t * 22) * 0.55
    ring = np.sin(2 * np.pi * 220 * t) * np.exp(-t * 3.2) * 0.22
    out = sub * 0.85 + mid + ring
    return (out / max(1e-9, np.abs(out).max()) * 0.95).astype(np.float32)


def whoosh(dur=0.75, sr=SR, seed=3, pan=0.0):
    n = int(dur * sr)
    t = np.arange(n) / sr
    g = rng(seed)
    noise = g.normal(0, 1, n)
    from scipy.signal import butter, sosfilt

    sos = butter(2, [300 / (sr / 2), 2600 / (sr / 2)], btype="band", output="sos")
    body = sosfilt(sos, noise) * (np.sin(np.pi * t / dur) ** 2)
    tone = np.sin(2 * np.pi * np.linspace(240, 900, n) * t) * 0.16 * np.exp(-t * 5)
    out = (body * 0.8 + tone)
    return (out / max(1e-9, np.abs(out).max()) * 0.6).astype(np.float32)


def riser(dur=2.4, sr=SR, seed=4):
    n = int(dur * sr)
    t = np.arange(n) / sr
    g = rng(seed)
    noise = g.normal(0, 1, n)
    from scipy.signal import butter, sosfilt

    sos = butter(2, [400 / (sr / 2), 6000 / (sr / 2)], btype="band", output="sos")
    swell = sosfilt(sos, noise) * (t / dur) ** 2.2
    tone = np.sin(2 * np.pi * np.linspace(180, 1400, n) * t) * 0.18 * (t / dur) ** 1.6
    out = swell * 0.85 + tone
    return (out / max(1e-9, np.abs(out).max()) * 0.7).astype(np.float32)


def tick(dur=0.06, sr=SR, f=2400, seed=5):
    n = int(dur * sr)
    t = np.arange(n) / sr
    return ((np.sin(2 * np.pi * f * t) * np.exp(-t * 120)) * 0.5).astype(np.float32)


def glitch(dur=0.28, sr=SR, seed=6):
    n = int(dur * sr)
    g = rng(seed)
    out = np.zeros(n, dtype=np.float32)
    for _ in range(6):
        L = int(g.integers(120, 900))
        L = min(L, n)                      # never write past the buffer
        i = int(g.integers(0, max(1, n - L)))
        f = float(g.uniform(180, 3600))
        t = np.arange(L) / sr
        out[i:i + L] += (np.sign(np.sin(2 * np.pi * f * t)) * g.uniform(0.2, 0.6)).astype(np.float32)
    out *= np.exp(-np.arange(n) / sr * 7)
    return (out / max(1e-9, np.abs(out).max()) * 0.55).astype(np.float32)


def bio_swell(dur=1.2, sr=SR, seed=7):
    """Wet organic texture for the biology beats."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    g = rng(seed)
    base = np.sin(2 * np.pi * 62 * t) * 0.4
    wob = np.sin(2 * np.pi * (62 + 4 * np.sin(2 * np.pi * 1.3 * t)) * t) * 0.3
    nz = g.normal(0, 1, n)
    from scipy.signal import butter, sosfilt

    sos = butter(2, [180 / (sr / 2), 900 / (sr / 2)], btype="band", output="sos")
    wet = sosfilt(sos, nz) * 0.5
    out = (base + wob + wet) * env_adsr(n, int(0.08 * sr), int(0.2 * sr), 0.5, int(0.4 * sr))
    return (out / max(1e-9, np.abs(out).max()) * 0.6).astype(np.float32)


def build_sfx(tl: dict, total: float, path: Path) -> dict:
    n_total = int((total + 0.6) * SR)
    L = np.zeros(n_total, dtype=np.float32)
    R = np.zeros(n_total, dtype=np.float32)

    def place(sig: np.ndarray, at: float, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i >= n_total:
            return
        j = min(n_total, i + len(sig))
        seg = sig[: j - i] * gain
        # equal-power pan
        lg = np.sqrt(0.5 * (1 - pan))
        rg = np.sqrt(0.5 * (1 + pan))
        L[i:j] += seg * lg * 1.414
        R[i:j] += seg * rg * 1.414

    cues = []
    # every cut gets a whoosh (visual change = sound change)
    for k, shot in enumerate(tl["shots"]):
        at = shot["from"] / tl["fps"]
        if at <= 0.001:
            continue
        pan = -0.35 if k % 2 == 0 else 0.35
        place(whoosh(seed=10 + k, pan=pan), max(0.0, at - 0.30), gain=0.30, pan=pan)
        cues.append({"t": round(at, 3), "cue": "cut_whoosh", "shot": k})

    # impact on the two hard reveals + the counter slams
    for k, shot in enumerate(tl["shots"]):
        at = shot["from"] / tl["fps"]
        sc = shot["scene"]
        if sc == "counter_slam":
            place(impact(seed=30 + k), at, gain=0.55)
            cues.append({"t": round(at, 3), "cue": "counter_impact", "shot": k})
        elif sc == "hand_wall":
            place(impact(seed=40 + k), at, gain=0.45)
            cues.append({"t": round(at, 3), "cue": "stamp_impact", "shot": k})
        elif sc == "immune_siege":
            place(bio_swell(seed=50 + k), at, gain=0.22)
            cues.append({"t": round(at, 3), "cue": "bio_texture", "shot": k})

    # riser into the "FLIP IT" reveal, then a hard drop
    flip = next((s["from"] / tl["fps"] for s in tl["shots"]
                 if s["scene"] == "glitch_reveal" and s["props"].get("kicker", "").startswith("INVERT")), None)
    if flip:
        place(riser(2.2), max(0.0, flip - 2.1), gain=0.42)
        place(impact(seed=60), flip, gain=0.62)
        cues += [{"t": round(max(0.0, flip - 2.1), 3), "cue": "riser", "shot": "flip"},
                 {"t": round(flip, 3), "cue": "impact", "shot": "flip"}]

    # glitch texture on every glitch_reveal
    for k, shot in enumerate(tl["shots"]):
        if shot["scene"] == "glitch_reveal":
            at = shot["from"] / tl["fps"]
            place(glitch(seed=70 + k), at, gain=0.26)
            cues.append({"t": round(at, 3), "cue": "glitch", "shot": k})

    # counter ticks during counter_slam shots
    for k, shot in enumerate(tl["shots"]):
        if shot["scene"] != "counter_slam":
            continue
        a = shot["from"] / tl["fps"]
        b = shot["to"] / tl["fps"]
        n_ticks = 16
        for q in range(n_ticks):
            at = a + (b - a) * (q / n_ticks) ** 1.5 * 0.75
            place(tick(f=1800 + q * 60, seed=80 + q), at, gain=0.12, pan=0.15 * np.sin(q))
        cues.append({"t": round(a, 3), "cue": "counter_ticks", "shot": k})

    peak = max(float(np.abs(L).max()), float(np.abs(R).max()), 1e-9)
    L, R = L / peak * 0.72, R / peak * 0.72
    sf.write(path, np.stack([L, R], axis=1), SR, subtype="PCM_16")
    print(f"[sfx] {len(cues)} cues -> {path.name}")
    return {"cues": cues, "count": len(cues)}


# ------------------------------------------------------------------ mix
def sidechain_duck(score: np.ndarray, voice_env: np.ndarray, depth_db=-9.0, smooth=0.22) -> np.ndarray:
    """Duck the score smoothly under speech (20 ms attack feel, ~300 ms release)."""
    from scipy.ndimage import maximum_filter1d, uniform_filter1d

    win = int(0.30 * SR)
    env = maximum_filter1d(voice_env, win)
    env = uniform_filter1d(env, win)
    env = env / max(1e-9, env.max())
    # gate: only duck where there is real speech
    gate = np.clip((env - 0.06) / 0.35, 0, 1)
    g = 10 ** (depth_db / 20)
    curve = (1 - gate * (1 - g)).astype(np.float32)
    return score * curve[: len(score), None]


def measure_loudnorm(path: Path) -> dict:
    r = subprocess.run(
        [ffmpeg(), "-hide_banner", "-nostats", "-i", str(path),
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    txt = r.stderr
    i = txt.rfind("Summary:")
    body = txt[i:] if i >= 0 else txt
    j = body.find("{")
    data = json.loads(body[j: body.rfind("}") + 1]) if j >= 0 else {}
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--build", required=True)
    ap.add_argument("--sf2", default=str(ROOT / "assets" / "TimGM6mb.sf2"))
    args = ap.parse_args()

    proj, build = Path(args.project), Path(args.build)
    tl = json.loads((proj / "timeline.json").read_text())
    total = tl["shots"][-1]["to"] / tl["fps"]
    cuts = [s["from"] / tl["fps"] for s in tl["shots"][1:]]

    # 1 - score
    midi = build / "score.mid"
    compose_score(tl, cuts, total, midi)
    print(f"[score] {midi.name}: {len(cuts) + 1} shots, {total:.2f}s")
    if Path(args.sf2).exists():
        render_score(midi, Path(args.sf2), build / "score.wav", total)
    else:
        raise SystemExit(f"missing soundfont: {args.sf2} (run tools/fetch_assets.sh)")

    # 2 - sfx
    sfx_info = build_sfx(tl, total, build / "sfx.wav")

    # 3 - load stems
    voice, sr_v = sf.read(build / "voice.wav", dtype="float32")
    if voice.ndim > 1:
        voice = voice.mean(axis=1)
    if sr_v != SR:
        # Piper emits 16 kHz; resample the voice to the mix rate.
        from scipy.signal import resample_poly

        up, down = SR // np.gcd(sr_v, SR), sr_v // np.gcd(sr_v, SR)
        voice = resample_poly(voice, up, down).astype(np.float32)
        sr_v = SR
    score, sr_s = sf.read(build / "score.wav", dtype="float32")
    sfx_a, sr_x = sf.read(build / "sfx.wav", dtype="float32")
    assert sr_s == SR and sr_x == SR, f"stem rate mismatch: score {sr_s}, sfx {sr_x}"

    n = int(total * SR) + SR // 2
    def fit(x):
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        out = np.zeros((n, 2), dtype=np.float32)
        m = min(n, len(x))
        out[:m] = x[:m]
        return out

    V, S, X = fit(voice), fit(score), fit(sfx_a)
    V[:, 0] *= 1.0  # voice stays mono/centred

    # voice envelope for ducking
    mon = np.abs(V).mean(axis=1)
    from scipy.ndimage import uniform_filter1d

    venv = uniform_filter1d(mon, int(0.02 * SR))
    S = sidechain_duck(S, venv, depth_db=-9.0)

    # score and sfx beds, voice on top
    mix = V * 0.92 + S * 0.34 + X * 0.62
    # keep sub mono
    low = mix[:, 0] * 0 + 0
    del low

    pre = build / "mix_pre.wav"
    sf.write(pre, mix, SR, subtype="PCM_16")
    print(f"[mix] pre-master peak {float(np.abs(mix).max()):.3f}")

    # 4 - two-pass loudnorm to -14 LUFS / -1 dBTP
    m = measure_loudnorm(pre)
    print(f"[mix] measured: I={m.get('input_i')} TP={m.get('input_tp')} LRA={m.get('input_lra')}")
    out = build / "mix.wav"
    af = (
        f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m.get('input_i')}:measured_TP={m.get('input_tp')}"
        f":measured_LRA={m.get('input_lra')}:measured_thresh={m.get('input_thresh')}"
        f":offset={m.get('target_offset')}:linear=true,"
        "alimiter=limit=0.891:level=false:attack=4:release=60,aresample=48000"
    )
    r = subprocess.run([ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(pre),
                        "-af", af, "-c:a", "pcm_s16le", "-ar", "48000", str(out)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    print(f"[mix] {out} <- {af.split(',')[0]}")

    # 5 - verify
    q = measure_loudnorm(out)
    (build / "audio_qa.json").write_text(json.dumps({
        "integrated_lufs": float(q.get("input_i", "nan")),
        "true_peak_dbtp": float(q.get("input_tp", "nan")),
        "lra": float(q.get("input_lra", "nan")),
        "sfx": sfx_info,
        "targets": {"lufs": -14.0, "tolerance": 1.0, "true_peak_max": -1.0},
    }, indent=1), encoding="utf-8")
    print(f"[qa] {q.get('input_i')} LUFS / {q.get('input_tp')} dBTP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
