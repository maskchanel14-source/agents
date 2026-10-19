"""Orchestration: scan strategies -> record every candidate -> risk -> execute."""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .config import Settings
from .domain import Opportunity
from .execution.base import ExecutionResult, Executor
from .money import ZERO
from .risk import KillSwitch, RiskManager
from .state.store import StateStore
from .strategies.common import StrategyContext
from .strategies.disabled import cross_logical, cross_venue
from .strategies.intra_binary import IntraBinaryStrategy
from .strategies.neg_risk import NegRiskStrategy
from .universe import Universe

log = logging.getLogger("polymarket_arb.engine")


@dataclass
class CycleReport:
    now_ms: int
    candidates: int = 0
    valid: int = 0
    executed: int = 0
    halted: list[str] = field(default_factory=list)
    rejections: Counter = field(default_factory=Counter)
    results: list[str] = field(default_factory=list)


def utc_midnight_ms(now_ms: int) -> int:
    dt = datetime.fromtimestamp(now_ms / 1000, tz=UTC)
    return int(dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)


class Engine:
    def __init__(
        self,
        *,
        settings: Settings,
        universe: Universe,
        books: Any,  # BookGetter (+ optional .consume for paper overlay)
        store: StateStore,
        executor: Executor,
        kill_switch: KillSwitch,
        stats: Counter | None = None,
    ) -> None:
        self.settings = settings
        self.universe = universe
        self.books = books
        self.store = store
        self.executor = executor
        self.kill_switch = kill_switch
        self.stats: Counter = stats if stats is not None else Counter()
        self.risk = RiskManager(settings.limits, kill_switch)
        exit_binary = settings.exit_method_binary
        self.strategies = []
        if settings.strategies.get("intra_binary", False):
            self.strategies.append(IntraBinaryStrategy(exit_method=exit_binary))
        if settings.strategies.get("neg_risk", False):
            self.strategies.append(NegRiskStrategy())
        if settings.strategies.get("cross_logical", False):
            self.strategies.append(cross_logical())  # always skipped (documented)
        if settings.strategies.get("cross_venue", False):
            self.strategies.append(cross_venue())  # always skipped (documented)
        self.markets_by_asset = universe.markets_by_asset()
        self.cycles = 0
        self.last_report: CycleReport | None = None

    def _keys(self, opp: Opportunity) -> tuple[str, str]:
        """(market_key, event_key) used for exposure caps."""
        if opp.strategy == "intra_binary":
            return opp.group_id, opp.group_id
        event = opp.group_id.split(":", 1)[0]
        return opp.group_id, event

    async def cycle(self, now_ms: int) -> CycleReport:
        self.cycles += 1
        report = CycleReport(now_ms=now_ms)
        self.risk.daily_pnl = self.store.realized_pnl_since(utc_midnight_ms(now_ms))
        halts = self.risk.halt_reasons(now_ms)
        if halts:
            report.halted = halts
            self.stats["cycle:halted"] += 1
            if any(h.startswith("kill_switch") for h in halts):
                await self._cancel_all("kill_switch")
            return self._finish(report)

        ctx = StrategyContext(
            costs=self.settings.costs,
            thresholds=self.settings.thresholds,
            limits=self.settings.limits,
            books=self.books,
            now_ms=now_ms,
            stats=self.stats,
        )
        candidates: list[Opportunity] = []
        for strat in self.strategies:
            if isinstance(strat, IntraBinaryStrategy):
                candidates.extend(strat.scan(ctx, self.universe.binaries))
            elif isinstance(strat, NegRiskStrategy):
                candidates.extend(strat.scan(ctx, self.universe.groups))
            else:  # disabled placeholders (cross_logical / cross_venue): record skip reason only
                strat.scan(ctx, [])

        report.candidates = len(candidates)
        valid: list[Opportunity] = []
        for opp in candidates:
            if opp.valid:
                self.store.record_opportunity(opp, now_ms)  # DB keeps valid candidates only
                valid.append(opp)
            else:  # rejections are aggregated in counters to keep the DB bounded
                for r in opp.reasons:
                    report.rejections[r] += 1
                    self.stats[f"rejected:{r}"] += 1
        report.valid = len(valid)

        valid.sort(key=lambda o: (o.net_pct, o.net_profit), reverse=True)
        for opp in valid:
            market_key, event_key = self._keys(opp)
            reasons = self.risk.check(opp, market_key=market_key, event_key=event_key, now_ms=now_ms)
            if reasons:
                for r in reasons:
                    report.rejections[f"risk:{r}"] += 1
                    self.stats[f"risk_rejected:{r}"] += 1
                continue
            result = await self.executor.execute(opp, now_ms)
            report.results.append(f"{opp.opp_id}:{result.status}:{result.reason}")
            self._after_execution(opp, result, market_key, event_key, now_ms, report)
            if self.kill_switch.is_active():
                break
        return self._finish(report)

    def _after_execution(self, opp, result: ExecutionResult, market_key, event_key, now_ms, report) -> None:
        self.stats[f"exec:{result.status}"] += 1
        if result.status == "filled":
            report.executed += 1
            self.risk.record_order(opp, market_key=market_key, event_key=event_key, now_ms=now_ms)
            self.risk.circuit.record_success()
            if opp.exit_method in ("merge", "sell"):
                self.risk.release(opp.capital_required, market_key=market_key, event_key=event_key)
            log.info(
                "trade filled",
                extra={
                    "fields": {
                        "opp_id": opp.opp_id,
                        "net": str(result.net_profit),
                        "status": result.status,
                    }
                },
            )
        elif result.status == "partial":
            self.kill_switch.trigger_manual("unhedged_partial")
            self.store.log_event(
                now_ms,
                "critical",
                "halt",
                {"reason": "unhedged_partial", "opp_id": opp.opp_id},
            )
            log.critical(
                "unhedged partial fill; kill switch engaged",
                extra={"fields": {"opp_id": opp.opp_id}},
            )
        elif result.status == "cancelled" and result.reason == "order_rejected":
            if self.risk.circuit.record_failure(now_ms):
                self.store.log_event(
                    now_ms,
                    "error",
                    "circuit_open",
                    {"errors": self.risk.circuit.consecutive_errors},
                )

    async def _cancel_all(self, reason: str) -> None:
        try:
            n = await self.executor.cancel_all()
            self.stats["cancel_all"] += int(n or 0)
        except Exception as exc:  # noqa: BLE001 - shutdown path must not raise
            self.store.log_event(
                0,
                "error",
                "cancel_all_failed",
                {"reason": reason, "error": type(exc).__name__},
            )

    def _finish(self, report: CycleReport) -> CycleReport:
        self.last_report = report
        return report

    async def run(self, stop: asyncio.Event, interval_s: float, clock_ms) -> None:
        try:
            while not stop.is_set():
                await self.cycle(clock_ms())
                try:
                    await asyncio.wait_for(stop.wait(), timeout=interval_s)
                except TimeoutError:
                    pass
        finally:
            await self._cancel_all("shutdown")

    def net_summary(self) -> dict[str, str]:
        return {
            "total_realized_pnl": str(self.store.total_pnl()),
            "cycles": str(self.cycles),
        }


__all__ = ["ZERO", "CycleReport", "Engine", "utc_midnight_ms"]
