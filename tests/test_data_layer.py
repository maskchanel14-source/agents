"""Test data layer: parsing Gamma, parsing book, delta WS, hub staleness."""

from __future__ import annotations

import asyncio

import pytest

from bot.data.clob import parse_book
from bot.data.gamma import parse_fee_schedule, parse_market
from bot.data.ws_feed import apply_price_change
from bot.decimal_utils import D
from bot.models import OrderBookSnapshot

NOW = 1_700_000_000_000

GAMMA_V1 = {
    "id": "703257",
    "slug": "will-the-us-confirm-that-aliens-exist-before-2027",
    "question": "Will the US confirm that aliens exist before 2027?",
    "conditionId": "0x747dc809fb79e1b05be09c42d6179459a58de2ef3e40f02484a4e1260f741f75",
    "version": "v1",
    "outcomes": '["Yes", "No"]',
    "outcomePrices": '["0.085", "0.915"]',
    "clobTokenIds": '["1075", "7305"]',
    "negRisk": False,
    "orderPriceMinTickSize": 0.01,
    "orderMinSize": 5,
    "feesEnabled": True,
    "feeSchedule": {"rate": 0.04, "exponent": 1, "takerOnly": True, "rebateRate": 0.25},
    "endDate": "2027-01-01T00:00:00Z",
    "description": "This market will resolve to \"Yes\" if ...",
    "active": True,
    "closed": False,
    "acceptingOrders": True,
    "enableOrderBook": True,
    "restricted": False,
    "events": [{"id": "90177"}],
}

GAMMA_V2 = {
    "id": "1",
    "slug": "x-market",
    "question": "X?",
    "conditionId": "0x017089ce",
    "version": "v2",
    "outcomes": '["Yes", "No"]',
    "outcomePrices": '["0.5", "0.5"]',
    "positionIds": ["6511508191", "6511508200"],
    "negRisk": False,
    "orderPriceMinTickSize": 0.001,
    "orderMinSize": 5,
    "feesEnabled": False,
    "active": True,
    "closed": False,
    "acceptingOrders": True,
    "enableOrderBook": True,
}


def test_parse_market_v1():
    m = parse_market(GAMMA_V1)
    assert m is not None
    assert m.version == "v1"
    assert m.yes_asset_id == "1075"
    assert m.no_asset_id == "7305"
    assert m.tick_size == D("0.01")
    assert m.min_order_notional == D("5")
    assert m.fee_schedule.rate == D("0.04")
    assert m.fee_schedule.available
    assert m.end_date is not None
    assert "Yes" in m.resolution_criteria
    assert m.tradeable


def test_parse_market_v2():
    m = parse_market(GAMMA_V2)
    assert m is not None
    assert m.version == "v2"
    assert m.yes_asset_id == "6511508191"
    assert m.no_asset_id == "6511508200"
    assert m.fee_schedule.fees_enabled is False
    assert m.fee_schedule.available  # feesEnabled=false eksplisit = fee 0, valid


def test_parse_market_fee_missing_is_invalid():
    raw = dict(GAMMA_V1)
    del raw["feeSchedule"]
    raw["feesEnabled"] = True
    m = parse_market(raw)
    assert m is not None
    assert not m.fee_schedule.available  # -> strategi harus menolak (fail-closed)


def test_parse_market_unsupported_version():
    raw = dict(GAMMA_V1)
    raw["version"] = "v3"
    assert parse_market(raw) is None


def test_parse_market_neg_risk_from_event():
    raw = dict(GAMMA_V1)
    raw["negRisk"] = True
    m = parse_market(raw, event_raw={"id": "90177", "enableNegRisk": True, "negRiskAugmented": True})
    assert m is not None
    assert m.neg_risk
    assert m.neg_risk_augmented


def test_parse_fee_schedule_missing():
    fs = parse_fee_schedule({})
    assert not fs.available
    fs2 = parse_fee_schedule({"feesEnabled": False})
    assert fs2.available and not fs2.fees_enabled


def test_parse_book_normalizes_order():
    raw = {
        "asset_id": "1075",
        "market": "0xabc",
        "timestamp": str(NOW),
        "hash": "0x1",
        "bids": [{"price": "0.48", "size": "30"}, {"price": "0.50", "size": "15"}],
        "asks": [{"price": "0.53", "size": "60"}, {"price": "0.52", "size": "25"}],
        "min_order_size": "5",
        "tick_size": "0.01",
        "neg_risk": False,
        "last_trade_price": "0.09",
    }
    snap = parse_book(raw)
    assert snap.best_bid.price == D("0.50")
    assert snap.best_ask.price == D("0.52")
    assert [lv.price for lv in snap.asks] == [D("0.52"), D("0.53")]
    assert snap.tick_size == D("0.01")
    assert snap.last_trade_price == D("0.09")


def test_apply_price_change_updates_level():
    snap = OrderBookSnapshot.from_levels(
        "1075",
        [("0.50", "15"), ("0.49", "10")],
        [("0.52", "25"), ("0.53", "60")],
        recv_ms=NOW,
    )
    # level bid 0.50 di-set jadi 200
    out = apply_price_change(snap, {"price": "0.5", "size": "200", "side": "BUY", "hash": "0x2"})
    assert out.best_bid.price == D("0.50")
    assert out.best_bid.size == D("200")
    # hapus level ask 0.53 (size 0)
    out2 = apply_price_change(out, {"price": "0.53", "size": "0", "side": "SELL"})
    assert [lv.price for lv in out2.asks] == [D("0.52")]
    # tambah level ask baru
    out3 = apply_price_change(out2, {"price": "0.51", "size": "5", "side": "SELL"})
    assert out3.best_ask.price == D("0.51")


def test_snapshot_staleness():
    snap = OrderBookSnapshot.from_levels("a", [("0.5", "1")], [("0.6", "1")], recv_ms=NOW - 5000)
    assert snap.is_stale(3000, now_ms=NOW)
    assert not snap.is_stale(10000, now_ms=NOW)


def test_feed_hub_register_and_stale_flag():
    from bot.data.feed import MarketDataHub
    from bot.data.clob import ClobClient
    from bot.data.ws_feed import MarketWsFeed
    from bot.costs import make_market

    class FakeClob(ClobClient):
        def __init__(self):
            pass
        async def get_books(self, asset_ids, *, batch_size=20):
            return {
                a: OrderBookSnapshot.from_levels(a, [("0.4", "10")], [("0.5", "10")], recv_ms=NOW)
                for a in asset_ids
            }

    async def run():
        ws = MarketWsFeed("ws://test", assets_per_connection=2)
        hub = MarketDataHub(FakeClob(), ws, stale_after_ms=3000)
        m1 = make_market("m1", fee_rate=D("0.04"))
        await hub.register_markets([m1])
        assert hub.get_book("yes-m1") is not None
        assert hub.is_fresh("yes-m1", now_ms=NOW)
        cov = hub.coverage_snapshot()
        assert cov.markets_monitored == 1
        # staleness pada waktu sekarang (bukan NOW yang lama)
        assert not hub.is_fresh("yes-m1", now_ms=NOW + 10000)

    asyncio.run(run())
