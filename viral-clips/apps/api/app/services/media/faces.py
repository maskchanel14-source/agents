"""Visual intelligence: subject/face tracking, motion and brightness per sample.

Frames are sampled at a low rate (default 0.5 fps, capped) so a 60-minute video
costs a few hundred frames instead of tens of thousands. Detection uses an
OpenCV Haar cascade vendored under vendor/models (Apache-2.0, see licenses).

When no face is found we fall back to motion-weighted saliency, so crop
planning still behaves sensibly for animation, screen recordings and
single-slide videos.
"""
from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .ffmpeg import run_ffmpeg

log = logging.getLogger(__name__)

_MODEL = Path(__file__).resolve().parents[3] / "vendor" / "models" / "haarcascade_frontalface_default.xml"
FRAME_W = 480


@dataclass
class FrameAnalysis:
    t: float
    faces: list[tuple[float, float, float, float]] = field(default_factory=list)  # nx, ny, nw, nh
    motion: float = 0.0
    brightness: float = 0.0

    @property
    def face_x(self) -> float | None:
        if not self.faces:
            return None
        # weight by box area so the dominant speaker wins
        total = sum(w * h for _, _, w, h in self.faces) or 1.0
        return sum((x + w / 2) * (w * h) for x, _, w, h in self.faces) / total


def _cascade():
    try:
        import cv2

        if not _MODEL.is_file():
            return None
        c = cv2.CascadeClassifier(str(_MODEL))
        return None if c.empty() else c
    except Exception:  # pragma: no cover
        return None


def sample_frames(path: str, *, fps: float = 0.5, max_frames: int = 900) -> tuple[list[str], Path]:
    tmp = Path(tempfile.mkdtemp(prefix="vcframes-"))
    run_ffmpeg(
        [
            "-y", "-i", path,
            "-vf", f"fps={fps},scale={FRAME_W}:-2",
            "-frames:v", str(max_frames),
            "-q:v", "4",
            str(tmp / "f_%05d.jpg"),
        ],
        timeout=1800,
    )
    return sorted(str(p) for p in tmp.glob("f_*.jpg")), tmp


def analyze_visuals(path: str, *, fps: float = 0.5, max_frames: int = 900) -> dict:
    """Return normalised timeline of faces, motion and brightness."""
    try:
        import cv2
    except Exception:  # pragma: no cover
        return {"available": False, "samples": [], "reason": "opencv missing"}

    frames, tmp = sample_frames(path, fps=fps, max_frames=max_frames)
    cascade = _cascade()
    samples: list[dict] = []
    prev = None
    for i, fp in enumerate(frames):
        img = cv2.imread(fp, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        small = cv2.resize(img, (160, 90))
        motion = 0.0
        if prev is not None:
            motion = float(np.mean(cv2.absdiff(small, prev)) / 255.0)
        prev = small
        faces: list[tuple[float, float, float, float]] = []
        if cascade is not None:
            h, w = img.shape[:2]
            boxes = cascade.detectMultiScale(
                cv2.equalizeHist(img), scaleFactor=1.12, minNeighbors=5, minSize=(36, 36)
            )
            for x, y, bw, bh in boxes:
                faces.append((x / w, y / h, bw / w, bh / h))
        t = round(i / fps, 2)
        fx = None
        if faces:
            total = sum(bw * bh for _, _, bw, bh in faces) or 1.0
            fx = sum((x + bw / 2) * (bw * bh) for x, _, bw, bh in faces) / total
        samples.append(
            {
                "t": t,
                "face_x": round(fx, 4) if fx is not None else None,
                "face_count": len(faces),
                "motion": round(motion, 4),
                "brightness": round(float(img.mean()) / 255.0, 4),
            }
        )

    for fp in frames:
        try:
            os.remove(fp)
        except OSError:
            pass
    try:
        tmp.rmdir()
    except OSError:
        pass

    with_faces = sum(1 for s in samples if s["face_x"] is not None)
    return {
        "available": True,
        "sampled_fps": fps,
        "samples": samples,
        "face_coverage": round(with_faces / len(samples), 3) if samples else 0.0,
        "mean_motion": round(float(np.mean([s["motion"] for s in samples])), 4) if samples else 0.0,
    }
