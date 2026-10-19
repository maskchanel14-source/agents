"""In-memory orderbooks maintained from the CLOB WebSocket (and REST snapshots).

Integrity rules (documented in docs/POLYMARKET_NOTES.md):
  * a ``book`` snapshot (re)initialises an asset's book;
  * ``price_change`` deltas are ignored until a snapshot has been received;
  * events older than the last applied exchange timestamp for an asset are dropped;
  * if a price_change carries best_bid/best_ask that disagree with our rebuilt top
    of book, the asset is invalidated until the next snapshot (book_mismatch);
  * on WebSocket disconnect every book is invalidated (no stale data is ever served).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from ..domain import BookSnapshot, Level
from ..markets import parse_book
from ..money import dec


@dataclass
class _Book:
    bids: dict[Decimal, Decimal] = field(default_factory=dict)
    asks: dict[Decimal, Decimal] = field(default_factory=dict)
    exchange_ts_ms: int = 0
    received_ms: int = 0
    tick: Decimal = Decimal("0.01")
    min_size: Decimal = Decimal(5)
    last_trade: Decimal | None = None
    condition_id: str = ""
    valid: bool = False


class BookStore:
    def __init__(self, default_tick: Decimal = Decimal("0.01")) -> None:
        self._books: dict[str, _Book] = {}
        self._default_tick = default_tick
        self.counters: dict[str, int] = {}

    def _count(self, key: str) -> None:
        self.counters[key] = self.counters.get(key, 0) + 1

    def count_external(self, key: str) -> None:
        """Public counter hook for transport-level events (malformed frames, etc.)."""
        self._count(key)

    # ---- meta ------------------------------------------------------------------
    def register(self, asset_id: str, tick: Decimal, min_size: Decimal, condition_id: str = "") -> None:
        b = self._books.setdefault(asset_id, _Book(tick=tick, min_size=min_size, condition_id=condition_id))
        b.tick = tick
        b.min_size = min_size
        if condition_id:
            b.condition_id = condition_id

    def known_assets(self) -> list[str]:
        return list(self._books)

    def invalidate_all(self, reason: str) -> None:
        for b in self._books.values():
            if b.valid:
                b.valid = False
                self._count(f"invalidated:{reason}")

    def invalidate(self, asset_id: str, reason: str) -> None:
        b = self._books.get(asset_id)
        if b is not None and b.valid:
            b.valid = False
            self._count(f"invalidated:{reason}")

    # ---- writes ----------------------------------------------------------------
    def apply_snapshot(self, raw: dict[str, Any], now_ms: int) -> str:
        """Apply a full ``book`` object (WS event or REST /book)."""
        snap = parse_book(raw, now_ms)
        aid = snap.asset_id
        cur = self._books.get(aid)
        if cur is None:
            cur = _Book(
                tick=snap.tick_size,
                min_size=snap.min_order_size,
                condition_id=snap.condition_id,
            )
            self._books[aid] = cur
        if cur.valid and snap.exchange_ts_ms < cur.exchange_ts_ms:
            self._count("out_of_order_snapshot")
            return aid
        cur.bids = {lv.price: lv.size for lv in snap.bids}
        cur.asks = {lv.price: lv.size for lv in snap.asks}
        cur.exchange_ts_ms = snap.exchange_ts_ms
        cur.received_ms = now_ms
        cur.last_trade = snap.last_trade_price
        cur.valid = True
        self._count("snapshot")
        return aid

    def apply_price_change(self, msg: dict[str, Any], now_ms: int) -> None:
        ts = int(str(msg.get("timestamp", 0)))
        for ch in msg.get("price_changes", []):
            aid = str(ch.get("asset_id", ""))
            cur = self._books.get(aid)
            if cur is None or not cur.valid:
                self._count("delta_before_snapshot")
                continue
            if ts < cur.exchange_ts_ms:
                self._count("out_of_order_delta")
                continue
            price = dec(str(ch["price"]))
            size = dec(str(ch["size"]))
            side = str(ch.get("side", "")).upper()
            book_side = cur.bids if side == "BUY" else cur.asks if side == "SELL" else None
            if book_side is None:
                self._count("bad_side")
                continue
            if size <= 0:
                book_side.pop(price, None)
            else:
                book_side[price] = size
            cur.exchange_ts_ms = ts
            cur.received_ms = now_ms
            self._count("delta")
            bb = ch.get("best_bid") or None
            ba = ch.get("best_ask") or None
            if (bb is not None or ba is not None) and not self._top_matches(cur, bb, ba):
                cur.valid = False
                self._count("invalidated:book_mismatch")

    def apply_tick_change(self, msg: dict[str, Any]) -> None:
        cur = self._books.get(str(msg.get("asset_id", "")))
        if cur is not None and msg.get("new_tick_size") is not None:
            cur.tick = dec(str(msg["new_tick_size"]))
            self._count("tick_change")

    def apply_last_trade(self, msg: dict[str, Any]) -> None:
        cur = self._books.get(str(msg.get("asset_id", "")))
        if cur is not None and msg.get("price") is not None:
            cur.last_trade = dec(str(msg["price"]))

    def apply_message(self, msg: dict[str, Any], now_ms: int) -> str:
        et = str(msg.get("event_type", ""))
        if et == "book":
            self.apply_snapshot(msg, now_ms)
        elif et == "price_change":
            self.apply_price_change(msg, now_ms)
        elif et == "tick_size_change":
            self.apply_tick_change(msg)
        elif et == "last_trade_price":
            self.apply_last_trade(msg)
        elif et == "best_bid_ask":
            pass  # top-of-book cross-check is done on price_change; nothing else to do
        else:
            self._count("unknown_event")
            return "unknown"
        return et

    # ---- reads -----------------------------------------------------------------
    def get(self, asset_id: str) -> BookSnapshot | None:
        """Snapshot of a VALID book (stale ages are judged by the caller)."""
        b = self._books.get(asset_id)
        if b is None or not b.valid:
            return None
        bids = tuple(Level(p, s) for p, s in sorted(b.bids.items(), reverse=True) if s > 0)
        asks = tuple(Level(p, s) for p, s in sorted(b.asks.items()) if s > 0)
        return BookSnapshot(
            asset_id=asset_id,
            condition_id=b.condition_id,
            bids=bids,
            asks=asks,
            exchange_ts_ms=b.exchange_ts_ms,
            received_ms=b.received_ms,
            tick_size=b.tick,
            min_order_size=b.min_size,
            last_trade_price=b.last_trade,
        )

    @staticmethod
    def _top_matches(cur: _Book, bb: Any, ba: Any) -> bool:
        best_bid = max(cur.bids) if any(s > 0 for s in cur.bids.values()) else None
        best_ask = min(cur.asks) if any(s > 0 for s in cur.asks.values()) else None
        if bb is not None and best_bid is not None and dec(str(bb)) != best_bid:
            return False
        return not (ba is not None and best_ask is not None and dec(str(ba)) != best_ask)
