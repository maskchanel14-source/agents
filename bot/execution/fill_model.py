"""Model probabilitas terisi (fill probability) — paper trading realistis (misi §3b)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ..decimal_utils import D, ONE, ZERO, dec_max, dec_min
from ..models import OrderBookSnapshot, WalkFill


@dataclass
class FillModelConfig:
    base_fill_prob: Decimal = D("0.95")
    depth_penalty: Decimal = D("0.5")
    staleness_penalty_per_ms: Decimal = D("0.0002")
    latency_penalty_per_ms: Decimal = D("0.00005")
    min_fill_prob: Decimal = D("0.05")
    latency_ms: int = 350

    @staticmethod
    def from_config(cfg: dict, latency_ms: int = 350) -> "FillModelConfig":
        return FillModelConfig(
            base_fill_prob=D(str(cfg.get("base_fill_prob", "0.95"))),
            depth_penalty=D(str(cfg.get("depth_penalty", "0.5"))),
            staleness_penalty_per_ms=D(str(cfg.get("staleness_penalty_per_ms", "0.0002"))),
            latency_penalty_per_ms=D(str(cfg.get("latency_penalty_per_ms", "0.00005"))),
            min_fill_prob=D(str(cfg.get("min_fill_prob", "0.05"))),
            latency_ms=latency_ms,
        )


class FillModel:
    def __init__(self, cfg: FillModelConfig | None = None) -> None:
        self.cfg = cfg or FillModelConfig()

    def leg_fill_probability(self, book: OrderBookSnapshot, walk: WalkFill, now_ms: int | None = None) -> Decimal:
        """Estimasi peluang satu leg terisi penuh, dengan asumsi latency order."""
        top = book.asks[0].size if book.asks else ZERO  # sisi yang kita sentuh (buy)
        if walk.requested_shares <= ZERO:
            return ZERO
        depth_frac = dec_min(ONE, walk.requested_shares / top) if top > ZERO else ONE
        p = self.cfg.base_fill_prob - self.cfg.depth_penalty * depth_frac
        p -= self.cfg.staleness_penalty_per_ms * D(book.age_ms(now_ms))
        p -= self.cfg.latency_penalty_per_ms * D(self.cfg.latency_ms)
        return dec_max(self.cfg.min_fill_prob, dec_min(ONE, p))

    def bundle_fill_probability(self, books_and_walks, now_ms: int | None = None) -> Decimal:
        """Semua leg harus terisi (FOK) — kalikan prob per leg (konservatif)."""
        p = ONE
        for book, walk in books_and_walks:
            p *= self.leg_fill_probability(book, walk, now_ms)
        return dec_max(self.cfg.min_fill_prob, p)

    def simulate_partial(self, walk: WalkFill, p: Decimal, rng) -> WalkFill:
        """Simulasi partial fill realistis: dengan prob (1-p) sebagian tidak terisi.

        Digunakan paper executor agar PnL simulasi tidak optimis.
        """
        if rng.random() < float(p):
            return walk
        # gagal penuh: hanya terisi fraksi (0..1) dari yang diminta
        frac = D(str(round(rng.uniform(0.0, 1.0), 4)))
        filled = walk.filled_shares * frac
        notional = walk.avg_price * filled
        return WalkFill(
            requested_shares=walk.requested_shares,
            filled_shares=filled,
            notional=notional,
            avg_price=walk.avg_price,
            levels_used=((walk.avg_price, filled),) if filled > ZERO else (),
            fully_filled=False,
        )
