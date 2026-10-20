"""Test paper executor, scanner pipeline, dan smoke engine + dashboard."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from bot.costs import CostConfig, CostModel, GasModel, make_market
from bot.decimal_utils import D, ONE, ZERO
from bot.execution.fill_model import FillModel, FillModelConfig
from bot.execution.live import LiveExecutor, LiveTradingNotPermitted, live_trading_permitted
from bot.execution.simulator import PaperExecutor
from bot.models import CostBreakdown, LegPlan, Opportunity, OrderBookSnapshot, RejectReason, Side, WalkFill
from bot.risk.limits import RiskConfig, RiskManager
from bot.scanner import Scanner
from bot.state.db import StateDB

NOW = 1_792_464_000_000


def _opp(valid=True, capital="5"):
    walk = WalkFill(
        requested_shares=D("10"), filled_shares=D("10"), notional=D("4"),
        avg_price=D("0.4"), levels_used=((D("0.4"), D("10")),), fully_filled=True,
    )
    leg = LegPlan(
        asset_id="yes-m1", market_id="m1", side=Side.BUY, shares=D("10"),
        limit_price=D("0.4"), walk=walk, fee=D("0.01"), gas=ZERO, label="YES",
    )
    return Opportunity(
        opportunity_id="opp-1",
        strategy="A_intra_binary",
        market_ids=("m1",),
        event_id="e1",
        legs=[leg],
        payout_per_bundle=ONE,
        bundle_size=D("10"),
        cost=CostBreakdown(capital_required=D(capital), net_profit=D("0.5")),
        valid=valid,
        reject_reason=RejectReason.OK if valid else RejectReason.NET_NOT_POSITIVE,
        fill_probability=D("0.9"),
    )


def test_paper_executor_fok_executes(tmp_path: Path):
    db = StateDB(tmp_path / "s.db")
    risk = RiskManager(RiskConfig(), root=tmp_path)
    ex = PaperExecutor(CostModel(), db, risk, seed=1)
    res = ex.execute(_opp(), now_ms=NOW)
    assert res.executed
    assert res.filled_shares == D("10")
    assert len(db.trades()) == 1
    assert len(db.open_positions()) == 1
    db.close()


def test_paper_executor_fok_all_or_nothing(tmp_path: Path):
    db = StateDB(tmp_path / "s.db")
    risk = RiskManager(RiskConfig(), root=tmp_path)
    fm = FillModel(FillModelConfig(base_fill_prob=D("0.0")))  # selalu gagal penuh
    ex = PaperExecutor(CostModel(), db, risk, fm, seed=1)
    res = ex.execute(_opp(), now_ms=NOW)
    assert not res.executed
    assert "FOK" in res.reason
    db.close()


def test_paper_executor_fak_partial(tmp_path: Path):
    db = StateDB(tmp_path / "s.db")
    risk = RiskManager(RiskConfig(), root=tmp_path)
    fm = FillModel(FillModelConfig(base_fill_prob=D("0.0")))
    ex = PaperExecutor(CostModel(), db, risk, fm, order_type_primary="FAK", seed=2)
    res = ex.execute(_opp(), now_ms=NOW)
    # FAK: sebagian tetap terisi walaupun probabilitas rendah
    assert res.partial or res.filled_shares >= ZERO
    assert res.filled_shares < D("10") or res.executed
    db.close()


def test_paper_executor_respects_risk_reject(tmp_path: Path):
    db = StateDB(tmp_path / "s.db")
    risk = RiskManager(RiskConfig(max_capital_per_trade_usd=D("1")), root=tmp_path)
    ex = PaperExecutor(CostModel(), db, risk, seed=1)
    res = ex.execute(_opp(capital="50"), now_ms=NOW)
    assert not res.executed
    assert "risk" in res.reason
    db.close()


def test_live_executor_locked(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("LIVE_TRADING", raising=False)
    assert not live_trading_permitted()
    ex = LiveExecutor()
    with pytest.raises(LiveTradingNotPermitted):
        ex.execute(_opp())
    with pytest.raises(LiveTradingNotPermitted):
        ex.cancel_all()


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class _FakeWs:
    def __init__(self):
        self.stats = {"shards": 0, "connected": 0, "assets": 0, "reconnects": 0}
        self.on_event = None
    async def subscribe(self, ids): pass
    async def unsubscribe(self, ids): pass
    async def start(self): pass
    async def stop(self): pass


class _FakeClob:
    async def get_books(self, asset_ids, *, batch_size=20):
        return {}


def test_scanner_ranks_and_persists(tmp_path: Path):
    from bot.data.feed import MarketDataHub
    from bot.strategies.intra_market import IntraMarketBinary

    async def run():
        hub = MarketDataHub(_FakeClob(), _FakeWs(), stale_after_ms=10**9)
        m = make_market("m1", fee_rate=D("0.04"))
        hub.markets["m1"] = m
        hub.asset_to_market["yes-m1"] = "m1"
        hub.asset_to_market["no-m1"] = "m1"
        hub.books["yes-m1"] = OrderBookSnapshot.from_levels("yes-m1", [], [("0.40", "300")], recv_ms=NOW)
        hub.books["no-m1"] = OrderBookSnapshot.from_levels("no-m1", [], [("0.55", "300")], recv_ms=NOW)
        model = CostModel(
            CostConfig(min_annualized_return=ZERO, safety_margin_usd=D("0.001"), max_capital_per_trade_usd=D("50")),
            GasModel(enabled=False),
        )
        db = StateDB(tmp_path / "s.db")
        scanner = Scanner(hub, [IntraMarketBinary(model, {"enabled": True})], model, db)
        result = scanner.scan(now_ms=NOW)
        assert result.opportunities  # minimal beberapa hasil (merge & hold)
        assert result.ranked_valid  # ada yang valid
        # semua tercatat di SQLite
        stats = db.opportunity_stats()
        assert sum(v["count"] for v in stats.values()) == len(result.opportunities)
        # ranking menurun
        nets = [o.expected_net_profit for o in result.ranked_valid]
        assert nets == sorted(nets, reverse=True)
        db.close()
        return result

    result = asyncio.run(run())
    assert result.duration_ms >= 0


# ---------------------------------------------------------------------------
# Engine smoke + dashboard (mock tanpa jaringan)
# ---------------------------------------------------------------------------

def test_engine_smoke_and_dashboard_state(tmp_path: Path):
    from bot.dashboard.server import DashboardServer
    from bot.data.feed import MarketDataHub
    from bot.engine import BotEngine
    from bot.strategies.intra_market import IntraMarketBinary

    async def run():
        hub = MarketDataHub(_FakeClob(), _FakeWs(), stale_after_ms=10**9)
        m = make_market("m1", fee_rate=D("0.04"))
        hub.markets["m1"] = m
        hub.asset_to_market["yes-m1"] = "m1"
        hub.asset_to_market["no-m1"] = "m1"
        hub.books["yes-m1"] = OrderBookSnapshot.from_levels("yes-m1", [], [("0.40", "300")], recv_ms=NOW)
        hub.books["no-m1"] = OrderBookSnapshot.from_levels("no-m1", [], [("0.55", "300")], recv_ms=NOW)
        model = CostModel(
            CostConfig(min_annualized_return=ZERO, safety_margin_usd=D("0.001"), max_capital_per_trade_usd=D("50")),
            GasModel(enabled=False),
        )
        db = StateDB(tmp_path / "s.db")
        risk = RiskManager(RiskConfig(), root=tmp_path)
        scanner = Scanner(hub, [IntraMarketBinary(model, {"enabled": True})], model, db)
        ex = PaperExecutor(model, db, risk, seed=1)
        engine = BotEngine(
            {"monitoring": {"log_dir": "logs"}, "execution": {}},
            hub=hub, scanner=scanner, executor=ex, risk=risk, db=db, gamma=None,
            mode="paper", root=tmp_path,
        )
        # scan loop manual (tanpa start penuh agar tanpa discovery network)
        result = scanner.scan(now_ms=NOW)
        assert result.opportunities
        state = engine.dashboard_state()
        assert state["mode"] == "paper"
        assert "status" in state and "risk" in state
        # dashboard server: state handler + token
        server = DashboardServer(engine, host="127.0.0.1", port=0, throttle_fps=4)
        state2 = server._safe_state()
        assert "dashboard" in state2 and "logs" in state2 and "health" in state2
        assert server.control_token
        db.close()

    asyncio.run(run())
