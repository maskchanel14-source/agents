"""Authenticated media delivery with HTTP Range support (needed for video seek)."""
from __future__ import annotations

import mimetypes
import os
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.models import User
from app.services.storage import get_storage

router = APIRouter(tags=["media"])
_RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
CHUNK = 1024 * 256


def _authorize(user: User, key: str) -> None:
    """A media key always starts with the owner's user id (see pipeline keys)."""
    if key.startswith(f"{user.id}/") or user.is_admin:
        return
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")


@router.get("/media/{key:path}")
async def media(
    key: str,
    request: Request,
    download: str | None = Query(default=None),
    user: User = Depends(get_current_user),
):
    _authorize(user, key)
    storage = get_storage()

    if settings.storage_backend != "local":
        return RedirectResponse(storage.url_for(key, download_name=download), status_code=307)

    path = storage.local_path(key)
    if path is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

    size = path.stat().st_size
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    headers = {
        "Accept-Ranges": "bytes",
        "Cache-Control": "private, max-age=600",
        "Content-Disposition": (
            f'attachment; filename="{download}"' if download else "inline"
        ),
    }

    range_header = request.headers.get("range")
    if not range_header:
        def _full():
            with path.open("rb") as fh:
                while chunk := fh.read(CHUNK):
                    yield chunk

        headers["Content-Length"] = str(size)
        return StreamingResponse(_full(), media_type=ctype, headers=headers)

    m = _RANGE_RE.match(range_header.strip())
    if not m:
        raise HTTPException(status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, "Bad range")
    start_s, end_s = m.groups()
    if start_s:
        start = int(start_s)
        end = int(end_s) if end_s else size - 1
    else:  # suffix range: last N bytes
        length = int(end_s or 0)
        start = max(0, size - length)
        end = size - 1
    end = min(end, size - 1)
    if start > end or start >= size:
        raise HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            "Range not satisfiable",
            headers={"Content-Range": f"bytes */{size}"},
        )

    def _partial():
        remaining = end - start + 1
        with path.open("rb") as fh:
            fh.seek(start)
            while remaining > 0:
                chunk = fh.read(min(CHUNK, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    headers["Content-Length"] = str(end - start + 1)
    return StreamingResponse(_partial(), status_code=206, media_type=ctype, headers=headers)
