#!/usr/bin/env python3
"""Original dark-pulse score and short-form sound effects for Shorts 023 v2.

No sampled music or third-party SFX are used. The score is deliberately built at
120 BPM so the Remotion timeline can cut every 15 frames at 30 fps.
"""
from __future__ import annotations

import math
import os
import struct
import wave

RATE = 48_000
DURATION = 41.0
BPM = 120.0
BPS = BPM / 60.0
ROOT = os.path.join(os.path.dirname(__file__), '..', 'public', 'shorts023', 'audio', 'v2')
os.makedirs(ROOT, exist_ok=True)


def clamp(value: float) -> float:
    return max(-0.98, min(0.98, value))


def sine(freq: float, t: float, phase: float = 0.0) -> float:
    return math.sin(2.0 * math.pi * freq * t + phase)


def noise(t: float, seed: float = 0.0) -> float:
    # Deterministic sample-level pseudo-noise: no sample file and stable render.
    return math.sin(math.sin(t * 17931.71 + seed) * 45758.5453)


def write_stereo(name: str, seconds: float, sample) -> None:
    path = os.path.join(ROOT, name)
    frames = int(seconds * RATE)
    with wave.open(path, 'wb') as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        data = bytearray()
        for index in range(frames):
            left, right = sample(index / RATE, seconds)
            data.extend(struct.pack('<hh', int(clamp(left) * 32767), int(clamp(right) * 32767)))
        out.writeframes(data)
    print(f'{path}: {seconds:.2f}s')


def dark_pulse(t: float, duration: float) -> tuple[float, float]:
    beat = t * BPS
    beat_index = int(beat)
    local = (beat - beat_index) / BPS
    bar = beat_index % 8
    fade = min(1.0, t / 1.2, max(0.0, (duration - t) / 1.5))

    # Cinematic sub hit. The rapid pitch fall gives each downbeat a physical impact.
    kick_env = math.exp(-local * 10.5)
    kick_freq = 83.0 - 37.0 * min(1.0, local * 4.5)
    kick = sine(kick_freq, t) * 0.40 * kick_env
    click = noise(t, 0.4) * math.exp(-local * 52.0) * 0.045

    # A minor 2-note pulse alternates in the stereo field; it becomes richer after the hook.
    root_notes = (55.0, 55.0, 65.41, 49.0, 55.0, 73.42, 65.41, 49.0)
    note = root_notes[bar]
    pluck_env = math.exp(-local * 4.9)
    pluck = (
        sine(note * 2.0, t) * 0.105
        + sine(note * 3.0, t + 0.012) * 0.045
        + sine(note * 4.0, t) * 0.018
    ) * pluck_env

    # Atmospheric bed is side-chained to the kick so narration remains intelligible.
    duck = 0.56 + 0.44 * min(1.0, local * 5.2)
    pad = (
        sine(55.0, t + 0.08 * sine(0.13, t)) * 0.070
        + sine(82.41, t) * 0.043
        + sine(164.81, t) * 0.014
    ) * duck

    # Restrained high pulse, opened only after the first two seconds.
    eighth = (t * BPS * 2.0) % 1.0
    hat_env = math.exp(-eighth * 19.0)
    high_open = min(1.0, max(0.0, (t - 1.8) / 1.0))
    hat = noise(t, 1.8) * hat_env * 0.018 * high_open

    # The second half has more pressure, then retreats for the final reveal.
    pressure = 0.75 + 0.25 * math.sin(min(1.0, max(0.0, (t - 8.0) / 20.0)) * math.pi)
    ending = 1.0 if t < 37.0 else max(0.52, 1.0 - (t - 37.0) * 0.10)
    body = (kick + click + pluck + pad + hat) * pressure * ending * fade
    width = sine(0.17, t) * 0.020 + (0.028 if bar in (2, 6) else -0.012)
    return body * (1.0 - width), body * (1.0 + width)


def whoosh(t: float, duration: float) -> tuple[float, float]:
    p = max(0.0, min(1.0, t / duration))
    env = math.sin(math.pi * p) ** 1.45
    tone = sine(165.0 + 1120.0 * p * p, t) * 0.070
    air_l = noise(t, 2.7) * 0.16
    air_r = noise(t, 3.9) * 0.16
    return env * (air_l + tone), env * (air_r - tone * 0.25)


def throw(t: float, duration: float) -> tuple[float, float]:
    p = max(0.0, min(1.0, t / duration))
    env = (1.0 - p) ** 1.8
    tone = sine(870.0 - 560.0 * p, t) * 0.11
    return env * (noise(t, 4.2) * 0.10 + tone), env * (noise(t, 5.1) * 0.10 - tone)


def sub_hit(t: float, duration: float) -> tuple[float, float]:
    p = max(0.0, min(1.0, t / duration))
    env = math.exp(-p * 4.8) * (1.0 - math.exp(-p * 55.0))
    sub = sine(78.0 - 35.0 * p, t) * 0.44
    body = sine(156.0 - 45.0 * p, t, 0.18) * 0.09
    crack_l = noise(t, 8.2) * math.exp(-p * 28.0) * 0.04
    crack_r = noise(t, 9.4) * math.exp(-p * 28.0) * 0.04
    return env * (sub + body + crack_l), env * (sub + body + crack_r)


def tick(t: float, duration: float) -> tuple[float, float]:
    p = max(0.0, min(1.0, t / duration))
    env = math.exp(-p * 18.0)
    tone = sine(1450.0 - 500.0 * p, t) * 0.12
    return env * (tone + noise(t, 11.0) * 0.04), env * (tone - noise(t, 12.0) * 0.03)


write_stereo('dark-pulse-score.wav', DURATION, dark_pulse)
write_stereo('sfx-whoosh.wav', 0.72, whoosh)
write_stereo('sfx-throw.wav', 0.44, throw)
write_stereo('sfx-sub-hit.wav', 0.90, sub_hit)
write_stereo('sfx-tick.wav', 0.16, tick)
