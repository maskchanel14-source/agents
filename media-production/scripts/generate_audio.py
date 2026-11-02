#!/usr/bin/env python3
"""Generate original non-percussive ambient score and soft transition effects."""
from __future__ import annotations

import math
import os
import random
import struct
import wave

RATE = 48_000
ROOT = os.path.join(os.path.dirname(__file__), '..', 'public', 'shorts023', 'audio')
os.makedirs(ROOT, exist_ok=True)


def write_stereo(name: str, seconds: float, sample):
    frames = int(seconds * RATE)
    path = os.path.join(ROOT, name)
    with wave.open(path, 'wb') as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        buf = bytearray()
        for i in range(frames):
            t = i / RATE
            left, right = sample(t, seconds)
            left = max(-0.98, min(0.98, left))
            right = max(-0.98, min(0.98, right))
            buf.extend(struct.pack('<hh', int(left * 32767), int(right * 32767)))
        out.writeframes(buf)
    print(f'{path}: {seconds:.2f}s')


def ambient(t: float, duration: float):
    # Evolving, non-percussive drone: low, fifth, high shimmer; no tick/click transient.
    fade = min(1, t / 2.5, (duration - t) / 3.0)
    wobble = 1 + 0.018 * math.sin(t * 0.17)
    low = math.sin(2 * math.pi * 49.0 * wobble * t) * 0.17
    fifth = math.sin(2 * math.pi * 73.42 * t + 0.4 * math.sin(t * 0.24)) * 0.09
    air = math.sin(2 * math.pi * (196 + 3 * math.sin(t * 0.11)) * t) * 0.018
    glass = math.sin(2 * math.pi * 392 * t + math.sin(t * 0.4)) * 0.012
    evolving = 0.55 + 0.45 * math.sin(t * 0.21 + 0.8) ** 2
    left = (low + fifth + air + glass) * fade * evolving
    right = (low * 0.96 + fifth * 1.08 + air * 0.78 + glass * 1.25) * fade * evolving
    return left, right


def riser(t: float, duration: float):
    p = max(0, min(1, t / duration))
    env = math.sin(math.pi * p) ** 1.2
    freq = 110 * (1 + 8.6 * p * p)
    tone = math.sin(2 * math.pi * freq * t + 0.65 * math.sin(t * 7.2))
    halo = math.sin(2 * math.pi * freq * 2.01 * t)
    return env * (tone * 0.17 + halo * 0.035), env * (tone * 0.15 - halo * 0.04)


def shimmer(t: float, duration: float):
    p = max(0, min(1, t / duration))
    env = math.sin(math.pi * p) ** 1.8
    freqs = (523.25, 659.25, 783.99, 1046.5)
    l = sum(math.sin(2 * math.pi * (f + p * 16) * t + i) for i, f in enumerate(freqs)) / len(freqs)
    r = sum(math.sin(2 * math.pi * (f + p * 22) * t + i * 1.23) for i, f in enumerate(freqs)) / len(freqs)
    return env * l * 0.10, env * r * 0.10


def impact(t: float, duration: float):
    # Soft low boom and reverse-like harmonic tail; no sharp attack.
    p = max(0, min(1, t / duration))
    env = (1 - p) ** 2.1 * (1 - math.exp(-t * 14))
    sub = math.sin(2 * math.pi * (57 - 14 * p) * t)
    body = math.sin(2 * math.pi * (114 - 20 * p) * t + 0.3)
    return env * (sub * 0.30 + body * 0.07), env * (sub * 0.30 - body * 0.05)


write_stereo('ambient-bed.wav', 41.0, ambient)
write_stereo('riser.wav', 2.7, riser)
write_stereo('shimmer.wav', 2.1, shimmer)
write_stereo('impact.wav', 2.4, impact)
