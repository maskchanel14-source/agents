"""End-to-end: upload → analyze → clips → render → download → export."""
from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from app.services.media.probe import probe
from tests.conftest import upload, wait_for_job


def _clips(client, headers, project_id):
    resp = client.get(f"/api/projects/{project_id}/clips", headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_analysis_produces_scored_clips(client, auth_a, analyzed_project):
    project = client.get(f"/api/projects/{analyzed_project['id']}", headers=auth_a).json()
    assert project["status"] == "analyzed"
    assert project["progress"] == 100
    assert project["duration_s"] and project["duration_s"] > 35

    clips = _clips(client, auth_a, project["id"])
    assert 1 <= len(clips) <= 3
    for clip in clips:
        assert 0 <= clip["score"] <= 100
        assert clip["end_s"] > clip["start_s"]
        assert clip["end_s"] <= project["duration_s"] + 0.5
        assert clip["start_s"] >= 0
        assert 10 <= clip["duration_s"] <= 41
        assert clip["title"]
        assert clip["explanation"], "every score must be explained"
        assert set(clip["score_breakdown"]) >= {
            "hook_strength", "curiosity", "emotional_impact", "story_completeness",
            "shareability", "engagement", "information_value", "context_independence",
            "visual_engagement",
        }
        assert clip["status"] == "suggested"


def test_clips_do_not_overlap(client, auth_a, analyzed_project):
    clips = _clips(client, auth_a, analyzed_project["id"])
    ordered = sorted(clips, key=lambda c: c["start_s"])
    for a, b in zip(ordered, ordered[1:], strict=False):
        overlap = min(a["end_s"], b["end_s"]) - max(a["start_s"], b["start_s"])
        assert overlap <= 0.26 * min(a["duration_s"], b["duration_s"])


def test_analysis_metadata_recorded(client, auth_a, analyzed_project):
    from app.core.db import SessionLocal
    from app.models import Project
    import asyncio

    async def load():
        async with SessionLocal() as s:
            return await s.get(Project, analyzed_project["id"])

    project = asyncio.run(load())
    analysis = project.analysis
    assert analysis["media"]["width"] == 1280
    assert analysis["media"]["height"] == 720
    assert analysis["audio"]["speech_regions"] >= 1
    assert analysis["transcript"]["provider"] == "none"
    assert isinstance(analysis["warnings"], list)
    assert analysis["candidates"]["selected"] >= 1


def test_transcript_404_when_asr_disabled(client, auth_a, analyzed_project):
    resp = client.get(f"/api/projects/{analyzed_project['id']}/transcript", headers=auth_a)
    assert resp.status_code == 404


def test_usage_minutes_are_metered(client, auth_a, analyzed_project):
    usage = client.get("/api/usage", headers=auth_a).json()
    assert usage["minutes_used"] > 0
    assert usage["minutes_remaining"] < usage["plan"]["minutes_per_month"]
    assert usage["plan"]["name"] == "free"


def test_render_single_clip_and_stream_it(client, auth_a, analyzed_project):
    clips = _clips(client, auth_a, analyzed_project["id"])
    clip_id = clips[0]["id"]
    resp = client.post(
        f"/api/projects/{analyzed_project['id']}/render",
        headers=auth_a,
        json={"clip_ids": [clip_id], "preset": "bold_viral"},
    )
    assert resp.status_code == 202, resp.text
    state = wait_for_job(client, auth_a, resp.json()["id"])
    assert state["status"] == "done", state

    clip = client.get(f"/api/clips/{clip_id}", headers=auth_a).json()
    assert clip["status"] == "ready", clip
    assert clip["video_url"], clip
    assert clip["thumb_url"]

    media = client.get(clip["video_url"], headers=auth_a)
    assert media.status_code == 200
    assert len(media.content) > 20_000

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "clip.mp4"
        out.write_bytes(media.content)
        info = probe(str(out))
        assert (info.width, info.height) == (1080, 1920), info
        assert info.video_codec == "h264"
        assert info.has_audio
        assert 5 < info.duration_s < 45

    thumb = client.get(clip["thumb_url"], headers=auth_a)
    assert thumb.status_code == 200
    assert thumb.content[:2] == b"\xff\xd8"  # JPEG magic


def test_range_requests_supported(client, auth_a, analyzed_project):
    clips = _clips(client, auth_a, analyzed_project["id"])
    ready = [c for c in clips if c["video_url"]]
    assert ready, "expected at least one rendered clip from the previous test"
    url = ready[0]["video_url"]
    first = client.get(url, headers={**auth_a, "Range": "bytes=0-1023"})
    assert first.status_code == 206
    assert len(first.content) == 1024
    assert first.headers["content-range"].startswith("bytes 0-1023/")
    tail = client.get(url, headers={**auth_a, "Range": "bytes=-256"})
    assert tail.status_code == 206 and len(tail.content) == 256


def test_export_bundle_zip(client, auth_a, analyzed_project):
    resp = client.get(f"/api/projects/{analyzed_project['id']}/export", headers=auth_a)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / "bundle.zip"
        zpath.write_bytes(resp.content)
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
            assert any(n.endswith(".mp4") for n in names)
            assert "manifest.json" in names
            assert zf.testzip() is None


def test_clip_edits_are_persisted(client, auth_a, analyzed_project):
    clips = _clips(client, auth_a, analyzed_project["id"])
    clip = clips[-1]
    resp = client.patch(
        f"/api/clips/{clip['id']}",
        headers=auth_a,
        json={
            "title": "Edited title",
            "crop_x": 0.25,
            "preset": "minimal_clean",
            "subtitle_json": {"cues": [{"start": 0.0, "end": 1.5, "text": "Halo semuanya"}]},
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["title"] == "Edited title"
    assert body["crop_x"] == 0.25
    assert body["preset"] == "minimal_clean"
    assert body["subtitle_json"]["edited"] is True
    assert body["subtitle_json"]["cues"][0]["text"] == "Halo semuanya"


def test_clip_edit_validation(client, auth_a, analyzed_project):
    clip = _clips(client, auth_a, analyzed_project["id"])[0]
    bad = client.patch(f"/api/clips/{clip['id']}", headers=auth_a, json={"start_s": 99999})
    assert bad.status_code == 422
    bad_preset = client.patch(
        f"/api/clips/{clip['id']}", headers=auth_a, json={"preset": "professional_edu"}
    )
    assert bad_preset.status_code == 402, "business-tier preset must be gated"
    unknown = client.patch(f"/api/clips/{clip['id']}", headers=auth_a, json={"preset": "nope"})
    assert unknown.status_code == 422


def test_render_only_selected_clip(client, auth_a, analyzed_project):
    clips = _clips(client, auth_a, analyzed_project["id"])
    resp = client.post(
        f"/api/projects/{analyzed_project['id']}/render",
        headers=auth_a,
        json={"clip_ids": ["does-not-exist"]},
    )
    assert resp.status_code == 404
    assert clips  # sanity


def test_project_deletion_cleans_storage(client, auth_a, sample_video):
    created = upload(client, auth_a, sample_video, title="to delete")
    assert created.status_code == 201
    pid = created.json()["id"]
    assert client.delete(f"/api/projects/{pid}", headers=auth_a).status_code == 204
    assert client.get(f"/api/projects/{pid}", headers=auth_a).status_code == 404
