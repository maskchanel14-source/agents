"""Domain types shared by data, strategies, costs, risk and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

from .money import ZERO


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Level:
    price: Decimal
    size: Decimal


@dataclass(frozen=True)
class BookSnapshot:
    """Immutable, normalised orderbook for one outcome token.

    ``bids`` are sorted descending (best first), ``asks`` ascending (best first).
    Times are epoch milliseconds.
    """

    asset_id: str
    condition_id: str
    bids: tuple[Level, ...]
    asks: tuple[Level, ...]
    exchange_ts_ms: int
    received_ms: int
    tick_size: Decimal
    min_order_size: Decimal
    last_trade_price: Decimal | None = None

    @property
    def best_bid(self) -> Decimal | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Decimal | None:
        return self.asks[0].price if self.asks else None


@dataclass(frozen=True)
class FeeSchedule:
    """Mirror of ``market.trading.feeSchedule`` (Gamma)."""

    rate: Decimal
    exponent: Decimal
    taker_only: bool
    rebate_rate: Decimal


@dataclass(frozen=True)
class OutcomeToken:
    label: str  # "Yes" / "No"
    asset_id: str  # CTF token id (v1) or position id (v2)


@dataclass(frozen=True)
class MarketInfo:
    condition_id: str
    slug: str
    question: str
    description: str
    resolution_source: str
    end_date_ms: int | None
    active: bool
    closed: bool
    accepting_orders: bool
    neg_risk: bool
    neg_risk_other: bool
    event_id: str | None
    event_neg_risk: bool
    event_neg_risk_augmented: bool
    version: str
    yes: OutcomeToken
    no: OutcomeToken
    tick_size: Decimal
    min_order_size: Decimal
    fees_enabled: bool | None
    fee_schedule: FeeSchedule | None
    seconds_delay: int = 0
    extra: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    @property
    def asset_ids(self) -> tuple[str, str]:
        return (self.yes.asset_id, self.no.asset_id)

    @property
    def ambiguous_resolution(self) -> bool:
        """True when resolution criteria look thin (no source or very short text)."""
        return (not self.resolution_source.strip()) or len(self.description.strip()) < 80


@dataclass(frozen=True)
class EventGroup:
    """A Gamma event whose markets form a (candidate) mutually-exclusive group."""

    event_id: str
    neg_risk: bool
    neg_risk_augmented: bool
    declared_market_count: int
    markets: tuple[MarketInfo, ...]


@dataclass(frozen=True)
class Leg:
    """One executable leg of an opportunity, priced by walking the book."""

    asset_id: str
    side: Side
    shares: Decimal
    avg_price: Decimal  # VWAP across consumed levels
    worst_price: Decimal  # deepest level touched (the limit price a FOK order must respect)
    notional: Decimal  # shares * avg_price (USDC)
    fee: Decimal  # taker fee in USDC (rounded 5dp, rounded up)
    top_price: Decimal  # best ask (BUY) or best bid (SELL) at snapshot time
    unwind_price: Decimal | None  # price to flatten this leg if a sibling leg fails
    unwind_fee: Decimal  # fee to flatten (taker)
    book_age_ms: int = 0


@dataclass(frozen=True)
class CostBreakdown:
    gross_edge: Decimal  # payout/proceeds minus cost, before any fee/cost
    taker_fees: Decimal
    gas_usd: Decimal
    leg_risk_expected_loss: Decimal
    resolution_haircut: Decimal
    safety_margin: Decimal
    capital_opportunity_cost: Decimal = ZERO

    @property
    def total_costs(self) -> Decimal:
        return (
            self.taker_fees
            + self.gas_usd
            + self.leg_risk_expected_loss
            + self.resolution_haircut
            + self.safety_margin
            + self.capital_opportunity_cost
        )

    @property
    def net_profit(self) -> Decimal:
        return self.gross_edge - self.total_costs


@dataclass(frozen=True)
class Opportunity:
    opp_id: str
    strategy: str
    group_id: str  # condition id (A) or event id (B)
    legs: tuple[Leg, ...]
    shares: Decimal
    capital_required: Decimal  # USDC locked (buy notionals + collateral + gas)
    costs: CostBreakdown
    holding_hours: Decimal
    annualized_pct: Decimal
    confidence: Decimal
    valid: bool
    reasons: tuple[str, ...]
    detected_ms: int
    exit_method: str = "merge"

    @property
    def net_profit(self) -> Decimal:
        return self.costs.net_profit

    @property
    def net_pct(self) -> Decimal:
        if self.capital_required <= ZERO:
            return ZERO
        return self.net_profit / self.capital_required

    def summary(self) -> dict[str, str]:
        return {
            "opp_id": self.opp_id,
            "strategy": self.strategy,
            "group": self.group_id,
            "valid": str(self.valid),
            "shares": str(self.shares),
            "gross_edge": str(self.costs.gross_edge),
            "taker_fees": str(self.costs.taker_fees),
            "gas_usd": str(self.costs.gas_usd),
            "leg_risk": str(self.costs.leg_risk_expected_loss),
            "haircut": str(self.costs.resolution_haircut),
            "safety": str(self.costs.safety_margin),
            "net_profit": str(self.net_profit),
            "net_pct": str(self.net_pct.quantize(Decimal("0.000001"))),
            "annualized_pct": str(self.annualized_pct.quantize(Decimal("0.01"))),
            "capital": str(self.capital_required),
            "reasons": ";".join(self.reasons),
        }
