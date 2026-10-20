"""Utilitas Decimal — SEMUA uang/harga/share dihitung dengan Decimal, bukan float."""

from __future__ import annotations

from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_UP, Decimal, InvalidOperation

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")

# Presisi internal untuk operasi pembagian/pangkat (hindari error tak terduga).
DECIMAL_CONTEXT_PREC = 28


def D(value) -> Decimal:
    """Parse nilai ke Decimal dari string/int/Decimal. Float DILARANG untuk hasil akhir.

    Float hanya diterima lewat konversi `str(value)` (untuk config YAML) — peringatan
    presisi dicatat di docstring; semua input kritis harus string.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        # float dari config: pakai repr standar via str; jangan pakai untuk uang.
        return Decimal(str(value))
    if isinstance(value, str):
        s = value.strip()
        if not s:
            raise InvalidOperation("empty string is not a valid Decimal")
        return Decimal(s)
    raise TypeError(f"cannot convert {type(value)!r} to Decimal")


def q_places(places: int) -> Decimal:
    """Quantum untuk pembulatan ke N desimal, mis. q_places(5) -> 0.00001."""
    return Decimal(1).scaleb(-places)


def round_half_up(value: Decimal, places: int) -> Decimal:
    return value.quantize(q_places(places), rounding=ROUND_HALF_UP)


def round_down(value: Decimal, places: int) -> Decimal:
    """Floor ke N desimal (ke arah nol untuk nilai positif = ROUND_DOWN)."""
    return value.quantize(q_places(places), rounding=ROUND_DOWN)


def round_up(value: Decimal, places: int) -> Decimal:
    """Ceiling ke N desimal (positif)."""
    return value.quantize(q_places(places), rounding=ROUND_CEILING)


def round_price_for_tick(price: Decimal, tick: Decimal, *, buy: bool) -> Decimal:
    """Bulatkan harga ke kelipatan tick secara konservatif.

    Beli (limit) -> ceil ke tick (harga maks yang masih aman tidak melewati batas),
    Jual -> floor ke tick.
    """
    if tick <= ZERO:
        raise ValueError("tick must be > 0")
    if price < ZERO:
        raise ValueError("price must be >= 0")
    ticks = (price / tick)
    if buy:
        n = ticks.to_integral_value(rounding=ROUND_CEILING)
    else:
        n = ticks.to_integral_value(rounding=ROUND_FLOOR)
    return n * tick


def price_on_tick(price: Decimal, tick: Decimal) -> bool:
    if tick <= ZERO:
        return False
    scaled = price / tick
    return scaled == scaled.to_integral_value()


def dec_min(a: Decimal, b: Decimal) -> Decimal:
    return a if a <= b else b


def dec_max(a: Decimal, b: Decimal) -> Decimal:
    return a if a >= b else b


def pct(part: Decimal, whole: Decimal) -> Decimal:
    if whole == ZERO:
        return ZERO
    return (part / whole) * HUNDRED
