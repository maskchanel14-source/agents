"""MarketDataHub — gabungan WS + REST: cache book, staleness, coverage.

Pipeline scanner memakai hub ini sebagai satu-satunya sumber orderbook.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional, Sequence

from ..models import CoverageReport, MarketMeta, OrderBookSnapshot
from .clob import ClobClient, parse_book
from .ws_feed import MarketWsFeed, apply_price_change

log = logging.getLogger("bot.data.feed")


class MarketDataHub:
    def __init__(
        self,
        clob: ClobClient,
        ws: MarketWsFeed,
        *,
        stale_after_ms: int = 3000,
        rest_reconcile_seconds: float = 60.0,
    ) -> None:
        self.clob = clob
        self.ws = ws
        self.stale_after_ms = stale_after_ms
        self.rest_reconcile_seconds = rest_reconcile_seconds
        self.books: dict[str, OrderBookSnapshot] = {}
        self.markets: dict[str, MarketMeta] = {}          # market_id -> meta
        self.asset_to_market: dict[str, str] = {}          # asset_id -> market_id
        self.coverage = CoverageReport()
        self._lock = asyncio.Lock()
        self._reconcile_task: Optional[asyncio.Task] = None
        self.ws.on_event = self._on_ws_event  # type: ignore[assignment]

    # -- lifecycle ---------------------------------------------------------

    async def start(self) -> None:
        await self.ws.start()
        self._reconcile_task = asyncio.create_task(self._reconcile_loop(), name="rest-reconcile")

    async def stop(self) -> None:
        if self._reconcile_task:
            self._reconcile_task.cancel()
            try:
                await self._reconcile_task
            except (asyncio.CancelledError, Exception):
                pass
        await self.ws.stop()

    # -- registry ----------------------------------------------------------

    async def register_markets(self, markets: Sequence[MarketMeta]) -> None:
        async with self._lock:
            for m in markets:
                self.markets[m.market_id] = m
                self.asset_to_market[m.yes_asset_id] = m.market_id
                self.asset_to_market[m.no_asset_id] = m.market_id
            assets = [a for m in markets for a in m.asset_ids]
        self.coverage.markets_monitored = len(self.markets)
        self.coverage.ws_connections = self.ws.stats["shards"]
        if assets:
            await self.ws.subscribe(assets)
            # seed awal via REST agar bisa scan sebelum WS snapshot datang
            await self._refresh_books_rest(assets)
        self.coverage.ws_subscribed_assets = self.ws.stats["assets"]

    async def remove_markets(self, market_ids: Sequence[str]) -> None:
        async with self._lock:
            assets: list[str] = []
            for mid in market_ids:
                m = self.markets.pop(mid, None)
                if m:
                    assets.extend(m.asset_ids)
                    self.asset_to_market.pop(m.yes_asset_id, None)
                    self.asset_to_market.pop(m.no_asset_id, None)
                    self.books.pop(m.yes_asset_id, None)
                    self.books.pop(m.no_asset_id, None)
        if assets:
            await self.ws.unsubscribe(assets)

    # -- akses -------------------------------------------------------------

    def get_book(self, asset_id: str) -> Optional[OrderBookSnapshot]:
        return self.books.get(asset_id)

    def is_fresh(self, asset_id: str, now_ms: Optional[int] = None) -> bool:
        snap = self.books.get(asset_id)
        return snap is not None and not snap.is_stale(self.stale_after_ms, now_ms)

    def market_for_asset(self, asset_id: str) -> Optional[MarketMeta]:
        mid = self.asset_to_market.get(asset_id)
        return self.markets.get(mid) if mid else None

    def coverage_snapshot(self) -> CoverageReport:
        self.coverage.ws_connections = self.ws.stats["shards"]
        self.coverage.ws_subscribed_assets = self.ws.stats["assets"]
        self.coverage.stale_assets = sum(
            1 for a, b in self.books.items() if b.is_stale(self.stale_after_ms)
        )
        self.coverage.markets_monitored = len(self.markets)
        return self.coverage

    # -- WS handler --------------------------------------------------------

    async def _on_ws_event(self, etype: str, data: dict) -> None:
        if etype == "book":
            try:
                snap = parse_book(data)
                if snap.asset_id:
                    async with self._lock:
                        self.books[snap.asset_id] = snap
            except Exception:
                log.debug("failed to parse book event", exc_info=True)
        elif etype == "price_change":
            changes = data.get("price_changes") or data.get("priceChanges") or []
            async with self._lock:
                for ch in changes:
                    aid = str(ch.get("asset_id") or ch.get("assetId") or "")
                    snap = self.books.get(aid)
                    if snap is not None:
                        self.books[aid] = apply_price_change(snap, ch)
        elif etype == "last_trade_price":
            aid = str(data.get("asset_id") or "")
            snap = self.books.get(aid)
            if snap is not None:
                from ..decimal_utils import D
                from ..models import OrderBookSnapshot as OBS
                self.books[aid] = OBS(
                    asset_id=snap.asset_id, bids=snap.bids, asks=snap.asks,
                    ts_ms=snap.ts_ms, recv_ms=snap.recv_ms, hash=snap.hash,
                    tick_size=snap.tick_size, min_order_size=snap.min_order_size,
                    neg_risk=snap.neg_risk,
                    last_trade_price=D(str(data["price"])) if data.get("price") is not None else snap.last_trade_price,
                )
        elif etype == "market_resolved":
            mid = str(data.get("id") or "")
            if mid:
                await self.remove_markets([mid])
        elif etype == "new_market":
            self.coverage.last_full_scan_ms = int(time.time() * 1000)
            # delta market baru diproses penuh oleh discovery loop; cukup catat
            log.info("new_market event: %s", data.get("slug"))

    # -- REST fallback / rekonsiliasi --------------------------------------

    async def _refresh_books_rest(self, asset_ids: Sequence[str]) -> int:
        books = await self.clob.get_books(asset_ids, batch_size=self.ws.assets_per_connection and 20)
        async with self._lock:
            for aid, snap in books.items():
                self.books[aid] = snap
        return len(books)

    async def _reconcile_loop(self) -> None:
        while True:
            await asyncio.sleep(self.rest_reconcile_seconds)
            try:
                assets = list(self.books.keys()) or list(self.asset_to_market.keys())
                if not assets:
                    continue
                n = await self._refresh_books_rest(assets)
                log.debug("reconciled %d books via REST", n)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.warning("REST reconcile failed", exc_info=True)

    async def refresh_all_now(self) -> int:
        assets = list(self.asset_to_market.keys())
        return await self._refresh_books_rest(assets)
