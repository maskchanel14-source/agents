"""Media probing without ffprobe (parses `ffmpeg -i` output).

The bundled imageio-ffmpeg build ships ffmpeg only, so we parse its banner.
Falls back gracefully for odd containers.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .ffmpeg import run_ffmpeg_capture

_DUR = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_VIDEO = re.compile(r"Stream #\S+.*Video:\s*([a-zA-Z0-9_]+).*?(\d{2,5})x(\d{2,5})")
_FPS = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
_AUDIO = re.compile(r"Stream #\S+.*Audio:\s*([a-zA-Z0-9_]+)")
_ROT = re.compile(r"rotation of (-?\d+(?:\.\d+)?) degrees")


@dataclass
class MediaInfo:
    duration_s: float
    width: int
    height: int
    fps: float
    video_codec: str | None
    audio_codec: str | None
    has_audio: bool
    rotation: int
    bitrate_kbps: int | None

    def to_dict(self) -> dict:
        return asdict(self)


def probe(path: str) -> MediaInfo:
    out = run_ffmpeg_capture(["-i", path])
    if "Duration:" not in out and "Stream #" not in out:
        raise ValueError("Unsupported or corrupt media file")

    duration = 0.0
    m = _DUR.search(out)
    if m:
        h, mnt, sec = m.groups()
        duration = int(h) * 3600 + int(mnt) * 60 + float(sec)

    video = _VIDEO.search(out)
    if video:
        vcodec, w, h = video.group(1), int(video.group(2)), int(video.group(3))
    else:
        vcodec, w, h = None, 0, 0

    fps_m = _FPS.search(out)
    fps = float(fps_m.group(1)) if fps_m else 0.0

    audio = _AUDIO.search(out)
    acodec = audio.group(1) if audio else None
    rot_m = _ROT.search(out)
    rotation = int(float(rot_m.group(1))) if rot_m else 0

    br = re.search(r"bitrate:\s*(\d+)\s*kb/s", out)
    return MediaInfo(
        duration_s=round(max(duration, 0.0), 3),
        width=w,
        height=h,
        fps=fps or 25.0,
        video_codec=vcodec,
        audio_codec=acodec,
        has_audio=acodec is not None,
        rotation=rotation,
        bitrate_kbps=int(br.group(1)) if br else None,
    )
