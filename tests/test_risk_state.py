"""Test risk manager (hard limits, kill switch, circuit breaker) + SQLite state."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from bot.costs import CostBreakdown
from bot.decimal_utils import D, ONE, ZERO
from bot.models import Opportunity, RejectReason
from bot.risk.limits import RiskConfig, RiskManager
from bot.state.db import StateDB


def _opp(capital="10", markets=("m1",), event="e1", valid=True):
    return Opportunity(
        opportunity_id="opp-x",
        strategy="A_intra_binary",
        market_ids=tuple(markets),
        event_id=event,
        legs=[],
        payout_per_bundle=ONE,
        bundle_size=ONE,
        cost=CostBreakdown(capital_required=D(capital), net_profit=D("1")),
        valid=valid,
        reject_reason=RejectReason.OK if valid else RejectReason.NET_NOT_POSITIVE,
    )


def test_risk_blocks_over_capital(tmp_path: Path):
    rm = RiskManager(RiskConfig(max_capital_per_trade_usd=D("50")), root=tmp_path)
    ok, reason = rm.check_opportunity(_opp(capital="60"))
    assert not ok and "capital" in reason


def test_risk_exposure_limits(tmp_path: Path):
    rm = RiskManager(
        RiskConfig(
            max_capital_per_trade_usd=D("50"),
            max_exposure_per_market_usd=D("30"),
            max_exposure_per_event_usd=D("30"),
            max_total_exposure_usd=D("100"),
        ),
        root=tmp_path,
    )
    opp = _opp(capital="20")
    ok, _ = rm.check_opportunity(opp)
    assert ok
    rm.commit_exposure(opp)
    # kedua di market sama melewati 30
    ok2, reason2 = rm.check_opportunity(_opp(capital="20"))
    assert not ok2 and "market exposure" in reason2
    # event exposure juga tercatat
    ok3, reason3 = rm.check_opportunity(_opp(capital="20", markets=("m2",)))
    assert not ok3 and "event exposure" in reason3


def test_risk_daily_loss_halts(tmp_path: Path):
    rm = RiskManager(RiskConfig(max_daily_loss_usd=D("50")), root=tmp_path)
    rm.record_realized_pnl(D("-49"))
    ok, _ = rm.check_opportunity(_opp())
    assert ok
    rm.record_realized_pnl(D("-2"))
    ok2, reason2 = rm.check_opportunity(_opp())
    assert not ok2 and "daily loss" in reason2
    assert rm.is_halted()


def test_kill_switch(tmp_path: Path):
    rm = RiskManager(RiskConfig(kill_switch_file="KILL_SWITCH"), root=tmp_path)
    assert not rm.kill_switch
    rm.trigger_kill_switch("test")
    assert rm.kill_switch
    assert rm.is_halted()
    ok, reason = rm.check_opportunity(_opp())
    assert not ok
    rm.clear_kill_switch()
    assert not rm.kill_switch


def test_circuit_breaker(tmp_path: Path):
    rm = RiskManager(RiskConfig(consecutive_errors=3, cooldown_seconds=0.2), root=tmp_path)
    assert not rm.record_error()
    assert not rm.record_error()
    assert rm.record_error()  # trip
    assert rm.is_halted()


def test_order_rate_limit(tmp_path: Path):
    rm = RiskManager(RiskConfig(max_orders_per_minute=3), root=tmp_path)
    assert rm.allow_order()
    assert rm.allow_order()
    assert rm.allow_order()
    assert not rm.allow_order()


def test_state_db_opportunity_roundtrip(tmp_path: Path):
    db = StateDB(tmp_path / "test.db")
    opp = _opp()
    opp.meta = {"k": "v"}
    db.save_opportunity(opp)
    stats = db.opportunity_stats()
    assert stats["ok"]["count"] == 1
    recent = db.recent_opportunities(10)
    assert recent[0]["id"] == "opp-x"
    assert recent[0]["capital_required"] == "10"
    db.close()


def test_state_db_trades_and_positions(tmp_path: Path):
    db = StateDB(tmp_path / "test.db")
    tid = db.record_trade(
        opportunity_id="opp-x", mode="paper", market_id="m1", asset_id="a1",
        label="YES", side="BUY", shares=D("10"), price=D("0.4"), fee=D("0.01"),
        notional=D("4"), status="filled", order_id="0x1", fill_probability=D("0.9"),
    )
    assert tid > 0
    db.upsert_position("m1", "a1", "YES", D("10"), D("0.4"))
    db.upsert_position("m1", "a1", "YES", D("10"), D("0.5"))
    pos = db.open_positions()
    assert Decimal(pos[0]["shares"]) == D("20")
    assert Decimal(pos[0]["avg_price"]) == D("0.45")
    db.snapshot_pnl(D("100"), D("1"), D("2"), D("-1"), 1, 1)
    assert len(db.pnl_history(10)) == 1
    db.kv_set("recovery", {"open_orders": []})
    assert db.kv_get("recovery") == {"open_orders": []}
    db.record_scan_run(markets_total=100, markets_monitored=90, candidates=5, valid=1, rejected=4, coverage={})
    db.close()
