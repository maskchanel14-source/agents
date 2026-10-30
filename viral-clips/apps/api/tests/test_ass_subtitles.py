"""Subtitle engine: cue grouping, ASS output, keyword highlighting, presets."""
from __future__ import annotations

from app.services.media.ass import (
    Cue,
    ass_time,
    build_ass,
    extract_keywords,
    group_cues,
    hex_to_ass,
    sentences_to_words,
    words_in_range,
)
from app.services.media.presets import PRESETS, get_preset, preset_allowed_for_plan


def _words(spec: list[tuple[str, float, float]]) -> list[dict]:
    return [{"w": w, "s": s, "e": e} for w, s, e in spec]


def test_ass_time_formatting():
    assert ass_time(0) == "0:00:00.00"
    assert ass_time(65.5) == "0:01:05.50"
    assert ass_time(3725.25) == "1:02:05.25"
    assert ass_time(-3) == "0:00:00.00"


def test_hex_to_ass_color_swaps_to_bgr():
    assert hex_to_ass("#FF0000") == "&H000000FF"
    assert hex_to_ass("#00FF00") == "&H0000FF00"
    assert hex_to_ass("FFFFFF") == "&H00FFFFFF"


def test_group_cues_respects_max_words_and_gaps():
    words = _words([("satu", 0.0, 0.3), ("dua", 0.3, 0.6), ("tiga", 0.6, 0.9), ("empat", 3.0, 3.2)])
    cues = group_cues(words, max_words=2)
    # "satu dua" (full group) | "tiga" (max words reached) | "empat" (pause split)
    assert [len(c.words) for c in cues] == [2, 1, 1]
    assert cues[-1].start == 3.0, "a pause must start a new caption chunk"
    assert all(c.end > c.start for c in cues)


def test_group_cues_never_overlaps():
    words = _words([(f"w{i}", i * 0.2, i * 0.2 + 0.19) for i in range(20)])
    cues = group_cues(words, max_words=3)
    for a, b in zip(cues, cues[1:], strict=False):
        assert a.end <= b.start + 0.001


def test_build_ass_contains_style_and_events():
    cues = group_cues(_words([("viral", 0.0, 0.5), ("clip", 0.5, 1.0)]), max_words=4)
    ass = build_ass(cues, preset="bold_viral", keywords={"viral"})
    assert "[Script Info]" in ass and "[V4+ Styles]" in ass and "[Events]" in ass
    assert "PlayResX: 1080" in ass and "PlayResY: 1920" in ass
    assert "DejaVu Sans" in ass
    assert "Dialogue:" in ass
    # keyword gets the accent colour override
    assert "&H0015CCFA" in ass.upper() or "\\c&H" in ass


def test_build_ass_uppercases_for_viral_preset_only():
    cues = group_cues(_words([("hello", 0.0, 0.5), ("world", 0.5, 1.0)]), max_words=4)
    viral = build_ass(cues, preset="bold_viral")
    clean = build_ass(cues, preset="minimal_clean")
    assert "HELLO" in viral
    assert "hello" in clean.lower()


def test_build_ass_escapes_override_braces():
    cues = [Cue(0.0, 1.0, [{"w": "{hack}", "s": 0.0, "e": 1.0}])]
    ass = build_ass(cues, preset="modern_podcast")
    assert "{hack}" not in ass
    assert "(hack)" in ass


def test_every_preset_produces_valid_ass():
    cues = group_cues(_words([("test", 0.0, 0.4), ("caption", 0.4, 0.9)]), max_words=2)
    for name in PRESETS:
        ass = build_ass(cues, preset=name)
        assert "Style: Caption," in ass, name
        assert "Dialogue:" in ass, name


def test_keywords_filter_stopwords_both_languages():
    words = _words(
        [
            ("yang", 0, 1), ("penting", 1, 2), ("ini", 2, 3), ("penting", 3, 4),
            ("the", 4, 5), ("strategy", 5, 6), ("strategy", 6, 7), ("and", 7, 8),
        ]
    )
    kw = extract_keywords(words)
    assert "strategy" in kw and "penting" in kw
    assert "yang" not in kw and "the" not in kw and "and" not in kw


def test_words_in_range_rebases_and_clips():
    words = _words([("a", 0.0, 0.5), ("b", 10.0, 10.6), ("c", 20.0, 20.5)])
    out = words_in_range(words, 9.5, 21.0)
    assert [w["w"] for w in out] == ["b", "c"]
    assert out[0]["s"] == 0.5  # 10.0 - 9.5


def test_sentences_to_words_covers_full_span():
    out = sentences_to_words("empat kata pendek saja", 5.0, 9.0)
    assert len(out) == 4
    assert out[0]["s"] == 5.0
    assert abs(out[-1]["e"] - 9.0) < 0.01
    for a, b in zip(out, out[1:], strict=False):
        assert abs(a["e"] - b["s"]) < 1e-6


def test_preset_plan_gating():
    assert preset_allowed_for_plan("minimal_clean", "free")
    assert not preset_allowed_for_plan("cinematic", "free")
    assert preset_allowed_for_plan("cinematic", "pro")
    assert preset_allowed_for_plan("professional_edu", "business")
    assert get_preset("does_not_exist")["label"] == PRESETS["bold_viral"]["label"]
