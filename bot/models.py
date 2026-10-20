"""Model data inti — semua harga/ukuran/uang bertipe Decimal."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, Sequence

from .decimal_utils import ONE, ZERO, D


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class RejectReason(str, Enum):
    """Alasan penolakan peluang (dipakai untuk statistik funnel & dashboard)."""

    OK = "ok"
    FEE_UNKNOWN = "fee_unknown"
    STALE_DATA = "stale_data"
    THIN_BOOK = "thin_book"
    BELOW_MIN_ORDER = "below_min_order"
    GROSS_NOT_POSITIVE = "gross_not_positive"
    NET_NOT_POSITIVE = "net_not_positive"
    BELOW_SAFETY_MARGIN = "below_safety_margin"
    ANNUALIZED_TOO_LOW = "annualized_too_low"
    CAPITAL_CAP = "capital_cap"
    RISK_LIMIT = "risk_limit"
    AMBIGUOUS_RESOLUTION = "ambiguous_resolution"
    NON_EXHAUSTIVE_EVENT = "non_exhaustive_event"
    UNSUPPORTED_MARKET = "unsupported_market"
    DUPLICATE = "duplicate"
    INVALID_INPUT = "invalid_input"


@dataclass(frozen=True)
class FeeSchedule:
    """Parameter fee per market (Gamma `feeSchedule`)."""

    fees_enabled: bool
    rate: Decimal
    exponent: Decimal
    taker_only: bool
    rebate_rate: Decimal
    source: str = "gamma"        # gamma | assumed | missing
    fetched_at: Optional[float] = None

    @property
    def available(self) -> bool:
        return self.source != "missing"

    @staticmethod
    def missing() -> "FeeSchedule":
        return FeeSchedule(
            fees_enabled=False,
            rate=ZERO,
            exponent=ONE,
            taker_only=True,
            rebate_rate=ZERO,
            source="missing",
        )


@dataclass(frozen=True)
class MarketMeta:
    """Metadata market dari Gamma (lihat docs/POLYMARKET_NOTES.md §2)."""

    market_id: str
    slug: str
    question: str
    condition_id: str
    event_id: str
    version: str                 # "v1" (CTF) | "v2"
    yes_asset_id: str
    no_asset_id: str
    neg_risk: bool
    neg_risk_augmented: bool
    tick_size: Decimal
    min_order_notional: Decimal  # USDC, dari `orderMinSize`
    fee_schedule: FeeSchedule
    end_date: Optional[datetime]
    category: str = ""
    resolution_criteria: str = ""
    accepting_orders: bool = True
    active: bool = True
    closed: bool = False
    restricted: bool = False
    enable_order_book: bool = True
    volume_24h: Optional[Decimal] = None
    liquidity: Optional[Decimal] = None

    @property
    def tradeable(self) -> bool:
        return (
            self.active
            and not self.closed
            and self.accepting_orders
            and self.enable_order_book
            and self.version in ("v1", "v2")
        )

    @property
    def asset_ids(self) -> tuple[str, str]:
        return (self.yes_asset_id, self.no_asset_id)


@dataclass(frozen=True)
class BookLevel:
    price: Decimal
    size: Decimal


@dataclass(frozen=True)
class OrderBookSnapshot:
    """Snapshot orderbook TERNORMALISASI.

    `bids`: best bid PERTAMA (harga menurun); `asks`: best ask PERTAMA (harga naik).
    Urutan mentah dari API TIDAK diandalkan (REST vs WS bisa beda) — sortir saat parse.
    """

    asset_id: str
    bids: tuple[BookLevel, ...]
    asks: tuple[BookLevel, ...]
    ts_ms: int                   # timestamp dari exchange (epoch ms), 0 bila tidak ada
    recv_ms: int                 # waktu lokal terima (epoch ms)
    hash: Optional[str] = None
    tick_size: Optional[Decimal] = None
    min_order_size: Optional[Decimal] = None
    neg_risk: Optional[bool] = None
    last_trade_price: Optional[Decimal] = None

    @staticmethod
    def from_levels(
        asset_id: str,
        bids: Sequence[tuple],
        asks: Sequence[tuple],
        ts_ms: int = 0,
        recv_ms: Optional[int] = None,
        hash: Optional[str] = None,
        tick_size: Optional[Decimal] = None,
        min_order_size: Optional[Decimal] = None,
        neg_risk: Optional[bool] = None,
        last_trade_price: Optional[Decimal] = None,
    ) -> "OrderBookSnapshot":
        def norm(levels: Sequence[tuple], reverse: bool) -> tuple[BookLevel, ...]:
            parsed = [
                BookLevel(price=D(p), size=D(s))
                for p, s in levels
                if D(s) > ZERO and ZERO <= D(p) <= ONE
            ]
            parsed.sort(key=lambda lv: lv.price, reverse=reverse)
            return tuple(parsed)

        return OrderBookSnapshot(
            asset_id=asset_id,
            bids=norm(bids, reverse=True),   # best bid dulu
            asks=norm(asks, reverse=False),  # best ask dulu
            ts_ms=ts_ms,
            recv_ms=recv_ms if recv_ms is not None else int(time.time() * 1000),
            hash=hash,
            tick_size=tick_size,
            min_order_size=min_order_size,
            neg_risk=neg_risk,
            last_trade_price=last_trade_price,
        )

    @property
    def best_bid(self) -> Optional[BookLevel]:
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> Optional[BookLevel]:
        return self.asks[0] if self.asks else None

    def age_ms(self, now_ms: Optional[int] = None) -> int:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        return max(0, now - self.recv_ms)

    def is_stale(self, max_age_ms: int, now_ms: Optional[int] = None) -> bool:
        return self.age_ms(now_ms) > max_age_ms


@dataclass(frozen=True)
class WalkFill:
    """Hasil walk-the-book untuk satu leg."""

    requested_shares: Decimal
    filled_shares: Decimal
    notional: Decimal             # USD yang dibayar (sebelum fee)
    avg_price: Decimal            # notional / filled_shares (0 bila tidak terisi)
    levels_used: tuple[tuple[Decimal, Decimal], ...]  # (price, shares) per level
    fully_filled: bool

    @property
    def shortfall_shares(self) -> Decimal:
        return self.requested_shares - self.filled_shares


@dataclass
class LegPlan:
    """Rencana satu leg eksekusi (satu asset, satu sisi)."""

    asset_id: str
    market_id: str
    side: Side
    shares: Decimal
    limit_price: Decimal          # harga batas untuk order (paritas py-clob-client)
    walk: WalkFill
    fee: Decimal                  # taker fee leg ini
    gas: Decimal                  # gas on-chain terkait leg (biasanya 0 untuk CLOB)
    label: str = ""               # mis. "YES", "NO", "outcome:Trump"


@dataclass
class CostBreakdown:
    """Rincian biaya — output wajib tiap Opportunity (misi §4)."""

    gross_edge: Decimal = ZERO            # payout - Σ best-ask (naive, sebelum biaya)
    notional: Decimal = ZERO              # Σ harga × share semua leg (walk-the-book)
    trading_fees: Decimal = ZERO
    slippage_cost: Decimal = ZERO         # Σ (notional - best_ask × shares)
    gas_cost: Decimal = ZERO
    leg_risk_cost: Decimal = ZERO
    resolution_risk_cost: Decimal = ZERO
    rounding_cost: Decimal = ZERO
    safety_margin: Decimal = ZERO
    total_costs: Decimal = ZERO           # fees+slippage+gas+leg+resolution+rounding
    net_profit: Decimal = ZERO            # payout - notional - total_costs - safety
    net_profit_pct: Decimal = ZERO        # terhadap capital
    capital_required: Decimal = ZERO      # notional + fees + gas
    annualized_return: Decimal = ZERO     # net / capital × 365 / days
    days_to_resolution: Optional[Decimal] = None

    def as_dict(self) -> dict:
        out = {}
        for k, v in self.__dict__.items():
            out[k] = format(v, "f") if isinstance(v, Decimal) else v
        return out


@dataclass
class Opportunity:
    """Satu peluang arbitrase (valid maupun ditolak — semua dicatat ke SQLite)."""

    opportunity_id: str
    strategy: str                       # A_intra_binary | B_multi_outcome | ...
    market_ids: tuple[str, ...]
    event_id: Optional[str]
    legs: list[LegPlan]
    payout_per_bundle: Decimal          # pembayaran pasti per bundle (biasanya 1.00)
    bundle_size: Decimal                # jumlah bundle = jumlah share per leg
    cost: CostBreakdown
    valid: bool
    reject_reason: RejectReason
    reject_detail: str = ""
    confidence: Decimal = ZERO
    fill_probability: Decimal = ZERO
    expected_net_profit: Decimal = ZERO # net × fill_probability (untuk ranking)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    meta: dict = field(default_factory=dict)

    @property
    def net_profit(self) -> Decimal:
        return self.cost.net_profit

    @property
    def ranking_score(self) -> Decimal:
        """Peringkat: expected net profit, lalu annualized."""
        return self.expected_net_profit


@dataclass
class CoverageReport:
    """Metrik cakupan scanner (misi §3b)."""

    total_active_markets: int = 0
    markets_discovered: int = 0
    markets_monitored: int = 0
    markets_skipped: int = 0
    skip_reasons: dict = field(default_factory=dict)
    ws_connections: int = 0
    ws_subscribed_assets: int = 0
    stale_assets: int = 0
    last_full_scan_ms: int = 0

    def add_skip(self, reason: str) -> None:
        self.markets_skipped += 1
        self.skip_reasons[reason] = self.skip_reasons.get(reason, 0) + 1

    def as_dict(self) -> dict:
        return dict(self.__dict__)
