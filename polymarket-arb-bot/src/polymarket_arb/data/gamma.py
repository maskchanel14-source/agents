"""Gamma API client: event/market discovery with a TTL cache."""

from __future__ import annotations

import time
from typing import Any

from .http import JsonHttp


class GammaClient:
    def __init__(self, http: JsonHttp, cache_ttl_s: int = 300) -> None:
        self._http = http
        self._ttl = cache_ttl_s
        self._cache: dict[str, tuple[float, Any]] = {}

    async def _cached(self, key: str, path: str, params: dict[str, Any]) -> Any:
        now = time.monotonic()
        hit = self._cache.get(key)
        if hit is not None and now - hit[0] < self._ttl:
            return hit[1]
        value = await self._http.get_json(path, params)
        self._cache[key] = (now, value)
        return value

    async def list_events(
        self,
        *,
        page_size: int = 100,
        max_events: int = 500,
        neg_risk: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Open events with embedded markets, paginated by offset."""
        out: list[dict[str, Any]] = []
        offset = 0
        while len(out) < max_events:
            params: dict[str, Any] = {
                "closed": "false",
                "active": "true",
                "limit": page_size,
                "offset": offset,
            }
            if neg_risk is not None:
                params["neg_risk"] = "true" if neg_risk else "false"
            page = await self._cached(f"events:{offset}:{page_size}:{neg_risk}", "/events", params)
            if not isinstance(page, list) or not page:
                break
            out.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
        return out[:max_events]
