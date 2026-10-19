"""Hard risk limits. Strategies cannot bypass these: every order goes through ``check``."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from decimal import Decimal

from ..config import RiskLimits
from ..domain import Opportunity
from ..money import ZERO
from .circuit import CircuitBreaker
from .kill_switch import KillSwitch


@dataclass
class RiskManager:
    limits: RiskLimits
    kill_switch: KillSwitch
    circuit: CircuitBreaker = field(init=False)
    exposure_by_market: dict[str, Decimal] = field(default_factory=dict)
    exposure_by_event: dict[str, Decimal] = field(default_factory=dict)
    total_exposure: Decimal = ZERO
    daily_pnl: Decimal = ZERO
    _order_times_ms: deque = field(default_factory=deque)

    def __post_init__(self) -> None:
        self.circuit = CircuitBreaker(self.limits.max_consecutive_errors, self.limits.circuit_cooldown_s)

    # ---- halts ------------------------------------------------------------------
    def halt_reasons(self, now_ms: int) -> list[str]:
        reasons: list[str] = []
        if self.kill_switch.is_active():
            reasons.append(f"kill_switch:{self.kill_switch.reason()}")
        if self.daily_pnl <= -self.limits.max_daily_loss:
            reasons.append("daily_loss_halt")
        if self.circuit.is_open(now_ms):
            reasons.append("circuit_open")
        return reasons

    # ---- per-opportunity checks -------------------------------------------------
    def check(
        self,
        opp: Opportunity,
        *,
        market_key: str,
        event_key: str,
        now_ms: int,
    ) -> list[str]:
        if not opp.valid:
            return ["opportunity_invalid"]
        reasons = self.halt_reasons(now_ms)
        capital = opp.capital_required
        if capital > self.limits.max_notional_per_trade:
            reasons.append("exceeds_max_notional")
        if self.exposure_by_market.get(market_key, ZERO) + capital > self.limits.max_exposure_per_market:
            reasons.append("exceeds_market_exposure")
        if self.exposure_by_event.get(event_key, ZERO) + capital > self.limits.max_exposure_per_event:
            reasons.append("exceeds_event_exposure")
        if self.total_exposure + capital > self.limits.max_total_exposure:
            reasons.append("exceeds_total_exposure")
        if self._orders_in_last_minute(now_ms) >= self.limits.max_orders_per_minute:
            reasons.append("order_rate_limit")
        return sorted(set(reasons))

    def record_order(self, opp: Opportunity, *, market_key: str, event_key: str, now_ms: int) -> None:
        cap = opp.capital_required
        self.exposure_by_market[market_key] = self.exposure_by_market.get(market_key, ZERO) + cap
        self.exposure_by_event[event_key] = self.exposure_by_event.get(event_key, ZERO) + cap
        self.total_exposure += cap
        self._order_times_ms.append(now_ms)

    def release(self, capital: Decimal, *, market_key: str, event_key: str) -> None:
        """Called when a position is closed (merged/sold/redeemed)."""
        self.exposure_by_market[market_key] = max(
            ZERO, self.exposure_by_market.get(market_key, ZERO) - capital
        )
        self.exposure_by_event[event_key] = max(ZERO, self.exposure_by_event.get(event_key, ZERO) - capital)
        self.total_exposure = max(ZERO, self.total_exposure - capital)

    def _orders_in_last_minute(self, now_ms: int) -> int:
        while self._order_times_ms and now_ms - self._order_times_ms[0] > 60_000:
            self._order_times_ms.popleft()
        return len(self._order_times_ms)
