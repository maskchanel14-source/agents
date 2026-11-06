#!/usr/bin/env python3
"""
vo_build.py -- turn the raw narration takes into timed voice-over stems.

Input : public/audio/vo/s1.mp3 .. s9.mp3   (one line per shot, in shot order)
Output: public/audio/vo/vo_<shotname>.wav  (48 kHz mono, trimmed to fit the shot)

For every line we
  1. strip the leading / trailing silence,
  2. detect the internal pauses,
  3. tighten those pauses until the line fits inside its shot with head-room,
  4. fall back to a light tempo lift only if pause tightening is not enough.

Usage: vo_build.py --shots build/shots.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
SR = 48000
HEAD = 0.15          # silence kept before the first word
TAIL = 0.22          # ... and after the last one


def ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(src: Path) -> np.ndarray:
    tmp = src.with_suffix(".tmp.wav")
    subprocess.run(
        [ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-ar", str(SR), "-ac", "1", str(tmp)],
        check=True,
    )
    x, _ = sf.read(str(tmp), dtype="float32")
    tmp.unlink(missing_ok=True)
    return x


def find_gaps(x: np.ndarray, thresh_db: float = -40.0, min_len: float = 0.12):
    """Return [(start, end)] of internal silences, in seconds."""
    win = int(0.01 * SR)
    n = len(x) // win
    frames = x[: n * win].reshape(n, win)
    rms = 20 * np.log10(np.maximum(np.sqrt((frames ** 2).mean(axis=1)), 1e-9))
    quiet = rms < thresh_db
    gaps = []
    i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * win / SR >= min_len:
                gaps.append((i * win / SR, j * win / SR))
            i = j
        else:
            i += 1
    return gaps


def splice(x: np.ndarray, gaps, new_lens) -> np.ndarray:
    """Rebuild the take with each internal gap shortened to new_lens[i]."""
    out = []
    cursor = 0
    for (a, b), keep in zip(gaps, new_lens):
        ia, ib = int(a * SR), int(b * SR)
        out.append(x[cursor:ia])
        # keep `keep` seconds from the middle of the pause, with a short fade
        mid = (ia + ib) // 2
        half = int(keep * SR / 2)
        seg = x[max(cursor, mid - half): mid + half].copy()
        fade = min(int(0.008 * SR), len(seg) // 2)
        if fade > 1:
            ramp = np.linspace(0, 1, fade)
            seg[:fade] *= ramp
            seg[-fade:] *= ramp[::-1]
        out.append(seg)
        cursor = ib
    out.append(x[cursor:])
    return np.concatenate(out)


def tempo(x: np.ndarray, factor: float) -> np.ndarray:
    """Cheap time-stretch via ffmpeg atempo (keeps pitch)."""
    if abs(factor - 1.0) < 0.01:
        return x
    a = Path(tempfile.gettempdir()) / "vo_a.wav"
    b = Path(tempfile.gettempdir()) / "vo_b.wav"
    sf.write(a, x, SR)
    subprocess.run(
        [ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(a),
         "-af", f"atempo={factor:.4f}", "-ar", str(SR), str(b)],
        check=True,
    )
    y, _ = sf.read(str(b), dtype="float32")
    a.unlink(missing_ok=True)
    b.unlink(missing_ok=True)
    return y


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True)
    ap.add_argument("--total", type=float, default=45.5)
    args = ap.parse_args()

    shots = json.loads(Path(args.shots).read_text())
    vo_dir = ROOT / "public" / "audio" / "vo"
    report = []

    for i, s in enumerate(shots, start=1):
        src = vo_dir / f"s{i}.mp3"
        if not src.exists():
            continue
        shot_len = (s["to"] - s["from"]) / s["fps"]
        budget = shot_len - 0.45          # leave room for the cut + a breath
        x = decode(src)

        # 1. head / tail trim
        loud = np.where(np.abs(x) > 10 ** (-42 / 20))[0]
        if len(loud):
            x = x[max(0, loud[0] - int(HEAD * SR)): loud[-1] + int(TAIL * SR)]

        # 2. tighten pauses, biggest first, floor 0.16 s
        gaps = find_gaps(x)
        lens = [b - a for a, b in gaps]
        new = list(lens)
        dur = len(x) / SR
        if dur > budget:
            for idx in np.argsort(lens)[::-1]:
                excess = dur - budget
                if excess <= 0:
                    break
                room = max(0.0, new[idx] - 0.16)
                take = min(room, excess)
                new[idx] -= take
                dur -= take
            x = splice(x, gaps, new)

        # 3. last resort: a very small tempo lift
        factor = 1.0
        if len(x) / SR > budget + 0.08:
            factor = min(1.12, len(x) / SR / budget)
            x = tempo(x, factor)
        if len(x) / SR > budget:
            print(f"[vo] {s['name']}: still {len(x)/SR:.2f}s > budget {budget:.2f}s", file=sys.stderr)

        # 4. level: consistent RMS, soft peak guard
        rms = float(np.sqrt(np.mean(x ** 2))) or 1e-6
        x *= 0.12 / rms
        peak = float(np.max(np.abs(x))) or 1e-6
        if peak > 0.89:
            x *= 0.89 / peak

        out = vo_dir / f"vo_{s['name']}.wav"
        sf.write(out, x.astype(np.float32), SR, subtype="PCM_24")
        report.append((s["name"], len(x) / SR, shot_len, budget, factor))

    print(f"{'shot':8} {'vo':>6} {'shot':>6} {'budget':>7}  tempo")
    for name, d, sl, b, f in report:
        flag = "  <-- over" if d > b else ""
        print(f"{name:8} {d:6.2f} {sl:6.2f} {b:7.2f}  x{f:.3f}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
