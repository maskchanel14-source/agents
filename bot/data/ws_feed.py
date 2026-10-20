"""WebSocket market channel — orderbook real-time dengan reconnect & sharding.

wss://ws-subscriptions-clob.polymarket.com/ws/market (docs/POLYMARKET_NOTES.md §4)

- Subscribe: {"assets_ids": [...], "type": "market"}
- Tambah:    {"operation": "subscribe", "assets_ids": [...]}
- Ping/pong: {}
- Event: book | price_change | last_trade_price | tick_size_change | best_bid_ask
         | new_market | market_resolved

Asumsi implementasi price_change (didokumentasikan): update level (price, size)
di sisi `side` (BUY = bids, SELL = asks); size 0 = hapus level. Snapshot `book`
dipakai untuk resinkronisasi penuh saat reconnect / mismatch hash.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional

import aiohttp

from ..decimal_utils import D
from ..models import BookLevel, OrderBookSnapshot

log = logging.getLogger("bot.data.ws")

EventCallback = Callable[[str, dict], Awaitable[None]]


@dataclass
class WsShard:
    shard_id: int
    asset_ids: set[str] = field(default_factory=set)
    connected: bool = False
    last_msg_ms: int = 0
    reconnects: int = 0


class MarketWsFeed:
    """Satu koneksi WS untuk sekerat asset_id (shard)."""

    def __init__(
        self,
        url: str,
        *,
        assets_per_connection: int = 400,
        on_event: Optional[EventCallback] = None,
        reconnect_min: float = 1.0,
        reconnect_max: float = 60.0,
        ping_interval: float = 20.0,
    ) -> None:
        self.url = url
        self.assets_per_connection = max(1, assets_per_connection)
        self.on_event = on_event
        self.reconnect_min = reconnect_min
        self.reconnect_max = reconnect_max
        self.ping_interval = ping_interval
        self.shards: list[WsShard] = []
        self._tasks: list[asyncio.Task] = []
        self._session: Optional[aiohttp.ClientSession] = None
        self._running = False
        self._subs_lock = asyncio.Lock()

    # -- lifecycle ---------------------------------------------------------

    async def start(self) -> None:
        self._running = True
        self._session = aiohttp.ClientSession()
        await self._resubscribe_all(set())

    async def stop(self) -> None:
        self._running = False
        for t in self._tasks:
            t.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        if self._session:
            await self._session.close()
            self._session = None

    async def subscribe(self, asset_ids: list[str]) -> None:
        """Daftarkan asset baru (shard otomatis)."""
        async with self._subs_lock:
            current = {a for s in self.shards for a in s.asset_ids}
            new = [a for a in asset_ids if a not in current]
            if not new:
                return
            for aid in new:
                placed = False
                for shard in self.shards:
                    if len(shard.asset_ids) < self.assets_per_connection:
                        shard.asset_ids.add(aid)
                        placed = True
                        break
                if not placed:
                    shard = WsShard(shard_id=len(self.shards), asset_ids={aid})
                    self.shards.append(shard)
            if self._running and self._session:
                await self._ensure_tasks()

    async def unsubscribe(self, asset_ids: list[str]) -> None:
        async with self._subs_lock:
            drop = set(asset_ids)
            for shard in self.shards:
                shard.asset_ids -= drop

    # -- internals ---------------------------------------------------------

    async def _ensure_tasks(self) -> None:
        active = {t.get_name() for t in self._tasks if not t.done()}
        for shard in self.shards:
            name = f"ws-shard-{shard.shard_id}"
            if name not in active and shard.asset_ids:
                task = asyncio.create_task(self._run_shard(shard), name=name)
                self._tasks.append(task)

    async def _resubscribe_all(self, seen: set) -> None:
        await self._ensure_tasks()

    async def _run_shard(self, shard: WsShard) -> None:
        backoff = self.reconnect_min
        while self._running:
            try:
                assert self._session is not None
                async with self._session.ws_connect(self.url, heartbeat=self.ping_interval) as ws:
                    shard.connected = True
                    backoff = self.reconnect_min
                    await ws.send_json({"assets_ids": sorted(shard.asset_ids), "type": "market"})
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            shard.last_msg_ms = int(time.time() * 1000)
                            try:
                                data = json.loads(msg.data)
                            except json.JSONDecodeError:
                                continue
                            await self._dispatch(data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
            except asyncio.CancelledError:
                shard.connected = False
                raise
            except Exception as exc:
                log.warning("ws shard %s error: %s", shard.shard_id, exc)
            shard.connected = False
            shard.reconnects += 1
            if not self._running:
                return
            jitter = random.uniform(0, backoff / 2)
            log.info("ws shard %s reconnecting in %.1fs", shard.shard_id, backoff + jitter)
            await asyncio.sleep(backoff + jitter)
            backoff = min(self.reconnect_max, backoff * 2)
            # setelah reconnect, subscribe ulang penuh (snapshot `book` dikirim ulang)
            try:
                async with self._subs_lock:
                    shard.asset_ids = set(shard.asset_ids)
            except Exception:
                pass

    async def _dispatch(self, data: dict) -> None:
        etype = data.get("event_type") or data.get("type") or ""
        if self.on_event and etype:
            try:
                await self.on_event(str(etype), data)
            except Exception:
                log.exception("ws event handler failed for %s", etype)

    @property
    def stats(self) -> dict:
        return {
            "shards": len(self.shards),
            "connected": sum(1 for s in self.shards if s.connected),
            "assets": sum(len(s.asset_ids) for s in self.shards),
            "reconnects": sum(s.reconnects for s in self.shards),
        }


# ---------------------------------------------------------------------------
# Penerapan event ke snapshot (dipakai MarketDataHub)
# ---------------------------------------------------------------------------

def apply_price_change(snap: OrderBookSnapshot, change: dict) -> OrderBookSnapshot:
    """Terapkan satu entri price_change ke snapshot.

    Asumsi: (price, size) meng-SET level di sisi `side` (BUY=bids, SELL=asks);
    size 0 menghapus level.
    """
    price = D(str(change.get("price")))
    size = D(str(change.get("size", "0")))
    side = str(change.get("side", "")).upper()
    if side == "BUY":
        bids = {lv.price: lv.size for lv in snap.bids}
        if size > 0:
            bids[price] = size
        else:
            bids.pop(price, None)
        new_bids = tuple(
            sorted((BookLevel(p, s) for p, s in bids.items()), key=lambda lv: lv.price, reverse=True)
        )
        new_asks = snap.asks
    else:
        asks = {lv.price: lv.size for lv in snap.asks}
        if size > 0:
            asks[price] = size
        else:
            asks.pop(price, None)
        new_asks = tuple(sorted((BookLevel(p, s) for p, s in asks.items()), key=lambda lv: lv.price))
        new_bids = snap.bids
    return OrderBookSnapshot(
        asset_id=snap.asset_id,
        bids=new_bids,
        asks=new_asks,
        ts_ms=snap.ts_ms,
        recv_ms=int(time.time() * 1000),
        hash=change.get("hash") or snap.hash,
        tick_size=snap.tick_size,
        min_order_size=snap.min_order_size,
        neg_risk=snap.neg_risk,
        last_trade_price=snap.last_trade_price,
    )
