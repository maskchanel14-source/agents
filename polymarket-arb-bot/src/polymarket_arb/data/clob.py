"""CLOB REST client (read-only): orderbook snapshots. No authentication, no orders."""

from __future__ import annotations

from typing import Any

from .http import JsonHttp


class ClobClient:
    def __init__(self, http: JsonHttp) -> None:
        self._http = http

    async def get_book(self, asset_id: str) -> dict[str, Any]:
        data = await self._http.get_json("/book", {"token_id": asset_id})
        if not isinstance(data, dict):
            raise TypeError("unexpected /book response")
        return data
