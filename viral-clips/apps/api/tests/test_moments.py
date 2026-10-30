"""Candidate generation, scoring ranges and selection behaviour."""
from __future__ import annotations

from app.services.moments.candidates import build_candidates, candidate_features
from app.services.moments.scoring import (
    DIMENSIONS,
    heuristic_dimensions,
    score_candidates,
    weighted_total,
)


def _segments(n: int, length: float = 4.0) -> list[dict]:
    return [
        {"start": i * length, "end": (i + 1) * length, "text": f"This is sentence number {i}."}
        for i in range(n)
    ]


def test_transcript_candidates_respect_bounds():
    cands = build_candidates(
        duration_s=180.0,
        segments=_segments(45),
        words=[],
        speech_regions=[[0, 180]],
        min_s=15,
        max_s=45,
        target_windows=12,
    )
    assert cands
    for c in cands:
        assert c.start >= 0
        assert c.end <= 180.5
        assert 14.0 <= c.duration <= 46.0, c.duration
        assert c.text


def test_candidates_cover_the_whole_video_not_just_the_start():
    cands = build_candidates(
        duration_s=3600.0,
        segments=_segments(900),
        words=[],
        speech_regions=[],
        min_s=20,
        max_s=60,
        target_windows=30,
    )
    assert len(cands) >= 10
    assert max(c.start for c in cands) > 600, "selection must not stop at the first minutes"


def test_candidates_without_transcript_use_speech_regions():
    cands = build_candidates(
        duration_s=120.0,
        segments=[],
        words=[],
        speech_regions=[[5, 40], [70, 110]],
        min_s=15,
        max_s=45,
    )
    assert cands
    assert all(c.text == "" for c in cands)
    assert cands[0].start >= 4.9


def test_dedupe_removes_near_identical_windows_only():
    """Length variants intentionally overlap; only near-duplicates are dropped."""
    cands = build_candidates(
        duration_s=240.0,
        segments=_segments(60, 4.0),
        words=[],
        speech_regions=[],
        min_s=15,
        max_s=45,
        target_windows=18,
    )
    assert len(cands) > 5
    keys = {(c.start, c.end) for c in cands}
    assert len(keys) == len(cands), "identical windows must be de-duplicated"
    durations = {round(c.duration) for c in cands}
    assert len(durations) >= 2, "a single duration gives the selector no packing options"


def test_features_and_dimensions_stay_in_range():
    cand = build_candidates(
        duration_s=90.0,
        segments=_segments(22),
        words=[],
        speech_regions=[],
        min_s=15,
        max_s=40,
        target_windows=8,
    )[0]
    features = candidate_features(
        cand,
        energy={"times": [i * 0.25 for i in range(360)], "db": [-40 + (i % 17) for i in range(360)]},
        visuals={"available": True, "samples": [{"t": i, "face_x": 0.5, "motion": 0.1} for i in range(90)]},
        scenes=[{"time": 30.0, "score": 0.4}],
    )
    dims = heuristic_dimensions(features)
    assert set(dims) == {k for k, _ in DIMENSIONS}
    assert all(0 <= v <= 100 for v in dims.values())
    total = weighted_total(dims)
    assert 0 <= total <= 100


def test_heuristic_score_is_deterministic():
    cand = build_candidates(
        duration_s=60.0, segments=_segments(15), words=[], speech_regions=[],
        min_s=15, max_s=40,
    )[0]
    f = candidate_features(cand, energy=None, visuals=None, scenes=None)
    assert heuristic_dimensions(f) == heuristic_dimensions(f)


def test_selection_is_capped_and_sorted_without_duplicates():
    features = []
    for i in range(12):
        features.append(
            {
                "start": i * 20.0,
                "end": i * 20.0 + 30,
                "duration": 30.0,
                "text": f"Why do most creators fail at clip {i}? They never test hooks.",
                "word_count": 12,
                "wpm": 24.0,
                "questions": 1,
                "numbers": 0,
                "has_cta": False,
                "energy_mean": -20,
                "energy_peak": -12,
                "energy_std": 6,
                "motion_mean": 0.05,
                "face_coverage": 0.8,
                "scene_cuts": 1,
                "has_transcript": True,
                "reason": "test",
            }
        )
    selected, meta = score_candidates(features, target_clips=4, use_deep_model=False)
    assert len(selected) == 4
    assert meta["scoring_source"] == "heuristic"
    assert [s.start for s in selected] == sorted(s.start for s in selected)
    assert all(s.explanation for s in selected)
    for a, b in zip(selected, selected[1:], strict=False):
        overlap = min(a.end, b.end) - max(a.start, b.start)
        assert overlap <= 0.25 * min(a.duration, b.duration)


def test_score_candidates_never_claims_guaranteed_virality():
    features = [
        {
            "start": 0, "end": 30, "duration": 30, "text": "The truth about hiring.",
            "word_count": 5, "wpm": 10, "questions": 0, "numbers": 0, "has_cta": False,
            "energy_mean": -30, "energy_peak": -20, "energy_std": 2, "motion_mean": 0.01,
            "face_coverage": 0.0, "scene_cuts": 0, "has_transcript": True, "reason": "test",
        }
    ]
    selected, _ = score_candidates(features, target_clips=1)
    text = (selected[0].explanation + " " + " ".join(selected[0].tags)).lower()
    assert "guarantee" not in text
    assert "viral" not in text or "guaranteed" not in text
