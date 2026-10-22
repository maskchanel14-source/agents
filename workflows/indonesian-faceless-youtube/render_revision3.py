#!/usr/bin/env python3
"""Render Revision 3 with the reviewed photorealistic source frames.

This renderer is deliberately separate from render.py. The older renderer makes
programmatic editorial cards; Revision 3 must use the reviewed AI source images
from 04_Visual/revision3, with local disclosures, chapter overlays, Ken Burns
motion, and the selected voice-over. It never uploads or changes permissions.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import Iterable

W, H, FPS = 1920, 1080, 30
VW, VH = 1080, 1920
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Four anchors plus every numbered scene are intentionally used at least once.
SOURCE_MAP: dict[str, list[str]] = {
    "01": ["ref-market.png", "scene-01-market-entrance.png"],
    "02": ["scene-02-market-aisle.png"],
    "03": ["ref-vendor.png", "scene-03-vendor-scale.png"],
    "04": ["scene-04-survey-clipboard.png"],
    "05": ["ref-home.png", "scene-05-household-receipt.png"],
    "06": ["scene-06-data-desk.png"],
    "07": ["ref-farm.png", "scene-07-two-baskets.png"],
    "08": ["scene-08-feed-and-volatility.png"],
    "09": ["scene-09-rural-truck.png"],
    "10": ["scene-10-loading-crates.png", "scene-17-transfer-depot.png", "scene-18-arrival-check.png"],
    "11": ["scene-11-farm-worker.png", "scene-19-feed-scoop-detail.png", "scene-20-three-stations-table.png"],
    "12": ["scene-12-public-scrutiny.png", "scene-21-market-observation.png", "scene-22-evidence-stages.png"],
    "13": ["scene-13-household-basket.png", "scene-23-meal-planning.png"],
    "14": ["scene-14-regional-road.png", "scene-24-harbor-transfer.png", "scene-25-warehouse-gap.png"],
    "15": ["scene-15-policy-evaluation.png", "scene-26-policy-review-table.png"],
    "16": ["scene-16-market-dusk.png", "scene-27-market-notes.png", "scene-28-dawn-market-threshold.png"],
}

# The selected Shorts already carry voice-over aligned to the short scripts. We
# reuse only their audio streams and replace their old visuals completely.
SHORT_SOURCES: dict[str, list[str]] = {
    "short-01": ["ref-market.png", "scene-01-market-entrance.png", "scene-02-market-aisle.png"],
    "short-02": ["scene-08-feed-and-volatility.png", "scene-13-household-basket.png", "scene-23-meal-planning.png"],
    "short-03": ["scene-17-transfer-depot.png", "scene-18-arrival-check.png", "scene-24-harbor-transfer.png"],
}


class RenderError(RuntimeError):
    pass


def ffmpeg_path() -> str:
    try:
        import imageio_ffmpeg  # type: ignore

        p = imageio_ffmpeg.get_ffmpeg_exe()
        if Path(p).exists():
            return p
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if p:
        return p
    raise RenderError("FFmpeg tidak ditemukan. Instal imageio-ffmpeg di environment lokal.")


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(str(x) for x in cmd))
    try:
        return subprocess.run(
            [str(x) for x in cmd],
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if capture else None,
        )
    except subprocess.CalledProcessError as exc:
        tail = (exc.stdout or "")[-4000:]
        raise RenderError(f"Perintah gagal: {' '.join(str(x) for x in cmd)}\n{tail}") from exc


def filter_path(path: Path) -> str:
    # ffmpeg filter arguments are not shell-parsed; escape filter metacharacters
    # while retaining spaces in the quoted textfile path.
    return str(path.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def probe_duration(ffmpeg: str, path: Path) -> float:
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path), "-f", "null", "-"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stdout or "")
    if not m:
        raise RenderError(f"Tidak bisa membaca durasi: {path}\n{(result.stdout or '')[-1000:]}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RenderError(f"Bukan PNG valid: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def parse_scene_durations(production: Path, scenes: list[dict]) -> dict[str, float]:
    naskah = (production / "02_Naskah" / "naskah-video-utama.md").read_text(encoding="utf-8")
    # Current selected-voice naskah has one timing bullet per scene.
    found: dict[str, float] = {}
    for line in naskah.splitlines():
        match = re.match(r"^-\s+`[^`]+`\s+—\s+\*\*(.+?)\*\*\s+—\s+([0-9.]+)\s+detik", line)
        if not match:
            continue
        title, duration = match.group(1), float(match.group(2))
        for scene in scenes:
            if scene["title"] == title:
                found[scene["id"]] = duration
    if len(found) != len(scenes):
        # This fallback keeps the render deterministic if the timing markdown
        # has been edited by hand; it matches the measured selected voice.
        fallback = [42.816, 47.136, 47.197, 49.834, 46.110, 42.468, 45.795, 49.998, 52.571, 54.887, 55.229, 45.067, 52.704, 39.662, 35.218, 28.357]
        found = {scene["id"]: fallback[i] for i, scene in enumerate(scenes)}
    return found


def write_textfile(path: Path, text: str, *, wrap: int | None = None) -> None:
    if wrap:
        text = "\n".join(textwrap.wrap(text, width=wrap, break_long_words=False, break_on_hyphens=False))
    path.write_text(text, encoding="utf-8")


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    minutes, sec = divmod(seconds, 60.0)
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}:{minutes:02d}:{sec:05.2f}"


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def make_overlay_ass(path: Path, width: int, height: int, title: str | None) -> None:
    # The bundled FFmpeg build has libass but not drawtext. ASS is a local,
    # deterministic overlay layer and keeps all disclosure/title text outside
    # the generated pixels.
    if width == VW:
        disclosure_size, title_size = 28, 34
        disclosure_margin = (34, 42, 34)
        title_margin = (56, 56, 140)
    else:
        disclosure_size, title_size = 28, 38
        disclosure_margin = (30, 42, 34)
        title_margin = (56, 56, 118)
    title_text = ass_escape("\\N".join(textwrap.wrap(title, width=42, break_long_words=False, break_on_hyphens=False))) if title else ""
    styles = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Disclosure,DejaVu Sans,{disclosure_size},&H00F2E8D5,&H00F2E8D5,&H00171916,&H90171916,0,0,0,0,100,100,0,0,1,2,1,9,{disclosure_margin[0]},{disclosure_margin[1]},{disclosure_margin[2]},1
Style: Title,DejaVu Sans,{title_size},&H00F2E8D5,&H00F2E8D5,&H00171916,&H90171916,1,0,0,0,100,100,0,0,1,2,1,7,{title_margin[0]},{title_margin[1]},{title_margin[2]},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,9:59:59.00,Disclosure,,0,0,0,,ILUSTRASI AI
"""
    if title_text:
        styles += f"Dialogue: 1,0:00:00.00,0:00:05.50,Title,,0,0,0,,{title_text}\n"
    path.write_text(styles, encoding="utf-8")


def motion_filter(width: int, height: int, variant: int) -> str:
    # A different crop anchor per clip prevents a held still from becoming a
    # single repeated image while retaining the photographic composition.
    x_frac = [0.0, 0.24, 0.5, 0.76][variant % 4]
    y_frac = [0.0, 0.18, 0.42][variant % 3]
    direction = "min(zoom+0.00065,1.08)" if variant % 2 == 0 else "max(zoom-0.00042,1.0)"
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase," 
        f"crop={width}:{height},"
        f"zoompan=z='{direction}':x='(iw-iw/zoom)*{x_frac}':y='(ih-ih/zoom)*{y_frac}':d=1:s={width}x{height}:fps={FPS},"
    )


def make_clip(
    ffmpeg: str,
    source: Path,
    seconds: float,
    out: Path,
    *,
    variant: int,
    overlay_ass: Path,
    vertical: bool = False,
) -> None:
    width, height = (VW, VH) if vertical else (W, H)
    filt = motion_filter(width, height, variant)
    # The ASS file is a local overlay layer: disclosure is persistent and the
    # scene title appears only for the first 5.5 seconds of its first clip.
    filt += f"subtitles='{filter_path(overlay_ass)}',format=yuv420p"
    run(
        [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            source,
            "-t",
            f"{seconds:.3f}",
            "-vf",
            filt,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "19" if not vertical else "21",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            out,
        ],
        capture=True,
    )


def concat_clips(ffmpeg: str, clips: list[Path], out: Path, list_path: Path) -> None:
    with list_path.open("w", encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for clip in clips:
            safe = clip.resolve().as_posix().replace("'", "'\\''")
            f.write(f"file '{safe}'\n")
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", "-movflags", "+faststart", out], capture=True)


def validate_sources(production: Path, review_path: Path) -> list[Path]:
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("pending_source_images") != 0 or review.get("generated_source_images") != 32:
        raise RenderError("Review belum lengkap: 32 source image dan pending=0 diwajibkan sebelum render.")
    bad = [x for x in review.get("reviewed", []) if x.get("status") == "FAIL"]
    if bad:
        raise RenderError(f"Masih ada frame FAIL: {bad}")
    source_dir = review_path.parent
    required = sorted({name for names in SOURCE_MAP.values() for name in names})
    missing: list[Path] = []
    for name in required:
        path = source_dir / name
        if not path.exists():
            missing.append(path)
            continue
        w, h = png_size(path)
        if w < 1000 or h < 700:
            raise RenderError(f"Dimensi source terlalu kecil: {path} = {w}x{h}")
    if missing:
        raise RenderError("Source image hilang: " + ", ".join(str(p) for p in missing))
    return [source_dir / name for name in required]


def render_main(ffmpeg: str, production: Path, scenes: list[dict], durations: dict[str, float], out_root: Path) -> dict:
    source_dir = production / "04_Visual" / "revision3"
    render_dir = source_dir / "rendered"
    clip_dir = render_dir / "clips"
    text_dir = render_dir / "overlay-text"
    clip_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    clips: list[Path] = []
    visual_manifest: list[dict] = []
    clip_index = 0
    for scene in scenes:
        sid = scene["id"]
        scene_duration = durations[sid]
        names = SOURCE_MAP[sid]
        allocation = scene_duration / len(names)
        for source_index, name in enumerate(names):
            slot_duration = allocation if source_index < len(names) - 1 else scene_duration - allocation * (len(names) - 1)
            count = max(1, math.ceil(slot_duration / 6.5))
            for j in range(count):
                seconds = slot_duration / count
                title = scene["onscreen"] if source_index == 0 and j == 0 else None
                overlay_ass = text_dir / f"main-{clip_index:04d}-scene-{sid}.ass"
                make_overlay_ass(overlay_ass, W, H, title)
                clip = clip_dir / f"main-{clip_index:04d}-scene-{sid}.mp4"
                make_clip(ffmpeg, source_dir / name, seconds, clip, variant=clip_index, overlay_ass=overlay_ass)
                clips.append(clip)
                visual_manifest.append({"clip": clip.name, "scene": sid, "source": name, "seconds": round(seconds, 3), "title_overlay": bool(title)})
                clip_index += 1
    silent = render_dir / "revision3-visual-silent.mp4"
    concat_clips(ffmpeg, clips, silent, render_dir / "main.ffconcat")
    final_dir = out_root
    final_dir.mkdir(parents=True, exist_ok=True)
    srt_source = production / "05_Video-Final" / "video.srt"
    if not srt_source.exists():
        raise RenderError(f"SRT utama tidak ada: {srt_source}")
    srt = final_dir / "video.srt"
    shutil.copyfile(srt_source, srt)
    audio = production / "03_Audio" / "voice-master.m4a"
    if not audio.exists():
        raise RenderError(f"Master voice-over tidak ada: {audio}")
    final = final_dir / "video-utama.mp4"
    subtitle = filter_path(srt)
    subtitle_filter = (
        f"subtitles='{subtitle}':fontsdir=/usr/share/fonts/truetype/dejavu:"
        "force_style='FontName=DejaVu Sans,FontSize=19,PrimaryColour=&H00F2E8D5,"
        "OutlineColour=&H90171916,BorderStyle=1,Outline=2,Shadow=1,MarginV=48'"
    )
    run([
        ffmpeg, "-y", "-i", silent, "-i", audio, "-vf", subtitle_filter,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "medium",
        "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", final,
    ], capture=True)
    shutil.copyfile(audio, final_dir / "audio-master.m4a")
    (render_dir / "main-visual-manifest.json").write_text(json.dumps({"sources": SOURCE_MAP, "clips": visual_manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"silent": silent, "final": final, "srt": srt, "clips": visual_manifest}


def render_short(ffmpeg: str, production: Path, short_id: str, source_names: list[str], out_root: Path, text_dir: Path) -> dict:
    source_dir = production / "04_Visual" / "revision3"
    old_short = production / "05_Video-Final" / f"{short_id}.mp4"
    if not old_short.exists():
        raise RenderError(f"Short audio source hilang: {old_short}")
    audio_dir = out_root / "short-audio"
    clip_dir = out_root / "short-clips" / short_id
    audio_dir.mkdir(parents=True, exist_ok=True)
    clip_dir.mkdir(parents=True, exist_ok=True)
    audio = audio_dir / f"{short_id}.m4a"
    run([ffmpeg, "-y", "-i", old_short, "-vn", "-c:a", "copy", audio], capture=True)
    duration = probe_duration(ffmpeg, audio)
    clips: list[Path] = []
    allocation = duration / len(source_names)
    for i, name in enumerate(source_names):
        slot = allocation if i < len(source_names) - 1 else duration - allocation * (len(source_names) - 1)
        count = max(1, math.ceil(slot / 6.5))
        for j in range(count):
            seconds = slot / count
            title = None
            if i == 0 and j == 0:
                title = {"short-01":"ANGKA TURUN, BELANJA BERAT?", "short-02":"INFLASI AYAM BUKAN LIMA PERSEN", "short-03":"UJI SUBSIDI ANGKUT"}[short_id]
            clip_number = len(clips)
            overlay_ass = text_dir / f"{short_id}-{clip_number:03d}.ass"
            make_overlay_ass(overlay_ass, VW, VH, title)
            clip = clip_dir / f"{short_id}-{clip_number:03d}.mp4"
            make_clip(ffmpeg, source_dir / name, seconds, clip, variant=clip_number+i, overlay_ass=overlay_ass, vertical=True)
            clips.append(clip)
    silent = out_root / "short-silent" / f"{short_id}.mp4"
    silent.parent.mkdir(parents=True, exist_ok=True)
    concat_clips(ffmpeg, clips, silent, out_root / "short-silent" / f"{short_id}.ffconcat")
    old_srt = production / "05_Video-Final" / f"{short_id}.srt"
    if not old_srt.exists():
        raise RenderError(f"SRT short hilang: {old_srt}")
    srt = out_root / f"{short_id}.srt"
    shutil.copyfile(old_srt, srt)
    final = out_root / f"{short_id}.mp4"
    subtitle = filter_path(srt)
    subtitle_filter = (
        f"subtitles='{subtitle}':fontsdir=/usr/share/fonts/truetype/dejavu:"
        "force_style='FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00F2E8D5,"
        "OutlineColour=&H90171916,BorderStyle=1,Outline=2,Shadow=1,MarginV=130'"
    )
    run([ffmpeg, "-y", "-i", silent, "-i", audio, "-vf", subtitle_filter, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", final], capture=True)
    return {"id": short_id, "mp4": str(final), "srt": str(srt), "duration": duration, "sources": source_names}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", required=True, type=Path)
    parser.add_argument("--skip-shorts", action="store_true")
    args = parser.parse_args()
    production = args.production.resolve()
    review = production / "04_Visual" / "revision3" / "image-review.json"
    scenes = json.loads((production / "02_Naskah" / "scenes.json").read_text(encoding="utf-8"))
    validate_sources(production, review)
    durations = parse_scene_durations(production, scenes)
    ffmpeg = ffmpeg_path()
    final_dir = production / "05_Video-Final" / "revision3"
    render_dir = production / "04_Visual" / "revision3" / "rendered"
    text_dir = render_dir / "overlay-text"
    text_dir.mkdir(parents=True, exist_ok=True)
    result = render_main(ffmpeg, production, scenes, durations, final_dir)
    shorts: list[dict] = []
    if not args.skip_shorts:
        for short_id, names in SHORT_SOURCES.items():
            shorts.append(render_short(ffmpeg, production, short_id, names, final_dir, text_dir))
    manifest = {
        "revision": 3,
        "status": "PRIVATE DRAFT — BELUM CLEAR UNTUK KOMERSIAL",
        "main": {"file": str(result["final"]), "duration_seconds": probe_duration(ffmpeg, result["final"]), "source_images": 32, "voice": "voice-01", "srt": str(result["srt"])},
        "shorts": shorts,
        "source_map": SOURCE_MAP,
        "rules": ["every source image is reviewed before render", "ILUSTRASI AI is local overlay on every clip", "factual text/numbers are local overlay or subtitle only", "no upload or permission change"],
    }
    (final_dir / "render-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RenderError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
