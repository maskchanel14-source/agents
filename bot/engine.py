"""Engine — orkestrasi discovery, scan, eksekusi, risk, monitoring.

Mode: paper (default) | backtest | live (terkunci).
Bot tetap jalan tanpa dashboard; dashboard hanya observer.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .costs import CostConfig, CostModel, GasModel
from .data.clob import ClobClient
from .data.feed import MarketDataHub
from .data.gamma import GammaClient
from .data.http import HttpClient
from .data.ws_feed import MarketWsFeed
from .decimal_utils import D, ZERO
from .execution.fill_model import FillModel, FillModelConfig
from .execution.simulator import ExecutionResult, PaperExecutor
from .risk.limits import RiskConfig, RiskManager
from .scanner import ScanResult, Scanner
from .state.db import StateDB
from .strategies.cross_market import CrossMarketLogical
from .strategies.cross_venue import CrossVenue
from .strategies.intra_market import IntraMarketBinary
from .strategies.multi_outcome import MultiOutcomeNegRisk

log = logging.getLogger("bot.engine")


@dataclass
class EngineStatus:
    mode: str = "paper"
    running: bool = False
    ws_connected: bool = False
    api_ok: bool = False
    last_scan_ms: int = 0
    markets_total: int = 0
    markets_monitored: int = 0
    opportunities_total: int = 0
    valid_total: int = 0
    executed_total: int = 0
    rejected_total: int = 0
    rejection_stats: dict = field(default_factory=dict)
    last_coverage: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    started_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict:
        return {
            "mode": self.mode,
            "running": self.running,
            "ws_connected": self.ws_connected,
            "api_ok": self.api_ok,
            "last_scan_ms": self.last_scan_ms,
            "markets_total": self.markets_total,
            "markets_monitored": self.markets_monitored,
            "opportunities_total": self.opportunities_total,
            "valid_total": self.valid_total,
            "executed_total": self.executed_total,
            "rejected_total": self.rejected_total,
            "rejection_stats": dict(self.rejection_stats),
            "coverage": dict(self.last_coverage),
            "errors": self.errors[-20:],
            "uptime_s": time.time() - self.started_at,
        }


class BotEngine:
    def __init__(
        self,
        cfg: dict,
        *,
        hub: MarketDataHub,
        scanner: Scanner,
        executor: PaperExecutor,
        risk: RiskManager,
        db: StateDB,
        gamma: Optional[GammaClient] = None,
        mode: str = "paper",
        root: Optional[Path] = None,
        http: Optional[HttpClient] = None,
    ) -> None:
        self.cfg = cfg
        self.hub = hub
        self.scanner = scanner
        self.executor = executor
        self.risk = risk
        self.db = db
        self.gamma = gamma
        self.http = http
        self.mode = mode
        self.root = root or Path.cwd()
        self.status = EngineStatus(mode=mode)
        self._tasks: list[asyncio.Task] = []
        self._stop = asyncio.Event()
        self.recent_opportunities: list = []
        self.recent_executions: list[tuple] = []

    # -- lifecycle ---------------------------------------------------------

    async def start(self) -> None:
        self.status.running = True
        self._stop.clear()
        await self.hub.start()
        self._tasks.append(asyncio.create_task(self._discovery_loop(), name="discovery"))
        self._tasks.append(asyncio.create_task(self._scan_loop(), name="scanner"))
        self._tasks.append(asyncio.create_task(self._health_loop(), name="health"))
        log.info("engine started (mode=%s)", self.mode)

    async def stop(self) -> None:
        self.status.running = False
        self._stop.set()
        for t in self._tasks:
            t.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        await self.hub.stop()
        if self.http is not None:
            await self.http.close()
        # shutdown bersih: batalkan order yang masih hidup (paper: cukup catat)
        await self._cancel_all_on_shutdown()
        log.info("engine stopped")

    async def run_for(self, seconds: float) -> None:
        """Jalankan engine untuk durasi tertentu (dipakai paper run & smoke test)."""
        await self.start()
        try:
            await asyncio.wait_for(self._stop.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            pass
        await self.stop()

    # -- loops -------------------------------------------------------------

    async def _discovery_loop(self) -> None:
        refresh = float(self.cfg.get("discovery", {}).get("refresh_seconds", 300))
        first = True
        while not self._stop.is_set():
            try:
                if self.gamma is not None:
                    markets, stats = await self.gamma.discover_all(
                        closed=False,
                        page_size=int(self.cfg.get("discovery", {}).get("page_size", 100)),
                        max_markets=int(self.cfg.get("discovery", {}).get("max_markets", 0) or 0),
                        skip_if_missing_fee=bool(self.cfg.get("discovery", {}).get("skip_if_missing_fee", True)),
                    )
                    self.status.api_ok = True
                    self.status.markets_total = stats["raw"]
                    new_ids = [m for m in markets.values()]
                    # market yang hilang (closed) -> hapus dari monitor
                    existing = set(self.hub.markets.keys())
                    current = set(markets.keys())
                    removed = existing - current
                    if removed:
                        await self.hub.remove_markets(list(removed))
                    await self.hub.register_markets(new_ids)
                    self.hub.coverage.total_active_markets = stats["raw"]
                    for reason, n in stats.get("skip_reasons", {}).items():
                        for _ in range(n):
                            self.hub.coverage.add_skip(reason)
                    log.info(
                        "discovery: raw=%d parsed=%d skipped=%d monitored=%d",
                        stats["raw"], stats["parsed"], stats["skipped"], len(self.hub.markets),
                    )
                first = False
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.status.api_ok = False
                self.status.errors.append(f"discovery: {exc}")
                self.risk.record_error()
                log.warning("discovery failed: %s", exc)
            if first:
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(refresh)

    async def _scan_loop(self) -> None:
        interval = float(self.cfg.get("monitoring", {}).get("scan_interval_seconds", 2.0))
        while not self._stop.is_set():
            try:
                if self.risk.is_halted():
                    await asyncio.sleep(1)
                    continue
                result = self.scanner.scan()
                self.status.last_scan_ms = result.duration_ms
                self.status.opportunities_total += len(result.opportunities)
                self.status.valid_total += len(result.ranked_valid)
                self.status.rejected_total += sum(
                    n for k, n in result.rejection_stats.items() if k != "ok"
                )
                for k, n in result.rejection_stats.items():
                    self.status.rejection_stats[k] = self.status.rejection_stats.get(k, 0) + n
                if result.coverage is not None:
                    self.status.last_coverage = result.coverage.as_dict()
                self.status.markets_monitored = len(self.hub.markets)
                self.recent_opportunities = result.ranked_valid[:50]

                if self.mode == "paper" and result.ranked_valid:
                    executions = self.scanner.execute_top(result, self.executor, max_trades=1)
                    for opp, res in executions:
                        self.recent_executions.append((opp, res))
                        if res.executed:
                            self.status.executed_total += 1
                    self.recent_executions = self.recent_executions[-50:]
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.status.errors.append(f"scan: {exc}")
                self.risk.record_error()
                log.exception("scan loop error")
            await asyncio.sleep(interval)

    async def _health_loop(self) -> None:
        while not self._stop.is_set():
            stats = self.hub.ws.stats
            self.status.ws_connected = bool(stats.get("connected"))
            await asyncio.sleep(5)

    async def _cancel_all_on_shutdown(self) -> None:
        if not self.cfg.get("execution", {}).get("cancel_on_shutdown", True):
            return
        # paper: tidak ada order nyata; live executor menolak aksi (terkunci).
        log.info("shutdown: cancel-all (paper: no live orders)")

    # -- snapshot untuk dashboard -------------------------------------------

    def dashboard_state(self) -> dict:
        positions = self.db.open_positions()
        opp_stats = self.db.opportunity_stats()
        return {
            "status": self.status.as_dict(),
            "risk": self.risk.snapshot(),
            "coverage": self.status.last_coverage,
            "opportunities": [
                {
                    "id": o.opportunity_id,
                    "strategy": o.strategy,
                    "markets": list(o.market_ids),
                    "net_profit": str(o.cost.net_profit),
                    "net_profit_pct": str(o.cost.net_profit_pct),
                    "gross_edge": str(o.cost.gross_edge),
                    "fees": str(o.cost.trading_fees),
                    "slippage": str(o.cost.slippage_cost),
                    "gas": str(o.cost.gas_cost),
                    "leg_risk": str(o.cost.leg_risk_cost),
                    "resolution_risk": str(o.cost.resolution_risk_cost),
                    "safety": str(o.cost.safety_margin),
                    "capital": str(o.cost.capital_required),
                    "annualized": str(o.cost.annualized_return),
                    "size": str(o.bundle_size),
                    "fill_prob": str(o.fill_probability),
                    "valid": o.valid,
                    "reject": o.reject_reason.value,
                }
                for o in self.recent_opportunities[:30]
            ],
            "rejection_stats": self.status.rejection_stats,
            "opportunity_stats_db": opp_stats,
            "positions": positions,
            "mode": self.mode,
        }


async def build_engine_async(cfg: dict, *, mode: str = "paper", root: Optional[Path] = None, db_path: Optional[Path] = None) -> BotEngine:
    root = root or Path(__file__).resolve().parents[1]
    endpoints = cfg.get("endpoints", {})
    cost_cfg = CostConfig.from_config(cfg.get("costs", {}), cfg.get("risk", {}))
    gas = GasModel.from_config(cfg.get("costs", {}).get("gas", {}))
    cost_model = CostModel(cost_cfg, gas)

    db = StateDB(db_path or root / cfg.get("state", {}).get("db_path", "logs/bot_state.db"))
    risk = RiskManager(RiskConfig.from_config(cfg.get("risk", {})), root=root)

    http = await HttpClient.create()
    clob = ClobClient(http, endpoints.get("clob", "https://clob.polymarket.com"))
    gamma = GammaClient(http, endpoints.get("gamma", "https://gamma-api.polymarket.com"))
    ws = MarketWsFeed(
        endpoints.get("ws_market", "wss://ws-subscriptions-clob.polymarket.com/ws/market"),
        assets_per_connection=int(cfg.get("ws", {}).get("assets_per_connection", 400)),
        reconnect_min=float(cfg.get("ws", {}).get("reconnect_min_seconds", 1)),
        reconnect_max=float(cfg.get("ws", {}).get("reconnect_max_seconds", 60)),
        ping_interval=float(cfg.get("ws", {}).get("ping_interval_seconds", 20)),
    )
    hub = MarketDataHub(
        clob,
        ws,
        stale_after_ms=int(cfg.get("ws", {}).get("stale_after_ms", 3000)),
        rest_reconcile_seconds=float(cfg.get("ws", {}).get("rest_reconcile_seconds", 60)),
    )

    strategies = [
        IntraMarketBinary(cost_model, cfg.get("strategies", {}).get("A_intra_binary", {})),
        MultiOutcomeNegRisk(cost_model, cfg.get("strategies", {}).get("B_multi_outcome", {})),
        CrossMarketLogical(cost_model, cfg.get("strategies", {}).get("C_cross_market", {})),
        CrossVenue(cost_model, cfg.get("strategies", {}).get("D_cross_venue", {})),
    ]
    scanner = Scanner(hub, strategies, cost_model, db)
    fill_model = FillModel(FillModelConfig.from_config(
        cfg.get("fill_model", {}), latency_ms=cost_cfg.latency_ms
    ))
    executor = PaperExecutor(
        cost_model,
        db,
        risk,
        fill_model,
        order_type_primary=str(cfg.get("execution", {}).get("order_type_primary", "FOK")),
        order_type_fallback=str(cfg.get("execution", {}).get("order_type_fallback", "FAK")),
    )
    return BotEngine(
        cfg, hub=hub, scanner=scanner, executor=executor, risk=risk, db=db,
        gamma=gamma, mode=mode, root=root, http=http,
    )
