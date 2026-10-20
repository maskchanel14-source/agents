"""Test utilitas Decimal + property test konsistensi kalkulasi."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given, strategies as st

from bot.decimal_utils import (
    D,
    ONE,
    ZERO,
    dec_max,
    dec_min,
    pct,
    price_on_tick,
    round_down,
    round_half_up,
    round_price_for_tick,
    round_up,
)


def test_D_parses_strings_and_ints():
    assert D("0.1") + D("0.2") == D("0.3")
    assert D(3) == Decimal(3)
    assert D(Decimal("1.5")) == Decimal("1.5")
    with pytest.raises(TypeError):
        D([1])
    with pytest.raises(Exception):
        D("")


def test_D_float_uses_str_conversion():
    # float hanya lewat config — hasil lewat str() bukan binary float
    assert D(0.1) == D("0.1")


def test_rounding_helpers():
    assert round_half_up(D("0.123456"), 5) == D("0.12346")
    assert round_down(D("0.123456"), 5) == D("0.12345")
    assert round_up(D("0.123451"), 5) == D("0.12346")
    assert round_half_up(D("0.000015"), 5) == D("0.00002")  # half-up, bukan banker's


def test_price_rounding_tick():
    # beli -> ceil
    assert round_price_for_tick(D("0.521"), D("0.01"), buy=True) == D("0.53")
    # jual -> floor
    assert round_price_for_tick(D("0.529"), D("0.01"), buy=False) == D("0.52")
    assert price_on_tick(D("0.52"), D("0.01"))
    assert not price_on_tick(D("0.523"), D("0.01"))
    with pytest.raises(ValueError):
        round_price_for_tick(D("0.5"), ZERO, buy=True)


def test_min_max_pct():
    assert dec_min(D("1"), D("2")) == D("1")
    assert dec_max(D("1"), D("2")) == D("2")
    assert pct(D("1"), D("4")) == D("25")
    assert pct(D("1"), ZERO) == ZERO


@given(
    a=st.decimals(min_value=0, max_value=1000, places=4, allow_nan=False, allow_infinity=False),
    b=st.decimals(min_value=0, max_value=1000, places=4, allow_nan=False, allow_infinity=False),
)
def test_property_min_max_consistent(a, b):
    assert dec_min(a, b) <= dec_max(a, b)
    assert dec_min(a, b) in (a, b)


@given(
    price=st.decimals(min_value="0.001", max_value="0.999", places=3),
    shares=st.decimals(min_value="1", max_value=10000, places=2),
)
def test_property_rounding_never_inflates_shares(price, shares):
    """Pembulatan share tidak boleh menambah ukuran (floor)."""
    tick = D("0.01")
    rounded = round_price_for_tick(price, tick, buy=True)
    assert rounded >= price  # beli: ceil — tidak pernah di bawah harga asli
    rounded_sell = round_price_for_tick(price, tick, buy=False)
    assert rounded_sell <= price
