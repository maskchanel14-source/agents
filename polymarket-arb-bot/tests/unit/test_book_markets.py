"""Order-book walking, tick/min-size logic, market parsing and the book store integrity rules."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from polymarket_arb.book import available_shares, candidate_sizes, consumed_levels, off_tick_prices, walk_book
from polymarket_arb.data.book_store import BookStore
from polymarket_arb.domain import FeeSchedule, Level
from polymarket_arb.markets import parse_book, parse_events, parse_market
from polymarket_arb.money import ONE, ZERO, ceil_to, dec, floor_to, is_multiple_of
from tests.fixtures.synth import gamma_event, gamma_market

ASKS = (Level(dec("0.45"), dec("100")), Level(dec("0.47"), dec("200")), Level(dec("0.50"), dec("50")))


class TestWalkBook:
    def test_full_fill_within_first_level(self):
        r = walk_book(ASKS, dec("50"))
        assert r.complete and r.shares == dec("50") and r.vwap == dec("0.45") and r.levels_used == 1

    def test_vwap_across_levels(self):
        r = walk_book(ASKS, dec("150"))
        assert r.complete
        assert r.notional == dec("100") * dec("0.45") + dec("50") * dec("0.47")
        assert r.vwap == r.notional / dec("150")
        assert r.worst_price == dec("0.47")

    def test_insufficient_depth_is_incomplete(self):
        r = walk_book(ASKS, dec("1000"))
        assert not r.complete and r.shares == dec("350") and r.worst_price == dec("0.50")

    def test_zero_target_is_empty(self):
        r = walk_book(ASKS, ZERO)
        assert r.shares == ZERO and r.vwap is None and r.complete

    def test_empty_book(self):
        r = walk_book((), dec("1"))
        assert not r.complete and r.vwap is None and r.worst_price is None

    def test_negative_target_rejected(self):
        with pytest.raises(ValueError):
            walk_book(ASKS, dec("-1"))

    def test_zero_size_levels_skipped(self):
        levels = (Level(dec("0.4"), ZERO), Level(dec("0.5"), dec("10")))
        r = walk_book(levels, dec("5"))
        assert r.vwap == dec("0.5") and r.levels_used == 1

    def test_fee_fn_accumulates_per_level(self):
        seen = []

        def fee(shares, price):
            seen.append((shares, price))
            return shares * dec("0.01")

        r = walk_book(ASKS, dec("150"), fee)
        assert r.fee == dec("1.50")
        assert seen == [(dec("100"), dec("0.45")), (dec("50"), dec("0.47"))]

    @given(
        sizes=st.lists(
            st.decimals(min_value=Decimal("0.01"), max_value=Decimal(500), places=2), min_size=1, max_size=8
        ),
        target=st.decimals(min_value=Decimal(0), max_value=Decimal(2000), places=2),
    )
    def test_walk_properties(self, sizes, target):
        levels = tuple(Level(dec("0.10") + dec("0.01") * i, s) for i, s in enumerate(sizes))
        r = walk_book(levels, target)
        assert r.shares <= target
        assert r.shares <= available_shares(levels)
        assert r.complete == (r.shares == target)
        if r.vwap is not None:
            assert levels[0].price <= r.vwap <= r.worst_price


class TestConsumedLevels:
    def test_pieces_match_walk(self):
        pieces = consumed_levels(ASKS, dec("150"))
        assert [(lv.price, lv.size) for lv in pieces] == [(dec("0.45"), dec("100")), (dec("0.47"), dec("50"))]

    def test_zero_target(self):
        assert consumed_levels(ASKS, ZERO) == []


class TestTickAndSizes:
    def test_off_tick_detected(self):
        levels = (Level(dec("0.455"), dec("1")), Level(dec("0.45"), dec("1")))
        assert off_tick_prices(levels, dec("0.01")) == [dec("0.455")]

    def test_candidate_sizes_include_kinks_and_cap(self):
        sizes = candidate_sizes([ASKS], dec("500"), dec("5"))
        assert sizes == [dec("100"), dec("300"), dec("350"), dec("500")]  # cumulative kinks + cap
        assert all(s <= dec("500") and s >= dec("5") for s in sizes)
        assert sizes == sorted(set(sizes))

    def test_candidate_sizes_empty_when_below_min(self):
        assert candidate_sizes([ASKS], dec("3"), dec("5")) == []

    def test_money_helpers(self):
        assert floor_to(dec("1.239"), dec("0.01")) == dec("1.23")
        assert ceil_to(dec("1.231"), dec("0.01")) == dec("1.24")
        assert is_multiple_of(dec("0.450"), dec("0.001"))
        assert not is_multiple_of(dec("0.4505"), dec("0.001"))


def _raw_market(cid="0x" + "c" * 64, **kw):
    return gamma_market(cid, "y-id", "n-id", neg_risk=False, **kw)


class TestParseMarkets:
    def test_v1_binary_parsed(self):
        m = parse_market(_raw_market(), event_meta={"id": "e1", "enableNegRisk": False})
        assert m.yes.asset_id == "y-id" and m.no.asset_id == "n-id"
        assert m.tick_size == dec("0.001") and m.min_order_size == dec("5")
        assert m.fee_schedule is not None and m.fee_schedule.rate == dec("0.04")

    def test_v2_uses_position_ids(self):
        raw = _raw_market()
        raw.update({"version": "v2", "positionIds": ["p-yes", "p-no"]})
        m = parse_market(raw)
        assert (m.yes.asset_id, m.no.asset_id) == ("p-yes", "p-no")

    def test_unknown_version_rejected(self):
        raw = _raw_market()
        raw["version"] = "v9"
        with pytest.raises(ValueError):
            parse_market(raw)

    def test_missing_condition_id_rejected(self):
        raw = _raw_market()
        raw["conditionId"] = ""
        with pytest.raises(ValueError):
            parse_market(raw)

    def test_missing_tick_rejected(self):
        raw = _raw_market()
        del raw["orderPriceMinTickSize"]
        with pytest.raises(ValueError):
            parse_market(raw)

    def test_bad_outcome_labels_rejected(self):
        raw = _raw_market()
        raw["outcomes"] = '["Up", "Down"]'
        with pytest.raises(ValueError):
            parse_market(raw)

    def test_fee_schedule_missing_fields_gives_none(self):
        raw = _raw_market()
        raw["feeSchedule"] = {"rate": "0.04"}  # no exponent
        assert parse_market(raw).fee_schedule is None

    def test_ambiguous_resolution_flag(self):
        assert not parse_market(_raw_market()).ambiguous_resolution
        raw = _raw_market()
        raw["resolutionSource"] = ""
        assert parse_market(raw).ambiguous_resolution

    def test_parse_events_flags_groups(self):
        ev = gamma_event("e9", [_raw_market("0x" + "d" * 64)], neg_risk=True)
        groups = parse_events([ev])
        assert groups[0].neg_risk and groups[0].declared_market_count == 1 and len(groups[0].markets) == 1


class TestParseBook:
    def test_levels_normalised(self):
        raw = {
            "asset_id": "a",
            "market": "m",
            "timestamp": "1000",
            "bids": [{"price": "0.1", "size": "1"}, {"price": "0.3", "size": "2"}],
            "asks": [{"price": "0.9", "size": "1"}, {"price": "0.5", "size": "2"}],
        }
        b = parse_book(raw, received_ms=1)
        assert [lv.price for lv in b.bids] == [dec("0.3"), dec("0.1")]
        assert [lv.price for lv in b.asks] == [dec("0.5"), dec("0.9")]

    def test_missing_timestamp_rejected(self):
        with pytest.raises(ValueError):
            parse_book({"asset_id": "a", "bids": [], "asks": []}, received_ms=1)


def _snap(asset, bids, asks, ts=1000):
    return {
        "event_type": "book",
        "asset_id": asset,
        "market": "m",
        "timestamp": str(ts),
        "bids": [{"price": p, "size": s} for p, s in bids],
        "asks": [{"price": p, "size": s} for p, s in asks],
    }


class TestBookStore:
    def _store(self):
        s = BookStore()
        s.register("a", dec("0.01"), dec("5"), "m")
        return s

    def test_delta_before_snapshot_ignored(self):
        s = self._store()
        s.apply_price_change(
            {
                "event_type": "price_change",
                "timestamp": "1",
                "price_changes": [{"asset_id": "a", "price": "0.5", "size": "3", "side": "BUY"}],
            },
            1,
        )
        assert s.get("a") is None
        assert s.counters.get("delta_before_snapshot") == 1

    def test_snapshot_then_delta_updates_level_and_removes_on_zero(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")], ts=1000), 1000)
        s.apply_message(
            {
                "event_type": "price_change",
                "timestamp": "1001",
                "price_changes": [
                    {
                        "asset_id": "a",
                        "price": "0.50",
                        "size": "0",
                        "side": "SELL",
                        "best_bid": "0.40",
                        "best_ask": "0.55",
                    }
                ],
            },
            1001,
        )
        assert s.get("a") is None or s.get("a").asks == ()

    def test_out_of_order_delta_dropped(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")], ts=2000), 2000)
        s.apply_message(
            {
                "event_type": "price_change",
                "timestamp": "1500",
                "price_changes": [{"asset_id": "a", "price": "0.50", "size": "99", "side": "SELL"}],
            },
            2001,
        )
        assert s.counters.get("out_of_order_delta") == 1
        assert s.get("a").asks[0].size == dec("10")

    def test_top_of_book_mismatch_invalidates(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")]), 1000)
        s.apply_message(
            {
                "event_type": "price_change",
                "timestamp": "1001",
                "price_changes": [
                    {
                        "asset_id": "a",
                        "price": "0.41",
                        "size": "1",
                        "side": "BUY",
                        "best_bid": "0.99",
                        "best_ask": "0.50",
                    }
                ],
            },
            1001,
        )
        assert s.get("a") is None  # invalid books are not served
        assert s.counters.get("invalidated:book_mismatch") == 1

    def test_disconnect_invalidates_everything(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")]), 1000)
        s.invalidate_all("disconnect")
        assert s.get("a") is None

    def test_new_snapshot_revalidates(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")]), 1000)
        s.invalidate_all("disconnect")
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")], ts=3000), 3000)
        assert s.get("a") is not None

    def test_unknown_event_counted(self):
        s = self._store()
        assert s.apply_message({"event_type": "weird"}, 1) == "unknown"
        assert s.counters.get("unknown_event") == 1

    def test_tick_change_applied(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.40", "10")], [("0.50", "10")]), 1000)
        s.apply_message({"event_type": "tick_size_change", "asset_id": "a", "new_tick_size": "0.001"}, 1)
        assert s.get("a").tick_size == dec("0.001")

    def test_snapshot_levels_ordered_best_first(self):
        s = self._store()
        s.apply_message(_snap("a", [("0.10", "1"), ("0.30", "1")], [("0.90", "1"), ("0.60", "1")]), 1000)
        snap = s.get("a")
        assert snap.bids[0].price == dec("0.30") and snap.asks[0].price == dec("0.60")


def test_fee_schedule_dataclass_roundtrip():
    fs = FeeSchedule(rate=dec("0.04"), exponent=ONE, taker_only=True, rebate_rate=dec("0.25"))
    assert fs.rate == dec("0.04")
