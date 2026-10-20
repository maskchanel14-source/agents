"""Gamma API — discovery penuh event/market + parsing metadata.

Endpoint: https://gamma-api.polymarket.com (lihat docs/POLYMARKET_NOTES.md §2).
Paginasi penuh (offset/keyset), semua market aktif, bukan sampel.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, AsyncIterator, Optional

from ..decimal_utils import D, ZERO, ONE
from ..models import FeeSchedule, MarketMeta
from .http import LIMITS, HttpClient

log = logging.getLogger("bot.data.gamma")


def _parse_json_array(value: Any) -> list[str]:
    """Gamma meng-encode array sebagai JSON string (atau sudah list di v2)."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            return [str(v) for v in parsed] if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _parse_dt(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        s = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def parse_fee_schedule(raw: dict) -> FeeSchedule:
    """Parse fee schedule Gamma -> FeeSchedule. Hilang -> source='missing' (INVALID).

    Menerima tiga bentuk yang beredar di API/docs:
    1. `feeSchedule` ternormalisasi: {rate, exponent, takerOnly, rebateRate}
    2. `feeSchedule` mentah: {baseFee|takerBaseFee|makerBaseFee, expScalar, expBase, ...}
       dengan `exponent = expScalar / 1e16` (rumus fee resmi `p(1-p)^e`).
    3. `fee` lama: {baseFee, expScalar, ...}.
    `feesEnabled: false` eksplisit = fee 0 (valid). Sisanya -> missing (fail-closed).
    """
    if not raw:
        return FeeSchedule.missing()

    def _mk(rate, exponent, taker_only, rebate=ZERO, fees_enabled=True) -> FeeSchedule:
        return FeeSchedule(
            fees_enabled=fees_enabled,
            rate=rate,
            exponent=exponent,
            taker_only=taker_only,
            rebate_rate=rebate,
            source="gamma",
        )

    def _from_raw_shape(sched: dict) -> FeeSchedule:
        base = sched.get("baseFee")
        taker = sched.get("takerBaseFee")
        maker = sched.get("makerBaseFee")
        rate_src = taker if taker is not None else base
        rate = D(str(rate_src)) if rate_src is not None else ZERO
        maker_val = D(str(maker)) if maker is not None else ZERO
        exp_scalar = sched.get("expScalar")
        if exp_scalar is not None:
            exponent = D(str(exp_scalar)) / D("1e16")
        else:
            exponent = D(str(sched.get("expBase", "1")))
            if exponent > 10:  # expBase bukan exponent; default 1
                exponent = ONE
        taker_only = maker_val == ZERO
        return _mk(rate, exponent, taker_only)

    sched = raw.get("feeSchedule")
    if sched is not None:
        try:
            if "rate" in sched or "exponent" in sched:
                return _mk(
                    D(str(sched.get("rate", "0"))),
                    D(str(sched.get("exponent", "1"))),
                    bool(sched.get("takerOnly", True)),
                    D(str(sched.get("rebateRate", "0"))),
                )
            return _from_raw_shape(sched)
        except Exception:
            return FeeSchedule.missing()

    fee = raw.get("fee")
    if fee is not None and isinstance(fee, dict):
        try:
            return _from_raw_shape(fee)
        except Exception:
            return FeeSchedule.missing()

    if raw.get("feesEnabled") is False:
        return _mk(ZERO, ONE, True, fees_enabled=False)
    return FeeSchedule.missing()


def parse_market(raw: dict, *, event_raw: Optional[dict] = None) -> Optional[MarketMeta]:
    """Konversi objek Gamma market -> MarketMeta. None bila tidak bisa ditrade."""
    version = str(raw.get("version") or ("v2" if raw.get("positionIds") else "v1"))
    if version not in ("v1", "v2"):
        return None

    outcomes = _parse_json_array(raw.get("outcomes"))
    if version == "v2":
        asset_ids = _parse_json_array(raw.get("positionIds"))
    else:
        asset_ids = _parse_json_array(raw.get("clobTokenIds"))
    if len(asset_ids) < 2:
        return None

    # pasangkan label -> index: 0 = YES, 1 = NO (konvensi Polymarket binary)
    yes_idx, no_idx = 0, 1
    for i, label in enumerate(outcomes):
        low = label.strip().lower()
        if low in ("yes", "y") and i < len(asset_ids):
            yes_idx = i
        elif low in ("no", "n") and i < len(asset_ids):
            no_idx = i

    events = raw.get("events") or []
    # event_raw (fetch penuh) diutamakan; fallback ke events[0] yang ter-embed di listing
    ev = event_raw or (events[0] if events and isinstance(events[0], dict) else {})
    trading = ev.get("trading") or {}
    neg_risk_augmented = bool(trading.get("negRiskAugmented")) or bool(ev.get("negRiskAugmented"))
    event_id = str(ev.get("id") or (events[0].get("id") if events and isinstance(events[0], dict) else "") or raw.get("eventId") or "")
    end_date = _parse_dt(raw.get("endDate")) or _parse_dt(ev.get("endDate"))

    try:
        tick = D(str(raw.get("orderPriceMinTickSize") or "0.01"))
        min_size = D(str(raw.get("orderMinSize") or "5"))
    except Exception:
        return None

    tags = raw.get("tags") or ev.get("tags") or []
    category = ""
    if tags and isinstance(tags, list):
        t0 = tags[0]
        category = str(t0.get("label") if isinstance(t0, dict) else t0)

    return MarketMeta(
        market_id=str(raw.get("id") or raw.get("conditionId")),
        slug=str(raw.get("slug") or ""),
        question=str(raw.get("question") or raw.get("title") or ""),
        condition_id=str(raw.get("conditionId") or ""),
        event_id=event_id,
        version=version,
        yes_asset_id=asset_ids[yes_idx],
        no_asset_id=asset_ids[no_idx],
        neg_risk=bool(raw.get("negRisk")) or bool(ev.get("enableNegRisk")),
        neg_risk_augmented=neg_risk_augmented,
        tick_size=tick,
        min_order_notional=min_size,
        fee_schedule=parse_fee_schedule(raw),
        end_date=end_date,
        category=category,
        resolution_criteria=str(raw.get("description") or ""),
        accepting_orders=bool(raw.get("acceptingOrders", True)),
        active=bool(raw.get("active", True)),
        closed=bool(raw.get("closed", False)),
        restricted=bool(raw.get("restricted", False)),
        enable_order_book=bool(raw.get("enableOrderBook", True)),
        volume_24h=D(str(raw["volume24hr"])) if raw.get("volume24hr") is not None else None,
        liquidity=D(str(raw["liquidity"])) if raw.get("liquidity") is not None else None,
    )


class GammaClient:
    def __init__(self, http: HttpClient, base_url: str) -> None:
        self.http = http
        self.base = base_url.rstrip("/")

    async def iter_markets(self, *, closed: bool = False, page_size: int = 100, max_markets: int = 0) -> AsyncIterator[dict]:
        """Paginasi penuh GET /markets. Yield raw market dict."""
        offset = 0
        yielded = 0
        while True:
            params = {"closed": str(closed).lower(), "limit": page_size, "offset": offset}
            data = await self.http.get_json(
                f"{self.base}/markets", params=params, limiter=LIMITS["gamma_markets"]
            )
            batch = data if isinstance(data, list) else (data.get("data") or data.get("markets") or [])
            if not batch:
                break
            for item in batch:
                yield item
                yielded += 1
                if max_markets and yielded >= max_markets:
                    return
            if len(batch) < page_size:
                break
            offset += page_size

    async def iter_markets_keyset(self, *, closed: bool = False, page_size: int = 100, max_markets: int = 0) -> AsyncIterator[dict]:
        """Alternatif cursor: GET /markets/keyset (bila tersedia)."""
        cursor: Optional[str] = None
        yielded = 0
        while True:
            params: dict = {"closed": str(closed).lower(), "limit": page_size}
            if cursor:
                params["next_cursor"] = cursor
            data = await self.http.get_json(
                f"{self.base}/markets/keyset", params=params, limiter=LIMITS["gamma_markets"]
            )
            batch = data.get("data") or []
            if not batch:
                break
            for item in batch:
                yield item
                yielded += 1
                if max_markets and yielded >= max_markets:
                    return
            cursor = data.get("next_cursor")
            if not cursor or cursor == "LTE=":  # END_CURSOR
                break

    async def get_event(self, event_id: str) -> dict:
        return await self.http.get_json(
            f"{self.base}/events/{event_id}", limiter=LIMITS["gamma_events"]
        )

    async def discover_all(
        self,
        *,
        closed: bool = False,
        page_size: int = 100,
        max_markets: int = 0,
        skip_if_missing_fee: bool = True,
        fetch_events_for_neg_risk: bool = True,
    ) -> tuple[dict[str, MarketMeta], dict]:
        """Discovery penuh -> ({market_id: MarketMeta}, statistik skip)."""
        out: dict[str, MarketMeta] = {}
        stats = {"raw": 0, "parsed": 0, "skipped": 0, "skip_reasons": {}}
        event_cache: dict[str, dict] = {}

        def skip(reason: str) -> None:
            stats["skipped"] += 1
            stats["skip_reasons"][reason] = stats["skip_reasons"].get(reason, 0) + 1

        async for raw in self.iter_markets(closed=closed, page_size=page_size, max_markets=max_markets):
            stats["raw"] += 1
            event_raw = None
            if fetch_events_for_neg_risk:
                events = raw.get("events") or []
                if events and isinstance(events[0], dict) and events[0].get("id"):
                    eid = str(events[0]["id"])
                    if eid not in event_cache:
                        try:
                            event_cache[eid] = await self.get_event(eid)
                        except Exception as exc:  # event gagal -> lanjut tanpa augment flag
                            log.debug("fetch event %s failed: %s", eid, exc)
                            event_cache[eid] = {}
                    event_raw = event_cache[eid]

            meta = parse_market(raw, event_raw=event_raw)
            if meta is None:
                skip("parse_failed")
                continue
            if not meta.tradeable:
                skip("not_tradeable")
                continue
            if meta.restricted:
                skip("restricted_geo")
                continue
            if skip_if_missing_fee and not meta.fee_schedule.available:
                skip("fee_unknown")
                continue
            out[meta.market_id] = meta
            stats["parsed"] += 1

        return out, stats
