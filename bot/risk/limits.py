"""Risk manager — hard limit yang TIDAK bisa di-bypass strategi (misi §6)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Optional

from ..decimal_utils import D, ZERO
from ..models import Opportunity


@dataclass
class RiskConfig:
    max_capital_per_trade_usd: Decimal = D("50")
    max_exposure_per_market_usd: Decimal = D("100")
    max_exposure_per_event_usd: Decimal = D("150")
    max_total_exposure_usd: Decimal = D("500")
    max_daily_loss_usd: Decimal = D("50")
    max_orders_per_minute: int = 30
    kill_switch_file: str = "KILL_SWITCH"
    consecutive_errors: int = 10
    error_window_seconds: float = 60.0
    halt_on_stale_data_seconds: float = 30.0
    cooldown_seconds: float = 120.0

    @staticmethod
    def from_config(cfg: dict) -> "RiskConfig":
        c = RiskConfig()
        c.max_capital_per_trade_usd = D(str(cfg.get("max_capital_per_trade_usd", "50")))
        c.max_exposure_per_market_usd = D(str(cfg.get("max_exposure_per_market_usd", "100")))
        c.max_exposure_per_event_usd = D(str(cfg.get("max_exposure_per_event_usd", "150")))
        c.max_total_exposure_usd = D(str(cfg.get("max_total_exposure_usd", "500")))
        c.max_daily_loss_usd = D(str(cfg.get("max_daily_loss_usd", "50")))
        c.max_orders_per_minute = int(cfg.get("max_orders_per_minute", 30))
        c.kill_switch_file = str(cfg.get("kill_switch_file", "KILL_SWITCH"))
        br = cfg.get("circuit_breaker") or {}
        c.consecutive_errors = int(br.get("consecutive_errors", 10))
        c.error_window_seconds = float(br.get("error_window_seconds", 60))
        c.halt_on_stale_data_seconds = float(br.get("halt_on_stale_data_seconds", 30))
        c.cooldown_seconds = float(br.get("cooldown_seconds", 120))
        return c


@dataclass
class RiskState:
    exposure_market: dict[str, Decimal] = field(default_factory=dict)
    exposure_event: dict[str, Decimal] = field(default_factory=dict)
    total_exposure: Decimal = ZERO
    daily_realized_pnl: Decimal = ZERO
    daily_key: str = ""
    order_timestamps: list[float] = field(default_factory=list)
    error_timestamps: list[float] = field(default_factory=list)
    halted: bool = False
    halt_reason: str = ""
    halt_until: float = 0.0


class RiskManager:
    def __init__(self, cfg: RiskConfig, root: Optional[Path] = None) -> None:
        self.cfg = cfg
        self.root = root or Path.cwd()
        self.state = RiskState()

    # -- kill switch --------------------------------------------------------

    @property
    def kill_switch(self) -> bool:
        return (self.root / self.cfg.kill_switch_file).exists()

    def trigger_kill_switch(self, reason: str = "manual") -> None:
        (self.root / self.cfg.kill_switch_file).touch()
        self.halt(reason)

    def clear_kill_switch(self) -> None:
        p = self.root / self.cfg.kill_switch_file
        if p.exists():
            p.unlink()

    def resume(self) -> None:
        """Pulihkan dari kill switch / halt manual (aksi sadar operator).

        Menghapus file kill switch dan membersihkan state halt. Riwayat
        error circuit-breaker TIDAK dihapus (tetap terlihat di snapshot).
        """
        self.clear_kill_switch()
        self.state.halted = False
        self.state.halt_reason = ""
        self.state.halt_until = 0.0

    # -- circuit breaker ----------------------------------------------------

    def halt(self, reason: str) -> None:
        self.state.halted = True
        self.state.halt_reason = reason
        self.state.halt_until = time.monotonic() + self.cfg.cooldown_seconds

    def record_error(self) -> bool:
        """Catat error; True bila circuit breaker trip."""
        now = time.monotonic()
        self.state.error_timestamps.append(now)
        window = [t for t in self.state.error_timestamps if now - t <= self.cfg.error_window_seconds]
        self.state.error_timestamps = window
        if len(window) >= self.cfg.consecutive_errors:
            self.halt(f"{len(window)} consecutive errors in {self.cfg.error_window_seconds}s")
            return True
        return False

    def is_halted(self) -> bool:
        if self.kill_switch:
            return True
        if self.state.halted:
            if time.monotonic() >= self.state.halt_until:
                self.state.halted = False
                self.state.halt_reason = ""
                return False
            return True
        return False

    # -- order rate ---------------------------------------------------------

    def allow_order(self) -> bool:
        now = time.monotonic()
        self.state.order_timestamps = [t for t in self.state.order_timestamps if now - t <= 60.0]
        if len(self.state.order_timestamps) >= self.cfg.max_orders_per_minute:
            return False
        self.state.order_timestamps.append(now)
        return True

    # -- exposure & loss ---------------------------------------------------

    def roll_day(self, now: Optional[float] = None) -> None:
        import datetime as _dt
        key = _dt.datetime.utcfromtimestamp(now or time.time()).date().isoformat()
        if key != self.state.daily_key:
            self.state.daily_key = key
            self.state.daily_realized_pnl = ZERO

    def record_realized_pnl(self, pnl: Decimal) -> None:
        self.roll_day()
        self.state.daily_realized_pnl += pnl

    def check_opportunity(self, opp: Opportunity) -> tuple[bool, str]:
        """Gate terakhir sebelum eksekusi — semua limit dicek di sini."""
        if self.is_halted():
            return False, f"halted: {self.state.halt_reason or 'kill switch'}"
        if not opp.valid:
            return False, f"opportunity not valid: {opp.reject_reason.value}"
        cap = opp.cost.capital_required
        if cap > self.cfg.max_capital_per_trade_usd:
            return False, f"capital {cap} > max per trade {self.cfg.max_capital_per_trade_usd}"

        self.roll_day()
        if self.state.daily_realized_pnl <= -self.cfg.max_daily_loss_usd:
            self.halt("daily loss limit reached")
            return False, "daily loss limit reached"

        for mid in opp.market_ids:
            used = self.state.exposure_market.get(mid, ZERO)
            if used + cap > self.cfg.max_exposure_per_market_usd:
                return False, f"market exposure {mid} would exceed {self.cfg.max_exposure_per_market_usd}"
        if opp.event_id:
            used = self.state.exposure_event.get(opp.event_id, ZERO)
            if used + cap > self.cfg.max_exposure_per_event_usd:
                return False, f"event exposure {opp.event_id} would exceed {self.cfg.max_exposure_per_event_usd}"
        if self.state.total_exposure + cap > self.cfg.max_total_exposure_usd:
            return False, f"total exposure would exceed {self.cfg.max_total_exposure_usd}"
        if not self.allow_order():
            return False, "order rate limit"
        return True, "ok"

    def commit_exposure(self, opp: Opportunity) -> None:
        cap = opp.cost.capital_required
        for mid in opp.market_ids:
            self.state.exposure_market[mid] = self.state.exposure_market.get(mid, ZERO) + cap
        if opp.event_id:
            self.state.exposure_event[opp.event_id] = self.state.exposure_event.get(opp.event_id, ZERO) + cap
        self.state.total_exposure += cap

    def release_exposure(self, opp: Opportunity) -> None:
        cap = opp.cost.capital_required
        for mid in opp.market_ids:
            self.state.exposure_market[mid] = self.state.exposure_market.get(mid, ZERO) - cap
        if opp.event_id:
            self.state.exposure_event[opp.event_id] = self.state.exposure_event.get(opp.event_id, ZERO) - cap
        self.state.total_exposure -= cap

    def snapshot(self) -> dict:
        return {
            "halted": self.is_halted(),
            "halt_reason": self.state.halt_reason,
            "kill_switch": self.kill_switch,
            "total_exposure": str(self.state.total_exposure),
            "daily_realized_pnl": str(self.state.daily_realized_pnl),
            "orders_last_minute": len(self.state.order_timestamps),
        }
