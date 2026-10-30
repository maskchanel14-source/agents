"""Scene-cut detection using FFmpeg's scene score (no model download needed)."""
from __future__ import annotations

import re

from .ffmpeg import run_ffmpeg_capture

_PTS = re.compile(r"pts_time:([0-9.]+)")
_SCORE = re.compile(r"scene_score[=:]([0-9.]+)")


def detect_scenes(path: str, *, threshold: float = 0.32, max_seconds: int = 3600) -> list[dict]:
    """Return [{time, score}] cuts. Cheap, single decode pass at low resolution."""
    out = run_ffmpeg_capture(
        [
            "-t", str(max_seconds),
            "-i", path,
            "-an",
            "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo",
            "-f", "null", "-",
        ],
        timeout=1800,
    )
    cuts: list[dict] = []
    for line in out.splitlines():
        if "pts_time:" not in line:
            continue
        t = _PTS.search(line)
        s = _SCORE.search(line)
        if t:
            cuts.append({"time": round(float(t.group(1)), 2), "score": float(s.group(1)) if s else 0.0})
    return cuts
