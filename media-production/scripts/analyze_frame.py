#!/usr/bin/env python3
"""
Objective frame QA for the animated shorts.

Measures the things the 7 style agents are supposed to judge, numerically, so
fixes are driven by data instead of vibes:

  palette    – are only the 6 sanctioned colours on screen? is pure black absent?
  depth      – is the background softer than the subject? (Laplacian energy)
  outlines   – ink edge density + how dark the darkest ink is (never #000)
  grade      – RMS contrast, warm cast, corner-vs-centre falloff (vignette)
  exposure   – mean luminance, clipped highlights/shadows
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np

FFMPEG = subprocess.run(
    ["node", "-e",
     "console.log(require('/home/user/agents/media-production/node_modules/"
     "@ffmpeg-installer/ffmpeg').path)"],
    capture_output=True, text=True, check=True).stdout.strip()

PALETTE = {
    "sun":    (0xFF, 0xD2, 0x3F),
    "pop":    (0xFF, 0x6B, 0x6B),
    "sky":    (0x4E, 0xCD, 0xC4),
    "town":   (0x1A, 0x53, 0x5C),
    "paper":  (0xF7, 0xFF, 0xF7),
    "shadow": (0x2A, 0x2E, 0x6B),
}


def load(path: str) -> np.ndarray:
    out = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    # dimensions come from ffprobe-less ffmpeg stderr parsing
    probe = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True).stderr
    w = h = None
    for line in probe.splitlines():
        if "Stream #" in line and "Video:" in line:
            for chunk in line.split(","):
                chunk = chunk.strip()
                if "x" in chunk and chunk.split(" ")[0].count("x") == 1:
                    try:
                        w, h = (int(v) for v in chunk.split(" ")[0].split("x"))
                    except ValueError:
                        pass
    if w is None:
        raise RuntimeError(f"could not read dimensions of {path}")
    return np.frombuffer(out, dtype=np.uint8).reshape(h, w, 3)


def luma(img: np.ndarray) -> np.ndarray:
    f = img.astype(np.float32) / 255.0
    return 0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2]


def lap_energy(gray: np.ndarray) -> float:
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    p = np.pad(gray, 1, mode="edge")
    out = (
        k[0, 1] * (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:])
        - 4 * p[1:-1, 1:-1]
    )
    return float(np.mean(np.abs(out)))


def palette_report(img: np.ndarray) -> dict:
    f = img.astype(np.int16).reshape(-1, 3)
    total = len(f)
    counts = {}
    for name, (r, g, b) in PALETTE.items():
        d = np.abs(f - np.array([r, g, b], dtype=np.int16)).sum(axis=1)
        counts[name] = round(float((d < 90).sum()) / total * 100, 2)
    near_black = float(((f.sum(axis=1)) < 24).sum()) / total * 100
    # how much of the frame is explained by the 6 colours (with tolerance)
    dmin = np.full(total, 9999, dtype=np.int32)
    for (r, g, b) in PALETTE.values():
        d = np.abs(f - np.array([r, g, b], dtype=np.int16)).sum(axis=1)
        dmin = np.minimum(dmin, d.astype(np.int32))
    covered = float((dmin < 120).sum()) / total * 100
    return {"pct": counts, "pct_near_black": round(near_black, 3),
            "pct_within_palette_t120": round(covered, 2)}


def analyze(path: str) -> dict:
    img = load(path)
    h, w, _ = img.shape
    g = luma(img)

    # thirds: the short's subject sits in the middle band, background top/bottom
    bands = {
        "top": g[: h // 3],
        "middle": g[h // 3: 2 * h // 3],
        "bottom": g[2 * h // 3:],
    }

    # vignette: mean luma of the four corners vs the centre
    m = int(min(h, w) * 0.12)
    corners = np.concatenate([
        g[:m, :m].ravel(), g[:m, -m:].ravel(), g[-m:, :m].ravel(), g[-m:, -m:].ravel()
    ])
    cy, cx = h // 2, w // 2
    centre = g[cy - m: cy + m, cx - m: cx + m]

    r, gg, b = (img[..., i].astype(np.float32).mean() for i in range(3))

    return {
        "file": os.path.basename(path),
        "size": f"{w}x{h}",
        "mean_luma": round(float(g.mean()), 4),
        "rms_contrast": round(float(g.std()), 4),
        "clipped_high_pct": round(float((g > 0.985).mean()) * 100, 3),
        "clipped_low_pct": round(float((g < 0.015).mean()) * 100, 3),
        "warm_cast_r_minus_b": round(float((r - b) / 255.0), 4),
        "vignette_corner_over_centre": round(float(corners.mean() / max(1e-6, centre.mean())), 4),
        "sharpness_laplacian": {k: round(lap_energy(v), 5) for k, v in bands.items()},
        "bg_vs_subject_softness": round(
            float(((bands["top"] if False else np.concatenate([bands["top"].ravel(), bands["bottom"].ravel()])).size and 0) or
                  (lap_energy(bands["top"]) + lap_energy(bands["bottom"])) / 2 /
                  max(1e-6, lap_energy(bands["middle"]))), 4),
        "palette": palette_report(img),
    }


if __name__ == "__main__":
    results = [analyze(p) for p in sys.argv[1:]]
    print(json.dumps(results if len(results) > 1 else results[0], indent=2))
