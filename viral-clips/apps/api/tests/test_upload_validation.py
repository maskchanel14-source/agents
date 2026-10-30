"""Upload validation: type, magic bytes, size, and URL rights policy."""
from __future__ import annotations

import io

from tests.conftest import upload


def test_rejects_unsupported_extension(client, auth_a):
    with io.BytesIO(b"ftypisom" + b"0" * 128) as fh:
        resp = client.post(
            "/api/projects/upload",
            headers=auth_a,
            files={"file": ("notes.txt", fh, "text/plain")},
        )
    assert resp.status_code == 415


def test_rejects_fake_video_without_magic_bytes(client, auth_a):
    resp = client.post(
        "/api/projects/upload",
        headers=auth_a,
        files={"file": ("fake.mp4", io.BytesIO(b"not really a video" * 100), "video/mp4")},
    )
    assert resp.status_code == 415
    assert "valid video container" in resp.json()["detail"]


def test_url_ingest_requires_rights_attestation(client, auth_a):
    resp = client.post(
        "/api/projects/from-url",
        headers=auth_a,
        json={"url": "https://example.com/video.mp4", "attests_rights": False},
    )
    assert resp.status_code == 422
    assert "authorised" in resp.json()["detail"].lower()


def test_youtube_ingest_disabled_by_default(client, auth_a):
    resp = client.post(
        "/api/projects/from-url",
        headers=auth_a,
        json={"url": "https://www.youtube.com/watch?v=abc12345678", "attests_rights": True},
    )
    assert resp.status_code == 422
    assert "disabled" in resp.json()["detail"].lower()


def test_upload_rejects_non_http_scheme(client, auth_a):
    resp = client.post(
        "/api/projects/from-url",
        headers=auth_a,
        json={"url": "file:///etc/passwd", "attests_rights": True},
    )
    assert resp.status_code == 422
