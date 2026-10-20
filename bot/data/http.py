"""HTTP client bersama: rate limit token-bucket, backoff 429, timeout, retry.

Sumber limit resmi: https://docs.polymarket.com/api-reference/rate-limits
(IP-based, throttled/queued; kita tetap antre client-side agar sopan).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import aiohttp

log = logging.getLogger("bot.data.http")


class RateLimiter:
    """Token bucket sederhana per kategori endpoint."""

    def __init__(self, calls_per_10s: float, *, burst: Optional[float] = None) -> None:
        self.rate = max(0.1, calls_per_10s / 10.0)  # token per detik
        self.capacity = burst if burst is not None else max(1.0, calls_per_10s / 10.0)
        self.tokens = self.capacity
        self.updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                wait = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(wait)


# Limit konservatif (70% dari resmi agar aman untuk komponen lain di IP yang sama)
LIMITS = {
    "gamma_markets": RateLimiter(210),    # resmi 300/10s
    "gamma_events": RateLimiter(350),     # resmi 500/10s
    "gamma_general": RateLimiter(2800),   # resmi 4000/10s
    "clob_book": RateLimiter(1050),       # resmi 1500/10s
    "clob_books": RateLimiter(350),       # resmi 500/10s
    "clob_general": RateLimiter(6300),    # resmi 9000/10s
    "data_general": RateLimiter(560),     # resmi 800/10s (v2)
}


@dataclass
class HttpClient:
    session: aiohttp.ClientSession
    max_retries: int = 4
    backoff_base: float = 1.5
    default_timeout: float = 10.0
    _stats: dict = field(default_factory=lambda: {"requests": 0, "retries": 0, "errors_429": 0, "errors_other": 0})

    @classmethod
    async def create(cls, *, headers: Optional[dict] = None) -> "HttpClient":
        session = aiohttp.ClientSession(
            headers=headers or {"User-Agent": "poly-arb-bot/0.1 (research; paper mode)"},
            timeout=aiohttp.ClientTimeout(total=15),
        )
        return cls(session=session)

    async def close(self) -> None:
        await self.session.close()

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    async def get_json(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        limiter: Optional[RateLimiter] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        return await self._request("GET", url, params=params, limiter=limiter, timeout=timeout)

    async def post_json(
        self,
        url: str,
        *,
        json: Any = None,
        limiter: Optional[RateLimiter] = None,
        headers: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        return await self._request("POST", url, json=json, limiter=limiter, headers=headers, timeout=timeout)

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        json: Any = None,
        headers: Optional[dict] = None,
        limiter: Optional[RateLimiter] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            if limiter is not None:
                await limiter.acquire()
            self._stats["requests"] += 1
            try:
                async with self.session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout),
                ) as resp:
                    if resp.status == 429:
                        self._stats["errors_429"] += 1
                        retry_after = resp.headers.get("Retry-After")
                        wait = float(retry_after) if retry_after else self.backoff_base ** (attempt + 1)
                        log.warning("429 rate limited on %s — backoff %.1fs", url, wait)
                        await asyncio.sleep(wait)
                        self._stats["retries"] += 1
                        continue
                    if resp.status >= 500:
                        self._stats["errors_other"] += 1
                        await asyncio.sleep(self.backoff_base ** attempt)
                        self._stats["retries"] += 1
                        last_exc = RuntimeError(f"HTTP {resp.status} from {url}")
                        continue
                    if resp.status >= 400:
                        text = await resp.text()
                        raise RuntimeError(f"HTTP {resp.status} from {url}: {text[:200]}")
                    return await resp.json(content_type=None)
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                last_exc = exc
                self._stats["errors_other"] += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_base ** attempt)
                    self._stats["retries"] += 1
                    continue
                break
        raise RuntimeError(f"request failed after retries: {url}: {last_exc}")
