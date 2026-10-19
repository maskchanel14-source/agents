"""Strategy A — intra-market binary arbitrage (YES + NO on the same market).

Two directions, both priced by walking the orderbook (never last/mid price):

* ``buy_pair``  : buy YES and NO at the asks; hold a complete set; MERGE it back
                  to pUSD. Profitable if  ask_yes + ask_no < 1  (after costs).
* ``split_sell``: split 1 pUSD into YES+NO; SELL both at the bids. Profitable if
                  bid_yes + bid_no > 1  (after costs).
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from ..book import available_shares
from ..domain import MarketInfo, Opportunity, Side
from ..money import ONE, ZERO
from .common import (
    LegRejected,
    StrategyContext,
    build_leg,
    check_books,
    days_to_end,
    guarded_search,
    make_opportunity,
    max_shares_for_limits,
    reject_opportunity,
)

NAME = "intra_binary"


class IntraBinaryStrategy:
    name = NAME

    def __init__(self, exit_method: str = "merge") -> None:
        if exit_method != "merge":
            raise ValueError("binary arb exit must be 'merge' (documented, no market exposure)")
        self.exit_method = exit_method

    def scan(self, ctx: StrategyContext, universe: Sequence[MarketInfo]) -> list[Opportunity]:
        out: list[Opportunity] = []
        for m in universe:
            ctx.stats["A:markets_seen"] += 1
            books, reasons = check_books(ctx, [m], m.asset_ids)
            if reasons:
                # Only log a rejection where a top-of-book edge would otherwise exist.
                top = _top_edge(books, m)
                if top:
                    out.append(reject_opportunity(ctx, NAME, m.condition_id, reasons, self.exit_method))
                for r in reasons:
                    ctx.stats[f"A:reject:{r}"] += 1
                continue
            yb, nb = books[m.yes.asset_id], books[m.no.asset_id]
            if yb.best_ask is not None and nb.best_ask is not None and yb.best_ask + nb.best_ask < ONE:
                opp = self._buy_pair(ctx, m, yb, nb)
                if opp is not None:
                    out.append(opp)
            if yb.best_bid is not None and nb.best_bid is not None and yb.best_bid + nb.best_bid > ONE:
                opp = self._split_sell(ctx, m, yb, nb)
                if opp is not None:
                    out.append(opp)
            if not _top_edge(books, m):
                ctx.stats["A:no_top_edge"] += 1
        return out

    def _buy_pair(self, ctx, m, yb, nb) -> Opportunity | None:
        cap_per_share = yb.best_ask + nb.best_ask
        depth = min(available_shares(yb.asks), available_shares(nb.asks))
        max_sh = max_shares_for_limits(ctx, cap_per_share, depth)
        days = days_to_end(m, ctx.now_ms)

        def evaluate(size: Decimal) -> Opportunity:
            try:
                ly = build_leg(m, m.yes.asset_id, Side.BUY, size, yb, ctx)
                ln = build_leg(m, m.no.asset_id, Side.BUY, size, nb, ctx)
            except LegRejected as exc:
                return reject_opportunity(ctx, NAME, m.condition_id, [exc.reason], self.exit_method)
            capital = ly.notional + ln.notional
            return make_opportunity(
                ctx=ctx,
                strategy=NAME,
                group_id=m.condition_id,
                shares=size,
                legs=(ly, ln),
                gross_edge=size - capital,
                capital=capital,
                gas_units_key="merge",
                exit_method="merge",
                payout_notional=size,
                days=days,
                ambiguous=m.ambiguous_resolution,
                complete_group=True,
            )

        best = guarded_search(ctx, NAME, m.condition_id, max_sh, [yb.asks, nb.asks], evaluate)
        if best is None:
            ctx.stats["A:buy_pair:no_size"] += 1
            return None
        ctx.stats["A:buy_pair:evaluated"] += 1
        return best

    def _split_sell(self, ctx, m, yb, nb) -> Opportunity | None:
        # Splitting costs 1 pUSD per set; capital per share is therefore 1.
        depth = min(available_shares(yb.bids), available_shares(nb.bids))
        max_sh = max_shares_for_limits(ctx, ONE, depth)
        days = days_to_end(m, ctx.now_ms)

        def evaluate(size: Decimal) -> Opportunity:
            try:
                ly = build_leg(m, m.yes.asset_id, Side.SELL, size, yb, ctx)
                ln = build_leg(m, m.no.asset_id, Side.SELL, size, nb, ctx)
            except LegRejected as exc:
                return reject_opportunity(ctx, NAME, m.condition_id, [exc.reason], "sell")
            proceeds = ly.notional + ln.notional
            return make_opportunity(
                ctx=ctx,
                strategy=NAME,
                group_id=m.condition_id,
                shares=size,
                legs=(ly, ln),
                gross_edge=proceeds - size,
                capital=size,
                gas_units_key="split",
                exit_method="sell",
                payout_notional=ZERO,
                days=days,
                ambiguous=m.ambiguous_resolution,
                complete_group=True,
            )

        best = guarded_search(ctx, NAME, m.condition_id, max_sh, [yb.bids, nb.bids], evaluate)
        if best is None:
            ctx.stats["A:split_sell:no_size"] += 1
            return None
        ctx.stats["A:split_sell:evaluated"] += 1
        return best


def _top_edge(books, m: MarketInfo) -> bool:
    yb = books.get(m.yes.asset_id)
    nb = books.get(m.no.asset_id)
    if yb is None or nb is None:
        return False
    if yb.best_ask is not None and nb.best_ask is not None and yb.best_ask + nb.best_ask < ONE:
        return True
    return bool(yb.best_bid is not None and nb.best_bid is not None and yb.best_bid + nb.best_bid > ONE)
