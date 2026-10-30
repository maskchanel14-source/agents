#!/usr/bin/env python3
"""Seed a demo account with a processed project (dev/demo convenience).

Creates (or reuses) demo@viralclips.example, uploads the generated sample video,
runs full analysis, renders every clip and prints a summary.

Usage: python scripts/seed_demo.py [api_base_url] [video_path]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
API = _ARGS[0] if _ARGS else "http://127.0.0.1:8000"
EMAIL = "demo@viralclips.example"
PASSWORD = "demo-password-123"
NAME = "Demo Creator"
TITLE = "Demo — podcast episode"


def ensure_video() -> Path:
    path = Path(_ARGS[1]) if len(_ARGS) > 1 else ROOT / "data" / "sample.mp4"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "make_sample.py"), str(path), "75"], check=True)
    return path


def wait_job(client: httpx.Client, job_id: str, label: str) -> dict:
    last = {}
    for _ in range(600):
        last = client.get(f"/api/jobs/{job_id}").json()
        print(f"  {label}: {last['status']} {last['stage']} {last['progress']}%", end="\r")
        if last["status"] in {"done", "failed"}:
            print()
            return last
        time.sleep(1.0)
    raise SystemExit(f"job {job_id} timed out: {last}")


def main() -> None:
    video = ensure_video()
    with httpx.Client(base_url=API, timeout=120, follow_redirects=True) as client:
        health = client.get("/api/health").json()
        print(f"API: {health}")

        reg = client.post(
            "/api/auth/register",
            json={"email": EMAIL, "password": PASSWORD, "display_name": NAME},
        )
        if reg.status_code == 409:
            login = client.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
            login.raise_for_status()
            print(f"reused existing demo account {EMAIL}")
        else:
            reg.raise_for_status()
            print(f"created demo account {EMAIL} / {PASSWORD}")

        projects = client.get("/api/projects").json()
        if projects and "--force" not in sys.argv:
            print(f"demo account already has {len(projects)} project(s); nothing to seed")
            print(json.dumps({"email": EMAIL, "password": PASSWORD}, indent=2))
            return

        print(f"uploading {video.name} ({video.stat().st_size/1e6:.1f} MB)…")
        with video.open("rb") as fh:
            up = client.post(
                "/api/projects/upload",
                files={"file": (video.name, fh, "video/mp4")},
                params={"auto_analyze": "false", "title": TITLE},
            )
        up.raise_for_status()
        project = up.json()
        print(f"project {project['id']} created")

        analyze = client.post(
            f"/api/projects/{project['id']}/analyze",
            json={
                "target_clips": int(os.environ.get("SEED_CLIPS", "3")),
                "min_seconds": 15,
                "max_seconds": 40,
                "use_deep_model": False,
            },
        )
        analyze.raise_for_status()
        state = wait_job(client, analyze.json()["id"], "analysis")
        if state["status"] != "done":
            raise SystemExit(f"analysis failed: {state.get('error')}")

        clips = client.get(f"/api/projects/{project['id']}/clips").json()
        print(f"{len(clips)} clips generated")
        for c in clips:
            print(f"  · {c['score']:.1f}  {c['start_s']:.1f}-{c['end_s']:.1f}s  {c['title']}")

        render = client.post(f"/api/projects/{project['id']}/render", json={})
        render.raise_for_status()
        state = wait_job(client, render.json()["id"], "render")
        if state["status"] != "done":
            raise SystemExit(f"render failed: {state.get('error')}")

        clips = client.get(f"/api/projects/{project['id']}/clips").json()
        ready = [c for c in clips if c["status"] == "ready"]
        print(f"{len(ready)} clips rendered")
        for c in ready:
            print(f"  · {c['video_url']}")
        print(json.dumps({"email": EMAIL, "password": PASSWORD, "project_id": project["id"]}, indent=2))


if __name__ == "__main__":
    main()
