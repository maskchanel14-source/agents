"""costs.py is the single source of truth for every cost component: exhaustive edge cases."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from polymarket_arb import costs as C
from polymarket_arb.domain import FeeSchedule, Leg, Side
from polymarket_arb.money import ONE, ZERO, dec

SCHED = FeeSchedule(rate=dec("0.04"), exponent=ONE, taker_only=True, rebate_rate=dec("0.25"))
P = C.CostParams()


def leg(side=Side.BUY, shares="100", avg="0.5", worst="0.5", unwind="0.5", ufee="0", fee="0"):
    notional = dec(shares) * dec(avg)
    return Leg(
        asset_id="a",
        side=side,
        shares=dec(shares),
        avg_price=dec(avg),
        worst_price=dec(worst),
        notional=notional,
        fee=dec(fee),
        top_price=dec(avg),
        unwind_price=None if unwind is None else dec(unwind),
        unwind_fee=dec(ufee),
    )


# ---- taker fee ---------------------------------------------------------------------------
class TestTakerFee:
    def test_documented_formula_exact(self):
        # C * rate * p * (1-p) = 100 * 0.04 * 0.5 * 0.5 = 1.00
        assert C.taker_fee(dec("100"), dec("0.5"), SCHED, True) == dec("1.00000")

    def test_rounds_up_to_5dp(self):
        fee = C.taker_fee(dec("55.44"), dec("0.45"), SCHED, True)
        raw = dec("55.44") * dec("0.04") * dec("0.45") * dec("0.55")
        assert fee >= raw
        assert fee - raw < dec("0.00001")
        assert fee == fee.quantize(dec("0.00001"))

    def test_zero_shares_zero_fee(self):
        assert C.taker_fee(ZERO, dec("0.3"), SCHED, True) == ZERO

    def test_fees_disabled_is_zero(self):
        assert C.taker_fee(dec("10"), dec("0.3"), None, False) == ZERO

    def test_fees_disabled_but_rate_set_is_conflict(self):
        with pytest.raises(C.FeeUnknown):
            C.taker_fee(dec("10"), dec("0.3"), SCHED, False)

    def test_missing_fee_flag_is_unknown(self):
        with pytest.raises(C.FeeUnknown):
            C.taker_fee(dec("10"), dec("0.3"), SCHED, None)

    def test_enabled_without_schedule_is_unknown(self):
        with pytest.raises(C.FeeUnknown):
            C.taker_fee(dec("10"), dec("0.3"), None, True)

    def test_zero_rate_schedule_is_zero(self):
        s = FeeSchedule(rate=ZERO, exponent=ONE, taker_only=True, rebate_rate=ZERO)
        assert C.taker_fee(dec("10"), dec("0.3"), s, True) == ZERO

    def test_non_unit_exponent_is_unverified(self):
        s = FeeSchedule(rate=dec("0.04"), exponent=dec("2"), taker_only=True, rebate_rate=ZERO)
        with pytest.raises(C.FeeModelUnverified):
            C.taker_fee(dec("10"), dec("0.3"), s, True)

    def test_negative_rate_is_unknown(self):
        s = FeeSchedule(rate=dec("-0.01"), exponent=ONE, taker_only=True, rebate_rate=ZERO)
        with pytest.raises(C.FeeUnknown):
            C.taker_fee(dec("10"), dec("0.3"), s, True)

    @pytest.mark.parametrize("price", ["0", "1", "-0.1", "1.2"])
    def test_price_outside_open_interval_rejected(self, price):
        with pytest.raises(ValueError):
            C.taker_fee(dec("10"), dec(price), SCHED, True)

    def test_negative_shares_rejected(self):
        with pytest.raises(ValueError):
            C.taker_fee(dec("-1"), dec("0.5"), SCHED, True)

    @given(
        shares=st.decimals(min_value=0, max_value=10_000, places=2),
        price=st.decimals(min_value=Decimal("0.001"), max_value=Decimal("0.999"), places=3),
    )
    def test_fee_properties(self, shares, price):
        fee = C.taker_fee(shares, price, SCHED, True)
        assert fee >= 0
        # symmetric around 0.5 and bounded by rate * C * 0.25 (max of p(1-p))
        mirror = C.taker_fee(shares, ONE - price, SCHED, True)
        assert abs(fee - mirror) <= dec("0.00002")
        assert fee <= shares * SCHED.rate * dec("0.25") + dec("0.00001")


# ---- gas -----------------------------------------------------------------------------------
class TestGas:
    def test_gas_usd_from_units_price_and_pol(self):
        params = C.CostParams(gas=C.GasEstimate(dec("200"), dec("1.0"), "override"))
        # 250_000 * 200 gwei * 1e-9 * $1 = $0.05
        assert C.gas_cost_usd("merge", params) == dec("0.050000")

    def test_gas_rounds_up(self):
        params = C.CostParams(gas=C.GasEstimate(dec("0.0000001"), dec("0.3"), "override"))
        g = C.gas_cost_usd("merge", params)
        assert g > 0 and g == g.quantize(dec("0.000001"))

    def test_gasless_relayer_is_zero(self):
        params = C.CostParams(gasless_relayer=True)
        assert C.gas_cost_usd("convert", params) == ZERO

    def test_unknown_operation_raises(self):
        with pytest.raises(KeyError):
            C.gas_cost_usd("teleport", P)


# ---- leg risk / unwind -------------------------------------------------------------------
class TestLegRisk:
    def test_buy_unwind_loss_with_liquidity(self):
        # paid 50, can sell 100 shares at 0.45 => recover 45 - fee 0 => loss 5
        l = leg(side=Side.BUY, shares="100", avg="0.5", unwind="0.45")
        assert C.unwind_loss(l) == dec("5.00")

    def test_buy_unwind_loss_never_negative(self):
        l = leg(side=Side.BUY, shares="100", avg="0.5", unwind="0.9")
        assert C.unwind_loss(l) == ZERO

    def test_buy_without_bid_is_worst_case_notional(self):
        l = leg(side=Side.BUY, shares="100", avg="0.5", unwind=None)
        assert C.unwind_loss(l) == dec("50")

    def test_sell_unwind_loss_with_liquidity(self):
        # received 50 for 100 shares, buy back at 0.55 => pay 55 => loss 5
        l = leg(side=Side.SELL, shares="100", avg="0.5", unwind="0.55")
        assert C.unwind_loss(l) == dec("5.00")

    def test_sell_without_ask_is_worst_case(self):
        l = leg(side=Side.SELL, shares="100", avg="0.5", unwind=None)
        assert C.unwind_loss(l) == dec("50")

    def test_single_leg_has_no_leg_risk(self):
        assert C.leg_risk_expected_loss((leg(),), dec("0.05")) == ZERO

    def test_expected_loss_scales_with_fail_probability(self):
        legs = (leg(unwind="0.4"), leg(unwind="0.4"))
        assert C.leg_risk_expected_loss(legs, ZERO) == ZERO
        full = C.leg_risk_expected_loss(legs, ONE)
        assert C.leg_risk_expected_loss(legs, dec("0.05")) == dec("0.05") * full

    def test_bad_probability_rejected(self):
        with pytest.raises(ValueError):
            C.leg_risk_expected_loss((leg(), leg()), dec("1.5"))


# ---- resolution / holding -----------------------------------------------------------------
class TestResolution:
    def test_merge_and_sell_have_no_haircut(self):
        for m in ("merge", "sell"):
            assert C.resolution_haircut(m, dec("100"), dec("90"), True, dec("30"), P) == ZERO

    def test_redeem_haircut_components(self):
        # rate = 0.001 + 0.0002*10 = 0.003; payout 100 -> 0.3 ; capital 90 * 0.005 = 0.45
        h = C.resolution_haircut("redeem", dec("100"), dec("90"), False, dec("10"), P)
        assert h == dec("0.3") + dec("0.45")

    def test_ambiguity_adds_penalty(self):
        base = C.resolution_haircut("redeem", dec("100"), dec("90"), False, dec("0"), P)
        amb = C.resolution_haircut("redeem", dec("100"), dec("90"), True, dec("0"), P)
        assert amb - base == dec("100") * P.ambiguous_resolution_haircut

    def test_negative_days_treated_as_zero(self):
        a = C.resolution_haircut("redeem", dec("100"), dec("90"), False, dec("-5"), P)
        b = C.resolution_haircut("redeem", dec("100"), dec("90"), False, ZERO, P)
        assert a == b

    def test_holding_hours(self):
        assert C.holding_hours("merge", dec("5"), P) == P.merge_lockup_hours
        assert C.holding_hours("sell", dec("5"), P) == P.sell_lockup_hours
        assert C.holding_hours("redeem", dec("2"), P) == dec("48") + dec("48")

    def test_unknown_exit_rejected(self):
        with pytest.raises(ValueError):
            C.holding_hours("pray", ZERO, P)


class TestAnnualisedAndOpportunityCost:
    def test_annualized_simple(self):
        # 1% over 24h => 365%
        assert C.annualized_pct(dec("0.01"), dec("24")) == dec("0.01") * dec("8760") / dec("24")

    def test_annualized_guards_tiny_holding(self):
        assert C.annualized_pct(dec("0.01"), ZERO) == dec("0.01") * dec("8760") / dec("0.01")

    def test_capital_opportunity_cost(self):
        # 1000 USDC idle 8760h at 4% => 40 USDC
        assert C.capital_opportunity_cost(dec("1000"), dec("8760"), P) == dec("40")

    def test_opportunity_cost_in_breakdown_and_total(self):
        legs = (leg(unwind="0.45"), leg(unwind="0.45"))
        b = C.build_breakdown(
            gross_edge=dec("10"),
            legs=legs,
            gas_usd=dec("0.05"),
            exit_method="merge",
            payout_notional=dec("100"),
            capital=dec("100"),
            days_to_end=dec("0"),
            ambiguous=False,
            params=P,
        )
        assert b.capital_opportunity_cost > ZERO
        assert b.net_profit == b.gross_edge - b.total_costs
        assert b.total_costs == (
            b.taker_fees
            + b.gas_usd
            + b.leg_risk_expected_loss
            + b.resolution_haircut
            + b.safety_margin
            + b.capital_opportunity_cost
        )


class TestConfidence:
    def test_clean_group_is_full_confidence(self):
        assert (
            C.confidence_score(ambiguous=False, max_book_age_ms=10, max_age_ms=1500, complete_group=True)
            == ONE
        )

    def test_penalties_accumulate_and_stay_in_unit_interval(self):
        s = C.confidence_score(ambiguous=True, max_book_age_ms=5000, max_age_ms=1500, complete_group=False)
        assert s == dec("0.2")  # 1 - 0.3 - 0.2 - 0.3
        assert ZERO <= s <= ONE

    def test_stale_book_penalised(self):
        s = C.confidence_score(ambiguous=False, max_book_age_ms=1000, max_age_ms=1500, complete_group=True)
        assert s < ONE
