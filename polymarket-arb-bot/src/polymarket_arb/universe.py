"""Build the tradable universe from Gamma events: binary markets and neg-risk groups."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from .domain import EventGroup, MarketInfo
from .markets import parse_event_groups_safe, parse_market


@dataclass
class Universe:
    binaries: list[MarketInfo] = field(default_factory=list)
    groups: list[EventGroup] = field(default_factory=list)
    skipped: Counter = field(default_factory=Counter)

    @property
    def assets(self) -> list[str]:
        seen: dict[str, None] = {}
        for m in self.binaries:
            seen[m.yes.asset_id] = None
            seen[m.no.asset_id] = None
        for g in self.groups:
            for m in g.markets:
                seen[m.yes.asset_id] = None
                seen[m.no.asset_id] = None
        return list(seen)

    def markets_by_asset(self) -> dict[str, MarketInfo]:
        out: dict[str, MarketInfo] = {}
        for m in self.binaries:
            out[m.yes.asset_id] = m
            out[m.no.asset_id] = m
        for g in self.groups:
            for m in g.markets:
                out[m.yes.asset_id] = m
                out[m.no.asset_id] = m
        return out


def build_universe(
    events: list[dict[str, Any]],
    max_assets: int | None = None,
    *,
    exclude_ambiguous: bool = True,
    blacklist_condition_ids: Iterable[str] = (),
) -> Universe:
    uni = Universe()
    seen: set[str] = set()
    blacklist = {c.lower() for c in blacklist_condition_ids}
    for ev in events:
        for raw in ev.get("markets") or []:
            cid = str(raw.get("conditionId") or "")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            try:
                m = parse_market(raw, event_meta=ev)
            except (ValueError, KeyError, TypeError):
                uni.skipped["unparseable_market"] += 1
                continue
            if m.closed or not m.active:
                uni.skipped["inactive"] += 1
                continue
            if cid.lower() in blacklist:
                uni.skipped["blacklisted"] += 1
                continue
            if exclude_ambiguous and m.ambiguous_resolution:
                uni.skipped["ambiguous_resolution"] += 1
                continue
            uni.binaries.append(m)
    uni.groups = [g for g in parse_event_groups_safe(events) if g.neg_risk]
    # neg-risk groups: drop any group containing a blacklisted/ambiguous market
    kept_groups = []
    for g in uni.groups:
        bad = [
            m
            for m in g.markets
            if m.condition_id.lower() in blacklist or (exclude_ambiguous and m.ambiguous_resolution)
        ]
        if bad:
            uni.skipped["group_blacklisted_or_ambiguous"] += 1
            continue
        kept_groups.append(g)
    uni.groups = kept_groups
    if max_assets is not None:
        _cap_assets(uni, max_assets)
    return uni


def _cap_assets(uni: Universe, max_assets: int) -> None:
    """Keep the most liquid markets so the subscription stays within budget."""

    def liq(raw_liq: Any) -> float:
        try:
            return float(raw_liq or 0)
        except (TypeError, ValueError):
            return 0.0

    keep = sorted(uni.binaries, key=lambda m: -liq(m.extra.get("liquidity")))
    kept: list[MarketInfo] = []
    budget = max_assets
    for m in keep:
        if budget < 2:
            break
        kept.append(m)
        budget -= 2
    uni.binaries = kept
    kept_groups: list[EventGroup] = []
    for g in uni.groups:
        if budget < 2 * len(g.markets):
            uni.skipped["group_over_asset_budget"] += 1
            continue
        kept_groups.append(g)
        budget -= 2 * len(g.markets)
    uni.groups = kept_groups
