"""Thin, auditable FFmpeg wrapper.

Binary resolution order: FFMPEG_BIN env → PATH → imageio-ffmpeg bundled build.
Every invocation is argument-list based (never shell=True) and time-boxed.
"""
from __future__ import annotations

import functools
import logging
import os
import shutil
import subprocess
from collections.abc import Callable, Sequence

from app.core.config import settings

log = logging.getLogger(__name__)


class MediaError(RuntimeError):
    """Raised when FFmpeg cannot process a file. Message is user-safe."""

    def __init__(self, message: str, stderr: str | None = None):
        super().__init__(message)
        self.stderr = (stderr or "")[-4000:]


@functools.lru_cache(maxsize=1)
def ffmpeg_path() -> str:
    if settings.ffmpeg_bin and os.path.isfile(settings.ffmpeg_bin):
        return settings.ffmpeg_bin
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover - depends on host
        raise MediaError(
            "FFmpeg not found. Install ffmpeg, or `pip install imageio-ffmpeg`, "
            "or set FFMPEG_BIN."
        ) from exc


@functools.lru_cache(maxsize=1)
def ffmpeg_version() -> str:
    try:
        out = subprocess.run(
           [ffmpeg_path(), "-hide_banner", "-version"],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception:
        return "unavailable"
    first = (out.stdout or "").splitlines()
    return first[0] if first else "unknown"


def run_ffmpeg(
    args: Sequence[str],
    *,
    timeout: int = 3600,
    on_progress: Callable[[float], None] | None = None,
    expected_seconds: float | None = None,
) -> str:
    """Run ffmpeg with the given arguments. Returns combined stderr/stdout tail."""
    cmd = [ffmpeg_path(), "-hide_banner", "-nostdin", *[str(a) for a in args]]
    log.debug("ffmpeg: %s", " ".join(cmd[:24]))
    if on_progress and expected_seconds:
        cmd = cmd[:-1] + ["-progress", "pipe:1", "-nostats", cmd[-1]]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        if on_progress and expected_seconds:
            assert proc.stdout is not None
            for line in proc.stdout:
                if line.startswith("out_time_ms="):
                    try:
                        done = int(line.split("=", 1)[1]) / 1_000_000
                        on_progress(min(0.99, done / expected_seconds))
                    except ValueError:
                        pass
        stderr = proc.stderr.read() if proc.stderr else ""
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise MediaError("Video processing timed out.", "timeout") from None
    if proc.returncode != 0:
        tail = (stderr or "").strip().splitlines()[-12:]
        raise MediaError("FFmpeg failed to process this media file.", "\n".join(tail))
    return stderr or ""


def run_ffmpeg_capture(args: Sequence[str], *, timeout: int = 120) -> str:
    """Run ffmpeg and return stderr (used for probing / filter introspection)."""
    proc = subprocess.run(
        [ffmpeg_path(), "-hide_banner", *[str(a) for a in args]],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return (proc.stderr or "") + (proc.stdout or "")
