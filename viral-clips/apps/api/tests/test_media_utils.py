"""Crop planning, storage safety and ASR provider selection."""
from __future__ import annotations

import io

import pytest

from app.services.media.crop import crop_window, plan_clip_crop
from app.services.storage import LocalStorage


@pytest.mark.parametrize(
    "w,h,expected_mode",
    [(1920, 1080, "crop_h"), (1080, 1920, "exact"), (1280, 720, "crop_h"), (800, 1600, "crop_v")],
)
def test_crop_window_modes(w, h, expected_mode):
    win = crop_window(w, h, 0.5)
    assert win["mode"] == expected_mode
    if expected_mode == "crop_h":
        assert abs(win["w"] / win["h"] - 1080 / 1920) < 0.01
        assert 0 <= win["x"] <= w - win["w"]


def test_crop_window_clamps_to_frame():
    left = crop_window(1920, 1080, 0.0)
    right = crop_window(1920, 1080, 1.0)
    assert left["x"] == 0
    assert right["x"] == 1920 - right["w"]


def test_plan_clip_crop_uses_faces_when_available():
    visuals = {
        "available": True,
        "samples": [{"t": float(i), "face_x": 0.8, "motion": 0.05} for i in range(30)],
    }
    plan = plan_clip_crop(visuals, 0, 20)
    assert plan["strategy"] == "face_tracking"
    assert plan["crop_x"] > 0.6
    assert plan["confidence"] == 1.0


def test_plan_clip_crop_defaults_to_center_without_signal():
    assert plan_clip_crop(None, 0, 20)["strategy"] == "center"
    assert plan_clip_crop({"available": False}, 0, 20)["crop_x"] == 0.5


def test_local_storage_blocks_path_traversal(tmp_path):
    storage = LocalStorage(tmp_path)
    with pytest.raises(ValueError):
        storage.save_stream("../escape.mp4", io.BytesIO(b"x"))
    assert not (tmp_path.parent / "escape.mp4").exists()


def test_local_storage_roundtrip(tmp_path):
    storage = LocalStorage(tmp_path)
    n = storage.save_stream("u1/p1/source.mp4", io.BytesIO(b"ftypfake" * 100))
    assert n == 800
    assert storage.exists("u1/p1/source.mp4")
    assert storage.url_for("u1/p1/source.mp4") == "/media/u1/p1/source.mp4"
    assert storage.delete_prefix("u1/p1") >= 1
    assert not storage.exists("u1/p1/source.mp4")


def test_local_storage_enforces_size_limit(tmp_path):
    storage = LocalStorage(tmp_path)
    with pytest.raises(ValueError):
        storage.save_stream("u1/big.mp4", io.BytesIO(b"x" * 2048), max_bytes=1024)
    assert not storage.exists("u1/big.mp4")


def test_asr_provider_selection_without_credentials(monkeypatch):
    from app.core.config import settings
    from app.services.asr import get_asr

    monkeypatch.setattr(settings, "asr_provider", "auto")
    monkeypatch.setattr(settings, "asr_api_key", None)
    assert get_asr().name == "none"

    monkeypatch.setattr(settings, "asr_provider", "openai")
    assert get_asr().name == "none", "no key must degrade to none, never fabricate"

    monkeypatch.setattr(settings, "asr_provider", "groq")
    monkeypatch.setattr(settings, "asr_api_key", "gsk_test")
    engine = get_asr()
    assert engine.name == "groq"
    assert engine.model == "whisper-large-v3-turbo"


def test_llm_registry_returns_none_without_key(monkeypatch):
    from app.core.config import settings
    from app.services.ai.registry import get_llm, reset_llm_cache

    reset_llm_cache()
    monkeypatch.setattr(settings, "llm_provider", "auto")
    monkeypatch.setattr(settings, "llm_api_key", None)
    monkeypatch.setattr(settings, "llm_base_url", None)
    assert get_llm() is None
    monkeypatch.setattr(settings, "llm_provider", "heuristic")
    assert get_llm() is None
    reset_llm_cache()


def test_cost_estimation():
    from app.services.ai.cost import estimate_asr_cost_usd, estimate_cost_usd

    assert estimate_cost_usd("gpt-4o-mini", 1_000_000, 0) == pytest.approx(0.15)
    assert estimate_cost_usd("gpt-4o-mini", 0, 1_000_000) == pytest.approx(0.60)
    assert estimate_asr_cost_usd("whisper-1", 600) == pytest.approx(0.06)
    assert estimate_asr_cost_usd("faster_whisper", 600) == 0.0
