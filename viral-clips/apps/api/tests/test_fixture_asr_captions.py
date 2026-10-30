"""Caption pipeline with ASR_PROVIDER=fixture: cues -> ASS -> burned-in MP4.

This proves the subtitle engine works end-to-end inside a real render without
requiring a paid transcription API.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from app.core.config import settings
from tests import fixtures_transcript
from tests.conftest import upload, wait_for_job


@pytest.fixture(scope="module")
def fixture_project(client, auth_a, sample_video):
    """Analyze a project with ASR_PROVIDER=fixture patched in for the module."""
    fixtures_dir = Path(settings.data_dir) / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    (fixtures_dir / "transcript.json").write_text(json.dumps(fixtures_transcript.build()))

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(settings, "asr_provider", "fixture")
        resp = upload(client, auth_a, sample_video, title="Caption pipeline test")
        assert resp.status_code == 201, resp.text
        project = resp.json()
        job = client.post(
            f"/api/projects/{project['id']}/analyze",
            headers=auth_a,
            json={"target_clips": 2, "min_seconds": 15, "max_seconds": 30, "use_deep_model": False},
        )
        assert job.status_code == 202, job.text
        state = wait_for_job(client, auth_a, job.json()["id"])
        assert state["status"] == "done", state
        yield project


def test_transcript_is_stored_with_words(client, auth_a, fixture_project):
    resp = client.get(f"/api/projects/{fixture_project['id']}/transcript", headers=auth_a)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["provider"] == "fixture"
    assert body["language"] == "id"
    assert len(body["words"]) > 40
    assert body["segments"][0]["text"].startswith("Halo")


def test_clips_have_caption_cues(client, auth_a, fixture_project):
    clips = client.get(f"/api/projects/{fixture_project['id']}/clips", headers=auth_a).json()
    assert clips
    with_cues = [c for c in clips if (c.get("subtitle_json") or {}).get("cues")]
    assert with_cues, "clips must carry caption cues when a transcript exists"
    cue = with_cues[0]["subtitle_json"]["cues"][0]
    assert cue["text"] and cue["end"] > cue["start"]


def test_ass_preview_contains_spoken_words(client, auth_a, fixture_project):
    clips = client.get(f"/api/projects/{fixture_project['id']}/clips", headers=auth_a).json()
    clip = clips[0]
    resp = client.get(f"/api/clips/{clip['id']}/subtitle-preview?preset=bold_viral", headers=auth_a)
    assert resp.status_code == 200
    ass = resp.json()["ass"]
    assert "Dialogue:" in ass
    spoken = " ".join(c["text"] for c in clip["subtitle_json"]["cues"]).lower()
    sample_word = spoken.split()[0].strip(".,!?")
    assert sample_word[:6] in ass.lower()


def test_render_burns_captions_into_pixels(client, auth_a, fixture_project):
    import cv2

    clips = client.get(f"/api/projects/{fixture_project['id']}/clips", headers=auth_a).json()
    clip = next(c for c in clips if (c.get("subtitle_json") or {}).get("cues"))
    resp = client.post(
        f"/api/projects/{fixture_project['id']}/render",
        headers=auth_a,
        json={"clip_ids": [clip["id"]], "preset": "bold_viral"},
    )
    assert resp.status_code == 202, resp.text
    state = wait_for_job(client, auth_a, resp.json()["id"])
    assert state["status"] == "done", state

    fresh = client.get(f"/api/clips/{clip['id']}", headers=auth_a).json()
    assert fresh["status"] == "ready"
    media = client.get(fresh["video_url"], headers=auth_a)
    assert media.status_code == 200

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "clip.mp4"
        path.write_bytes(media.content)
        cap = cv2.VideoCapture(str(path))
        cap.set(cv2.CAP_PROP_POS_MSEC, 1200)
        ok, frame = cap.read()
        cap.release()
        assert ok
        assert frame.shape[0] == 1920 and frame.shape[1] == 1080
        bottom = frame[int(1920 * 0.62) : int(1920 * 0.95), :, :]
        gray = cv2.cvtColor(bottom, cv2.COLOR_BGR2GRAY)
        bright_pixels = int(np.sum(gray > 232))
        assert bright_pixels > 400, (
            f"expected burned-in white captions in the lower band, found {bright_pixels} bright pixels"
        )
