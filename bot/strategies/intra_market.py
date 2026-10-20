"""Strategi A — intra-market binary arbitrage.

A1 (buy pair):  beli ask YES + ask NO; payout pasti $1 per pasang
                (exit: merge ke pUSD atau hold ke resolusi — pilih yang lebih murah).
A2 (mint&sell): split 1 pUSD -> YES+NO, jual keduanya di BID; untung jika
                bid_YES + bid_NO > 1 + fee + gas.

Pakai ASK/BID orderbook, bukan last price/midpoint (misi §3A).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from ..costs import BundleRequest, LegInput
from ..data.feed import MarketDataHub
from ..decimal_utils import D, ONE, ZERO
from ..models import Opportunity, Side
from .base import Strategy

log = logging.getLogger("bot.strategies.intra")


class IntraMarketBinary(Strategy):
    name = "A_intra_binary"

    def scan(self, hub: MarketDataHub, now_ms: Optional[int] = None) -> list[Opportunity]:
        out: list[Opportunity] = []
        for meta in hub.markets.values():
            if not meta.tradeable or meta.restricted:
                continue
            if not meta.fee_schedule.available:
                # fail-closed: fee tidak diketahui -> market dilewati;
                # coverage/skip stats mencatat alasannya di lapisan scanner
                continue
            yes_book = hub.get_book(meta.yes_asset_id)
            no_book = hub.get_book(meta.no_asset_id)
            if yes_book is None or no_book is None:
                continue

            # ---- filter murah: gross top-of-book harus positif ----
            yes_ask = yes_book.best_ask
            no_ask = no_book.best_ask
            if yes_ask is not None and no_ask is not None:
                gross = ONE - (yes_ask.price + no_ask.price)
                if gross > ZERO:
                    out.extend(self._eval_buy_pair(hub, meta, yes_book, no_book, now_ms))
            # ---- A2: mint & sell ----
            yes_bid = yes_book.best_bid
            no_bid = no_book.best_bid
            if yes_bid is not None and no_bid is not None:
                gross_sell = (yes_bid.price + no_bid.price) - ONE
                if gross_sell > ZERO:
                    out.extend(self._eval_mint_sell(hub, meta, yes_book, no_book, now_ms))
        return out

    # -- A1 -----------------------------------------------------------------

    def _eval_buy_pair(self, hub, meta, yes_book, no_book, now_ms) -> list[Opportunity]:
        hours_to_end = self._hours_to_end(meta, now_ms)
        results = []

        # jalur merge: modal kembali cepat, kena gas merge
        req_merge = BundleRequest(
            strategy=self.name,
            legs=[
                LegInput(market=meta, asset_id=meta.yes_asset_id, side=Side.BUY, book=yes_book, label="YES"),
                LegInput(market=meta, asset_id=meta.no_asset_id, side=Side.BUY, book=no_book, label="NO"),
            ],
            fixed_payout_per_bundle=ONE,
            exit_hours=self.cost_model.cfg.exit_hours_merge,
            gas_op="merge",
            gas_op_count_per_bundle=ONE,
            event_id=meta.event_id,
            opportunity_id=f"{self.name}-{meta.market_id}-merge",
            meta={"exit_mode": "merge", "market": meta.market_id},
        )
        results.append(self.cost_model.evaluate(req_merge, now_ms=now_ms).opportunity)

        # jalur hold ke resolusi: tanpa gas merge, kena gas redeem + waktu kunci
        req_hold = BundleRequest(
            strategy=self.name,
            legs=[
                LegInput(market=meta, asset_id=meta.yes_asset_id, side=Side.BUY, book=yes_book, label="YES"),
                LegInput(market=meta, asset_id=meta.no_asset_id, side=Side.BUY, book=no_book, label="NO"),
            ],
            fixed_payout_per_bundle=ONE,
            exit_hours=hours_to_end,
            gas_op="redeem",
            gas_op_count_per_bundle=ONE,
            event_id=meta.event_id,
            opportunity_id=f"{self.name}-{meta.market_id}-hold",
            meta={"exit_mode": "resolution", "market": meta.market_id},
        )
        results.append(self.cost_model.evaluate(req_hold, now_ms=now_ms).opportunity)

        # dedup: jika keduanya valid, simpan yang net terbaik; jika tidak, simpan
        # yang paling mendekati valid (untuk statistik) — keduanya tetap dicatat
        # oleh scanner (semua peluang masuk SQLite).
        return results

    # -- A2 -----------------------------------------------------------------

    def _eval_mint_sell(self, hub, meta, yes_book, no_book, now_ms) -> list[Opportunity]:
        req = BundleRequest(
            strategy=self.name + "_sell",
            legs=[
                LegInput(market=meta, asset_id=meta.yes_asset_id, side=Side.SELL, book=yes_book, label="YES"),
                LegInput(market=meta, asset_id=meta.no_asset_id, side=Side.SELL, book=no_book, label="NO"),
            ],
            fixed_payout_per_bundle=ZERO,
            collateral_consumed_per_bundle=ONE,
            exit_hours=self.cost_model.cfg.exit_hours_immediate,
            gas_op="split",
            gas_op_count_per_bundle=ONE,
            event_id=meta.event_id,
            opportunity_id=f"{self.name}-{meta.market_id}-mint_sell",
            meta={"exit_mode": "mint_sell", "market": meta.market_id},
        )
        return [self.cost_model.evaluate(req, now_ms=now_ms).opportunity]

    def _hours_to_end(self, meta, now_ms: Optional[int]) -> Decimal:
        if meta.end_date is None:
            return D("24")  # default konservatif 1 hari
        now = datetime.now(timezone.utc) if now_ms is None else datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
        delta = meta.end_date - now
        hours = D(str(max(delta.total_seconds(), 3600.0))) / D("3600")
        return hours
