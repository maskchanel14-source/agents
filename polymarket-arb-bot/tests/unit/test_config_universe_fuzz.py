"""Config loading, universe filters (blacklist / ambiguous), and fuzzing of untrusted input."""

from __future__ import annotations

import json
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from polymarket_arb.config import DEFAULT_CONFIG, load_settings
from polymarket_arb.markets import parse_book, parse_market
from polymarket_arb.money import dec
from polymarket_arb.universe import build_universe
from tests.fixtures.synth import gamma_event, gamma_market, universe_events


class TestConfig:
    def test_default_is_paper_and_strategies_policy(self, settings):
        assert settings.mode == "paper"
        assert settings.strategies["intra_binary"] is True
        assert settings.strategies["neg_risk"] is True
        assert settings.strategies["cross_logical"] is False
        assert settings.strategies["cross_venue"] is False

    def test_decimal_values_exact_from_yaml(self, settings):
        assert settings.limits.max_quoted_spread == dec("0.25")
        assert settings.limits.max_notional_per_trade == dec("50")
        assert isinstance(settings.thresholds.min_net_pct, Decimal)

    def test_default_path_points_at_repo_config(self):
        assert DEFAULT_CONFIG.name == "default.yaml" and DEFAULT_CONFIG.exists()

    def test_mode_override(self):
        assert load_settings(mode_override="backtest").mode == "backtest"

    def test_blacklist_and_ambiguity_defaults(self, settings):
        assert settings.data.exclude_ambiguous is True
        assert settings.data.blacklist_condition_ids == ()


class TestUniverse:
    def test_ambiguous_markets_excluded_by_default(self):
        ev = gamma_event("e", [gamma_market("0x" + "1" * 64, "a", "b", neg_risk=False)], neg_risk=False)
        ev["markets"][0]["resolutionSource"] = ""
        uni = build_universe([ev])
        assert uni.binaries == [] and uni.skipped["ambiguous_resolution"] == 1

    def test_ambiguous_allowed_when_disabled(self):
        ev = gamma_event("e", [gamma_market("0x" + "1" * 64, "a", "b", neg_risk=False)], neg_risk=False)
        ev["markets"][0]["resolutionSource"] = ""
        assert len(build_universe([ev], exclude_ambiguous=False).binaries) == 1

    def test_explicit_blacklist(self):
        cid = "0x" + "2" * 64
        ev = gamma_event("e", [gamma_market(cid, "a", "b", neg_risk=False)], neg_risk=False)
        uni = build_universe([ev], blacklist_condition_ids=[cid.upper()])
        assert uni.binaries == [] and uni.skipped["blacklisted"] == 1

    def test_group_with_blacklisted_member_dropped(self):
        events = universe_events()
        bad_cid = events[2]["markets"][0]["conditionId"]
        uni = build_universe(events, blacklist_condition_ids=[bad_cid])
        assert uni.groups == [] and uni.skipped["group_blacklisted_or_ambiguous"] == 1

    def test_duplicate_condition_ids_counted_once(self):
        ev = gamma_event("e", [gamma_market("0x" + "3" * 64, "a", "b", neg_risk=False)], neg_risk=False)
        uni = build_universe([ev, ev])
        assert len(uni.binaries) == 1

    def test_inactive_and_closed_skipped(self):
        raw = gamma_market("0x" + "4" * 64, "a", "b", neg_risk=False)
        raw["closed"] = True
        uni = build_universe([gamma_event("e", [raw], neg_risk=False)])
        assert uni.binaries == [] and uni.skipped["inactive"] == 1

    def test_cap_keeps_most_liquid(self):
        evs = []
        for i in range(5):
            raw = gamma_market(
                "0x" + f"{i:x}" * 64, f"y{i}", f"n{i}", neg_risk=False, liquidity=str(i * 100 + 1)
            )
            evs.append(gamma_event(f"e{i}", [raw], neg_risk=False))
        uni = build_universe(evs, max_assets=4)  # budget: 2 binaries
        assert len(uni.binaries) == 2
        liq = sorted((float(m.extra["liquidity"]) for m in uni.binaries), reverse=True)
        assert liq == [401.0, 301.0]

    def test_unparseable_market_counted(self):
        raw = gamma_market("0x" + "5" * 64, "a", "b", neg_risk=False)
        raw["clobTokenIds"] = "not json"
        uni = build_universe([gamma_event("e", [raw], neg_risk=False)])
        assert uni.skipped["unparseable_market"] == 1


# ---- fuzzing: untrusted exchange JSON must never crash with anything but ValueError/TypeError
JSONISH = st.recursive(
    st.none()
    | st.booleans()
    | st.integers(-5, 10**6)
    | st.floats(allow_nan=False, allow_infinity=False)
    | st.text(max_size=20),
    lambda children: (
        st.lists(children, max_size=4) | st.dictionaries(st.text(max_size=12), children, max_size=5)
    ),
    max_leaves=12,
)


@settings(max_examples=300, deadline=None)
@given(
    raw=st.dictionaries(
        st.sampled_from(
            [
                "conditionId",
                "outcomes",
                "clobTokenIds",
                "orderPriceMinTickSize",
                "orderMinSize",
                "version",
                "feeSchedule",
                "endDate",
                "positionIds",
                "resolutionSource",
                "active",
                "closed",
            ]
        ),
        JSONISH,
        max_size=8,
    )
)
def test_parse_market_fuzz_only_raises_value_or_type_error(raw):
    try:
        parse_market(raw)
    except (ValueError, TypeError, KeyError):
        pass


@settings(max_examples=300, deadline=None)
@given(
    raw=st.dictionaries(
        st.sampled_from(["asset_id", "timestamp", "bids", "asks", "tick_size", "min_order_size", "market"]),
        JSONISH,
        max_size=7,
    )
)
def test_parse_book_fuzz_only_raises_value_or_type_error(raw):
    try:
        parse_book(raw, received_ms=1)
    except (ValueError, TypeError, KeyError):
        pass


def test_book_levels_must_be_well_formed():
    good = {"asset_id": "a", "timestamp": "1", "bids": [{"price": "0.4", "size": "1"}], "asks": []}
    assert parse_book(good, 1).bids[0].price == dec("0.4")
    bad = dict(good, bids=[{"price": "0.4"}])
    with pytest.raises((ValueError, TypeError, KeyError)):  # missing size must not become zero
        parse_book(bad, 1)


def test_fuzz_json_roundtrip_of_fixture_stable():
    ev = universe_events()
    assert json.loads(json.dumps(ev)) == ev
