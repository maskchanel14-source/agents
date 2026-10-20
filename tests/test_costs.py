"""Unit test costs.py — model biaya (inti presisi).

Kasus wajib (misi §7): fee 0, fee >0, depth tipis, rounding, partial fill,
fee tidak tersedia -> INVALID, dan verifikasi terhadap TABEL FEE RESMI.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from bot.costs import (
    FEE_MIN_USD,
    FEE_ROUNDING_PLACES,
    ROUNDING_CONFIG,
    BundleRequest,
    CostConfig,
    CostModel,
    GasModel,
    LegInput,
    fee_for_walk,
    make_market,
    round_order_amounts,
    rounding_for_tick,
    taker_fee,
    walk_the_book,
)
from bot.decimal_utils import D, ONE, ZERO
from bot.models import FeeSchedule, OrderBookSnapshot, RejectReason, Side

MODEL = CostModel()  # default config


# ---------------------------------------------------------------------------
# 1. Fee terhadap tabel resmi (docs/trading/fees, 100 share)
# ---------------------------------------------------------------------------

def _fs(rate: str) -> FeeSchedule:
    return FeeSchedule(
        fees_enabled=True,
        rate=D(rate),
        exponent=ONE,
        taker_only=True,
        rebate_rate=D("0.25"),
        source="gamma",
    )


@pytest.mark.parametrize(
    "rate,price,expected_exact,expected_display",
    [
        # Crypto 0.07: 100 share — nilai eksak (5 desimal) & tampilan tabel docs (2 desimal)
        ("0.07", "0.01", "0.06930", "0.07"), ("0.07", "0.05", "0.33250", "0.33"),
        ("0.07", "0.10", "0.63000", "0.63"), ("0.07", "0.15", "0.89250", "0.89"),
        ("0.07", "0.20", "1.12000", "1.12"), ("0.07", "0.25", "1.31250", "1.31"),
        ("0.07", "0.30", "1.47000", "1.47"), ("0.07", "0.35", "1.59250", "1.59"),
        ("0.07", "0.40", "1.68000", "1.68"), ("0.07", "0.45", "1.73250", "1.73"),
        ("0.07", "0.50", "1.75000", "1.75"), ("0.07", "0.55", "1.73250", "1.73"),
        ("0.07", "0.60", "1.68000", "1.68"), ("0.07", "0.65", "1.59250", "1.59"),
        ("0.07", "0.70", "1.47000", "1.47"), ("0.07", "0.75", "1.31250", "1.31"),
        ("0.07", "0.80", "1.12000", "1.12"), ("0.07", "0.85", "0.89250", "0.89"),
        ("0.07", "0.90", "0.63000", "0.63"), ("0.07", "0.95", "0.33250", "0.33"),
        ("0.07", "0.99", "0.06930", "0.07"),
        # Sports 0.05
        ("0.05", "0.50", "1.25000", "1.25"), ("0.05", "0.25", "0.93750", "0.94"),
        ("0.05", "0.10", "0.45000", "0.45"),
        # Finance/Politics 0.04
        ("0.04", "0.50", "1.00000", "1.00"), ("0.04", "0.25", "0.75000", "0.75"),
        ("0.04", "0.99", "0.03960", "0.04"),
    ],
)
def test_fee_matches_official_tables(rate: str, price: str, expected_exact: str, expected_display: str):
    got = taker_fee(D("100"), D(price), _fs(rate))
    # 1) nilai presisi 5 desimal sesuai rumus resmi
    assert got == D(expected_exact), f"fee(100@{price}, rate={rate}) = {got}, formula = {expected_exact}"
    # 2) tabel resmi di docs ditampilkan dibulatkan 2 desimal (cents)
    display = got.quantize(D("0.01"))
    assert display == D(expected_display), f"display {display} != docs table {expected_display}"


def test_fee_symmetry_around_half():
    fs = _fs("0.07")
    assert taker_fee(D("100"), D("0.30"), fs) == taker_fee(D("100"), D("0.70"), fs)


def test_fee_zero_when_disabled():
    fs = FeeSchedule(fees_enabled=False, rate=D("0.07"), exponent=ONE, taker_only=True, rebate_rate=ZERO, source="gamma")
    assert taker_fee(D("100"), D("0.5"), fs) == ZERO


def test_fee_missing_schedule_raises():
    fs = FeeSchedule.missing()
    with pytest.raises(ValueError):
        taker_fee(D("10"), D("0.5"), fs)


def test_fee_rounding_5_places_and_min_fee():
    fs = _fs("0.04")
    # 10 share @ 0.50: 10*0.04*0.25 = 0.1 -> tepat 1 desimal
    assert taker_fee(D("10"), D("0.50"), fs) == D("0.10000")
    # kasus sangat kecil: 0.5 share @ 0.99 rate 0.04 -> 0.5*0.04*0.0099 = 0.000198 -> 0.00020
    got = taker_fee(D("0.5"), D("0.99"), fs)
    assert got == D("0.00020")
    # kasus ekstrem kecil dibulatkan ke 0: 0.01 share @ 0.9999 rate 0.04
    # raw = 0.01*0.04*0.00009999 = 3.9996e-8 -> 0.00000 -> < FEE_MIN -> 0
    assert taker_fee(D("0.01"), D("0.9999"), fs) == ZERO
    # tepat di batas: raw = 0.00001 -> 0.00001 (dipertahankan)
    # cari share yang menghasilkan raw = 0.00001 pada p=0.5, rate 0.04:
    # raw = C*0.04*0.25 = C*0.01 -> C = 0.001
    assert taker_fee(D("0.001"), D("0.50"), fs) == D("0.00001")


def test_fee_exponent_applied_to_price_component():
    fs = FeeSchedule(fees_enabled=True, rate=D("0.07"), exponent=D("2"), taker_only=True, rebate_rate=ZERO, source="gamma")
    # exponent=2: fee = 100 * 0.07 * (0.25)^2 = 0.4375
    assert taker_fee(D("100"), D("0.50"), fs) == D("0.43750")


def test_fee_invalid_inputs():
    fs = _fs("0.07")
    with pytest.raises(ValueError):
        taker_fee(ZERO, D("0.5"), fs)
    with pytest.raises(ValueError):
        taker_fee(D("10"), ONE, fs)  # price harus di (0,1)


# ---------------------------------------------------------------------------
# 2. Walk-the-book
# ---------------------------------------------------------------------------

def _book(bids, asks, *, age_recv_ms=None, tick="0.01", min_size="5"):
    return OrderBookSnapshot.from_levels(
        asset_id="tok1",
        bids=bids,
        asks=asks,
        tick_size=D(tick),
        min_order_size=D(min_size),
        recv_ms=age_recv_ms,
    )


def test_walk_basic():
    book = _book([], [("0.52", "10"), ("0.53", "20"), ("0.54", "5")])
    fill = walk_the_book(book, Side.BUY, D("15"))
    assert fill.fully_filled
    assert fill.filled_shares == D("15")
    # 10 @ 0.52 + 5 @ 0.53
    assert fill.notional == D("10") * D("0.52") + D("5") * D("0.53")
    assert fill.levels_used == ((D("0.52"), D("10")), (D("0.53"), D("5")))
    assert fill.avg_price == fill.notional / D("15")


def test_walk_partial_when_thin():
    book = _book([], [("0.52", "3")])
    fill = walk_the_book(book, Side.BUY, D("10"))
    assert not fill.fully_filled
    assert fill.filled_shares == D("3")
    assert fill.shortfall_shares == D("7")


def test_walk_sell_uses_bids():
    book = _book([("0.48", "10"), ("0.47", "5")], [])
    fill = walk_the_book(book, Side.SELL, D("12"))
    assert fill.fully_filled
    assert fill.notional == D("10") * D("0.48") + D("2") * D("0.47")


def test_book_normalizes_unsorted_levels():
    # sengaja acak — REST vs WS bisa beda urutan
    book = _book(
        [("0.48", "1"), ("0.50", "1"), ("0.49", "1")],
        [("0.53", "1"), ("0.51", "1"), ("0.52", "1")],
    )
    assert book.best_bid.price == D("0.50")
    assert book.best_ask.price == D("0.51")
    assert [lv.price for lv in book.asks] == [D("0.51"), D("0.52"), D("0.53")]


def test_walk_rejects_bad_size():
    book = _book([], [("0.5", "1")])
    with pytest.raises(ValueError):
        walk_the_book(book, Side.BUY, ZERO)


def test_fee_for_walk_per_level_rounding():
    fs = _fs("0.07")
    book = _book([], [("0.50", "10"), ("0.55", "10")])
    fill = walk_the_book(book, Side.BUY, D("20"))
    fee = fee_for_walk(fill, fs)
    # per level: 10*0.07*0.25 = 0.175 ; 10*0.07*0.2475 = 0.17325 -> 0.17325 (5 desimal)
    assert fee == D("0.17500") + D("0.17325")


# ---------------------------------------------------------------------------
# 3. Pembulatan order (paritas py-clob-client)
# ---------------------------------------------------------------------------

def test_rounding_config_values():
    assert rounding_for_tick(D("0.01")) == (2, 2, 4)
    assert rounding_for_tick(D("0.1")) == (1, 2, 3)
    assert rounding_for_tick(D("0.001")) == (3, 2, 5)
    assert rounding_for_tick(D("0.0001")) == (4, 2, 6)


def test_round_order_amounts_buy():
    # docs: BUY 10 share @ 0.52 -> maker 5200000, taker 10000000
    maker, taker = round_order_amounts(Side.BUY, D("10"), D("0.52"), D("0.01"))
    assert (maker, taker) == (5200000, 10000000)


def test_round_order_amounts_sell():
    maker, taker = round_order_amounts(Side.SELL, D("10"), D("0.52"), D("0.01"))
    assert (maker, taker) == (10000000, 5200000)


def test_round_order_amounts_share_floor():
    # size dibulatkan TURUN ke 2 desimal: 10.009 -> 10.00
    maker, taker = round_order_amounts(Side.BUY, D("10.009"), D("0.5"), D("0.01"))
    assert taker == 10000000
    assert maker == 5000000


def test_round_order_amounts_zero_shares_raises():
    with pytest.raises(ValueError):
        round_order_amounts(Side.BUY, D("0.001"), D("0.5"), D("0.01"))


# ---------------------------------------------------------------------------
# 4. Gas
# ---------------------------------------------------------------------------

def test_gas_cost_formula():
    g = GasModel(enabled=True, gas_price_gwei=D("100"), pol_usd=D("0.25"))
    # 150000 gas * 100 gwei = 0.015 POL * 0.25 = 0.00375
    assert g.cost_usd("split") == D("0.00375")


def test_gas_disabled():
    g = GasModel(enabled=False)
    assert g.cost_usd("split") == ZERO


def test_gas_amortized_approval():
    g = GasModel(enabled=True, gas_price_gwei=D("100"), pol_usd=D("0.25"), amortize_approvals_over_trades=10)
    # approve 60000 gas * 100 gwei = 0.006 POL * $0.25 = $0.0015 penuh; amortisasi /10
    assert g.cost_usd("approve") == D("0.0015")
    assert g.amortized_approval_cost() == D("0.00015")


# ---------------------------------------------------------------------------
# 5. Evaluasi bundle end-to-end
# ---------------------------------------------------------------------------

NOW = 1_700_000_000_000


def _fresh_book(bids, asks):
    return OrderBookSnapshot.from_levels("tok", bids, asks, recv_ms=NOW)


def test_pair_arb_valid_after_all_costs():
    """A1: ask YES 0.40 + ask NO 0.55 = 0.95 < 1 -> valid setelah fee."""
    mkt = make_market("m1", fee_rate=D("0.04"))
    yes_book = _fresh_book([], [("0.40", "100"), ("0.41", "100")])
    no_book = _fresh_book([], [("0.55", "100"), ("0.56", "100")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book, label="YES"),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book, label="NO"),
        ],
        fixed_payout_per_bundle=ONE,
        exit_hours=D("2"),
        gas_op="merge",
        gas_op_count_per_bundle=ONE,
        opportunity_id="opp-1",
    )
    model = CostModel(
        CostConfig(min_annualized_return=D("0.0"), safety_margin_usd=D("0.001")),
        GasModel(enabled=True, gas_price_gwei=D("100"), pol_usd=D("0.25")),
    )
    res = model.evaluate(req, now_ms=NOW)
    opp = res.opportunity
    assert opp.valid, (opp.reject_reason, opp.reject_detail)
    # per bundle: cost 0.95 + fees + gas + haircuts + safety
    fee_yes = taker_fee(D("1"), D("0.40"), mkt.fee_schedule)
    fee_no = taker_fee(D("1"), D("0.55"), mkt.fee_schedule)
    assert opp.cost.trading_fees == (fee_yes + fee_no) * opp.bundle_size
    assert opp.cost.net_profit > ZERO
    assert opp.cost.annualized_return > ZERO


def test_pair_arb_invalid_when_gross_negative():
    mkt = make_market("m1", fee_rate=D("0.04"))
    yes_book = _fresh_book([], [("0.60", "100")])
    no_book = _fresh_book([], [("0.50", "100")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
        exit_hours=D("2"),
    )
    res = CostModel().evaluate(req, now_ms=NOW)
    assert not res.opportunity.valid
    assert res.opportunity.reject_reason == RejectReason.GROSS_NOT_POSITIVE


def test_pair_arb_invalid_when_net_not_positive_after_fees():
    """Gross kecil positif tapi termakan fee -> net <= 0 -> ditolak."""
    mkt = make_market("m1", fee_rate=D("0.07"))  # crypto
    yes_book = _fresh_book([], [("0.50", "100")])
    no_book = _fresh_book([], [("0.499", "100")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
        exit_hours=D("2"),
    )
    res = CostModel(CostConfig(min_annualized_return=D("0"))).evaluate(req, now_ms=NOW)
    assert not res.opportunity.valid
    assert res.opportunity.reject_reason in (
        RejectReason.NET_NOT_POSITIVE,
        RejectReason.BELOW_SAFETY_MARGIN,
    )


def test_fee_unknown_rejects():
    mkt = make_market("m1", fee_rate=D("0.04"))
    object.__setattr__(mkt, "fee_schedule", FeeSchedule.missing())
    yes_book = _fresh_book([], [("0.40", "100")])
    no_book = _fresh_book([], [("0.55", "100")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
    )
    res = CostModel().evaluate(req, now_ms=NOW)
    assert not res.opportunity.valid
    assert res.opportunity.reject_reason == RejectReason.FEE_UNKNOWN


def test_stale_data_rejects():
    mkt = make_market("m1", fee_rate=D("0.04"))
    old = NOW - 10_000
    yes_book = OrderBookSnapshot.from_levels("yes", [], [("0.40", "100")], recv_ms=old)
    no_book = OrderBookSnapshot.from_levels("no", [], [("0.55", "100")], recv_ms=old)
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
    )
    res = CostModel().evaluate(req, now_ms=NOW)
    assert res.opportunity.reject_reason == RejectReason.STALE_DATA


def test_below_min_order_size_rejects():
    """Depth cukup tapi size optimal di bawah min notional (5 USDC)."""
    mkt = make_market("m1", fee_rate=D("0"), min_notional=D("5"))
    # hanya 2 share tersedia @ 0.40 -> notional 0.80 < 5 -> harus ditolak
    yes_book = _fresh_book([], [("0.40", "2")])
    no_book = _fresh_book([], [("0.55", "2")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
        exit_hours=D("2"),
    )
    res = CostModel().evaluate(req, now_ms=NOW)
    assert not res.opportunity.valid
    assert res.opportunity.reject_reason == RejectReason.BELOW_MIN_ORDER


def test_annualized_gate_rejects():
    mkt = make_market("m1", fee_rate=D("0"))
    yes_book = _fresh_book([], [("0.40", "1000")])
    no_book = _fresh_book([], [("0.55", "1000")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
        exit_hours=D("4320"),  # 180 hari
    )
    res = CostModel(CostConfig(min_annualized_return=D("0.50"), safety_margin_usd=ZERO)).evaluate(req, now_ms=NOW)
    assert not res.opportunity.valid
    assert res.opportunity.reject_reason == RejectReason.ANNUALIZED_TOO_LOW


def test_capital_cap_limits_size():
    mkt = make_market("m1", fee_rate=D("0"), min_notional=D("5"))
    yes_book = _fresh_book([], [("0.40", "10000")])
    no_book = _fresh_book([], [("0.55", "10000")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
        exit_hours=D("2"),
    )
    model = CostModel(
        CostConfig(max_capital_per_trade_usd=D("20"), min_annualized_return=ZERO, safety_margin_usd=ZERO),
        GasModel(enabled=False),
    )
    res = model.evaluate(req, now_ms=NOW)
    assert res.opportunity.valid
    # capital <= 20
    assert res.opportunity.cost.capital_required <= D("20")
    # ukuran optimal memakai penuh batas modal & memenuhi min order (12.5 bundle)
    assert res.opportunity.bundle_size >= D("12.5")


def test_sell_bundle_mint_and_sell():
    """A2: bid YES 0.52 + bid NO 0.51 = 1.03 > 1 -> split & jual keduanya."""
    mkt = make_market("m1", fee_rate=D("0.04"))
    yes_book = _fresh_book([("0.52", "100")], [])
    no_book = _fresh_book([("0.51", "100")], [])
    req = BundleRequest(
        strategy="A_intra_binary_sell",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.SELL, book=yes_book, label="YES"),
            LegInput(market=mkt, asset_id="no", side=Side.SELL, book=no_book, label="NO"),
        ],
        fixed_payout_per_bundle=ZERO,
        collateral_consumed_per_bundle=ONE,
        exit_hours=D("1"),
        gas_op="split",
        gas_op_count_per_bundle=ONE,
    )
    model = CostModel(
        CostConfig(min_annualized_return=ZERO, safety_margin_usd=D("0.001")),
        GasModel(enabled=True, gas_price_gwei=D("100"), pol_usd=D("0.25")),
    )
    res = model.evaluate(req, now_ms=NOW)
    assert res.opportunity.valid, (res.opportunity.reject_reason, res.opportunity.reject_detail)
    assert res.opportunity.cost.net_profit > ZERO


def test_multi_outcome_bundle():
    """B1: 3 outcome, Σ ask YES = 0.40+0.35+0.20 = 0.95 < 1."""
    m1 = make_market("m1", fee_rate=D("0.04"), neg_risk=True)
    m2 = make_market("m2", fee_rate=D("0.04"), neg_risk=True)
    m3 = make_market("m3", fee_rate=D("0.04"), neg_risk=True)
    req = BundleRequest(
        strategy="B_multi_outcome",
        legs=[
            LegInput(market=m1, asset_id="y1", side=Side.BUY, book=_fresh_book([], [("0.40", "200")]), label="YES-1"),
            LegInput(market=m2, asset_id="y2", side=Side.BUY, book=_fresh_book([], [("0.35", "200")]), label="YES-2"),
            LegInput(market=m3, asset_id="y3", side=Side.BUY, book=_fresh_book([], [("0.20", "200")]), label="YES-3"),
        ],
        fixed_payout_per_bundle=ONE,
        exit_hours=D("48"),
        gas_op="redeem",
        gas_op_count_per_bundle=ONE,
    )
    model = CostModel(CostConfig(min_annualized_return=ZERO, safety_margin_usd=D("0.001")), GasModel(enabled=False))
    res = model.evaluate(req, now_ms=NOW)
    assert res.opportunity.valid, (res.opportunity.reject_reason, res.opportunity.reject_detail)
    assert res.opportunity.cost.gas_cost == ZERO


def test_depth_breakpoint_picks_best_size():
    """Level kedua lebih mahal — ukuran optimal berhenti sebelum level itu bila margin tipis."""
    mkt = make_market("m1", fee_rate=D("0"), min_notional=D("1"), end_date=None)
    yes_book = _fresh_book([], [("0.40", "5"), ("0.48", "500")])
    no_book = _fresh_book([], [("0.55", "5"), ("0.56", "500")])
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=yes_book),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=no_book),
        ],
        exit_hours=D("2"),
    )
    model = CostModel(CostConfig(min_annualized_return=ZERO, safety_margin_usd=ZERO, max_capital_per_trade_usd=D("10000")), GasModel(enabled=False))
    res = model.evaluate(req, now_ms=NOW)
    assert res.opportunity.valid
    # pada bundle=5: net per bundle = 1 - 0.95 = 0.05 -> total 0.25
    # pada bundle lebih besar: YES menyentuh 0.48 -> cost 1.04 > 1 -> kalah
    assert res.opportunity.bundle_size == D("5")


def test_all_opportunities_recorded_even_rejected():
    """Semua hasil evaluasi punya id + alasan (untuk SQLite)."""
    mkt = make_market("m1", fee_rate=D("0.04"))
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="yes", side=Side.BUY, book=_fresh_book([], [("0.60", "10")])),
            LegInput(market=mkt, asset_id="no", side=Side.BUY, book=_fresh_book([], [("0.50", "10")])),
        ],
    )
    res = CostModel().evaluate(req, now_ms=NOW)
    opp = res.opportunity
    assert opp.opportunity_id
    assert opp.reject_reason != RejectReason.OK
    assert opp.created_at is not None
    d = opp.cost.as_dict()
    assert "gross_edge" in d
