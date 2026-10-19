"""Walk an orderbook side to price a concrete share quantity (VWAP + fees).

Prices are never taken from best-bid/ask alone when size matters: ``walk_book``
consumes levels in order and reports the exact notional, VWAP and whether the
requested size was fully available.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal

from .domain import Level
from .money import SHARE_STEP, ZERO, floor_to, is_multiple_of

FeeFn = Callable[[Decimal, Decimal], Decimal]  # (shares, price) -> fee USDC


@dataclass(frozen=True)
class WalkResult:
    shares: Decimal  # shares actually available/filled (<= requested)
    notional: Decimal  # sum(size * price) over consumed levels
    fee: Decimal  # sum of per-level taker fees (0 if no fee_fn)
    complete: bool  # True iff requested shares were fully covered
    levels_used: int
    worst_price: Decimal | None  # deepest price touched

    @property
    def vwap(self) -> Decimal | None:
        if self.shares <= ZERO:
            return None
        return self.notional / self.shares


def walk_book(
    levels: Sequence[Level],
    target_shares: Decimal,
    fee_fn: FeeFn | None = None,
) -> WalkResult:
    """Consume ``levels`` in the given order until ``target_shares`` is covered.

    ``levels`` must already be ordered from best to worst for the taking side
    (asks ascending for a BUY, bids descending for a SELL) — see ``BookSnapshot``.
    """
    if target_shares < ZERO:
        raise ValueError("target_shares must be non-negative")
    remaining = target_shares
    filled = ZERO
    notional = ZERO
    fee = ZERO
    used = 0
    worst: Decimal | None = None
    for level in levels:
        if remaining <= ZERO:
            break
        if level.size <= ZERO:
            continue
        take = min(level.size, remaining)
        filled += take
        notional += take * level.price
        if fee_fn is not None:
            fee += fee_fn(take, level.price)
        remaining -= take
        used += 1
        worst = level.price
    return WalkResult(
        shares=filled,
        notional=notional,
        fee=fee,
        complete=remaining <= ZERO,
        levels_used=used,
        worst_price=worst,
    )


def available_shares(levels: Iterable[Level]) -> Decimal:
    return sum((lv.size for lv in levels if lv.size > ZERO), ZERO)


def off_tick_prices(levels: Iterable[Level], tick: Decimal) -> list[Decimal]:
    """Prices that are not multiples of the market tick (should never happen)."""
    return [lv.price for lv in levels if not is_multiple_of(lv.price, tick)]


def candidate_sizes(
    books_levels: Sequence[Sequence[Level]],
    max_shares: Decimal,
    min_shares: Decimal,
) -> list[Decimal]:
    """Sizes where the marginal VWAP of at least one leg changes.

    Cost of a multi-leg set is piecewise linear in size with kinks at cumulative
    level boundaries; checking these (plus ``max_shares``) finds the optimum.
    Sizes are floored to ``SHARE_STEP`` so they are orderable.
    """
    points: set[Decimal] = set()
    for levels in books_levels:
        acc = ZERO
        for lv in levels:
            acc += lv.size
            if acc > max_shares:
                break
            points.add(floor_to(acc, SHARE_STEP))
    cap = floor_to(max_shares, SHARE_STEP)
    points.add(cap)
    return sorted(p for p in points if p >= min_shares and p > ZERO)


def consumed_levels(levels: Sequence[Level], target_shares: Decimal) -> list[Level]:
    """The (price, size) pieces a walk of ``target_shares`` would consume."""
    remaining = target_shares
    out: list[Level] = []
    for lv in levels:
        if remaining <= ZERO:
            break
        if lv.size <= ZERO:
            continue
        take = min(lv.size, remaining)
        out.append(Level(lv.price, take))
        remaining -= take
    return out
