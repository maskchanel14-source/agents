"""A synthetic transcript used by the fixture-ASR caption test.

Text is hand-written (a realistic bilingual podcast exchange). Timings are
evenly distributed across the file so word-level caption rendering can be
verified without calling a paid ASR API. This is NOT speech recognition output
and is never used unless ASR_PROVIDER=fixture is explicitly configured.
"""
from __future__ import annotations

SEGMENTS = [
    "Halo semuanya, welcome back to the show.",
    "Today we are talking about why most creators give up in month two.",
    "The truth is that consistency beats talent almost every single time.",
    "Most people publish three videos and then quit because nobody watched.",
    "But here is the secret: the algorithm rewards the creators who keep shipping.",
    "So my challenge for you is simple. Publish one clip today.",
]

TOTAL_SECONDS = 60.0


def build() -> dict:
    per = TOTAL_SECONDS / len(SEGMENTS)
    segments, words = [], []
    for i, text in enumerate(SEGMENTS):
        start = round(i * per, 3)
        end = round(start + per, 3)
        segments.append({"start": start, "end": end, "text": text})
        tokens = text.split()
        # weight word durations by length so long words linger on screen
        weights = [max(2, len(t)) + 1 for t in tokens]
        span = (end - start) / sum(weights)
        cursor = start
        for tok, w in zip(tokens, weights, strict=True):
            dur = span * w
            words.append({"w": tok, "s": round(cursor, 3), "e": round(cursor + dur, 3)})
            cursor += dur
    return {
        "language": "id",
        "text": " ".join(SEGMENTS),
        "segments": segments,
        "words": words,
        "_note": "synthetic fixture (hand-written text, synthetic timings) for tests/demos",
    }
