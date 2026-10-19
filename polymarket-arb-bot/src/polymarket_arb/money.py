"""Decimal-only money helpers. Floats are rejected on purpose."""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_UP, Decimal, InvalidOperation

ZERO = Decimal(0)
ONE = Decimal(1)
FEE_QUANT = Decimal("0.00001")  # fees are rounded to 5 dp (docs/fees)
SHARE_STEP = Decimal("0.01")  # order share size granularity used by the bot
USDC_QUANT = Decimal("0.000001")  # 6 dp, base unit of pUSD/USDC


def dec(value: object) -> Decimal:
    """Convert str/int/Decimal to Decimal. Floats are refused (precision bugs).

    Malformed strings raise ``ValueError`` (not ``decimal.InvalidOperation``), so untrusted
    exchange data can be rejected with one exception type.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise TypeError("bool is not a numeric value here")
    if isinstance(value, float):
        raise TypeError("float not allowed; pass str/int/Decimal")
    if isinstance(value, (int, str)):
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"not a decimal: {value!r}") from exc
    raise TypeError(f"cannot convert {type(value).__name__} to Decimal")


def floor_to(value: Decimal, step: Decimal) -> Decimal:
    """Round toward zero to a multiple of ``step``."""
    if step <= 0:
        raise ValueError("step must be positive")
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def ceil_to(value: Decimal, step: Decimal) -> Decimal:
    """Round away from zero (for non-negative values: up) to a multiple of ``step``."""
    if step <= 0:
        raise ValueError("step must be positive")
    return (value / step).to_integral_value(rounding=ROUND_UP) * step


def is_multiple_of(value: Decimal, step: Decimal) -> bool:
    if step <= 0:
        raise ValueError("step must be positive")
    return (value / step) == (value / step).to_integral_value()
