"""Test strategi A & B (end-to-end dengan fake hub), termasuk gate validasi."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from bot.costs import CostConfig, CostModel, GasModel, make_market
from bot.data.feed import MarketDataHub
from bot.decimal_utils import D, ZERO
from bot.models import OrderBookSnapshot
from bot.strategies.cross_market import CrossMarketLogical, normalize_criteria
from bot.strategies.cross_venue import CrossVenue
from bot.strategies.intra_market import IntraMarketBinary
from bot.strategies.multi_outcome import MultiOutcomeNegRisk, looks_like_other_outcome

NOW = 1_792_464_000_000  # 2026-10-20T00:00:00Z
END = datetime(2026, 10, 25, tzinfo=timezone.utc)  # resolusi dekat: uji fokus biaya, bukan waktu kunci


class FakeClob:
    async def get_books(self, asset_ids, *, batch_size=20):
        return {}


def make_hub(markets_books: dict) -> MarketDataHub:
    async def run():
        hub = MarketDataHub(FakeClob(), _FakeWs(), stale_after_ms=10**9)
        for meta, (bids_yes, asks_yes, bids_no, asks_no) in markets_books.items():
            hub.markets[meta.market_id] = meta
            hub.asset_to_market[meta.yes_asset_id] = meta.market_id
            hub.asset_to_market[meta.no_asset_id] = meta.market_id
            hub.books[meta.yes_asset_id] = OrderBookSnapshot.from_levels(
                meta.yes_asset_id, bids_yes, asks_yes, recv_ms=NOW
            )
            hub.books[meta.no_asset_id] = OrderBookSnapshot.from_levels(
                meta.no_asset_id, bids_no, asks_no, recv_ms=NOW
            )
        return hub

    return asyncio.run(run())


class _FakeWs:
    assets_per_connection = 100

    def __init__(self):
        self.stats = {"shards": 0, "connected": 0, "assets": 0, "reconnects": 0}
        self.on_event = None

    async def subscribe(self, ids):
        pass

    async def unsubscribe(self, ids):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass


def model():
    return CostModel(
        CostConfig(min_annualized_return=ZERO, safety_margin_usd=D("0.001"), max_capital_per_trade_usd=D("200")),
        GasModel(enabled=True, gas_price_gwei=D("100"), pol_usd=D("0.25")),
    )


# ---------------------------------------------------------------------------
# Strategi A
# ---------------------------------------------------------------------------

def test_strategy_a_detects_pair_arb():
    m = make_market("m1", fee_rate=D("0.04"), end_date=END)
    hub = make_hub({
        m: ([("0.30", "200")], [("0.40", "200")], [("0.45", "200")], [("0.55", "200")]),
    })
    strat = IntraMarketBinary(model(), {"enabled": True})
    opps = strat.scan(hub, now_ms=NOW)
    valid = [o for o in opps if o.valid]
    assert valid, [(o.reject_reason, o.reject_detail) for o in opps]
    # minimal satu jalur (merge/hold) valid dengan net > 0
    assert all(o.cost.net_profit > ZERO for o in valid)
    assert any(o.strategy == "A_intra_binary" for o in valid)


def test_strategy_a_no_opportunity_when_sum_ge_1():
    m = make_market("m1", fee_rate=D("0.04"), end_date=END)
    hub = make_hub({
        m: ([], [("0.60", "200")], [], [("0.50", "200")]),
    })
    strat = IntraMarketBinary(model(), {"enabled": True})
    opps = strat.scan(hub, now_ms=NOW)
    assert opps == []  # filter murah menahan


def test_strategy_a2_mint_sell():
    m = make_market("m1", fee_rate=D("0"), end_date=END)
    hub = make_hub({
        m: ([("0.52", "200")], [], [("0.51", "200")], []),
    })
    strat = IntraMarketBinary(model(), {"enabled": True})
    opps = strat.scan(hub, now_ms=NOW)
    valid = [o for o in opps if o.valid and o.strategy.endswith("_sell")]
    assert valid
    assert valid[0].cost.net_profit > ZERO


# ---------------------------------------------------------------------------
# Strategi B
# ---------------------------------------------------------------------------

def _neg_risk_event(n=3, ask_yes=("0.30", "0.30", "0.30"), other=False):
    members = []
    books = {}
    for i in range(n):
        slug = f"outcome-{i}"
        if other and i == n - 1:
            slug = "other-candidate"
        m = make_market(f"m{i}", fee_rate=D("0.04"), neg_risk=True, end_date=END)
        object.__setattr__(m, "event_id", "evt-1")
        object.__setattr__(m, "slug", slug)
        object.__setattr__(m, "question", f"Will {slug} win?")
        members.append(m)
        books[m] = (
            [("0.20", "500")], [(ask_yes[i], "500")],
            [("0.55", "500")], [("0.65", "500")],
        )
    return members, books


def test_strategy_b_buy_all_yes():
    members, books = _neg_risk_event(3, ask_yes=("0.30", "0.30", "0.30"))
    hub = make_hub(books)
    strat = MultiOutcomeNegRisk(model(), {"enabled": True, "require_exhaustive": True})
    opps = strat.scan(hub, now_ms=NOW)
    valid = [o for o in opps if o.valid and o.strategy == "B_multi_outcome"]
    assert valid, [(o.strategy, o.reject_reason, o.reject_detail) for o in opps]
    assert valid[0].cost.net_profit > ZERO


def test_strategy_b_skips_when_other_outcome_present():
    members, books = _neg_risk_event(3, ask_yes=("0.10", "0.10", "0.10"), other=True)
    hub = make_hub(books)
    strat = MultiOutcomeNegRisk(model(), {"enabled": True, "require_exhaustive": True})
    opps = strat.scan(hub, now_ms=NOW)
    assert opps == []  # outcome "Other" -> skip (risiko tidak exhaustive)


def test_strategy_b_skips_non_neg_risk():
    members, books = _neg_risk_event(3, ask_yes=("0.10", "0.10", "0.10"))
    for m in members:
        object.__setattr__(m, "neg_risk", False)
    hub = make_hub(books)
    strat = MultiOutcomeNegRisk(model(), {"enabled": True, "require_exhaustive": True})
    assert strat.scan(hub, now_ms=NOW) == []


def test_strategy_b_conversion_variant():
    members, books = _neg_risk_event(3, ask_yes=("0.55", "0.55", "0.55"))
    # NO ask 0.65; YES bids 0.20+0.20 = 0.40 -> konversi tidak untung.
    # Balik: NO ask murah, YES bid tinggi
    for m in members:
        bids_yes, asks_yes, bids_no, asks_no = books[m]
        books[m] = (bids_yes, asks_yes, bids_no, [("0.30", "500")])  # NO ask 0.30
        # YES bid tinggi di market lain: set YES bid 0.40
        books[m] = ([("0.40", "500")], asks_yes, bids_no, [("0.30", "500")])
    hub = make_hub(books)
    strat = MultiOutcomeNegRisk(model(), {"enabled": True, "require_exhaustive": True})
    opps = strat.scan(hub, now_ms=NOW)
    conv = [o for o in opps if o.strategy.endswith("_convert")]
    assert conv
    # konversi: beli NO 0.30 + jual 2x YES @0.40 = masuk 0.80 -> net positif
    assert any(o.valid for o in conv), [(o.reject_reason, o.reject_detail) for o in conv]


def test_looks_like_other_outcome():
    m = make_market("m", fee_rate=D("0"))
    object.__setattr__(m, "slug", "who-wins-other")
    assert looks_like_other_outcome(m)
    m2 = make_market("m2", fee_rate=D("0"))
    object.__setattr__(m2, "slug", "will-trump-win")
    assert not looks_like_other_outcome(m2)


# ---------------------------------------------------------------------------
# Strategi C & D
# ---------------------------------------------------------------------------

def test_cross_market_disabled_by_default():
    hub = make_hub({})
    strat = CrossMarketLogical(model(), {"enabled": False})
    assert strat.scan(hub, now_ms=NOW) == []


def test_cross_market_identical_criteria_arb():
    a = make_market("ma", fee_rate=D("0"), end_date=END)
    b = make_market("mb", fee_rate=D("0"), end_date=END)
    crit = "This market resolves Yes if the official result is confirmed."
    object.__setattr__(a, "resolution_criteria", crit)
    object.__setattr__(b, "resolution_criteria", crit)
    object.__setattr__(a, "question", "Same question?")
    object.__setattr__(b, "question", "Same question?")
    hub = make_hub({
        a: ([], [("0.40", "500")], [], []),
        b: ([("0.55", "500")], [], [], []),
    })
    strat = CrossMarketLogical(model(), {"enabled": True})
    opps = strat.scan(hub, now_ms=NOW)
    assert opps
    assert any(o.valid for o in opps), [(o.reject_reason, o.reject_detail) for o in opps]


def test_cross_market_skips_non_identical():
    a = make_market("ma", fee_rate=D("0"), end_date=END)
    b = make_market("mb", fee_rate=D("0"), end_date=END)
    object.__setattr__(a, "resolution_criteria", "Resolves Yes if X happens by Friday.")
    object.__setattr__(b, "resolution_criteria", "Resolves Yes if X happens by Saturday.")
    hub = make_hub({
        a: ([], [("0.40", "500")], [], []),
        b: ([("0.55", "500")], [], [], []),
    })
    strat = CrossMarketLogical(model(), {"enabled": True})
    assert strat.scan(hub, now_ms=NOW) == []


def test_normalize_criteria():
    assert normalize_criteria("Resolves  YES, if X!!") == "resolves yes if x"


def test_cross_venue_stub_disabled():
    hub = make_hub({})
    assert CrossVenue(model(), {"enabled": False}).scan(hub, now_ms=NOW) == []
