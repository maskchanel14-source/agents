"""Paper FOK execution, idempotency, the paper overlay, live gating, and the state store."""

from __future__ import annotations

from pathlib import Path

import pytest

from polymarket_arb.config import LiveGateError, check_live_gate
from polymarket_arb.domain import Side
from polymarket_arb.execution.book_view import PaperBookView
from polymarket_arb.execution.live import LiveExecutor, LiveNotArmed, build_order_draft
from polymarket_arb.execution.paper import PaperExecutor
from polymarket_arb.money import ZERO, dec
from polymarket_arb.state.store import OrderRecord, StateStore
from polymarket_arb.strategies.intra_binary import IntraBinaryStrategy
from tests.fixtures.synth import BASE_MS, book_msg
from tests.unit.helpers import NOW, ctx_for, seeded, universe


def arb_opp(store, uni):
    opps = IntraBinaryStrategy().scan(ctx_for(store, books=PaperBookView(store)), uni.binaries)
    valid = [o for o in opps if o.valid and o.group_id.startswith("0xa1")]
    assert valid
    return valid[0]


def make_exec(tmp_path, store, uni, view=None):
    st = StateStore(tmp_path / "s.sqlite", mode="paper")
    view = view or PaperBookView(store)
    ex = PaperExecutor(st, view, uni.markets_by_asset(), max_book_age_ms=1500)
    return st, ex, view


class TestPaperExecutor:
    @pytest.mark.asyncio
    async def test_full_fill_creates_orders_and_realized_pnl(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        st, ex, _ = make_exec(tmp_path, store, uni)
        res = await ex.execute(opp, NOW)
        assert res.status == "filled"
        assert len(res.fills) == 2
        assert st.count("orders") == 2
        assert st.pnl_by_kind()["realized"] > ZERO
        assert st.positions() == {}  # merge exit: flat
        st.close()

    @pytest.mark.asyncio
    async def test_idempotent_per_opportunity_id(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        st, ex, _ = make_exec(tmp_path, store, uni)
        assert (await ex.execute(opp, NOW)).status == "filled"
        again = await ex.execute(opp, NOW)
        assert again.status == "skipped_duplicate"
        assert st.count("orders") == 2
        st.close()

    @pytest.mark.asyncio
    async def test_insufficient_depth_at_execution_cancels_everything(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        # book moved: depth at execution time is far smaller than the signal size
        store.apply_message(book_msg("tok-b1-no", [("0.44", "1")], [("0.45", "1")], BASE_MS + 1), BASE_MS + 1)
        st, ex, _ = make_exec(tmp_path, store, uni)
        res = await ex.execute(opp, NOW)
        assert res.status == "cancelled" and res.reason == "insufficient_depth_at_execution"
        assert st.count("orders") == 0 and st.pnl_by_kind() == {}
        st.close()

    @pytest.mark.asyncio
    async def test_stale_book_at_execution_cancels(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        st, ex, _ = make_exec(tmp_path, store, uni)
        res = await ex.execute(opp, NOW + 60_000)
        assert res.status == "cancelled" and res.reason == "stale_book_at_execution"
        st.close()

    @pytest.mark.asyncio
    async def test_missing_book_cancels(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        store.invalidate_all("disconnect")
        st, ex, _ = make_exec(tmp_path, store, uni)
        assert (await ex.execute(opp, NOW)).reason == "no_book_at_execution"
        st.close()

    @pytest.mark.asyncio
    async def test_unknown_market_cancels(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        st = StateStore(tmp_path / "s.sqlite", mode="paper")
        ex = PaperExecutor(st, PaperBookView(store), {}, max_book_age_ms=1500)
        assert (await ex.execute(opp, NOW)).reason == "unknown_market"
        st.close()

    @pytest.mark.asyncio
    async def test_invalid_opportunity_refused(self, tmp_path):
        from dataclasses import replace

        store, uni = seeded()
        opp = replace(arb_opp(store, uni), valid=False)
        st, ex, _ = make_exec(tmp_path, store, uni)
        assert (await ex.execute(opp, NOW)).status == "refused"
        st.close()

    @pytest.mark.asyncio
    async def test_paper_fill_consumes_overlay_liquidity(self, tmp_path):
        store, uni = seeded()
        opp = arb_opp(store, uni)
        st, ex, view = make_exec(tmp_path, store, uni)
        before = view.get("tok-b1-yes").asks[0].size
        await ex.execute(opp, NOW)
        after = view.get("tok-b1-yes").asks[0].size
        assert after < before
        st.close()

    @pytest.mark.asyncio
    async def test_redeem_exit_is_expected_not_realized(self, tmp_path):
        store, uni = seeded()
        ctx = ctx_for(store)
        from polymarket_arb.strategies.neg_risk import NegRiskStrategy

        g = next(g for g in uni.groups if g.event_id == "ev-neg-1")
        opps = [o for o in NegRiskStrategy().scan(ctx, [g]) if o.valid and o.exit_method == "redeem"]
        assert opps
        st, ex, _ = make_exec(tmp_path, store, uni)
        res = await ex.execute(opps[0], NOW)
        assert res.status == "filled"
        assert set(st.pnl_by_kind()) == {"expected_pending_resolution"}
        assert sum(st.positions().values()) > ZERO  # redeem legs hold shares until resolution
        assert st.positions_from_orders() == st.positions()
        st.close()


class TestPaperOverlay:
    def test_consume_reduces_depth_until_book_changes(self):
        store, _uni = seeded()
        view = PaperBookView(store)
        base_size = view.get("tok-b1-yes").asks[0].size
        from polymarket_arb.domain import Side as S

        view.consume("tok-b1-yes", S.BUY, dec("0.45"), dec("50"))
        assert view.get("tok-b1-yes").asks[0].size == base_size - dec("50")
        # a new book message for that asset invalidates the overlay
        store.apply_message(
            book_msg("tok-b1-yes", [("0.44", "300")], [("0.45", "200")], BASE_MS + 9), BASE_MS + 9
        )
        assert view.get("tok-b1-yes").asks[0].size == dec("200")

    def test_consume_fully_removes_level(self):
        store, _ = seeded()
        view = PaperBookView(store)
        from polymarket_arb.domain import Side as S

        view.consume("tok-b1-yes", S.BUY, dec("0.45"), dec("200"))
        assert all(lv.price != dec("0.45") for lv in view.get("tok-b1-yes").asks)

    def test_sell_consumes_bids(self):
        store, _ = seeded()
        view = PaperBookView(store)
        from polymarket_arb.domain import Side as S

        view.consume("tok-b1-yes", S.SELL, dec("0.44"), dec("100"))
        assert view.get("tok-b1-yes").bids[0].size == dec("200")
        assert view.get("tok-b1-yes").asks[0].size == dec("200")  # asks untouched

    def test_base_store_unaffected(self):
        store, _ = seeded()
        view = PaperBookView(store)
        from polymarket_arb.domain import Side as S

        view.consume("tok-b1-yes", S.BUY, dec("0.45"), dec("50"))
        assert store.get("tok-b1-yes").asks[0].size == dec("200")


class TestLive:
    def test_gate_refuses_without_env(self, tmp_path):
        conf = tmp_path / "LIVE_CONFIRMED.txt"
        conf.write_text("ok")
        with pytest.raises(LiveGateError):
            check_live_gate("live", {}, conf)

    def test_gate_refuses_without_confirmation_file(self, tmp_path):
        with pytest.raises(LiveGateError):
            check_live_gate("live", {"LIVE_TRADING": "true"}, tmp_path / "missing")

    def test_gate_requires_exact_true(self, tmp_path):
        conf = tmp_path / "c"
        conf.write_text("ok")
        with pytest.raises(LiveGateError):
            check_live_gate("live", {"LIVE_TRADING": "yes"}, conf)

    def test_gate_passes_only_with_both(self, tmp_path):
        conf = tmp_path / "c"
        conf.write_text("ok")
        check_live_gate("live", {"LIVE_TRADING": "true"}, conf)  # no raise
        check_live_gate("paper", {}, tmp_path / "none")  # paper never gated

    def test_live_executor_not_armed_refuses_to_trade(self, tmp_path):
        from polymarket_arb.state.store import StateStore as SS

        st = SS(tmp_path / "l.sqlite", mode="live")
        conf = tmp_path / "c"
        conf.write_text("ok")
        ex = LiveExecutor(st, None, None, env={"LIVE_TRADING": "true"}, mode="live", confirmation_file=conf)
        with pytest.raises(LiveNotArmed):
            ex.assert_armed()
        st.close()

    def test_order_draft_buy_amounts(self):
        d = build_order_draft("c1", "tok", Side.BUY, dec("10"), dec("0.45"))
        assert (d.maker_amount, d.taker_amount) == (4_500_000, 10_000_000)

    def test_order_draft_sell_amounts(self):
        d = build_order_draft("c1", "tok", Side.SELL, dec("10"), dec("0.45"))
        assert (d.maker_amount, d.taker_amount) == (10_000_000, 4_500_000)

    def test_order_draft_sub_micro_rounds_conservatively(self):
        b = build_order_draft("c", "t", Side.BUY, dec("0.0000005"), dec("0.5"))
        assert b.maker_amount >= 0
        s = build_order_draft("c", "t", Side.SELL, dec("0.0000005"), dec("0.5"))
        assert s.taker_amount >= 0

    @pytest.mark.parametrize("shares,price", [("0", "0.5"), ("1", "0"), ("1", "1")])
    def test_order_draft_rejects_bad_inputs(self, shares, price):
        with pytest.raises(ValueError):
            build_order_draft("c", "t", Side.BUY, dec(shares), dec(price))


class TestStateStore:
    def test_order_rows_and_duplicate_guard(self, tmp_path):
        st = StateStore(tmp_path / "x.sqlite", mode="paper")
        rec = OrderRecord(
            "cid1", "opp1", "a", "BUY", dec("0.4"), dec("5"), "FOK", "matched", dec("5"), dec("0")
        )
        st.record_order(rec, 1)
        assert st.order_exists("cid1")
        with pytest.raises(ValueError):  # duplicate client id must fail loudly, never double-submit
            st.record_order(rec, 2)
        assert st.count("orders") == 1
        st.close()

    def test_positions_add_and_sub(self, tmp_path):
        st = StateStore(tmp_path / "x.sqlite", mode="paper")
        st.add_fill("a", dec("10"))
        st.add_fill("a", dec("-4"))
        assert st.position("a") == dec("6") and st.positions() == {"a": dec("6")}
        st.close()

    def test_pnl_split_and_window(self, tmp_path):
        st = StateStore(tmp_path / "x.sqlite", mode="paper")
        st.record_pnl(100, "o1", "realized", dec("2.5"))
        st.record_pnl(200, "o2", "expected_pending_resolution", dec("-1"))
        assert st.realized_pnl_since(150) == dec("-1")
        assert st.total_pnl() == dec("1.5")
        assert st.pnl_by_kind() == {"realized": dec("2.5"), "expected_pending_resolution": dec("-1")}
        st.close()

    def test_modes_isolated(self, tmp_path):
        p = tmp_path / "shared.sqlite"
        a = StateStore(p, mode="paper")
        a.add_fill("x", dec("3"))
        a.close()
        b = StateStore(p, mode="live")
        assert b.positions() == {}
        b.close()

    def test_count_rejects_unknown_table(self, tmp_path):
        st = StateStore(tmp_path / "x.sqlite", mode="paper")
        with pytest.raises(ValueError):
            st.count("users")
        st.close()

    def test_mark_executed_idempotent(self, tmp_path):
        st = StateStore(tmp_path / "x.sqlite", mode="paper")
        assert st.mark_executed("o") is True
        assert st.mark_executed("o") is False
        st.close()


def test_universe_sanity():
    assert universe().assets
    assert Path(".").exists()
