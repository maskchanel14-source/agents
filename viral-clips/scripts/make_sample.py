#!/usr/bin/env python3
"""Generate a deterministic sample video for local demos and smoke tests.

Produces a 1280x720 H.264/AAC file with a moving subject, three visual phases
and speech-like audio bursts separated by silence, so acoustic segmentation,
scene detection, subject tracking and rendering all have real signal to work on.

Usage: python scripts/make_sample.py [out.mp4] [seconds]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from app.services.media.ffmpeg import ffmpeg_path  # noqa: E402

SR = 48_000


def speech_like_audio(seconds: int) -> np.ndarray:
    """Bursts of voiced tone + noise with pauses; amplitude varies per phrase."""
    t = np.arange(int(SR * seconds)) / SR
    gate = (np.mod(t, 10.0) < 6.0).astype(np.float32)  # 6s speech / 4s pause
    # slow envelope so words feel articulated rather than a flat tone
    env = 0.55 + 0.45 * np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 0.7 * t)
    tone = (
        0.5 * np.sin(2 * np.pi * 185 * t)
        + 0.28 * np.sin(2 * np.pi * 370 * t)
        + 0.12 * np.sin(2 * np.pi * 740 * t)
    )
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 0.05, t.shape)
    sig = (tone * env + noise) * gate * 0.45
    return np.clip(sig, -1, 1).astype(np.float32)


def write_wav(path: Path, signal: np.ndarray) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((signal * 32767).astype("<i2").tobytes())


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "sample.mp4")
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    out.parent.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg_path()

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        wav = td_path / "audio.wav"
        write_wav(wav, speech_like_audio(seconds))
        silent = td_path / "video.mp4"
        # NOTE: the bundled static ffmpeg has libass but no freetype/drawtext,
        # so any on-screen text is burned through the ASS subtitle engine.
        subprocess.run(
            [
                ff, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", f"color=c=0x0b1020:s=1280x720:r=25:d={seconds}",
                "-f", "lavfi", "-i", f"color=c=0x1e3a8a:s=1280x720:r=25:d={seconds}",
                "-f", "lavfi", "-i", f"color=c=0x22d3ee:s=460x520:r=25:d={seconds}",
                "-filter_complex",
                "[0:v][1:v]overlay=x='if(lt(t,30),0,if(lt(t,60),420,840))'[bg];"
                "[bg][2:v]overlay=x='320+80*sin(t*0.9)':y=120[v]",
                "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                "-pix_fmt", "yuv420p", str(silent),
            ],
            check=True,
        )
        subprocess.run(
            [
                ff, "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(silent), "-i", str(wav),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-ac", "1",
                "-shortest", "-movflags", "+faststart", str(out),
            ],
            check=True,
        )
    print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB, {seconds}s)")


if __name__ == "__main__":
    main()
