#!/usr/bin/env python3
"""
voice_kit.py -- script.txt -> voice.wav + words.json + captions.srt

Engine: Piper (VITS, en_US-lessac-medium), fully offline, no API keys.
Reads projects/<ID>/script.txt (one sentence per line), synthesises each line,
joins with breath gaps, light EQ, then derives word timings by distributing
each line's duration across its words weighted by syllable count.

Usage:
  voice_kit.py --project projects/DS-003 --build build/DS-003 \
               [--length-scale 0.95] [--noise-scale 0.667] [--gap 0.13]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VOICE = ROOT / ".models" / "lessac.onnx"


# ---------------------------------------------------------------- text helpers
def syllables(word: str) -> int:
    """Rough syllable count — good enough for proportional word timing."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 1
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(1, n)


def synth_line(voice, text: str, syn_config) -> np.ndarray:
    """Synthesise one line to a mono float32 numpy array."""
    import io

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voice.synthesize_wav(text, w, syn_config=syn_config)
    buf.seek(0)
    data, sr = sf.read(buf, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data, sr


# ---------------------------------------------------------------- main pipeline
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--build", required=True)
    ap.add_argument("--voice", default=str(DEFAULT_VOICE))
    ap.add_argument("--length-scale", type=float, default=0.95, help=">1 is slower")
    ap.add_argument("--noise-scale", type=float, default=0.667)
    ap.add_argument("--noise-w", type=float, default=0.8)
    ap.add_argument("--gap", type=float, default=0.13, help="seconds between lines")
    ap.add_argument("--tail", type=float, default=0.45, help="silence at the end")
    args = ap.parse_args()

    proj = Path(args.project)
    build = Path(args.build)
    build.mkdir(parents=True, exist_ok=True)

    script_path = proj / "script.txt"
    lines = [ln.strip() for ln in script_path.read_text(encoding="utf-8").splitlines()]
    lines = [ln for ln in lines if ln]
    if not lines:
        raise SystemExit("script.txt is empty")

    from piper import PiperVoice, SynthesisConfig

    voice = PiperVoice.load(args.voice)
    cfg = SynthesisConfig(
        length_scale=args.length_scale,
        noise_scale=args.noise_scale,
        noise_w_scale=args.noise_w,
    )

    print(f"[voice] {Path(args.voice).name} -> {len(lines)} lines")
    chunks: list[np.ndarray] = []
    words: list[dict] = []
    sr_hz = None
    cursor = 0.0  # seconds

    for idx, line in enumerate(lines):
        audio, sr = synth_line(voice, line, cfg)
        sr_hz = sr_hz or sr
        if sr != sr_hz:
            raise SystemExit(f"sample-rate drift: {sr} != {sr_hz}")

        # trim leading/trailing near-silence so gaps are exact
        env = np.abs(audio)
        thr = max(0.004, env.max() * 0.02)
        nz = np.nonzero(env > thr)[0]
        if len(nz):
            audio = audio[max(0, nz[0] - int(0.02 * sr)) : nz[-1] + int(0.05 * sr)]

        dur = len(audio) / sr
        toks = line.split()
        weights = np.array([syllables(t) for t in toks], dtype=float)
        weights /= weights.sum()
        t = cursor
        for tok, w in zip(toks, weights):
            d = dur * w
            words.append(
                {
                    "word": tok,
                    "start": round(t, 3),
                    "end": round(t + d, 3),
                    "line": idx,
                }
            )
            t += d

        chunks.append(audio)
        cursor += dur
        gap = args.gap * (1.6 if line.rstrip().endswith((".", "?", "!")) else 1.0)
        chunks.append(np.zeros(int(gap * sr), dtype=np.float32))
        cursor += gap

    chunks.append(np.zeros(int(args.tail * sr), dtype=np.float32))
    voice_audio = np.concatenate(chunks)

    # ---- light mastering: high-pass 70 Hz, presence lift, gentle comp
    sr = sr_hz
    voice_audio = highpass(voice_audio, sr, 70.0)
    voice_audio = presence_boost(voice_audio, sr, centre=3200.0, gain_db=1.8)
    peak = float(np.abs(voice_audio).max()) or 1.0
    voice_audio = voice_audio / peak * 0.82
    voice_audio = soft_compress(voice_audio, threshold=0.55, ratio=3.0)

    wav_path = build / "voice.wav"
    sf.write(wav_path, voice_audio.astype(np.float32), sr, subtype="PCM_16")

    total = len(voice_audio) / sr
    (build / "words.json").write_text(json.dumps(words, indent=1), encoding="utf-8")
    write_srt(words, proj / "captions.srt")
    write_spec(proj / "script_spec.json", lines, words, total, sr)

    n_words = len(words)
    print(f"[voice] {wav_path}  {total:.2f}s  {n_words} words  {sr} Hz")
    print(f"[voice] mean {n_words / total * 60:.0f} wpm")
    return 0


# ---------------------------------------------------------------- dsp helpers
def highpass(x: np.ndarray, sr: int, fc: float) -> np.ndarray:
    from scipy.signal import butter, sosfilt

    sos = butter(2, fc / (sr / 2), btype="highpass", output="sos")
    return sosfilt(sos, x).astype(np.float32)


def presence_boost(x: np.ndarray, sr: int, centre: float, gain_db: float) -> np.ndarray:
    """Peaking EQ via a biquad built by hand (no scipy iirpeak needed)."""
    from scipy.signal import sosfilt

    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * centre / sr
    alpha = np.sin(w0) / (2 * 1.0)
    b = np.array([1 + alpha * A, -2 * np.cos(w0), 1 - alpha * A])
    a = np.array([1 + alpha / A, -2 * np.cos(w0), 1 - alpha / A])
    b /= a[0]
    a = a / a[0]
    return sosfilt(np.array([[b[0], b[1], b[2], 1.0, a[1], a[2]]]), x).astype(np.float32)


def soft_compress(x: np.ndarray, threshold: float, ratio: float) -> np.ndarray:
    sign = np.sign(x)
    mag = np.abs(x)
    over = mag > threshold
    mag[over] = threshold + (mag[over] - threshold) / ratio
    return (sign * mag).astype(np.float32)


# ---------------------------------------------------------------- outputs
def write_srt(words: list[dict], path: Path, max_words: int = 4) -> None:
    """Group words into readable cues and emit SRT."""
    cues = []
    cur: list[dict] = []
    for w in words:
        cur.append(w)
        hard = w["word"].rstrip('"”).,!?;:').endswith((".", "?", "!", "…"))
        if len(cur) >= max_words or hard:
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)

    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        h, ms = divmod(ms, 3600_000)
        m, ms = divmod(ms, 60_000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    out = []
    for i, c in enumerate(cues, 1):
        start = c[0]["start"]
        end = max(c[-1]["end"], start + 0.4)
        out.append(f"{i}\n{ts(start)} --> {ts(end)}\n{' '.join(w['word'] for w in c)}\n")
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"[voice] {path}  {len(cues)} cues")


def write_spec(path: Path, lines, words, total, sr) -> None:
    spec = {
        "engine": "piper en_US-lessac-medium",
        "sample_rate": sr,
        "duration_s": round(total, 3),
        "word_count": len(words),
        "wpm": round(len(words) / total * 60, 1),
        "lines": [{"i": i, "text": ln} for i, ln in enumerate(lines)],
    }
    path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
