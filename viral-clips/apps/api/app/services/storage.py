"""Storage abstraction: local disk (dev) and Cloudflare R2 / S3 (production)."""
from __future__ import annotations

import logging
import shutil
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path

from app.core.config import settings

log = logging.getLogger(__name__)


class Storage(ABC):
    @abstractmethod
    def save_stream(self, key: str, stream, max_bytes: int | None = None) -> int:
        """Persist a binary stream, returning bytes written."""

    @abstractmethod
    def save_file(self, key: str, src: Path) -> None: ...

    @abstractmethod
    def local_path(self, key: str) -> Path | None:
        """Return a local filesystem path when the backend is local."""

    @abstractmethod
    def url_for(self, key: str, *, download_name: str | None = None) -> str: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    def download_to(self, key: str, dest: Path) -> Path:
        """Materialise an object locally (needed for remote backends)."""
        local = self.local_path(key)
        if local is not None:
            return local
        raise NotImplementedError

    @abstractmethod
    def delete_prefix(self, prefix: str) -> int: ...


class LocalStorage(Storage):
    def __init__(self, root: Path | None = None):
        self.root = Path(root or settings.media_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        p = (self.root / key).resolve()
        if not str(p).startswith(str(self.root.resolve())):
            raise ValueError("invalid storage key")  # path traversal guard
        return p

    def save_stream(self, key: str, stream, max_bytes: int | None = None) -> int:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        written = 0
        with p.open("wb") as fh:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if max_bytes and written > max_bytes:
                    fh.close()
                    p.unlink(missing_ok=True)
                    raise ValueError("upload exceeds the size limit")
                fh.write(chunk)
        return written

    def save_file(self, key: str, src: Path) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, p)

    def local_path(self, key: str) -> Path | None:
        p = self._path(key)
        return p if p.exists() else None

    def url_for(self, key: str, *, download_name: str | None = None) -> str:
        base = f"/media/{key}"
        return f"{base}?download={download_name}" if download_name else base

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def delete_prefix(self, prefix: str) -> int:
        target = self._path(prefix)
        if target.is_dir():
            count = sum(1 for _ in target.rglob("*"))
            shutil.rmtree(target, ignore_errors=True)
            return count
        if target.exists():
            target.unlink()
            return 1
        return 0


class R2Storage(Storage):
    """Cloudflare R2 via the S3-compatible API (presigned GET for delivery)."""

    def __init__(self) -> None:
        import boto3
        from botocore.config import Config

        missing = [
            name
            for name, val in {
                "R2_ACCOUNT_ID": settings.r2_account_id,
                "R2_ACCESS_KEY_ID": settings.r2_access_key_id,
                "R2_SECRET_ACCESS_KEY": settings.r2_secret_access_key,
                "R2_BUCKET": settings.r2_bucket,
            }.items()
            if not val
        ]
        if missing:
            raise RuntimeError(f"R2 storage selected but missing: {', '.join(missing)}")
        self.bucket = settings.r2_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto",
            config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
        )

    def save_stream(self, key: str, stream, max_bytes: int | None = None) -> int:
        # boto3 handles multipart chunking for large files internally
        import tempfile

        written = 0
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if max_bytes and written > max_bytes:
                    raise ValueError("upload exceeds the size limit")
                tmp.write(chunk)
            tmp.flush()
            self.client.upload_file(tmp.name, self.bucket, key)
        return written

    def save_file(self, key: str, src: Path) -> None:
        self.client.upload_file(str(src), self.bucket, key)

    def local_path(self, key: str) -> Path | None:
        return None

    def url_for(self, key: str, *, download_name: str | None = None) -> str:
        if settings.r2_public_base_url and not download_name:
            return f"{settings.r2_public_base_url.rstrip('/')}/{key}"
        params = {"Bucket": self.bucket, "Key": key}
        if download_name:
            params["ResponseContentDisposition"] = f'attachment; filename="{download_name}"'
        return self.client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=settings.signed_url_ttl_seconds
        )

    def download_to(self, key: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self.bucket, key, str(dest))
        return dest

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def delete_prefix(self, prefix: str) -> int:
        paginator = self.client.get_paginator("list_objects_v2")
        removed = 0
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            keys: Iterable[dict] = page.get("Contents", [])
            batch = [{"Key": o["Key"]} for o in keys]
            if batch:
                self.client.delete_objects(Bucket=self.bucket, Delete={"Objects": batch})
                removed += len(batch)
        return removed


_storage: Storage | None = None


def get_storage() -> Storage:
    global _storage
    if _storage is None:
        _storage = R2Storage() if settings.storage_backend == "r2" else LocalStorage()
    return _storage


def reset_storage() -> None:
    """Test helper."""
    global _storage
    _storage = None
