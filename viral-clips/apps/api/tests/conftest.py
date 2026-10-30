"""Test harness: isolated temp data dir, SQLite DB and a real ASGI client.

Environment is configured *before* importing the app so the settings singleton
and engine pick up the test paths.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_TMP = Path(tempfile.mkdtemp(prefix="vc-tests-"))
os.environ.update(
    {
        "ENV": "test",
        "DATA_DIR": str(_TMP / "data"),
        "DATABASE_URL": f"sqlite+aiosqlite:///{_TMP}/test.db",
        "JWT_SECRET": "test-secret-not-for-production-0123456789abcdef",
        "STORAGE_BACKEND": "local",
        "QUEUE_BACKEND": "inline",
        "JOB_MAX_WORKERS": "1",
        "ASR_PROVIDER": "none",
        "LLM_PROVIDER": "heuristic",
        "FFMPEG_THREADS": "1",
        "MAX_UPLOAD_MB": "64",
        "CORS_ORIGINS": '["http://localhost:3000"]',
    }
)
(_TMP / "data").mkdir(parents=True, exist_ok=True)

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.services.media.ffmpeg import run_ffmpeg  # noqa: E402


@pytest.fixture(scope="session")
def sample_video() -> Path:
    """A 40s 1280x720 sample with speech-like audio, built once per session."""
    out = _TMP / "sample.mp4"
    if out.exists():
        return out
    script = ROOT.parents[1] / "scripts" / "make_sample.py"
    import subprocess

    subprocess.run(
        [sys.executable, str(script), str(out), "40"], check=True, capture_output=True
    )
    return out


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def user_a(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "correct-horse-9", "display_name": "Alice"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture(scope="session")
def user_b(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "bob@example.com", "password": "correct-horse-9", "display_name": "Bob"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def auth(user: dict) -> dict:
    return {"Authorization": f"Bearer {user['access_token']}"}


@pytest.fixture(scope="session")
def auth_a(user_a):
    return auth(user_a)


@pytest.fixture(scope="session")
def auth_b(user_b):
    return auth(user_b)


def upload(client, headers, path: Path, *, title: str, auto_analyze: bool = False):
    with path.open("rb") as fh:
        return client.post(
            "/api/projects/upload",
            headers=headers,
            files={"file": (path.name, fh, "video/mp4")},
            params={"title": title, "auto_analyze": str(auto_analyze).lower()},
        )


def wait_for_job(client, headers, job_id: str, *, timeout: float = 420.0) -> dict:
    deadline = time.time() + timeout
    last = {}
    while time.time() < deadline:
        resp = client.get(f"/api/jobs/{job_id}", headers=headers)
        assert resp.status_code == 200, resp.text
        last = resp.json()
        if last["status"] in {"done", "failed"}:
            return last
        time.sleep(0.5)
    raise AssertionError(f"job {job_id} timed out; last state {last}")


@pytest.fixture(scope="session")
def analyzed_project(client, auth_a, sample_video):
    """A project that has completed analysis (shared by read-only tests)."""
    resp = upload(client, auth_a, sample_video, title="Podcast episode 1")
    assert resp.status_code == 201, resp.text
    project = resp.json()
    job = client.post(
        f"/api/projects/{project['id']}/analyze",
        headers=auth_a,
        json={"target_clips": 3, "min_seconds": 15, "max_seconds": 40, "use_deep_model": False},
    )
    assert job.status_code == 202, job.text
    state = wait_for_job(client, auth_a, job.json()["id"])
    assert state["status"] == "done", state
    return project
