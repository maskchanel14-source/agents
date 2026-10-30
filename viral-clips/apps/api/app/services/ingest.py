"""Upload validation and URL ingestion with an explicit rights policy."""
from __future__ import annotations

import io
import logging
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

ALLOWED_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
ALLOWED_MIME = {
    "video/mp4", "video/quicktime", "video/x-m4v", "video/webm",
    "video/x-matroska", "application/octet-stream",
}
# ISO-BMFF / Matroska / WebM magic bytes
MAGIC = (b"ftyp", b"\x1aE\xdf\xa3")

YOUTUBE_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "youtube-nocookie.com",
}


class IngestError(ValueError):
    pass


@dataclass
class PreparedUpload:
    stream: io.BufferedReader
    extension: str
    size_limit: int


class PrefixedReader:
    """Re-attach an already-read head chunk to a stream (magic-byte sniffing)."""

    def __init__(self, head: bytes, rest):
        self._head = head
        self._rest = rest

    def read(self, n: int = -1) -> bytes:
        if self._head:
            chunk, self._head = self._head, b""
            return chunk
        return self._rest.read(n)


def validate_upload(filename: str | None, content_type: str | None, head: bytes) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise IngestError(
            f"Unsupported file type '{ext or 'unknown'}'. Allowed: {', '.join(sorted(ALLOWED_EXT))}"
        )
    if content_type and content_type.split(";")[0].strip() not in ALLOWED_MIME:
        raise IngestError(f"Unsupported content type '{content_type}'")
    if not any(m in head[:64] for m in MAGIC):
        raise IngestError("File does not look like a valid video container")
    return ext


def size_limit_for_plan(plan: dict) -> int:
    mb = min(int(plan.get("max_upload_mb", settings.max_upload_mb)), settings.max_upload_mb)
    return mb * 1024 * 1024


def classify_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise IngestError("Only http(s) URLs are supported")
    host = (parsed.hostname or "").lower()
    if host in YOUTUBE_HOSTS or host.endswith(".youtube.com"):
        return "youtube"
    if not parsed.path:
        raise IngestError("URL has no path")
    ext = Path(parsed.path).suffix.lower()
    if ext in ALLOWED_EXT:
        return "direct_media"
    # signed object URLs often have no extension but are direct media
    return "generic"


def check_url_policy(url: str, *, attests_rights: bool) -> str:
    kind = classify_url(url)
    if not attests_rights:
        raise IngestError(
            "You must confirm you own or are authorised to process this video."
        )
    if kind == "youtube":
        if not settings.enable_youtube_ingest:
            raise IngestError(
                "YouTube ingestion is disabled on this deployment. Upload the file "
                "you own, or set ENABLE_YOUTUBE_INGEST=true where the operator has "
                "confirmed the platform's terms allow it."
            )
        if not _ytdlp_available():
            raise IngestError(
                "YouTube ingestion requires the optional `yt-dlp` package on the worker "
                "(pip install yt-dlp)."
            )
    return kind


def _ytdlp_available() -> bool:
    try:
        import yt_dlp  # noqa: F401

        return True
    except Exception:
        return False


async def fetch_direct(url: str, dest: Path, *, max_bytes: int, timeout_s: float = 900) -> Path:
    """Stream a direct media URL to disk with a hard size cap."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    async with httpx.AsyncClient(timeout=timeout_s, follow_redirects=True) as client:
        async with client.stream("GET", url) as resp:
            if resp.status_code >= 400:
                raise IngestError(f"Source returned HTTP {resp.status_code}")
            ctype = resp.headers.get("content-type", "")
            if ctype and not (
                ctype.startswith("video/") or ctype in {"application/octet-stream", "binary/octet-stream"}
            ):
                raise IngestError(f"URL did not return a video (content-type: {ctype})")
            declared = resp.headers.get("content-length")
            if declared and int(declared) > max_bytes:
                raise IngestError("Remote file exceeds the upload limit for your plan")
            with dest.open("wb") as fh:
                async for chunk in resp.aiter_bytes(512 * 1024):
                    written += len(chunk)
                    if written > max_bytes:
                        fh.close()
                        dest.unlink(missing_ok=True)
                        raise IngestError("Remote file exceeds the upload limit for your plan")
                    fh.write(chunk)
    if written < 64 * 1024:
        raise IngestError("Downloaded file is too small to be a video")
    return dest


def ytdlp_download(url: str, dest_dir: Path, *, max_bytes: int) -> Path:
    """Optional YouTube ingest. Only reachable when explicitly enabled."""
    import yt_dlp

    dest_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(dest_dir / "source.%(ext)s")
    opts = {
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "max_filesize": max_bytes,
        "restrictfilenames": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
    if path.suffix != ".mp4":
        candidate = path.with_suffix(".mp4")
        path = candidate if candidate.exists() else path
    if not path.exists():
        raise IngestError("Downloader did not produce a file")
    if path.stat().st_size > max_bytes:
        path.unlink(missing_ok=True)
        raise IngestError("File exceeds the upload limit for your plan")
    return path


def guess_mime(path: Path) -> str:
    return mimetypes.guess_type(str(path))[0] or "video/mp4"


def safe_filename(name: str, fallback: str = "clip") -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.")
    return base[:80] or fallback
