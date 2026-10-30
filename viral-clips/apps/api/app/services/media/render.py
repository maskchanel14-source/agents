"""Clip rendering: 9:16 crop / blurred-fit, burned-in captions, loudness
normalisation, optional background music, H.264 + AAC for Shorts/TikTok/Reels.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from .crop import crop_window
from .ffmpeg import run_ffmpeg

log = logging.getLogger(__name__)


def _esc_filter_path(path: str) -> str:
    """Escape a path for use inside an FFmpeg filtergraph argument."""
    p = str(path).replace("\\", "/")
    return p.replace(":", r"\:").replace("'", r"\'").replace(",", r"\,")


def render_clip(
    src: str,
    dst: str | Path,
    *,
    start_s: float,
    end_s: float,
    src_w: int,
    src_h: int,
    crop_x: float = 0.5,
    fit_mode: str = "crop",
    ass_path: str | Path | None = None,
    bgm_path: str | Path | None = None,
    bgm_volume: float = 0.12,
    width: int = 1080,
    height: int = 1920,
    fps_cap: int = 30,
    crf: int = 20,
    preset: str = "veryfast",
    threads: int = 2,
    has_audio: bool = True,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.5, end_s - start_s)

    win = crop_window(src_w, src_h, crop_x)
    filters: list[str] = []

    if fit_mode == "blur" and win["mode"] == "crop_h":
        # keep the whole frame, put a blurred copy behind it
        filters.append(
            f"[0:v]split=2[bg][fg];"
            f"[bg]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},gblur=sigma=42[bgb];"
            f"[fg]scale={width}:-2:force_original_aspect_ratio=decrease[fgs];"
            f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2[vbase]"
        )
    else:
        if win["mode"] == "scale":
            vchain = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
        else:
            vchain = (
                f"crop={win['w']}:{win['h']}:{win['x']}:{win['y']},"
                f"scale={width}:{height}:flags=lanczos"
            )
        filters.append(f"[0:v]{vchain},setsar=1[vbase]")

    post = f"fps={fps_cap},format=yuv420p"
    if ass_path:
        post += f",ass='{_esc_filter_path(ass_path)}'"
    filters.append(f"[vbase]{post}[vout]")

    if not has_audio and not bgm_path:
        filters.append(
            f"anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration={duration:.3f}[aout]"
        )
    else:
        filters.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=none[a1]")
        if bgm_path:
            filters.append(f"[1:a]volume={bgm_volume},atrim=duration={duration:.3f}[bg]")
            filters.append("[a1][bg]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        else:
            filters.append("[a1]anull[aout]")

    args: list[str] = [
        "-y",
        "-ss", f"{start_s:.3f}",
        "-t", f"{duration:.3f}",
        "-i", src,
    ]
    if bgm_path:
        args += ["-stream_loop", "-1", "-i", str(bgm_path)]
    args += [
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "160k",
        "-ar", "48000",
        "-ac", "2",
        "-movflags", "+faststart",
        "-threads", str(threads),
        str(dst),
    ]
    run_ffmpeg(args, timeout=3600, on_progress=on_progress, expected_seconds=duration)
    if not dst.exists() or dst.stat().st_size < 1024:
        raise RuntimeError("Render produced an empty file")
    return dst


def make_thumb(
    src: str, dst: str | Path, *, at_s: float, src_w: int, src_h: int, crop_x: float = 0.5
) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    win = crop_window(src_w, src_h, crop_x)
    if win["mode"] == "scale":
        vf = "scale=360:640:force_original_aspect_ratio=increase,crop=360:640"
    else:
        vf = f"crop={win['w']}:{win['h']}:{win['x']}:{win['y']},scale=360:640"
    run_ffmpeg(
        [
            "-y", "-ss", f"{max(0.0, at_s):.3f}", "-i", src,
            "-frames:v", "1", "-vf", vf, "-q:v", "3", str(dst),
        ],
        timeout=120,
    )
    return dst
