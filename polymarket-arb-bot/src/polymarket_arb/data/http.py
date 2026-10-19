"""Small async HTTP helper: local token-bucket throttle, retries with backoff, JSON."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx


class TokenBucket:
    """Allow ``rate`` requests per ``per_s`` seconds (sliding approximation)."""

    def __init__(self, rate: int, per_s: float = 10.0) -> None:
        self.capacity = float(rate)
        self.refill_per_s = float(rate) / per_s
        self.tokens = float(rate)
        self.updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                self.tokens = min(
                    self.capacity,
                    self.tokens + (now - self.updated) * self.refill_per_s,
                )
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                await asyncio.sleep((1 - self.tokens) / self.refill_per_s)


class JsonHttp:
    def __init__(
        self,
        base_url: str,
        *,
        timeout_s: float = 10.0,
        max_requests_per_10s: int = 200,
        retries: int = 3,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(
            timeout=timeout_s, headers={"User-Agent": "polymarket-arb-bot/0.1"}
        )
        self._bucket = TokenBucket(max_requests_per_10s, 10.0)
        self._retries = retries

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None
        for attempt in range(self._retries + 1):
            await self._bucket.acquire()
            try:
                resp = await self._client.get(url, params=params)
            except httpx.TransportError as exc:
                last_exc = exc
            else:
                if resp.status_code == 429 or resp.status_code >= 500:
                    last_exc = httpx.HTTPStatusError(
                        f"{resp.status_code} for {path}",
                        request=resp.request,
                        response=resp,
                    )
                elif resp.status_code >= 400:
                    raise httpx.HTTPStatusError(
                        f"{resp.status_code} for {path}",
                        request=resp.request,
                        response=resp,
                    )
                else:
                    return resp.json()
            await asyncio.sleep(min(10.0, 0.5 * (2**attempt)))
        assert last_exc is not None
        raise last_exc

    async def aclose(self) -> None:
        await self._client.aclose()
