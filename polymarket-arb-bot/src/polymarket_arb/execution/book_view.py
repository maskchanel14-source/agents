"""Paper-only book overlay: simulated fills consume liquidity until the book changes.

Without this, the same liquidity would be "filled" again on every cycle, because a
paper fill never reduces the real book. Consumption is kept per (asset, side, price)
and is tied to the book *stamp* (exchange timestamp, receive time) at the moment of
the fill. Any later book message for that asset changes the stamp, which drops the
overlay: the market is assumed to have moved, so the old depth is no longer trusted.
This is conservative in both directions (no double-spending of depth, no phantom
refill inside a static book).
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from ..domain import BookSnapshot, Level, Side
from ..money import ZERO
from ..strategies.common import BookGetter

Stamp = tuple[int, int]


class PaperBookView:
    def __init__(self, base: BookGetter) -> None:
        self._base = base
        # asset -> {(side_key, price): (consumed, stamp_at_fill)}
        self._consumed: dict[str, dict[tuple[str, Decimal], tuple[Decimal, Stamp]]] = defaultdict(dict)

    @staticmethod
    def _stamp(snap: BookSnapshot | None) -> Stamp:
        return (0, 0) if snap is None else (snap.exchange_ts_ms, snap.received_ms)

    def consume(self, asset_id: str, side: Side, price: Decimal, size: Decimal) -> None:
        """Record a simulated fill. A BUY consumes asks, a SELL consumes bids."""
        stamp = self._stamp(self._base.get(asset_id))
        key = (side.value, price)
        cur, cur_stamp = self._consumed[asset_id].get(key, (ZERO, stamp))
        if cur_stamp != stamp:
            cur = ZERO  # book moved since the earlier fill: old overlay no longer applies
        self._consumed[asset_id][key] = (cur + size, stamp)

    def _overlay(
        self, asset_id: str, side_key: str, levels: tuple[Level, ...], stamp: Stamp
    ) -> tuple[Level, ...]:
        table = self._consumed.get(asset_id)
        if not table:
            return levels
        out = []
        for lv in levels:
            entry = table.get((side_key, lv.price))
            if entry is not None and entry[1] == stamp:
                size = lv.size - entry[0]
                if size > ZERO:
                    out.append(Level(lv.price, size))
            else:
                out.append(lv)
        return tuple(out)

    def get(self, asset_id: str) -> BookSnapshot | None:
        snap = self._base.get(asset_id)
        if snap is None:
            return None
        stamp = self._stamp(snap)
        bids = self._overlay(asset_id, Side.SELL.value, snap.bids, stamp)
        asks = self._overlay(asset_id, Side.BUY.value, snap.asks, stamp)
        return BookSnapshot(
            asset_id=snap.asset_id,
            condition_id=snap.condition_id,
            bids=bids,
            asks=asks,
            exchange_ts_ms=snap.exchange_ts_ms,
            received_ms=snap.received_ms,
            tick_size=snap.tick_size,
            min_order_size=snap.min_order_size,
            last_trade_price=snap.last_trade_price,
        )
