"""Parse raw Gamma / CLOB JSON into typed domain objects.

Parsing is strict: anything ambiguous raises ``ValueError`` so the caller can
skip the market with a logged reason instead of guessing (e.g. YES/NO swapped).
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from .domain import (
    BookSnapshot,
    EventGroup,
    FeeSchedule,
    Level,
    MarketInfo,
    OutcomeToken,
)
from .money import dec


def _iso_to_ms(value: Any) -> int | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    if len(text) == 10:  # date only, e.g. "2027-01-01"
        text = text + "T00:00:00+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp without timezone: {value!r}")
    return int(dt.timestamp() * 1000)


def _json_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if not value.strip():
            return []
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            raise TypeError("expected JSON array")
        return parsed
    raise ValueError(f"unexpected type {type(value).__name__}")


def parse_fee_schedule(value: Any) -> FeeSchedule | None:
    if not isinstance(value, dict):
        return None
    if "rate" not in value or "exponent" not in value:
        return None
    return FeeSchedule(
        rate=dec(str(value["rate"])),
        exponent=dec(str(value["exponent"])),
        taker_only=bool(value.get("takerOnly", value.get("taker_only", True))),
        rebate_rate=dec(str(value.get("rebateRate", value.get("rebate_rate", "0")))),
    )


def _tokens(d: dict[str, Any]) -> tuple[OutcomeToken, OutcomeToken]:
    labels = [str(x).strip() for x in _json_list(d.get("outcomes"))]
    version = str(d.get("version", "v1"))
    if version == "v2":
        ids = [str(x) for x in (d.get("positionIds") or [])]
    elif version == "v1":
        ids = [str(x) for x in _json_list(d.get("clobTokenIds"))]
    else:
        raise ValueError(f"unsupported market version {version!r}")
    if len(labels) != 2 or len(ids) != 2:
        raise ValueError("binary market requires exactly 2 outcomes and 2 ids")
    mapping = {label.lower(): asset for label, asset in zip(labels, ids)}
    if set(mapping) != {"yes", "no"}:
        raise ValueError(f"unexpected outcome labels {labels!r}")
    return OutcomeToken("Yes", mapping["yes"]), OutcomeToken("No", mapping["no"])


def parse_market(d: dict[str, Any], event_meta: dict[str, Any] | None = None) -> MarketInfo:
    """Parse a Gamma market object. ``event_meta`` is the parent event (flags)."""
    condition_id = str(d.get("conditionId") or "")
    if not condition_id:
        raise ValueError("market without conditionId")
    yes, no = _tokens(d)
    tick = d.get("orderPriceMinTickSize")
    min_size = d.get("orderMinSize")
    if tick is None or min_size is None:
        raise ValueError("missing tick size or min order size")
    events = d.get("events") or []
    event_id = None
    ev_neg = False
    ev_aug = False
    if event_meta is not None:
        event_id = str(event_meta.get("id")) if event_meta.get("id") is not None else None
        ev_neg = bool(event_meta.get("enableNegRisk", False))
        ev_aug = bool(event_meta.get("negRiskAugmented", False))
    elif events:
        ev = events[0]
        event_id = str(ev.get("id")) if ev.get("id") is not None else None
        ev_neg = bool(ev.get("enableNegRisk", False))
        ev_aug = bool(ev.get("negRiskAugmented", False))
    fees_enabled = d.get("feesEnabled")
    end_ms = _iso_to_ms(d.get("endDate") or d.get("endDateIso"))
    return MarketInfo(
        condition_id=condition_id,
        slug=str(d.get("slug") or ""),
        question=str(d.get("question") or ""),
        description=str(d.get("description") or ""),
        resolution_source=str(d.get("resolutionSource") or ""),
        end_date_ms=end_ms,
        active=bool(d.get("active", False)),
        closed=bool(d.get("closed", False)),
        accepting_orders=bool(d.get("acceptingOrders", False)),
        neg_risk=bool(d.get("negRisk", False)),
        neg_risk_other=bool(d.get("negRiskOther", False)),
        event_id=event_id,
        event_neg_risk=ev_neg,
        event_neg_risk_augmented=ev_aug,
        version=str(d.get("version", "v1")),
        yes=yes,
        no=no,
        tick_size=dec(str(tick)),
        min_order_size=dec(str(min_size)),
        fees_enabled=None if fees_enabled is None else bool(fees_enabled),
        fee_schedule=parse_fee_schedule(d.get("feeSchedule")),
        seconds_delay=int(d.get("secondsDelay") or 0),
    )


def parse_events(events: list[dict[str, Any]]) -> list[EventGroup]:
    """Build neg-risk candidate groups from Gamma ``/events`` objects.

    Only events with ``enableNegRisk`` are returned as neg-risk groups. The caller
    decides whether a group is complete (see strategies/neg_risk.py).
    """
    groups: list[EventGroup] = []
    for ev in events:
        markets_raw = ev.get("markets") or []
        parsed: list[MarketInfo] = []
        for m in markets_raw:
            try:
                parsed.append(parse_market(m, event_meta=ev))
            except ValueError:
                continue  # unparseable market: group becomes incomplete below
        groups.append(
            EventGroup(
                event_id=str(ev.get("id")),
                neg_risk=bool(ev.get("enableNegRisk", False)),
                neg_risk_augmented=bool(ev.get("negRiskAugmented", False)),
                declared_market_count=len(markets_raw),
                markets=tuple(parsed),
            )
        )
    return groups


def _levels(raw: Any, descending: bool) -> tuple[Level, ...]:
    out: list[Level] = []
    for item in raw or []:
        price = dec(str(item["price"]))
        size = dec(str(item["size"]))
        if size <= 0 or not (Decimal(0) < price < Decimal(1)):
            continue
        out.append(Level(price=price, size=size))
    out.sort(key=lambda lv: lv.price, reverse=descending)
    return tuple(out)


def parse_book(
    d: dict[str, Any],
    received_ms: int,
    *,
    tick_size: Decimal | None = None,
    min_order_size: Decimal | None = None,
) -> BookSnapshot:
    """Parse a CLOB ``/book`` object (or WS ``book`` event) into a BookSnapshot."""
    asset_id = str(d.get("asset_id") or d.get("assetId") or "")
    if not asset_id:
        raise ValueError("book without asset_id")
    ts_raw = d.get("timestamp")
    if ts_raw is None:
        raise ValueError("book without timestamp")
    tick = tick_size if tick_size is not None else dec(str(d.get("tick_size", "0.01")))
    min_size = min_order_size if min_order_size is not None else dec(str(d.get("min_order_size", "5")))
    last = d.get("last_trade_price")
    return BookSnapshot(
        asset_id=asset_id,
        condition_id=str(d.get("market") or d.get("condition_id") or ""),
        bids=_levels(d.get("bids"), descending=True),
        asks=_levels(d.get("asks"), descending=False),
        exchange_ts_ms=int(str(ts_raw)),
        received_ms=received_ms,
        tick_size=tick,
        min_order_size=min_size,
        last_trade_price=None if last in (None, "") else dec(str(last)),
    )


def parse_event_groups_safe(events: list[dict[str, Any]]) -> list[EventGroup]:
    """Same as ``parse_events`` but tolerant of malformed events (skipped)."""
    try:
        return parse_events(events)
    except (KeyError, TypeError, ValueError):
        out: list[EventGroup] = []
        for ev in events:
            try:
                out.extend(parse_events([ev]))
            except (KeyError, TypeError, ValueError):
                continue
        return out
