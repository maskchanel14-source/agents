#!/usr/bin/env python3
"""Build a synthetic transcript fixture covering an arbitrary duration.

Used for demos and tests when no paid ASR provider is configured. The text is
hand-written; timings are evenly distributed. The provider is always recorded as
"fixture" so nobody mistakes it for real speech recognition.

Usage: python scripts/make_fixture.py [seconds] [out.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LINES = [
    "Halo semuanya, welcome back to the show.",
    "Today we are talking about why most creators give up in month two.",
    "The truth is that consistency beats talent almost every single time.",
    "Most people publish three videos and then quit because nobody watched.",
    "But here is the secret: the algorithm rewards the creators who keep shipping.",
    "So my challenge for you is simple. Publish one clip today.",
]


def build(duration_s: float) -> dict:
    loop_len = 60.0
    reps = max(1, round(duration_s / loop_len))
    per = duration_s / (len(LINES) * reps)
    segments, words = [], []
    for rep in range(reps):
        for line in LINES:
            start = round((rep * len(LINES) + LINES.index(line)) * per, 3)
            end = round(start + per, 3)
            segments.append({"start": start, "end": end, "text": line})
            tokens = line.split()
            weights = [max(2, len(t)) + 1 for t in tokens]
            span = (end - start) / sum(weights)
            cursor = start
            for tok, w in zip(tokens, weights, strict=True):
                dur = span * w
                words.append({"w": tok, "s": round(cursor, 3), "e": round(cursor + dur, 3)})
                cursor += dur
    return {
        "language": "id",
        "text": " ".join(s["text"] for s in segments),
        "segments": segments,
        "words": words,
        "_note": "synthetic demo fixture (hand-written text, synthetic timings)",
    }


def main() -> None:
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 240
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/fixtures/transcript.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = build(seconds)
    out.write_text(json.dumps(payload, indent=1))
    print(f"wrote {out} ({len(payload['segments'])} segments, {len(payload['words'])} words, {seconds:.0f}s)")


if __name__ == "__main__":
    main()
