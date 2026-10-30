#!/usr/bin/env python3
"""Build a synthetic transcript fixture covering an arbitrary duration.

Used for demos and tests when no paid ASR provider is configured. The text is
hand-written; timings are evenly distributed. The provider is always recorded as
"fixture" so nobody mistakes it for real speech recognition.

The script is a single continuous episode (Indonesian + English, the two launch
languages) so the demo shows *different* moments being picked with different
scores — a repeating 60-second loop would make every window score identically.

Usage: python scripts/make_fixture.py [seconds] [out.json]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# One continuous episode, roughly 10 s per line. Written to exercise the scorer:
# hooks, questions, numbers, a personal story, a contrarian take, and a CTA.
LINES = [
    "Halo semuanya, welcome back to the show.",
    "Hari ini kita bahas hal yang jarang dibicarakan: kenapa kreator berhenti di bulan kedua.",
    "Most creators give up in month two, and almost never because of talent.",
    "Sebenarnya masalahnya bukan skill, tapi ekspektasi yang tidak realistis.",
    "Kami mewawancarai 40 kreator tahun ini, dan 31 di antaranya berhenti sebelum video ke-20.",
    "The pattern was brutal: their first three videos flopped and they took it personally.",
    "Padahal platform tidak menghukum kamu karena gagal, platform hanya belum tahu siapa penontonmu.",
    "Kenapa kebanyakan orang berhenti? Karena mereka mengukur hasil mingguan di permainan tahunan.",
    "Jujur ya, saya juga hampir berhenti waktu itu.",
    "Waktu itu video ke-14 saya dapat 200 views, dan saya hampir hapus channel.",
    "Then one video hit 300 ribu views in three days, and it was the one I almost didn't upload.",
    "The difference was not the camera, it was the first three seconds.",
    "Hook adalah segalanya: kalau tiga detik pertama lemah, sisanya tidak akan ditonton.",
    "Contohnya, mulai dengan pertanyaan yang membuat orang penasaran, bukan dengan perkenalan.",
    "Our retention data shows a 40 percent drop when the intro runs longer than four seconds.",
    "Jadi rumusnya sederhana: potong intro, taruh klaim paling tajam di depan.",
    "Kedua, konsistensi mengalahkan bakat hampir setiap saat.",
    "Publish one clip today, not five clips someday.",
    "Kami melihat kreator yang posting tiga kali seminggu tumbuh tiga kali lebih cepat dari yang posting sebulan sekali.",
    "Tapi hati-hati, konsisten bukan berarti asal posting.",
    "Ada satu kesalahan besar yang hampir semua orang lakukan: menyalin gaya orang lain tanpa konteks.",
    "Akhirnya, cerita adalah alasan orang membagikan video.",
    "Data boleh meyakinkan, tapi cerita yang membuat orang menekan tombol share.",
    "So my challenge for you is simple: publish one clip today, then tell me what happened.",
]


def _script_for(duration_s: float) -> tuple[list[str], float]:
    """Pick the lines to speak and how long each one lasts."""
    duration_s = max(1.0, float(duration_s))
    # ~10 s per line; cycle the script when the target duration needs more lines.
    count = max(1, math.ceil(duration_s / 10.0))
    lines = [LINES[i % len(LINES)] for i in range(count)]
    return lines, duration_s / count


def build(duration_s: float) -> dict:
    lines, per = _script_for(duration_s)
    segments, words = [], []
    for idx, line in enumerate(lines):
        start = round(idx * per, 3)
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
