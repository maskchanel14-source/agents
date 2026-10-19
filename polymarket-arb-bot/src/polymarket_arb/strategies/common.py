"""Shared pricing / validation / sizing used by every strategy.

Flow for one candidate group of outcome tokens:
  1. ``check_books`` — every book present, fresh, skew-bounded, tradable market.
  2. ``build_leg`` — walk the book for a concrete share count; fees via ``costs``.
  3. ``search_best`` — evaluate every breakpoint size; keep the best one.
  4. ``make_opportunity`` — compute full cost breakdown, annualised return, reasons.

Every rejection is an explicit reason string; nothing is silently dropped.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol

from ..book import candidate_sizes, off_tick_prices, walk_book
from ..config import RiskLimits, Thresholds
from ..costs import (
    CostParams,
    FeeModelUnverified,
    FeeUnknown,
    annualized_pct,
    build_breakdown,
    confidence_score,
    gas_cost_usd,
    holding_hours,
    taker_fee,
    unwind_loss,
)
from ..domain import BookSnapshot, Leg, MarketInfo, Opportunity, Side
from ..money import SHARE_STEP, ZERO, floor_to

MS_PER_DAY = Decimal(86400000)


class BookGetter(Protocol):
    def get(self, asset_id: str) -> BookSnapshot | None: ...


class LegRejected(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class StrategyContext:
    costs: CostParams
    thresholds: Thresholds
    limits: RiskLimits
    books: BookGetter
    now_ms: int
    stats: Counter = field(default_factory=Counter)


def days_to_end(market: MarketInfo, now_ms: int) -> Decimal:
    if market.end_date_ms is None:
        return ZERO
    return max(ZERO, Decimal(market.end_date_ms - now_ms) / MS_PER_DAY)


def check_books(
    ctx: StrategyContext,
    markets: Sequence[MarketInfo],
    asset_ids: Iterable[str],
) -> tuple[dict[str, BookSnapshot], list[str]]:
    """Return fresh snapshots for ``asset_ids`` and a list of rejection reasons."""
    reasons: list[str] = []
    books: dict[str, BookSnapshot] = {}
    for aid in asset_ids:
        snap = ctx.books.get(aid)
        if snap is None:
            reasons.append("no_book")
            continue
        books[aid] = snap
    if reasons:
        return books, sorted(set(reasons))

    for m in markets:
        if m.closed or not m.active or not m.accepting_orders:
            reasons.append("market_not_tradable")
    ages = [ctx.now_ms - s.received_ms for s in books.values()]
    if any(age > ctx.thresholds.max_book_age_ms for age in ages):
        reasons.append("stale_book")
    if ages and (max(ages) - min(ages)) > ctx.thresholds.max_book_skew_ms:
        reasons.append("book_skew")
    for s in books.values():
        if (
            s.best_bid is not None
            and s.best_ask is not None
            and s.best_ask - s.best_bid > ctx.limits.max_quoted_spread
        ):
            reasons.append("spread_anomaly")
    return books, sorted(set(reasons))


def _fee_fn(market: MarketInfo) -> Callable[[Decimal, Decimal], Decimal]:
    def fee(shares: Decimal, price: Decimal) -> Decimal:
        return taker_fee(shares, price, market.fee_schedule, market.fees_enabled)

    return fee


def build_leg(
    market: MarketInfo,
    asset_id: str,
    side: Side,
    shares: Decimal,
    book: BookSnapshot,
    ctx: StrategyContext,
) -> Leg:
    """Walk the book for ``shares`` and return a fully-costed Leg, or raise LegRejected."""
    levels = book.asks if side is Side.BUY else book.bids
    fee_fn = _fee_fn(market)
    try:
        walk = walk_book(levels, shares, fee_fn=fee_fn)
    except FeeUnknown as exc:
        raise LegRejected("fee_unknown") from exc
    except FeeModelUnverified as exc:
        raise LegRejected("fee_model_unverified") from exc
    if not walk.complete:
        raise LegRejected("insufficient_depth")
    consumed = levels[: walk.levels_used]
    if off_tick_prices(consumed, market.tick_size):
        raise LegRejected("off_tick_price")
    if walk.vwap is None:
        raise LegRejected("empty_fill")
    if shares < ctx.thresholds.min_shares or shares < market.min_order_size:
        raise LegRejected("below_min_shares")
    if walk.notional < market.min_order_size:
        raise LegRejected("below_min_notional")

    if side is Side.BUY:
        top = book.best_ask
        unwind_price = book.best_bid
    else:
        top = book.best_bid
        unwind_price = book.best_ask
    if top is None:
        raise LegRejected("no_top_of_book")
    try:
        unwind_fee = ZERO if unwind_price is None else fee_fn(shares, unwind_price)
    except (FeeUnknown, FeeModelUnverified) as exc:
        raise LegRejected("fee_unknown") from exc
    leg = Leg(
        asset_id=asset_id,
        side=side,
        shares=shares,
        avg_price=walk.vwap,
        worst_price=walk.worst_price if walk.worst_price is not None else walk.vwap,
        notional=walk.notional,
        fee=walk.fee,
        top_price=top,
        unwind_price=unwind_price,
        unwind_fee=unwind_fee,
        book_age_ms=ctx.now_ms - book.received_ms,
    )
    return leg


@dataclass(frozen=True)
class Evaluation:
    shares: Decimal
    legs: tuple[Leg, ...]
    gross_edge: Decimal
    capital: Decimal
    gas_units_key: str | None
    exit_method: str
    payout_notional: Decimal
    reasons: tuple[str, ...]
    # populated by make_opportunity
    opportunity: Opportunity | None = None


def gas_reserve_usd(ctx: StrategyContext) -> Decimal:
    """Largest configured on-chain operation cost; reserved out of the notional cap."""
    costs = [gas_cost_usd(k, ctx.costs) for k in ctx.costs.gas_units]
    return max(costs, default=ZERO)


def max_shares_for_limits(
    ctx: StrategyContext,
    capital_per_share: Decimal,
    depth_limit: Decimal,
) -> Decimal:
    """Upper bound on shares from max notional, max shares and book depth."""
    if capital_per_share <= ZERO:
        return ZERO
    reserve = gas_reserve_usd(ctx)
    by_notional = max(ZERO, ctx.limits.max_notional_per_trade - reserve) / capital_per_share
    cap = min(by_notional, ctx.thresholds.max_shares_per_trade, depth_limit)
    return floor_to(cap, SHARE_STEP)


def make_opportunity(
    *,
    ctx: StrategyContext,
    strategy: str,
    group_id: str,
    shares: Decimal,
    legs: tuple[Leg, ...],
    gross_edge: Decimal,
    capital: Decimal,
    gas_units_key: str | None,
    exit_method: str,
    payout_notional: Decimal,
    days: Decimal,
    ambiguous: bool,
    complete_group: bool,
    extra_reasons: Iterable[str] = (),
) -> Opportunity:
    p = ctx.costs
    gas = gas_cost_usd(gas_units_key, p) if gas_units_key else ZERO
    breakdown = build_breakdown(
        gross_edge=gross_edge,
        legs=legs,
        gas_usd=gas,
        exit_method=exit_method,
        payout_notional=payout_notional,
        capital=capital + gas,
        days_to_end=days,
        ambiguous=ambiguous,
        params=p,
    )
    net = breakdown.net_profit
    hours = holding_hours(exit_method, days, p)
    net_pct = net / (capital + gas) if (capital + gas) > ZERO else ZERO
    annual = annualized_pct(net_pct, hours)
    max_age = max((leg.book_age_ms for leg in legs), default=0)
    conf = confidence_score(
        ambiguous=ambiguous,
        max_book_age_ms=max_age,
        max_age_ms=ctx.thresholds.max_book_age_ms,
        complete_group=complete_group,
    )
    reasons: list[str] = list(extra_reasons)
    if capital + gas > ctx.limits.max_notional_per_trade:
        # enforced here so the size search picks a smaller valid size instead of
        # emitting an oversized one that risk would later reject
        reasons.append("exceeds_max_notional")
    if not complete_group:
        reasons.append("incomplete_group")
    if net <= ZERO:
        reasons.append("net_not_positive")
    else:
        if net < ctx.thresholds.min_net_profit_usdc:
            reasons.append("below_min_net_profit")
        if net_pct < ctx.thresholds.min_net_pct:
            reasons.append("below_min_net_pct")
        if annual < ctx.thresholds.min_annualized_pct:
            reasons.append("below_min_annualized")
    opp_id = (
        f"{strategy}:{group_id}:{exit_method}:{shares}:{ctx.now_ms}"  # per detection; idempotency per attempt
    )
    return Opportunity(
        opp_id=opp_id,
        strategy=strategy,
        group_id=group_id,
        legs=legs,
        shares=shares,
        capital_required=capital + gas,
        costs=breakdown,
        holding_hours=hours,
        annualized_pct=annual,
        confidence=conf,
        valid=not reasons,
        reasons=tuple(sorted(set(reasons))),
        detected_ms=ctx.now_ms,
        exit_method=exit_method,
    )


def search_best(
    sizes: Sequence[Decimal],
    evaluate: Callable[[Decimal], Opportunity | None],
) -> Opportunity | None:
    """Evaluate every candidate size and return the best one.

    Preference: a valid opportunity with the highest net profit; otherwise the
    candidate with the highest (possibly negative) net, so the log explains why.
    """
    best: Opportunity | None = None
    for size in sizes:
        opp = evaluate(size)
        if opp is None:
            continue
        if best is None:
            best = opp
            continue
        if (opp.valid, opp.net_profit) > (best.valid, best.net_profit):
            best = opp
    return best


def unwind_summary(legs: Sequence[Leg]) -> Decimal:
    return sum((unwind_loss(leg) for leg in legs), ZERO)


def guarded_search(
    ctx: StrategyContext,
    strategy: str,
    group_id: str,
    max_shares: Decimal,
    level_sets: Sequence[Sequence],
    evaluate: Callable[[Decimal], Opportunity | None],
) -> Opportunity | None:
    sizes = candidate_sizes(level_sets, max_shares, ctx.thresholds.min_shares)
    if not sizes:
        ctx.stats[f"{strategy}:no_sizes"] += 1
        return None
    return search_best(sizes, evaluate)


def reject_opportunity(
    ctx: StrategyContext,
    strategy: str,
    group_id: str,
    reasons: Iterable[str],
    exit_method: str = "merge",
) -> Opportunity:
    """Build an explicit invalid Opportunity (no legs) for logging purposes."""
    zero_cost = build_breakdown(
        gross_edge=ZERO,
        legs=(),
        gas_usd=ZERO,
        exit_method=exit_method,
        payout_notional=ZERO,
        capital=ZERO,
        days_to_end=ZERO,
        ambiguous=False,
        params=ctx.costs,
    )
    rs = tuple(sorted(set(reasons)))
    return Opportunity(
        opp_id=f"{strategy}:{group_id}:rejected",
        strategy=strategy,
        group_id=group_id,
        legs=(),
        shares=ZERO,
        capital_required=ZERO,
        costs=zero_cost,
        holding_hours=ZERO,
        annualized_pct=ZERO,
        confidence=ZERO,
        valid=False,
        reasons=rs,
        detected_ms=ctx.now_ms,
        exit_method=exit_method,
    )
