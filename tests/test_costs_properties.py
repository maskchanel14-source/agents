"""Property/fuzz test kalkulasi biaya (misi §7.2).

Invariant yang dijaga:
1. net profit TIDAK boleh positif bila ada biaya tak terhitung (identitas konservasi kas).
2. Hasil konsisten antar jalur perhitungan.
3. Fee tidak pernah melebihi batas teoritis; walk tidak pernah "gratis".
"""

from __future__ import annotations


from hypothesis import given, settings, strategies as st

from bot.costs import (
    BundleRequest,
    CostConfig,
    CostModel,
    GasModel,
    LegInput,
    make_market,
    taker_fee,
    walk_the_book,
)
from bot.decimal_utils import D, ONE, ZERO
from bot.models import FeeSchedule, OrderBookSnapshot, Side

NOW = 1_700_000_000_000

prices = st.decimals(min_value="0.001", max_value="0.999", places=3)
shares = st.decimals(min_value="0.01", max_value=500, places=2)
rates = st.decimals(min_value="0", max_value="0.07", places=3)


@given(price=prices, sh=shares, rate=rates)
@settings(max_examples=100)
def test_property_fee_bounded(price, sh, rate):
    fs = FeeSchedule(fees_enabled=True, rate=rate, exponent=ONE, taker_only=True, rebate_rate=ZERO, source="gamma")
    fee = taker_fee(sh, price, fs)
    assert fee >= ZERO
    # batas teoritis: shares * rate * 0.25 (maksimum di p=0.5) + pembulatan
    assert fee <= sh * rate * D("0.25") + D("0.00001")


@given(
    ask1=st.decimals(min_value="0.05", max_value="0.9", places=2),
    ask2=st.decimals(min_value="0.05", max_value="0.9", places=2),
    size=st.decimals(min_value="5", max_value=200, places=2),
    rate=rates,
)
@settings(max_examples=100)
def test_property_valid_opportunity_net_le_gross(ask1, ask2, size, rate):
    """Net tidak boleh melampaui gross (biaya tidak boleh 'menghasilkan' uang)."""
    if ask1 + ask2 >= D("1.20"):
        return  # gross sangat negatif — bukan objek uji
    mkt = make_market("m", fee_rate=rate)
    book1 = OrderBookSnapshot.from_levels("y", [], [(str(ask1), "10000")], recv_ms=NOW)
    book2 = OrderBookSnapshot.from_levels("n", [], [(str(ask2), "10000")], recv_ms=NOW)
    req = BundleRequest(
        strategy="A_intra_binary",
        legs=[
            LegInput(market=mkt, asset_id="y", side=Side.BUY, book=book1),
            LegInput(market=mkt, asset_id="n", side=Side.BUY, book=book2),
        ],
        fixed_payout_per_bundle=ONE,
        exit_hours=D("2"),
        max_bundle_size=size,
    )
    model = CostModel(
        CostConfig(min_annualized_return=ZERO, safety_margin_usd=ZERO, max_capital_per_trade_usd=D("1e9")),
        GasModel(enabled=False),
    )
    res = model.evaluate(req, now_ms=NOW)
    opp = res.opportunity
    c = opp.cost
    # identitas konservasi kas untuk jalur BUY dua leg + payout:
    # payout = notional_buy + fees + gas + leg_risk + resolution + rounding + safety + net
    lhs = ONE * opp.bundle_size
    rhs = (
        c.notional
        + c.trading_fees
        + c.gas_cost
        + c.leg_risk_cost
        + c.resolution_risk_cost
        + c.rounding_cost
        + c.safety_margin
        + c.net_profit
    )
    if opp.bundle_size > ZERO:
        assert abs(lhs - rhs) <= D("0.000001"), (lhs, rhs)
        # net <= gross (biaya >= 0)
        assert c.net_profit <= c.gross_edge + D("0.000001")
        if opp.valid:
            assert c.net_profit > ZERO


@given(
    bid=st.decimals(min_value="0.10", max_value="0.90", places=2),
    sh=st.decimals(min_value="0.5", max_value=100, places=2),
)
@settings(max_examples=80)
def test_property_walk_never_free(bid, sh):
    book = OrderBookSnapshot.from_levels("x", [(str(bid), "1000")], [], recv_ms=NOW)
    fill = walk_the_book(book, Side.SELL, sh)
    assert fill.filled_shares == sh
    assert fill.notional == bid * sh  # satu level: tepat harga level
    assert fill.avg_price == bid


@given(
    ask=st.decimals(min_value="0.05", max_value="0.95", places=2),
    depth=st.decimals(min_value="0.1", max_value=50, places=1),
    sh=st.decimals(min_value="0.1", max_value=100, places=1),
)
@settings(max_examples=80)
def test_property_walk_partial_consistent(ask, depth, sh):
    book = OrderBookSnapshot.from_levels("x", [], [(str(ask), str(depth))], recv_ms=NOW)
    fill = walk_the_book(book, Side.BUY, sh)
    assert fill.filled_shares <= sh
    assert fill.filled_shares <= depth
    assert fill.notional == fill.filled_shares * ask
    if sh > depth:
        assert not fill.fully_filled
        assert fill.shortfall_shares == sh - depth
