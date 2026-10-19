"""Single source of truth for every cost that can erase an arbitrage edge.

Everything here is pure, Decimal-only and side-effect free. Formulas are
documented in ``docs/COST_MODEL.md`` with their sources; keep the two in sync.

Units: prices and fees are USDC per share; ``shares`` are outcome-token units
(1 share pays 1 USDC on resolution); gas is USDC (converted from POL).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from .domain import CostBreakdown, FeeSchedule, Leg, Side
from .money import FEE_QUANT, ONE, USDC_QUANT, ZERO, ceil_to, dec

HOURS_PER_YEAR = Decimal(8760)
MIN_HOLDING_HOURS = Decimal("0.01")
DEFAULT_GAS_UNITS: dict[str, int] = {
    # Conservative gas-unit estimates; replace with eth_estimateGas when RPC is reachable.
    "merge": 250_000,
    "split": 250_000,
    "convert": 500_000,
    "redeem": 250_000,
}


class FeeUnknown(ValueError):
    """Fee configuration is missing or contradictory — the opportunity is INVALID."""


class FeeModelUnverified(ValueError):
    """Fee schedule uses a shape the docs do not describe — the opportunity is INVALID."""


def taker_fee(
    shares: Decimal,
    price: Decimal,
    schedule: FeeSchedule | None,
    fees_enabled: bool | None,
) -> Decimal:
    """Taker fee in USDC for filling ``shares`` at ``price``.

    Docs: ``fee = C * feeRate * p * (1 - p)``, rounded to 5 dp (smallest 0.00001).
    We round UP (conservative). Makers pay nothing; this bot is taker-only.
    """
    if shares < 0:
        raise ValueError("shares must be non-negative")
    if not (ZERO < price < ONE):
        raise ValueError(f"price must be in (0,1), got {price}")
    if fees_enabled is None:
        raise FeeUnknown("feesEnabled missing")
    if fees_enabled is False:
        if schedule is not None and schedule.rate != ZERO:
            raise FeeUnknown("feesEnabled=false but feeSchedule.rate != 0 (conflict)")
        return ZERO
    if schedule is None:
        raise FeeUnknown("feeSchedule missing while fees are enabled")
    if schedule.rate == ZERO:
        return ZERO
    if schedule.exponent != ONE:
        raise FeeModelUnverified(f"feeSchedule.exponent={schedule.exponent} not documented")
    if schedule.rate < ZERO:
        raise FeeUnknown("negative fee rate")
    raw = shares * schedule.rate * price * (ONE - price)
    return ceil_to(raw, FEE_QUANT)


@dataclass(frozen=True)
class GasEstimate:
    gas_price_gwei: Decimal
    pol_usd: Decimal
    source: str  # "rpc" | "config_fallback" | "override"


@dataclass(frozen=True)
class CostParams:
    """All tunable cost assumptions. Defaults are deliberately conservative."""

    gas: GasEstimate = field(
        default_factory=lambda: GasEstimate(Decimal(200), Decimal("1.0"), "config_fallback")
    )
    gas_units: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_GAS_UNITS))
    gasless_relayer: bool = False  # True only if a Relayer key pays gas (not configured here)
    safety_margin_rate: Decimal = Decimal("0.001")  # 10 bps of capital, always deducted
    base_resolution_haircut: Decimal = Decimal("0.001")  # applied only when holding to resolution
    ambiguous_resolution_haircut: Decimal = Decimal("0.01")
    per_day_resolution_haircut: Decimal = Decimal("0.0002")  # per day until resolution
    uma_resolution_hours: Decimal = Decimal(48)  # time after endDate until payout (undisputed ~2h)
    merge_lockup_hours: Decimal = Decimal("0.25")
    sell_lockup_hours: Decimal = Decimal("0.1")
    leg_fail_probability: Decimal = Decimal("0.05")  # P(a sibling leg fails to fill)
    p_unknown_resolution: Decimal = Decimal("0.005")  # P(50/50 / unknown outcome), hold-to-resolution only
    # Annual return on idle USDC we give up while capital is locked (assumption, not a market quote).
    opportunity_cost_annual_rate: Decimal = Decimal("0.04")


def gas_cost_usd(units_key: str, params: CostParams) -> Decimal:
    """USDC cost of one on-chain operation (split/merge/convert/redeem)."""
    if params.gasless_relayer:
        return ZERO
    if units_key not in params.gas_units:
        raise KeyError(f"no gas units configured for {units_key!r}")
    units = Decimal(params.gas_units[units_key])
    # gwei -> POL: * 1e-9 ; POL -> USD: * pol_usd
    cost = units * params.gas.gas_price_gwei * Decimal("0.000000001") * params.gas.pol_usd
    return ceil_to(cost, USDC_QUANT)


def unwind_loss(leg: Leg) -> Decimal:
    """Expected loss if this leg must be flattened because a sibling leg failed.

    BUY leg: we paid ``notional``; flattening sells at ``unwind_price``.
    SELL leg: we received ``notional``; flattening buys back at ``unwind_price``.
    No unwind price (no liquidity on the other side) => worst case for that leg.
    """
    if leg.side is Side.BUY:
        if leg.unwind_price is None:
            return leg.notional
        recovery = leg.shares * leg.unwind_price - leg.unwind_fee
        return max(ZERO, leg.notional - recovery)
    # SELL
    if leg.unwind_price is None:
        return leg.shares * ONE - leg.notional
    buyback = leg.shares * leg.unwind_price + leg.unwind_fee
    return max(ZERO, buyback - leg.notional)


def leg_risk_expected_loss(legs: tuple[Leg, ...], fail_probability: Decimal) -> Decimal:
    """Expected unhedged loss. Pessimistic: each leg may be the one that fails."""
    if fail_probability < ZERO or fail_probability > ONE:
        raise ValueError("fail_probability must be in [0,1]")
    if len(legs) <= 1:
        return ZERO
    return fail_probability * sum((unwind_loss(leg) for leg in legs), ZERO)


def holding_hours(
    exit_method: str,
    days_to_end: Decimal,
    params: CostParams,
) -> Decimal:
    """Capital lock-up in hours until the position is converted back to USDC."""
    if exit_method == "merge":
        return params.merge_lockup_hours
    if exit_method == "sell":
        return params.sell_lockup_hours
    if exit_method == "redeem":
        remaining = max(ZERO, days_to_end) * Decimal(24)
        return remaining + params.uma_resolution_hours
    raise ValueError(f"unknown exit_method {exit_method!r}")


def resolution_haircut(
    exit_method: str,
    payout_notional: Decimal,
    capital: Decimal,
    ambiguous: bool,
    days_to_end: Decimal,
    params: CostParams,
) -> Decimal:
    """Haircut for resolution risk. Zero when we exit via merge/sell (no market exposure).

    For ``redeem`` (hold to resolution):
      * ``payout_notional * rate`` where rate = base + per-day + ambiguity penalty;
      * ``capital * p_unknown_resolution``: docs describe rare 50/50 (unknown) outcomes
        where the payout can fall well below the cost. Pessimistically, the whole
        capital is at risk in that tail.
    """
    if exit_method != "redeem":
        return ZERO
    rate = params.base_resolution_haircut + params.per_day_resolution_haircut * max(ZERO, days_to_end)
    if ambiguous:
        rate += params.ambiguous_resolution_haircut
    return payout_notional * rate + capital * params.p_unknown_resolution


def annualized_pct(net_pct: Decimal, hours: Decimal) -> Decimal:
    """Simple annualised return of ``net_pct`` earned over ``hours`` (no compounding)."""
    return net_pct * HOURS_PER_YEAR / max(hours, MIN_HOLDING_HOURS)


def capital_opportunity_cost(capital: Decimal, hours: Decimal, params: CostParams) -> Decimal:
    """Simple (non-compounding) forgone return on ``capital`` held for ``hours``."""
    return capital * params.opportunity_cost_annual_rate * hours / HOURS_PER_YEAR


def safety_margin(capital: Decimal, params: CostParams) -> Decimal:
    return capital * params.safety_margin_rate


def build_breakdown(
    *,
    gross_edge: Decimal,
    legs: tuple[Leg, ...],
    gas_usd: Decimal,
    exit_method: str,
    payout_notional: Decimal,
    capital: Decimal,
    days_to_end: Decimal,
    ambiguous: bool,
    params: CostParams,
) -> CostBreakdown:
    """Assemble every cost component into one auditable breakdown."""
    fees = sum((leg.fee for leg in legs), ZERO)
    hours = holding_hours(exit_method, days_to_end, params)
    return CostBreakdown(
        gross_edge=gross_edge,
        taker_fees=fees,
        gas_usd=gas_usd,
        leg_risk_expected_loss=leg_risk_expected_loss(legs, params.leg_fail_probability),
        resolution_haircut=resolution_haircut(
            exit_method, payout_notional, capital, ambiguous, days_to_end, params
        ),
        safety_margin=safety_margin(capital, params),
        capital_opportunity_cost=capital_opportunity_cost(capital, hours, params),
    )


def confidence_score(
    *,
    ambiguous: bool,
    max_book_age_ms: int,
    max_age_ms: int,
    complete_group: bool,
) -> Decimal:
    """Heuristic in [0,1] for reporting only; never used to make a trade pass."""
    score = ONE
    if ambiguous:
        score -= dec("0.3")
    if max_age_ms > 0 and max_book_age_ms * 2 > max_age_ms:
        score -= dec("0.2")
    if not complete_group:
        score -= dec("0.3")
    return max(ZERO, min(ONE, score))
