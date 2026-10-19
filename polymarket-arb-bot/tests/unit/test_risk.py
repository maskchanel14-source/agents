"""Risk controls: limits, exposure caps, daily-loss halt, rate limit, kill switch, circuit breaker."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from polymarket_arb.config import RiskLimits
from polymarket_arb.domain import CostBreakdown, Opportunity
from polymarket_arb.money import ZERO, dec
from polymarket_arb.risk import CircuitBreaker, KillSwitch, RiskManager
from polymarket_arb.state.reconcile import reconcile

LIMITS = RiskLimits()


def opp(capital="40", valid=True, reasons=()):
    return Opportunity(
        opp_id=f"o-{capital}",
        strategy="intra_binary",
        group_id="m1",
        legs=(),
        shares=dec("10"),
        capital_required=dec(capital),
        costs=CostBreakdown(
            gross_edge=dec("1"),
            taker_fees=ZERO,
            gas_usd=ZERO,
            leg_risk_expected_loss=ZERO,
            resolution_haircut=ZERO,
            safety_margin=ZERO,
        ),
        holding_hours=dec("0.25"),
        annualized_pct=dec("1"),
        confidence=dec("1"),
        valid=valid,
        reasons=tuple(reasons),
        detected_ms=0,
    )


@pytest.fixture
def rm(tmp_path):
    return RiskManager(LIMITS, KillSwitch(tmp_path / "KILL"))


class TestKillSwitch:
    def test_file_switch_on_and_off(self, tmp_path):
        ks = KillSwitch(tmp_path / "KILL")
        assert not ks.is_active() and ks.reason() is None
        ks.activate_file("operator")
        assert ks.is_active() and ks.reason() == "file:KILL"
        ks.clear_file()
        assert not ks.is_active()

    def test_manual_trigger_overrides(self, tmp_path):
        ks = KillSwitch(tmp_path / "KILL")
        ks.trigger_manual("unhedged_partial")
        assert ks.is_active() and ks.reason() == "manual:unhedged_partial"

    def test_clear_when_missing_is_noop(self, tmp_path):
        KillSwitch(tmp_path / "nope").clear_file()


class TestCircuitBreaker:
    def test_opens_after_n_failures_then_cools_down(self):
        cb = CircuitBreaker(max_consecutive_errors=3, cooldown_s=10)
        assert not cb.record_failure(0)
        assert not cb.record_failure(0)
        assert cb.record_failure(0)  # third failure opens
        assert cb.is_open(5_000)
        assert not cb.is_open(10_000)  # cooldown elapsed

    def test_success_resets(self):
        cb = CircuitBreaker(2, 10)
        cb.record_failure(0)
        cb.record_success()
        assert not cb.record_failure(0)
        assert cb.consecutive_errors == 1

    def test_invalid_config_rejected(self):
        with pytest.raises(ValueError):
            CircuitBreaker(0, 1)


class TestRiskManager:
    def test_valid_small_trade_passes(self, rm):
        assert rm.check(opp("40"), market_key="m", event_key="e", now_ms=0) == []

    def test_invalid_opportunity_refused(self, rm):
        assert rm.check(opp(valid=False), market_key="m", event_key="e", now_ms=0) == ["opportunity_invalid"]

    def test_per_trade_notional_cap(self, rm):
        r = rm.check(opp("50.01"), market_key="m", event_key="e", now_ms=0)
        assert "exceeds_max_notional" in r

    def test_market_exposure_cap(self, rm):
        rm.record_order(opp("90"), market_key="m", event_key="e", now_ms=0)
        r = rm.check(opp("20"), market_key="m", event_key="e2", now_ms=1)
        assert "exceeds_market_exposure" in r

    def test_event_exposure_cap(self, rm):
        rm.record_order(opp("45"), market_key="m1", event_key="E", now_ms=0)
        rm.record_order(opp("45"), market_key="m2", event_key="E", now_ms=0)
        rm.record_order(opp("45"), market_key="m3", event_key="E", now_ms=0)
        rm.record_order(opp("45"), market_key="m5", event_key="E", now_ms=0)  # event exposure = 180
        assert rm.check(opp("20"), market_key="m4", event_key="E", now_ms=1) == []  # 180 + 20 = 200 <= cap
        r = rm.check(opp("45"), market_key="m4", event_key="E", now_ms=1)  # 180 + 45 = 225 > 200
        assert "exceeds_event_exposure" in r

    def test_total_exposure_cap(self, rm):
        for i in range(12):
            rm.record_order(opp("40"), market_key=f"m{i}", event_key=f"e{i}", now_ms=0)
        r = rm.check(opp("40"), market_key="mz", event_key="ez", now_ms=1)
        assert "exceeds_total_exposure" in r

    def test_release_frees_exposure(self, rm):
        rm.record_order(opp("90"), market_key="m", event_key="e", now_ms=0)
        rm.release(dec("90"), market_key="m", event_key="e")
        assert rm.total_exposure == ZERO
        assert rm.check(opp("40"), market_key="m", event_key="e", now_ms=1) == []

    def test_release_never_goes_negative(self, rm):
        rm.release(dec("10"), market_key="m", event_key="e")
        assert rm.total_exposure == ZERO and rm.exposure_by_market["m"] == ZERO

    def test_order_rate_limit(self, rm):
        for i in range(LIMITS.max_orders_per_minute):
            rm.record_order(opp("1"), market_key=f"m{i}", event_key="e", now_ms=i)
        assert "order_rate_limit" in rm.check(opp("1"), market_key="z", event_key="z", now_ms=100)
        # window slides: a minute later it is allowed again
        assert "order_rate_limit" not in rm.check(opp("1"), market_key="z", event_key="z", now_ms=120_000)

    def test_daily_loss_halts_everything(self, rm):
        rm.daily_pnl = -LIMITS.max_daily_loss
        assert "daily_loss_halt" in rm.check(opp("1"), market_key="m", event_key="e", now_ms=0)

    def test_kill_switch_halts(self, rm):
        rm.kill_switch.trigger_manual("test")
        assert any(r.startswith("kill_switch") for r in rm.halt_reasons(0))

    def test_circuit_open_halts(self, rm):
        for _ in range(LIMITS.max_consecutive_errors):
            rm.circuit.record_failure(0)
        assert rm.circuit.is_open(1)
        assert any(r.startswith("circuit") for r in rm.halt_reasons(1))
        assert rm.check(opp("1"), market_key="m", event_key="e", now_ms=1) != []


class TestReconcile:
    def test_matching_ledgers_no_diff(self):
        assert reconcile({"a": dec("5")}, {"a": dec("5")}) == []

    def test_mismatch_reported_with_delta(self):
        diffs = reconcile({"a": dec("5")}, {"a": dec("4")})
        assert len(diffs) == 1 and diffs[0].delta == dec("-1")

    def test_missing_on_one_side_is_a_diff(self):
        diffs = reconcile({}, {"b": dec("2")})
        assert [d.asset_id for d in diffs] == ["b"]

    def test_within_tolerance_ignored(self):
        assert reconcile({"a": dec("1")}, {"a": dec("1.0000001")}) == []


def test_replace_helper_keeps_limits_immutable():
    assert replace(LIMITS, max_orders_per_minute=1).max_orders_per_minute == 1
    assert LIMITS.max_orders_per_minute == 30
    assert Decimal(0) == ZERO
