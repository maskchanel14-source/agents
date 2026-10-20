"""Strategi C — cross-market logis (GATED, default OFF).

Aturan misi §3C: hanya aktif jika presisi bisa DIJAMIN. Implementasi ini hanya
mendeteksi peluang untuk pasangan market dengan **kriteria resolusi identik
literal** (teks resolusi ternormalisasi sama persis + endDate sejalan), karena
hanya untuk kasus itu payoff identik bisa dibuktikan:

    market A & B resolusi identik ->
    beli YES_A (ask) + split B & jual YES_B (bid), simpan NO_B ->
    payoff selalu $1 tidak peduli hasilnya; profit = bid_B - ask_A - fee - gas.

Setiap keraguan (teks beda, tanggal beda, "Other", dsb.) -> SKIP.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Optional

from ..costs import BundleRequest, LegInput
from ..data.feed import MarketDataHub
from ..decimal_utils import D, ONE
from ..models import MarketMeta, Opportunity, Side
from .base import Strategy

log = logging.getLogger("bot.strategies.cross_market")

_PUNCT_RE = re.compile(r"[^a-z0-9\s]")


def normalize_criteria(text: str) -> str:
    t = text.strip().lower()
    t = _PUNCT_RE.sub(" ", t)
    return " ".join(t.split())


class CrossMarketLogical(Strategy):
    name = "C_cross_market"

    def scan(self, hub: MarketDataHub, now_ms: Optional[int] = None) -> list[Opportunity]:
        if not self.enabled:
            return []
        min_similarity = D(str(self.config.get("min_resolution_text_similarity", "0.9")))
        out: list[Opportunity] = []

        # kelompokkan berdasarkan kriteria resolusi ternormalisasi + tanggal
        groups: dict[str, list[MarketMeta]] = defaultdict(list)
        for meta in hub.markets.values():
            if not meta.tradeable or not meta.fee_schedule.available:
                continue
            if not meta.resolution_criteria or meta.end_date is None:
                continue
            key = f"{normalize_criteria(meta.resolution_criteria)}|{meta.end_date.date().isoformat()}"
            groups[key].append(meta)

        for _key, members in groups.items():
            if len(members) < 2:
                continue
            # hanya pasangan dengan teks 100% identik (similarity = 1 >= threshold)
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    if normalize_criteria(a.resolution_criteria) != normalize_criteria(b.resolution_criteria):
                        continue  # ragu -> skip
                    if D("1") < min_similarity:
                        continue
                    out.extend(self._eval_identical_pair(hub, a, b, now_ms))
        return out

    def _eval_identical_pair(self, hub, a: MarketMeta, b: MarketMeta, now_ms) -> list[Opportunity]:
        out: list[Opportunity] = []
        pairs = [
            (a, b, "A_cheap"),
            (b, a, "B_cheap"),
        ]
        for cheap, rich, tag in pairs:
            cheap_book = hub.get_book(cheap.yes_asset_id)
            rich_book = hub.get_book(rich.yes_asset_id)
            if cheap_book is None or rich_book is None:
                continue
            ask = cheap_book.best_ask
            bid = rich_book.best_bid
            if ask is None or bid is None:
                continue
            if bid.price <= ask.price:
                continue  # filter murah: tidak ada dislokasi
            req = BundleRequest(
                strategy=self.name,
                legs=[
                    LegInput(market=cheap, asset_id=cheap.yes_asset_id, side=Side.BUY,
                             book=cheap_book, label=f"YES:{cheap.slug[:20]}"),
                    LegInput(market=rich, asset_id=rich.yes_asset_id, side=Side.SELL,
                             book=rich_book, label=f"YES:{rich.slug[:20]}"),
                ],
                fixed_payout_per_bundle=ONE,
                collateral_consumed_per_bundle=ONE,
                exit_hours=self._hours_to_end(cheap, now_ms),
                gas_op="split",
                gas_op_count_per_bundle=ONE,
                event_id=cheap.event_id or rich.event_id,
                opportunity_id=f"{self.name}-{cheap.market_id}-{rich.market_id}-{tag}",
                meta={"variant": "identical_criteria", "cheap": cheap.market_id, "rich": rich.market_id},
            )
            out.append(self.cost_model.evaluate(req, now_ms=now_ms).opportunity)
        return out

    def _hours_to_end(self, meta, now_ms: Optional[int]) -> D:
        from datetime import datetime, timezone
        if meta.end_date is None:
            return D("24")
        now = datetime.now(timezone.utc) if now_ms is None else datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
        delta = meta.end_date - now
        return D(str(max(delta.total_seconds(), 3600.0))) / D("3600")
