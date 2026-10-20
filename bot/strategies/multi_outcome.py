"""Strategi B — multi-outcome / neg-risk (misi §3B).

B1      : Σ ask YES semua outcome < $1 (setelah semua biaya) -> beli semua leg,
          payout pasti $1 (tepat satu YES menang) — hanya untuk event yang
          mutually exclusive & exhaustive.
B-no    : Σ ask NO semua outcome < $(n-1) -> beli semua NO; payout n-1.
B2      : konversi neg-risk: beli NO_i (ask) + konversi -> jual YES_j≠i (bid);
          untung jika Σ bid YES_j≠i > ask NO_i + fee + gas convert.

Validasi wajib: flag negRisk, exhaustiveness (deteksi outcome "Other"/placeholder
-> skip atau haircut), hanya named outcomes (augmented neg risk).
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from ..costs import BundleRequest, LegInput
from ..data.feed import MarketDataHub
from ..decimal_utils import D, ONE, ZERO
from ..models import MarketMeta, Opportunity, Side
from .base import Strategy

log = logging.getLogger("bot.strategies.multi")

_OTHER_RE = re.compile(r"\b(other|anyone else|others|else|tbd|placeholder|another)\b", re.I)


def looks_like_other_outcome(meta: MarketMeta) -> bool:
    """Heuristik konservatif: outcome 'Other'/placeholder -> tidak boleh diandalkan."""
    text = f"{meta.slug} {meta.question}"
    return bool(_OTHER_RE.search(text))


class MultiOutcomeNegRisk(Strategy):
    name = "B_multi_outcome"

    def scan(self, hub: MarketDataHub, now_ms: Optional[int] = None) -> list[Opportunity]:
        out: list[Opportunity] = []
        by_event: dict[str, list[MarketMeta]] = defaultdict(list)
        for meta in hub.markets.values():
            if meta.event_id:
                by_event[meta.event_id].append(meta)

        require_exhaustive = bool(self.config.get("require_exhaustive", True))
        augmented_mode = str(self.config.get("augmented_neg_risk", "named_only"))

        for event_id, members in by_event.items():
            if len(members) < 2:
                continue
            members = [m for m in members if m.tradeable and not m.restricted]
            if len(members) < 2:
                continue

            # ---- validasi mutual exclusivity ----
            all_neg_risk = all(m.neg_risk for m in members)
            if not all_neg_risk:
                # tanpa neg-risk tidak ada jaminan eksklusif -> skip (akurasi dulu)
                continue

            # ---- validasi exhaustiveness / outcome tak jelas ----
            has_other = any(looks_like_other_outcome(m) for m in members)
            augmented = any(m.neg_risk_augmented for m in members)
            if has_other and require_exhaustive:
                continue  # outcome "Other" -> risiko payout < $1, skip
            ambiguous = has_other or (augmented and augmented_mode != "named_only")

            # pastikan semua leg punya book & fee
            legs_books = {}
            ok = True
            for m in members:
                yb, nb = hub.get_book(m.yes_asset_id), hub.get_book(m.no_asset_id)
                if yb is None or nb is None or not m.fee_schedule.available:
                    ok = False
                    break
                legs_books[m.market_id] = (yb, nb)
            if not ok:
                continue

            out.extend(self._eval_buy_all_yes(members, legs_books, now_ms, ambiguous))
            out.extend(self._eval_buy_all_no(members, legs_books, now_ms, ambiguous))
            if all_neg_risk:
                out.extend(self._eval_conversion(members, legs_books, now_ms, ambiguous))
        return out

    # -- B1: beli semua YES --------------------------------------------------

    def _eval_buy_all_yes(self, members, legs_books, now_ms, ambiguous) -> list[Opportunity]:
        naive = ZERO
        for m in members:
            ask = legs_books[m.market_id][0].best_ask
            if ask is None:
                return []
            naive += ask.price
        if naive >= ONE:
            return []  # filter murah

        exit_hours = self._hours_to_event_end(members, now_ms)
        req = BundleRequest(
            strategy=self.name,
            legs=[
                LegInput(market=m, asset_id=m.yes_asset_id, side=Side.BUY,
                         book=legs_books[m.market_id][0], label=f"YES:{m.slug[:24]}")
                for m in members
            ],
            fixed_payout_per_bundle=ONE,
            exit_hours=exit_hours,
            gas_op="redeem",
            gas_op_count_per_bundle=ONE,
            event_id=members[0].event_id,
            opportunity_id=f"{self.name}-{members[0].event_id}-allyes",
            meta={"variant": "buy_all_yes", "outcomes": len(members), "ambiguous": ambiguous},
        )
        req.ambiguous_resolution = ambiguous
        return [self.cost_model.evaluate(req, now_ms=now_ms).opportunity]

    # -- B-no: beli semua NO -------------------------------------------------

    def _eval_buy_all_no(self, members, legs_books, now_ms, ambiguous) -> list[Opportunity]:
        n = D(len(members))
        payout = n - ONE  # tepat satu YES menang -> n-1 NO menang
        naive = ZERO
        for m in members:
            ask = legs_books[m.market_id][1].best_ask
            if ask is None:
                return []
            naive += ask.price
        if naive >= payout:
            return []

        req = BundleRequest(
            strategy=self.name + "_no",
            legs=[
                LegInput(market=m, asset_id=m.no_asset_id, side=Side.BUY,
                         book=legs_books[m.market_id][1], label=f"NO:{m.slug[:24]}")
                for m in members
            ],
            fixed_payout_per_bundle=payout,
            exit_hours=self._hours_to_event_end(members, now_ms),
            gas_op="redeem",
            gas_op_count_per_bundle=n,
            event_id=members[0].event_id,
            opportunity_id=f"{self.name}-{members[0].event_id}-allno",
            meta={"variant": "buy_all_no", "outcomes": len(members), "ambiguous": ambiguous},
        )
        req.ambiguous_resolution = ambiguous
        return [self.cost_model.evaluate(req, now_ms=now_ms).opportunity]

    # -- B2: konversi neg-risk ----------------------------------------------

    def _eval_conversion(self, members, legs_books, now_ms, ambiguous) -> list[Opportunity]:
        out: list[Opportunity] = []
        for i, m_i in enumerate(members):
            no_book = legs_books[m_i.market_id][1]
            ask_no = no_book.best_ask
            if ask_no is None:
                continue
            # pendapatan hasil konversi & jual YES di market lain
            naive_sell = ZERO
            sell_ok = True
            for j, m_j in enumerate(members):
                if j == i:
                    continue
                bid = legs_books[m_j.market_id][0].best_bid
                if bid is None:
                    sell_ok = False
                    break
                naive_sell += bid.price
            if not sell_ok:
                continue
            if naive_sell <= ask_no.price:
                continue  # filter murah

            req = BundleRequest(
                strategy=self.name + "_convert",
                legs=[
                    LegInput(market=m_i, asset_id=m_i.no_asset_id, side=Side.BUY,
                             book=no_book, label=f"NO:{m_i.slug[:24]}"),
                ]
                + [
                    LegInput(market=m_j, asset_id=m_j.yes_asset_id, side=Side.SELL,
                             book=legs_books[m_j.market_id][0], label=f"YES:{m_j.slug[:24]}")
                    for j, m_j in enumerate(members)
                    if j != i
                ],
                fixed_payout_per_bundle=ZERO,
                collateral_consumed_per_bundle=ZERO,
                exit_hours=self.cost_model.cfg.exit_hours_immediate,
                gas_op="convert_neg_risk",
                gas_op_count_per_bundle=ONE,
                event_id=m_i.event_id,
                opportunity_id=f"{self.name}-{m_i.event_id}-convert-{m_i.market_id}",
                meta={"variant": "neg_risk_convert", "convert_from": m_i.market_id, "ambiguous": ambiguous},
            )
            req.ambiguous_resolution = ambiguous
            out.append(self.cost_model.evaluate(req, now_ms=now_ms).opportunity)
        return out

    def _hours_to_event_end(self, members, now_ms: Optional[int]) -> Decimal:
        """Modal terkunci sampai outcome terakhir resolve (konservatif)."""
        now = datetime.now(timezone.utc) if now_ms is None else datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
        hours = D("24")
        for m in members:
            if m.end_date is not None:
                delta = m.end_date - now
                h = D(str(max(delta.total_seconds(), 3600.0))) / D("3600")
                if h > hours:
                    hours = h
        return hours
