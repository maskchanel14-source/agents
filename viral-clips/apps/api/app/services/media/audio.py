"""Audio extraction, loudness/energy analysis and speech-region detection."""
from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .ffmpeg import run_ffmpeg

SR = 16_000


def extract_wav(src: str, dst: Path, *, sr: int = SR) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "-y", "-i", src,
            "-vn", "-ac", "1", "-ar", sr, "-c:a", "pcm_s16le",
            str(dst),
        ],
        timeout=1800,
    )
    return dst


def load_pcm(wav_path: str | Path) -> np.ndarray:
    with wave.open(str(wav_path), "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        width = wf.getsampwidth()
        ch = wf.getnchannels()
    if width != 2:
        raise ValueError("expected 16-bit PCM wav")
    y = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        y = y.reshape(-1, ch).mean(axis=1)
    return y


@dataclass
class EnergyProfile:
    hop_s: float
    times: list[float]
    rms: list[float]
    db: list[float]

    def to_dict(self) -> dict:
        return {
            "hop_s": self.hop_s,
            "times": self.times,
            "rms": [round(v, 5) for v in self.rms],
            "db": [round(v, 2) for v in self.db],
        }


def energy_profile(y: np.ndarray, sr: int = SR, hop_s: float = 0.25) -> EnergyProfile:
    hop = max(1, int(sr * hop_s))
    n = len(y) // hop
    if n == 0:
        return EnergyProfile(hop_s, [], [], [])
    frames = y[: n * hop].reshape(n, hop)
    rms = np.sqrt(np.mean(frames.astype(np.float32) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    times = [round(i * hop_s, 3) for i in range(n)]
    return EnergyProfile(hop_s, times, rms.tolist(), db.tolist())


def speech_regions(profile: EnergyProfile, *, min_gap_s: float = 0.6, min_len_s: float = 1.2):
    """Adaptive-threshold speech activity from the RMS curve.

    Returns merged [start, end] regions in seconds. Used for silence trimming,
    candidate boundaries and as a transcript-free segmentation signal.
    """
    if not profile.db:
        return []
    db = np.array(profile.db, dtype=np.float32)
    floor = float(np.percentile(db, 12))
    peak = float(np.percentile(db, 92))
    thr = floor + max(6.0, 0.30 * max(peak - floor, 1.0))
    active = db > thr

    regions: list[list[float]] = []
    hop = profile.hop_s
    i = 0
    while i < len(active):
        if active[i]:
            j = i
            while j < len(active) and active[j]:
                j += 1
            regions.append([i * hop, j * hop])
            i = j
        else:
            i += 1

    merged: list[list[float]] = []
    for r in regions:
        if merged and r[0] - merged[-1][1] < min_gap_s:
            merged[-1][1] = r[1]
        else:
            merged.append(list(r))
    return [[round(a, 2), round(b, 2)] for a, b in merged if b - a >= min_len_s]


def dynamic_range_db(profile: EnergyProfile) -> float:
    """Spread of loudness — a proxy for vocal energy / excitement."""
    if not profile.db:
        return 0.0
    return float(np.percentile(profile.db, 95) - np.percentile(profile.db, 20))


def loudness_normalize_args() -> list[str]:
    return ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
