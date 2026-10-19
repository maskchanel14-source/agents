"""Strategy B — multi-outcome (neg-risk) arbitrage.

Only groups that are provably mutually exclusive AND complete are traded:
  * event.enableNegRisk == true, event.negRiskAugmented == false
  * every declared market parsed, every market negRisk == true
  * no market flagged negRiskOther (the "Other" catch-all is skipped on purpose)
  * all markets active, not closed, accepting orders

Directions (priced by walking every involved book):

* ``buy_all``  : buy YES in every market. Exactly one outcome pays 1, so a set of
                 S shares pays S. Profitable if  sum(ask_yes_i) < 1  after costs.
                 Held to resolution -> resolution haircut applies.
* ``convert``  : for outcome j, buy NO_j and convert it into 1 YES in every other
                 market i != j (atomic conversion per docs); then SELL each YES_i at
                 the bid. Profitable if  sum_{i!=j} bid_yes_i > ask_no_j  after costs.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from ..book import available_shares
from ..domain import EventGroup, Opportunity, Side
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

NAME = "neg_risk"


def completeness_reasons(group: EventGroup) -> list[str]:
    """Reasons a group may NOT be treated as mutually exclusive & exhaustive."""
    reasons: list[str] = []
    if not group.neg_risk:
        reasons.append("not_neg_risk")
    if group.neg_risk_augmented:
        reasons.append("augmented_neg_risk")
    if len(group.markets) < 2:
        reasons.append("group_too_small")
    if group.declared_market_count != len(group.markets):
        reasons.append("group_incomplete")
    if any(not m.neg_risk for m in group.markets):
        reasons.append("market_not_neg_risk")
    if any(m.neg_risk_other for m in group.markets):
        reasons.append("neg_risk_other")
    if any(m.event_id != group.event_id for m in group.markets):
        reasons.append("event_mismatch")
    return sorted(set(reasons))


class NegRiskStrategy:
    name = NAME

    def scan(self, ctx: StrategyContext, universe: Sequence[EventGroup]) -> list[Opportunity]:
        out: list[Opportunity] = []
        for group in universe:
            ctx.stats["B:groups_seen"] += 1
            markets = group.markets
            if not markets:
                ctx.stats["B:reject:empty_group"] += 1
                continue
            comp = completeness_reasons(group)
            if comp:
                for r in comp:
                    ctx.stats[f"B:reject:{r}"] += 1
                if group.neg_risk_augmented:
                    continue  # documented: augmented events are never traded
                # Still log only if a top-of-book edge exists (cheap check w/o books)
                continue
            asset_ids = [a for m in markets for a in (m.yes.asset_id, m.no.asset_id)]
            books, reasons = check_books(ctx, markets, asset_ids)
            if reasons:
                for r in reasons:
                    ctx.stats[f"B:reject:{r}"] += 1
                continue
            out.extend(self._buy_all(ctx, group, books))
            out.extend(self._convert(ctx, group, books))
        return out

    # --- B1: buy YES in every market -------------------------------------------------
    def _buy_all(self, ctx, group, books) -> list[Opportunity]:
        markets = group.markets
        yes_books = [books[m.yes.asset_id] for m in markets]
        if any(b.best_ask is None for b in yes_books):
            ctx.stats["B:buy_all:no_ask"] += 1
            return []
        top_sum = sum((b.best_ask for b in yes_books), ZERO)
        if top_sum >= ONE:
            ctx.stats["B:buy_all:no_top_edge"] += 1
            return []
        depth = min(available_shares(b.asks) for b in yes_books)
        max_sh = max_shares_for_limits(ctx, top_sum, depth)
        days = max(days_to_end(m, ctx.now_ms) for m in markets)
        ambiguous = any(m.ambiguous_resolution for m in markets)

        def evaluate(size: Decimal) -> Opportunity:
            legs = []
            try:
                for m in markets:
                    legs.append(
                        build_leg(
                            m,
                            m.yes.asset_id,
                            Side.BUY,
                            size,
                            books[m.yes.asset_id],
                            ctx,
                        )
                    )
            except LegRejected as exc:
                return reject_opportunity(ctx, NAME, group.event_id, [exc.reason], "redeem")
            capital = sum((leg.notional for leg in legs), ZERO)
            return make_opportunity(
                ctx=ctx,
                strategy=NAME,
                group_id=f"{group.event_id}:buy_all",
                shares=size,
                legs=tuple(legs),
                gross_edge=size - capital,
                capital=capital,
                gas_units_key="redeem",
                exit_method="redeem",
                payout_notional=size,
                days=days,
                ambiguous=ambiguous,
                complete_group=True,
            )

        best = guarded_search(ctx, NAME, group.event_id, max_sh, [b.asks for b in yes_books], evaluate)
        if best is None:
            ctx.stats["B:buy_all:no_size"] += 1
            return []
        ctx.stats["B:buy_all:evaluated"] += 1
        return [best]

    # --- B2: buy NO_j, convert to YES_i (i != j), sell YES_i ---------------------------
    def _convert(self, ctx, group, books) -> list[Opportunity]:
        markets = group.markets
        results: list[Opportunity] = []
        for j, mj in enumerate(markets):
            no_j = books[mj.no.asset_id]
            if no_j.best_ask is None:
                ctx.stats["B:convert:no_ask"] += 1
                continue
            others = [m for i, m in enumerate(markets) if i != j]
            bids = [books[m.yes.asset_id] for m in others]
            if any(b.best_bid is None for b in bids):
                ctx.stats["B:convert:no_bid"] += 1
                continue
            proceeds_top = sum((b.best_bid for b in bids), ZERO)
            if proceeds_top <= no_j.best_ask:
                ctx.stats["B:convert:no_top_edge"] += 1
                continue
            depth = min([available_shares(no_j.asks)] + [available_shares(b.bids) for b in bids])
            max_sh = max_shares_for_limits(ctx, no_j.best_ask, depth)
            days = max(days_to_end(m, ctx.now_ms) for m in markets)
            ambiguous = any(m.ambiguous_resolution for m in markets)

            def evaluate(
                size: Decimal,
                mj=mj,
                others=others,
                no_j=no_j,
                days=days,
                ambiguous=ambiguous,
            ):
                try:
                    legs = [build_leg(mj, mj.no.asset_id, Side.BUY, size, no_j, ctx)]
                    for m in others:
                        legs.append(
                            build_leg(
                                m,
                                m.yes.asset_id,
                                Side.SELL,
                                size,
                                books[m.yes.asset_id],
                                ctx,
                            )
                        )
                except LegRejected as exc:
                    return reject_opportunity(ctx, NAME, group.event_id, [exc.reason], "sell")
                buy_leg = legs[0]
                proceeds = sum((leg.notional for leg in legs[1:]), ZERO)
                return make_opportunity(
                    ctx=ctx,
                    strategy=NAME,
                    group_id=f"{group.event_id}:convert:{mj.condition_id}",
                    shares=size,
                    legs=tuple(legs),
                    gross_edge=proceeds - buy_leg.notional,
                    capital=buy_leg.notional,
                    gas_units_key="convert",
                    exit_method="sell",
                    payout_notional=ZERO,
                    days=days,
                    ambiguous=ambiguous,
                    complete_group=True,
                )

            level_sets = [no_j.asks] + [b.bids for b in bids]
            best = guarded_search(
                ctx,
                NAME,
                f"{group.event_id}:convert:{mj.condition_id}",
                max_sh,
                level_sets,
                evaluate,
            )
            if best is None:
                ctx.stats["B:convert:no_size"] += 1
                continue
            ctx.stats["B:convert:evaluated"] += 1
            results.append(best)
        return results
