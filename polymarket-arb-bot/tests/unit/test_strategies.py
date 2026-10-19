"""Strategy A (intra binary) and B (neg-risk) on the synthetic universe + edge cases."""

from __future__ import annotations

from dataclasses import replace

from polymarket_arb.money import dec
from polymarket_arb.strategies.intra_binary import IntraBinaryStrategy
from polymarket_arb.strategies.neg_risk import NegRiskStrategy
from tests.fixtures.synth import BASE_MS, book_msg, initial_books
from tests.unit.helpers import NOW, ctx_for, seeded, universe


def _binary(uni, cid_prefix):
    return next(m for m in uni.binaries if m.condition_id.startswith(cid_prefix))


class TestIntraBinary:
    def test_arb_market_found_and_valid(self):
        store, uni = seeded()
        ctx = ctx_for(store)
        opps = IntraBinaryStrategy(exit_method="merge").scan(ctx, uni.binaries)
        arb = [o for o in opps if o.group_id.startswith("0xa1")]
        assert arb, "planted YES+NO < 1 arbitrage must be detected"
        o = arb[0]
        assert o.valid, o.reasons
        assert o.exit_method == "merge"
        assert o.costs.net_profit > 0
        assert o.capital_required <= ctx.limits.max_notional_per_trade
        assert o.shares >= ctx.thresholds.min_shares
        assert {leg.side.value for leg in o.legs} == {"BUY"}

    def test_fair_market_no_opportunity(self):
        store, uni = seeded()
        opps = IntraBinaryStrategy().scan(ctx_for(store), uni.binaries)
        assert not [o for o in opps if o.group_id.startswith("0xa2") and o.valid]

    def test_stale_books_rejected(self):
        store, uni = seeded(received=BASE_MS - 10_000)
        opps = IntraBinaryStrategy().scan(ctx_for(store), uni.binaries)
        assert opps and all(not o.valid for o in opps)
        assert any("stale_book" in o.reasons for o in opps)

    def test_book_skew_rejected(self):
        msgs = initial_books(BASE_MS)
        store, uni = seeded(msgs, received=BASE_MS)
        # refresh only the YES side 5 seconds later => skew between the two legs
        store.apply_message(
            book_msg("tok-b1-yes", [("0.44", "300")], [("0.45", "200")], BASE_MS + 5000), BASE_MS + 5000
        )
        ctx = ctx_for(store, now_ms=BASE_MS + 5500)
        opps = IntraBinaryStrategy().scan(ctx, [_binary(uni, "0xa1")])
        assert opps and "book_skew" in opps[0].reasons

    def test_missing_book_rejected(self):
        msgs = [m for m in initial_books(BASE_MS) if m["asset_id"] != "tok-b1-no"]
        store, uni = seeded(msgs)
        ctx = ctx_for(store)
        opps = IntraBinaryStrategy().scan(ctx, [_binary(uni, "0xa1")])
        assert not [o for o in opps if o.valid]
        assert ctx.stats["A:reject:no_book"] >= 1

    def test_sell_exit_is_not_supported_for_binary(self):
        # documented: binary arbitrage exits via merge only (no market exposure)
        import pytest

        with pytest.raises(ValueError):
            IntraBinaryStrategy(exit_method="sell")


class TestNegRisk:
    def test_buy_all_arb_detected_with_redeem_exit(self):
        store, uni = seeded()
        ctx = ctx_for(store)
        groups = [g for g in uni.groups if g.event_id == "ev-neg-1"]
        opps = NegRiskStrategy().scan(ctx, groups)
        buy_all = [o for o in opps if o.group_id.endswith(":buy_all")]
        assert buy_all and buy_all[0].exit_method == "redeem"
        assert buy_all[0].valid, buy_all[0].reasons
        assert buy_all[0].costs.resolution_haircut > 0

    def test_incomplete_group_is_never_valid(self):
        store, uni = seeded()
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        partial = replace(g, markets=g.markets[:2], declared_market_count=3)
        opps = NegRiskStrategy().scan(ctx_for(store), [partial])
        assert not [o for o in opps if o.valid]  # group with a missing leg is never tradable

    def test_mismatched_event_id_group_rejected(self):
        store, uni = seeded()
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        bad = replace(g, markets=tuple(replace(m, event_id="other") for m in g.markets))
        opps = NegRiskStrategy().scan(ctx_for(store), [bad])
        assert all(not o.valid for o in opps)

    def test_far_resolution_fails_annualised_threshold(self):
        store, uni = seeded()
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        far = replace(
            g, markets=tuple(replace(m, end_date_ms=m.end_date_ms + 400 * 86_400_000) for m in g.markets)
        )
        opps = NegRiskStrategy().scan(ctx_for(store), [far])
        buy_all = [o for o in opps if o.group_id.endswith(":buy_all")]
        assert buy_all and not buy_all[0].valid
        # 400 days of resolution haircut (0.0002/day) erases the edge; either reason is economic
        assert set(buy_all[0].reasons) & {"net_not_positive", "below_min_annualized"}

    def test_no_arb_when_asks_sum_above_one(self):
        msgs = [m for m in initial_books(BASE_MS) if not m["asset_id"].startswith("tok-n")]
        for i in range(3):
            msgs.append(book_msg(f"tok-n{i}-yes", [("0.29", "300")], [("0.40", "300")], BASE_MS))
            msgs.append(book_msg(f"tok-n{i}-no", [("0.60", "300")], [("0.62", "300")], BASE_MS))
        store, uni = seeded(msgs)
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        opps = NegRiskStrategy().scan(ctx_for(store), [g])
        assert all(not o.valid for o in opps)


def test_universe_has_expected_shape():
    uni = universe()
    # binaries = every active binary market (incl. neg-risk members: YES+NO check still valid)
    assert len(uni.binaries) == 5
    assert len(uni.groups) == 1 and len(uni.groups[0].markets) == 3
    assert NOW > BASE_MS
    assert dec("0") == dec("0")


def _convert_books():
    """Neg-risk convert edge: NO_0 ask 0.30 while YES_1 and YES_2 bid 0.45 each.

    Docs: 1 NO of outcome j converts to 1 YES of every other outcome (no collateral),
    so buying NO_0 and selling YES_1 + YES_2 nets 0.90 - 0.30 per share.
    """
    msgs = []
    for i in range(3):
        yes_bid = "0.30" if i == 0 else "0.45"  # keep spreads under max_quoted_spread (0.25)
        no_ask = "0.30" if i == 0 else "0.70"
        no_bid = "0.25" if i == 0 else "0.65"
        msgs.append(book_msg(f"tok-n{i}-yes", [(yes_bid, "300")], [("0.50", "300")], BASE_MS))
        msgs.append(book_msg(f"tok-n{i}-no", [(no_bid, "300")], [(no_ask, "300")], BASE_MS))
    return msgs


class TestNegRiskConvert:
    def test_convert_arb_detected_and_valid(self):
        store, uni = seeded(_convert_books())
        ctx = ctx_for(store)
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        opps = NegRiskStrategy().scan(ctx, [g])
        conv = [o for o in opps if ":convert:" in o.group_id and o.valid]
        assert conv, [(o.group_id, o.reasons) for o in opps]
        o = conv[0]
        assert o.exit_method == "sell"
        assert o.legs[0].side.value == "BUY" and all(leg.side.value == "SELL" for leg in o.legs[1:])
        assert len(o.legs) == 3  # one NO buy + two YES sells
        assert o.costs.resolution_haircut == dec("0")  # sell exit has no resolution exposure
        assert o.capital_required <= ctx.limits.max_notional_per_trade

    def test_convert_no_edge_is_counted(self):
        store, uni = seeded()  # default books: no convert edge
        ctx = ctx_for(store)
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        NegRiskStrategy().scan(ctx, [g])
        assert ctx.stats["B:convert:no_top_edge"] >= 1

    def test_convert_missing_bid_rejected(self):
        msgs = [m for m in _convert_books() if m["asset_id"] != "tok-n1-yes"]
        msgs.append(book_msg("tok-n1-yes", [], [("0.50", "300")], BASE_MS))
        store, uni = seeded(msgs)
        ctx = ctx_for(store)
        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        NegRiskStrategy().scan(ctx, [g])
        assert ctx.stats["B:convert:no_bid"] >= 1


class TestDisabledStrategies:
    """C (cross-market logical) and D (cross-venue) are default-off stubs; they must never emit."""

    def test_cross_strategies_return_nothing(self):
        from polymarket_arb.strategies import disabled

        store, uni = seeded()
        ctx = ctx_for(store)
        for make in (disabled.cross_logical, disabled.cross_venue):
            strat = make()
            assert strat.scan(ctx, uni.binaries) == []
        assert ctx.stats["cross_logical:skipped:not_implemented_precision_unverifiable"] == 1
        assert ctx.stats["cross_venue:skipped:disabled_default_off"] == 1
