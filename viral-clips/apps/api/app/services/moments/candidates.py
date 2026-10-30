"""Candidate window generation over the *whole* timeline.

Two modes:
  transcript mode — snap windows to sentence/segment boundaries so a clip never
    starts or stops mid-sentence (preserves the speaker's meaning).
  no-transcript mode — derive windows from adaptive speech-activity regions so
    the product still works with ASR disabled (energy-only analysis).
Both modes cover the entire video, not just the opening minutes.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Candidate:
    start: float
    end: float
    text: str
    words: list[dict] = field(default_factory=list)
    segment_start: float = 0.0
    reason: str = ""

    @property
    def duration(self) -> float:
        return round(self.end - self.start, 3)


def _units_from_segments(segments: list[dict], max_unit_s: float = 14.0) -> list[dict]:
    units: list[dict] = []
    for seg in segments:
        start, end = float(seg["start"]), float(seg["end"])
        text = (seg.get("text") or "").strip()
        if not text or end <= start:
            continue
        if end - start <= max_unit_s:
            units.append({"start": start, "end": end, "text": text})
        else:
            # split very long segments on sentence-ish punctuation
            parts = [p.strip() for p in _split_sentences(text) if p.strip()]
            total = sum(len(p) for p in parts) or 1
            cursor = start
            for p in parts:
                share = (end - start) * len(p) / total
                units.append({"start": round(cursor, 3), "end": round(cursor + share, 3), "text": p})
                cursor += share
    return units


def _split_sentences(text: str) -> list[str]:
    out, buf = [], ""
    for ch in text:
        buf += ch
        if ch in ".!?。！？":
            out.append(buf)
            buf = ""
    if buf.strip():
        out.append(buf)
    return out


def _snap_to_boundary(units: list[dict], t: float, mode: str) -> float:
    if not units:
        return t
    if mode == "start":
        for u in units:
            if u["start"] >= t - 0.05:
                return u["start"]
        return units[-1]["start"]
    for u in reversed(units):
        if u["end"] <= t + 0.05:
            return u["end"]
    return units[-1]["end"]


def build_candidates(
    *,
    duration_s: float,
    segments: list[dict] | None,
    words: list[dict] | None,
    speech_regions: list[list[float]] | None,
    min_s: float = 15,
    max_s: float = 60,
    target_windows: int = 18,
) -> list[Candidate]:
    """Generate de-duplicated candidate windows covering the full timeline."""
    duration_s = max(1.0, duration_s)
    words = words or []
    min_s = max(6.0, min(min_s, duration_s))
    max_s = min(max(max_s, min_s + 2), duration_s)

    if segments:
        units = _units_from_segments(segments)
        if units:
            return _transcript_candidates(units, words, duration_s, min_s, max_s, target_windows)

    return _energy_candidates(speech_regions or [], duration_s, min_s, max_s, target_windows)


def _transcript_candidates(units, words, duration_s, min_s, max_s, target_windows) -> list[Candidate]:
    """Sentence-aligned windows in three length variants (short / medium / long).

    Variety matters: a 20 s window can be packed into gaps where a 45 s window
    would collide with its neighbour, so the selector gets real options without
    ever slicing through a sentence.
    """
    out: list[Candidate] = []
    n = len(units)
    hop = max(1, n // max(8, target_windows))
    mid = (min_s + max_s) / 2
    variants = [min_s * 1.2, mid, max_s * 0.92]

    for i in range(0, n, hop):
        start = units[i]["start"]
        if start >= duration_s - min_s:
            break
        for k, desired in enumerate(variants):
            best_end, best_gap = None, 1e9
            j = i
            while j < n:
                end = units[j]["end"]
                span = end - start
                if span > max_s + 0.01:
                    break
                if span >= min_s:
                    gap = abs(span - desired)
                    if gap < best_gap:
                        best_gap, best_end = gap, end
                j += 1
            if best_end is None:
                continue
            text = " ".join(
                u["text"] for u in units[i:j] if u["start"] >= start - 0.05 and u["end"] <= best_end + 0.05
            ).strip()
            out.append(
                Candidate(
                    start=round(start, 2),
                    end=round(best_end, 2),
                    text=text,
                    words=[
                        w for w in words
                        if float(w["s"]) >= start - 0.2 and float(w["e"]) <= best_end + 0.2
                    ],
                    reason=f"sentence_boundary_window_{k}",
                )
            )
    return _dedupe(out, min_overlap=0.8)


def _merge_blocks(regions: list[list[float]], gap_s: float = 6.0) -> list[list[float]]:
    """Join speech regions separated by short pauses into conversation blocks.

    A 6 s tolerance keeps normal conversational back-and-forth in one block while
    still splitting on real breaks (music, ad reads, camera resets).
    """
    blocks: list[list[float]] = []
    for r_start, r_end in sorted(regions):
        if blocks and r_start - blocks[-1][1] <= gap_s:
            blocks[-1][1] = max(blocks[-1][1], r_end)
        else:
            blocks.append([r_start, r_end])
    return blocks


def _energy_candidates(regions, duration_s, min_s, max_s, target_windows) -> list[Candidate]:
    """No transcript available: window over conversation blocks across the file.

    Uses adaptive speech-activity regions (already merged for short pauses) so a
    video longer than the opening minutes still yields candidates later on.
    """
    blocks = _merge_blocks(regions or [], gap_s=6.0)
    if not blocks:
        blocks = [[0.0, duration_s]]
    # never let a block run past the media duration
    blocks = [[max(0.0, a), min(duration_s, b)] for a, b in blocks if min(duration_s, b) - a >= 8.0]

    length = min(max_s, max(min_s, (min_s + max_s) / 2))
    out: list[Candidate] = []
    for b_start, b_end in blocks:
        span = b_end - b_start
        if span < 8.0:
            continue
        window = min(length, span)
        cursor = b_start
        while cursor + 8.0 <= b_end + 0.25:
            end = min(cursor + window, b_end)
            if end - cursor >= 8.0:
                out.append(
                    Candidate(
                        start=round(cursor, 2),
                        end=round(end, 2),
                        text="",
                        reason="speech_activity_window",
                    )
                )
            if end >= b_end - 0.25:
                break
            cursor += max(4.0, window * 0.45)

    if not out:
        # last resort: evenly spaced windows covering the whole file
        n = max(1, int(duration_s // max(8.0, length)))
        for i in range(min(n, max(1, target_windows))):
            start = min(duration_s - 8.0, i * length)
            out.append(
                Candidate(
                    start=round(max(0.0, start), 2),
                    end=round(min(duration_s, start + length), 2),
                    text="",
                    reason="fallback_window",
                )
            )
    return _dedupe(out, min_overlap=0.55)[: max(4, target_windows)]


def _dedupe(cands: list[Candidate], *, min_overlap: float = 0.55) -> list[Candidate]:
    """Drop near-duplicate windows while keeping full-timeline coverage."""
    kept: list[Candidate] = []
    for c in sorted(cands, key=lambda c: (c.start, -c.duration)):
        duplicate = False
        for k in kept:
            inter = max(0.0, min(c.end, k.end) - max(c.start, k.start))
            union = max(c.duration, k.duration) or 1
            if inter / union >= min_overlap:
                duplicate = True
                break
        if not duplicate:
            kept.append(c)
    return kept


def candidate_features(
    cand: Candidate,
    *,
    energy: dict | None,
    visuals: dict | None,
    scenes: list[dict] | None,
    language_hint: str | None = None,
) -> dict:
    """Audio/visual/textual feature bundle used by the scorer."""
    text = cand.text or ""
    low = text.lower()
    nl = max(1, len(text.split()))
    wpm = nl / max(cand.duration, 1) * 60

    def _in_range(values: list[tuple[float, float]], col: str) -> list[float]:
        return [v for t, v in values if cand.start <= t <= cand.end]

    energy_db: list[float] = []
    if energy and energy.get("db"):
        times = energy.get("times") or []
        energy_db = [
            d for t, d in zip(times, energy["db"], strict=False) if cand.start <= t <= cand.end
        ]
    motion_vals: list[float] = []
    face_vals: list[float] = []
    if visuals and visuals.get("samples"):
        sel = [s for s in visuals["samples"] if cand.start <= s["t"] <= cand.end]
        motion_vals = [s.get("motion", 0.0) for s in sel]
        face_vals = [1.0 for s in sel if s.get("face_x") is not None]

    cuts = [c for c in (scenes or []) if cand.start <= c["time"] <= cand.end]

    return {
        "duration": cand.duration,
        "word_count": nl,
        "wpm": round(wpm, 1),
        "questions": low.count("?") + sum(low.count(m) for m in (" kenapa", " mengapa", " why", " how ")),
        "numbers": sum(1 for tok in text.split() if any(ch.isdigit() for ch in tok)),
        "has_cta": any(m in low for m in ("subscribe", "follow", "comment", "share", "like")),
        "energy_mean": round(sum(energy_db) / len(energy_db), 2) if energy_db else 0.0,
        "energy_peak": round(max(energy_db), 2) if energy_db else 0.0,
        "energy_std": round(_std(energy_db), 2),
        "motion_mean": round(sum(motion_vals) / len(motion_vals), 4) if motion_vals else 0.0,
        "face_coverage": round(sum(face_vals) / len(face_vals), 3) if face_vals else 0.0,
        "scene_cuts": len(cuts),
        "language_hint": language_hint,
        "start": cand.start,
        "end": cand.end,
        "reason": cand.reason,
        "text": text,
        "has_transcript": bool(text),
    }


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
