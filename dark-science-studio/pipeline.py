#!/usr/bin/env python3
"""
pipeline.py -- ONE command to take a project folder from script.txt to a QA-gated mp4.

    python pipeline.py --video DS-005 --stage all
    python pipeline.py --video DS-005 --stage render     # just re-render
    python pipeline.py --video DS-005,DS-006 --stage all # batch

Stages (each is resumable; a stage is skipped when its outputs exist and are
newer than its inputs, unless --force):
    voice    script.txt -> build/<id>/voice.wav + words.json ; projects/<id>/captions.srt
    timeline build/<id>/words.json -> projects/<id>/timeline.json + build/<id>/props.json
    score    -> build/<id>/mix.wav   (music bed + SFX + narration, -14 LUFS)
    render   -> renders/<id>/final.mp4            (Remotion, 1080x1920@30)
    qa       -> projects/<id>/qa_report.json + qa_selfreview.md (+ renders/<id>/contact.jpg)
    all      = voice, timeline, score, render, qa

Every stage appends one line to logs/<id>.log and rewrites build/<id>/status.json
so a session that dies can be resumed by re-running the same command.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
RENDERS = ROOT / "renders"
LOGS = ROOT / "logs"
STUDIO = ROOT / "tools" / "studio"
PUBLIC_PROJ = STUDIO / "public" / "projects"

VOICE_ARGS = [
    "--length-scale", "0.95",
    "--noise-scale", "0.667",
    "--gap", "0.13",
    "--tail", "0.45",
]

STAGES = ["voice", "timeline", "score", "render", "qa"]


def log(vid: str, msg: str) -> None:
    LOGS.mkdir(exist_ok=True)
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}"
    with (LOGS / f"{vid}.log").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line)


def status_path(vid: str) -> Path:
    return BUILD / vid / "status.json"


def read_status(vid: str) -> dict:
    p = status_path(vid)
    return json.loads(p.read_text()) if p.exists() else {"video": vid, "stages": {}}


def write_status(vid: str, stage: str, state: str, **extra) -> None:
    st = read_status(vid)
    st.setdefault("stages", {})[stage] = {"state": state, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **extra}
    st["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status_path(vid).parent.mkdir(parents=True, exist_ok=True)
    status_path(vid).write_text(json.dumps(st, indent=2), encoding="utf-8")


def fresh(outputs: list[Path], inputs: list[Path]) -> bool:
    if not all(p.exists() and p.stat().st_size > 0 for p in outputs):
        return False
    newest_in = max((p.stat().st_mtime for p in inputs if p.exists()), default=0)
    oldest_out = min(p.stat().st_mtime for p in outputs)
    return oldest_out >= newest_in


def run(cmd: list[str], vid: str, label: str, cwd: Path | None = None) -> None:
    LOGS.mkdir(exist_ok=True)
    with (LOGS / f"{vid}.log").open("a", encoding="utf-8") as fh:
        fh.write(f"$ {' '.join(cmd)}\n")
        fh.flush()
        proc = subprocess.run(cmd, cwd=cwd or ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        fh.write(proc.stdout)
        fh.flush()
    tail = "\n".join(proc.stdout.strip().splitlines()[-6:])
    print(tail)
    if proc.returncode != 0:
        raise SystemExit(f"{label} failed (exit {proc.returncode}); full log: logs/{vid}.log")


# ----------------------------------------------------------------- stages
def stage_voice(vid: str, proj: Path, force: bool) -> None:
    out = [BUILD / vid / "voice.wav", BUILD / vid / "words.json", proj / "captions.srt"]
    if not force and fresh(out, [proj / "script.txt"]):
        log(vid, "voice: cached")
        write_status(vid, "voice", "cached")
        return
    run([sys.executable, "tools/voice_kit.py", "--project", str(proj), "--build", str(BUILD / vid), *VOICE_ARGS], vid, "voice")
    write_status(vid, "voice", "ok")


def stage_timeline(vid: str, proj: Path, force: bool) -> None:
    out = [proj / "timeline.json", BUILD / vid / "props.json"]
    if not force and fresh(out, [BUILD / vid / "words.json", proj / "meta.json"]):
        log(vid, "timeline: cached")
        write_status(vid, "timeline", "cached")
        return
    run([sys.executable, "tools/make_timeline.py", "--project", str(proj), "--build", str(BUILD / vid)], vid, "timeline")
    write_status(vid, "timeline", "ok")


def stage_score(vid: str, proj: Path, force: bool) -> None:
    out = [BUILD / vid / "mix.wav"]
    if not force and fresh(out, [BUILD / vid / "voice.wav", proj / "timeline.json"]):
        log(vid, "score: cached")
        write_status(vid, "score", "cached")
        return
    run([sys.executable, "tools/audio_kit.py", "--project", str(proj), "--build", str(BUILD / vid),
         "--sf2", str(ROOT / "assets" / "TimGM6mb.sf2")], vid, "score")
    import shutil
    (PUBLIC_PROJ / vid).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BUILD / vid / "mix.wav", PUBLIC_PROJ / vid / "mix.wav")
    write_status(vid, "score", "ok")


def stage_render(vid: str, proj: Path, force: bool, concurrency: int = 2) -> None:
    out = RENDERS / vid / "final.mp4"
    if not force and fresh([out], [BUILD / vid / "props.json", BUILD / vid / "mix.wav"]):
        log(vid, f"render: cached ({out.stat().st_size / 1e6:.1f} MB)")
        write_status(vid, "render", "cached")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_PROJ.mkdir(parents=True, exist_ok=True)
    import shutil
    src = BUILD / vid / "mix.wav"
    if not (PUBLIC_PROJ / vid / "mix.wav").exists() or (PUBLIC_PROJ / vid / "mix.wav").stat().st_mtime < src.stat().st_mtime:
        (PUBLIC_PROJ / vid).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, PUBLIC_PROJ / vid / "mix.wav")
    try:
        gpu = subprocess.run(["nvidia-smi"], capture_output=True, timeout=10).returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        gpu = False
    cmd = [
        "bash", str(STUDIO / "scripts" / "remotion-run.sh"), "npx", "remotion", "render",
        "src/index.ts", "DarkScienceShort", str(out),
        f"--props={BUILD / vid / 'props.json'}",
        f"--concurrency={concurrency}",
        f"--browser-executable={ROOT / '.chromium' / 'chrome-wrapper.sh'}",
    ]
    if not gpu:
        cmd.append("--gl=swiftshader")
    run(cmd, vid, "render", cwd=STUDIO)
    write_status(vid, "render", "ok", bytes=out.stat().st_size)


def stage_qa(vid: str, proj: Path, force: bool) -> None:
    video = RENDERS / vid / "final.mp4"
    if not video.exists():
        raise SystemExit(f"qa: no video at {video}")
    run([sys.executable, "tools/qa_gate.py", "--project", str(proj), "--build", str(BUILD / vid),
         "--video", str(video), "--contact"], vid, "qa")
    report = proj / "qa_report.json"
    verdict = json.loads(report.read_text()).get("all_passed") if report.exists() else None
    write_status(vid, "qa", "pass" if verdict else "fail", verdict=verdict)


# ----------------------------------------------------------------- driver
def do_stage(stage: str, vid: str, proj: Path, force: bool, concurrency: int) -> None:
    if stage == "voice":
        stage_voice(vid, proj, force)
    elif stage == "timeline":
        stage_timeline(vid, proj, force)
    elif stage == "score":
        stage_score(vid, proj, force)
    elif stage == "render":
        stage_render(vid, proj, force, concurrency)
    elif stage == "qa":
        stage_qa(vid, proj, force)
    else:
        raise SystemExit(f"unknown stage {stage}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="DS-005 or a comma list DS-005,DS-006")
    ap.add_argument("--stage", default="all", choices=STAGES + ["all"])
    ap.add_argument("--force", action="store_true", help="ignore cached outputs")
    ap.add_argument("--concurrency", type=int, default=2)
    args = ap.parse_args()

    for vid in [v.strip() for v in args.video.split(",") if v.strip()]:
        proj = ROOT / "projects" / vid
        if not (proj / "script.txt").exists():
            raise SystemExit(f"no script at {proj / 'script.txt'}")
        stages = STAGES if args.stage == "all" else [args.stage]
        t0 = time.time()
        log(vid, f"=== pipeline start stages={stages} ===")
        for stage in stages:
            do_stage(stage, vid, proj, args.force, args.concurrency)
        log(vid, f"=== pipeline done in {time.time() - t0:.1f}s ===")
        print(f"[{vid}] {read_status(vid)['stages']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
