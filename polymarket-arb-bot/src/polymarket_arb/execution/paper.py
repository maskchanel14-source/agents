"""Paper executor: simulates FOK fills against the LIVE book at execution time.

* Every leg is re-walked on the current book for the full share count. If any leg
  cannot be filled completely (or the book is gone/stale), the whole opportunity is
  cancelled — no partial positions are ever created (FOK semantics).
* Fees use the same ``taker_fee`` function as the signal, on the re-walked levels.
* Gas is taken from the opportunity's cost breakdown (already conservative).
* Idempotent: an opportunity id can only be executed once per mode.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from ..book import consumed_levels, walk_book
from ..costs import FeeModelUnverified, FeeUnknown, taker_fee
from ..domain import MarketInfo, Opportunity, Side
from ..money import ZERO
from ..state.store import OrderRecord, StateStore
from ..strategies.common import BookGetter
from .base import ExecutionResult, LegFill


class PaperExecutor:
    mode = "paper"

    def __init__(
        self,
        store: StateStore,
        books: BookGetter,
        markets_by_asset: dict[str, MarketInfo],
        max_book_age_ms: int,
    ) -> None:
        self.store = store
        self.books = books
        self.markets_by_asset = markets_by_asset
        self.max_book_age_ms = max_book_age_ms

    async def cancel_all(self) -> int:
        return 0  # nothing resting in paper mode

    async def execute(self, opp: Opportunity, now_ms: int) -> ExecutionResult:
        if not opp.valid:
            return ExecutionResult(status="refused", reason="opportunity_invalid")
        if not self.store.mark_executed(opp.opp_id):
            return ExecutionResult(status="skipped_duplicate", reason="already_executed")

        fills: list[LegFill] = []
        consumption: list[tuple[Side, str, list]] = []
        cash_now = ZERO
        cash_then = ZERO
        fees = ZERO
        for leg in opp.legs:
            book = self.books.get(leg.asset_id)
            if book is None:
                return self._cancel(opp, now_ms, "no_book_at_execution")
            if now_ms - book.received_ms > self.max_book_age_ms:
                return self._cancel(opp, now_ms, "stale_book_at_execution")
            market = self.markets_by_asset.get(leg.asset_id)
            if market is None:
                return self._cancel(opp, now_ms, "unknown_market")
            levels = book.asks if leg.side is Side.BUY else book.bids
            try:
                fee_fn = _fee_fn(market)
                walk = walk_book(levels, leg.shares, fee_fn=fee_fn)
            except FeeUnknown:
                return self._cancel(opp, now_ms, "fee_unknown_at_execution")
            except FeeModelUnverified:
                return self._cancel(opp, now_ms, "fee_model_unverified_at_execution")
            if not walk.complete or walk.vwap is None:
                return self._cancel(opp, now_ms, "insufficient_depth_at_execution")
            sign = Decimal(-1) if leg.side is Side.BUY else Decimal(1)
            cash_now += sign * walk.notional
            cash_then += sign * leg.notional
            fees += walk.fee
            fills.append(LegFill(leg.asset_id, leg.side, leg.shares, walk.vwap, walk.fee))
            consumption.append((leg.side, leg.asset_id, consumed_levels(levels, leg.shares)))

        gross_now = opp.costs.gross_edge + (cash_now - cash_then)
        consume = getattr(self.books, "consume", None)
        if consume is not None:  # paper overlay: simulated fills remove liquidity
            for side, aid, pieces in consumption:
                for lv in pieces:
                    consume(aid, side, lv.price, lv.size)
        for i, (leg, fill) in enumerate(zip(opp.legs, fills)):
            cid = f"{opp.opp_id}#{i}"
            self.store.record_order(
                OrderRecord(
                    client_order_id=cid,
                    opp_id=opp.opp_id,
                    asset_id=leg.asset_id,
                    side=leg.side.value,
                    price=fill.price,
                    shares=fill.shares,
                    order_type="FOK",
                    status="matched",
                    filled_shares=fill.shares,
                    fee=fill.fee,
                ),
                now_ms,
            )
            if opp.exit_method == "redeem" and leg.side is Side.BUY:
                self.store.add_fill(leg.asset_id, fill.shares)
            # merge / sell exits return to flat, so positions net to zero.

        kind = "realized" if opp.exit_method in ("merge", "sell") else "expected_pending_resolution"
        net = gross_now - fees - opp.costs.gas_usd
        self.store.record_pnl(now_ms, opp.opp_id, kind, net)
        return ExecutionResult(
            status="filled",
            fills=tuple(fills),
            gross_edge=gross_now,
            fees=fees,
            gas_usd=opp.costs.gas_usd,
            extra={"pnl_kind": kind},
        )

    def _cancel(self, opp: Opportunity, now_ms: int, reason: str) -> ExecutionResult:
        self.store.log_event(now_ms, "warn", "fok_cancelled", {"opp_id": opp.opp_id, "reason": reason})
        return ExecutionResult(status="cancelled", reason=reason)


def _fee_fn(market: MarketInfo) -> Callable[[Decimal, Decimal], Decimal]:
    def fee(shares: Decimal, price: Decimal) -> Decimal:
        return taker_fee(shares, price, market.fee_schedule, market.fees_enabled)

    return fee
