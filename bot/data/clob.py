"""CLOB REST — order book (single & batch) sebagai fallback/rekonsiliasi.

Endpoint: https://clob.polymarket.com (docs/POLYMARKET_NOTES.md §3).
"""

from __future__ import annotations

import logging
from typing import Optional, Sequence

from ..decimal_utils import D
from ..models import OrderBookSnapshot
from .http import LIMITS, HttpClient

log = logging.getLogger("bot.data.clob")


class ClobClient:
    def __init__(self, http: HttpClient, base_url: str) -> None:
        self.http = http
        self.base = base_url.rstrip("/")

    async def get_book(self, asset_id: str) -> OrderBookSnapshot:
        raw = await self.http.get_json(
            f"{self.base}/book", params={"token_id": asset_id}, limiter=LIMITS["clob_book"]
        )
        return parse_book(raw)

    async def get_books(self, asset_ids: Sequence[str], *, batch_size: int = 20) -> dict[str, OrderBookSnapshot]:
        """POST /books batch (batas payload per request — batch kecil)."""
        out: dict[str, OrderBookSnapshot] = {}
        ids = list(asset_ids)
        for i in range(0, len(ids), batch_size):
            chunk = ids[i : i + batch_size]
            try:
                raw = await self.http.post_json(
                    f"{self.base}/books",
                    json=[{"token_id": a} for a in chunk],
                    limiter=LIMITS["clob_books"],
                )
            except Exception as exc:
                log.warning("POST /books chunk failed: %s", exc)
                continue
            items = raw if isinstance(raw, list) else raw.get("data") or []
            for item in items:
                try:
                    snap = parse_book(item)
                    out[snap.asset_id] = snap
                except Exception as exc:
                    log.debug("book parse failed: %s", exc)
        return out


def parse_book(raw: dict) -> OrderBookSnapshot:
    """Parse response /book atau event WS 'book' -> snapshot ternormalisasi.

    Urutan level TIDAK diandalkan (REST vs WS berbeda) — difile `from_levels`.
    """
    ts = raw.get("timestamp") or 0
    try:
        ts_ms = int(ts)
    except (TypeError, ValueError):
        ts_ms = 0
    tick = raw.get("tick_size") or raw.get("tickSize")
    min_size = raw.get("min_order_size") or raw.get("minOrderSize")
    return OrderBookSnapshot.from_levels(
        asset_id=str(raw.get("asset_id") or raw.get("assetId") or ""),
        bids=[(lv.get("price"), lv.get("size")) for lv in (raw.get("bids") or [])],
        asks=[(lv.get("price"), lv.get("size")) for lv in (raw.get("asks") or [])],
        ts_ms=ts_ms,
        hash=raw.get("hash"),
        tick_size=D(str(tick)) if tick is not None else None,
        min_order_size=D(str(min_size)) if min_size is not None else None,
        neg_risk=raw.get("neg_risk") if raw.get("neg_risk") is not None else raw.get("negRisk"),
        last_trade_price=D(str(raw["last_trade_price"])) if raw.get("last_trade_price") is not None else None,
    )
