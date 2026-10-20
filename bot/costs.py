"""costs.py — SUMBER KEBENARAN TUNGGAL untuk SEMUA perhitungan biaya.

Prinsip (misi §4):
- Semua aritmetika uang dengan `Decimal` (BUKAN float).
- Fee mengikuti rumus resmi Polymarket: ``fee = C x feeRate x (p x (1 - p)) ** exponent``
  (exponent=1 persis rumus docs ``fee = C x feeRate x p x (1 - p)``; dibulatkan 5
  desimal, minimum 0.00001 USDC — lebih kecil dibulatkan jadi 0).
- Fee rate per market diambil dari API (Gamma ``feeSchedule``). Jika tidak tersedia
  -> peluang INVALID (fail-closed), tidak pernah berasumsi 0.
- Slippage memakai walk-the-book per level, bukan best price.
- Gas on-chain (approve/split/merge/redeem/convert) dimodelkan; eksekusi taker via
  CLOB tidak kena gas user (settlement oleh operator exchange).
- Pembulatan mengikuti ROUNDING_CONFIG resmi py-clob-client per tick size.

Sumber: docs/POLYMARKET_NOTES.md §5-6, docs/COST_MODEL.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from .decimal_utils import (
    ONE,
    ZERO,
    D,
    dec_max,
    dec_min,
    round_down,
    round_half_up,
    round_up,
)
from .models import (
    CostBreakdown,
    FeeSchedule,
    LegPlan,
    MarketMeta,
    Opportunity,
    OrderBookSnapshot,
    RejectReason,
    Side,
    WalkFill,
)

# ---------------------------------------------------------------------------
# Presisi pembulatan — paritas dengan py-clob-client ``ROUNDING_CONFIG``
# (tick -> {price decimals, size decimals, amount decimals}).
# ---------------------------------------------------------------------------
ROUNDING_CONFIG: dict[str, tuple[int, int, int]] = {
    "0.1": (1, 2, 3),
    "0.01": (2, 2, 4),
    "0.005": (3, 2, 5),
    "0.0025": (4, 2, 6),
    "0.001": (3, 2, 5),
    "0.0001": (4, 2, 6),
}

FEE_ROUNDING_PLACES = 5
FEE_MIN_USD = D("0.00001")
TOKEN_DECIMALS = 6  # encoding integer 6 desimal untuk makerAmount/takerAmount


def _tick_key(tick: Decimal) -> Optional[str]:
    s = format(tick.normalize(), "f")
    return s if s in ROUNDING_CONFIG else None


def rounding_for_tick(tick: Decimal) -> tuple[int, int, int]:
    key = _tick_key(tick)
    if key is None:
        # Tick tak dikenal (mis. 0.0025 lawas): default konservatif 2 desimal size.
        places = max(0, -tick.as_tuple().exponent)
        return (places, 2, 6)
    return ROUNDING_CONFIG[key]


# ---------------------------------------------------------------------------
# Fee
# ---------------------------------------------------------------------------

def taker_fee(
    shares: Decimal,
    price: Decimal,
    fee_schedule: FeeSchedule,
    *,
    exponent: Optional[Decimal] = None,
) -> Decimal:
    """Fee taker untuk trade `shares` pada `price`.

    fee = shares * rate * (price * (1 - price)) ** exponent
    Dibulatkan HALF_UP ke 5 desimal; hasil < 0.00001 -> 0 (per dokumen resmi).
    Maker tidak pernah kena fee — pemanggil memastikan sisi taker.
    """
    if shares <= ZERO or price <= ZERO or price >= ONE:
        raise ValueError("shares must be > 0 and price in (0, 1)")
    if not fee_schedule.available:
        raise ValueError("fee schedule missing — opportunity must be INVALID")
    if not fee_schedule.fees_enabled:
        return ZERO
    e = exponent if exponent is not None else fee_schedule.exponent
    price_component = (price * (ONE - price)) ** e
    raw = shares * fee_schedule.rate * price_component
    fee = round_half_up(raw, FEE_ROUNDING_PLACES)
    if fee < FEE_MIN_USD:
        return ZERO
    return fee


def fee_for_walk(walk: WalkFill, fee_schedule: FeeSchedule) -> Decimal:
    """Fee total untuk hasil walk-the-book (per level, lalu dijumlahkan)."""
    total = ZERO
    for price, shares in walk.levels_used:
        total += taker_fee(shares, price, fee_schedule)
    return total


# ---------------------------------------------------------------------------
# Walk-the-book
# ---------------------------------------------------------------------------

def walk_the_book(book: OrderBookSnapshot, side: Side, shares: Decimal) -> WalkFill:
    """Isi `shares` dari sisi orderbook yang benar (BUY=asks, SELL=bids).

    Level sudah ternormalisasi (best lebih dulu). Sisa yang tidak terisi
    dicatat sebagai shortfall (fully_filled=False).
    """
    if shares <= ZERO:
        raise ValueError("shares must be > 0")
    levels = book.asks if side == Side.BUY else book.bids
    remaining = shares
    filled = ZERO
    notional = ZERO
    used: list[tuple[Decimal, Decimal]] = []
    for lv in levels:
        if remaining <= ZERO:
            break
        take = dec_min(lv.size, remaining)
        used.append((lv.price, take))
        filled += take
        notional += take * lv.price
        remaining -= take
    avg = (notional / filled) if filled > ZERO else ZERO
    return WalkFill(
        requested_shares=shares,
        filled_shares=filled,
        notional=notional,
        avg_price=avg,
        levels_used=tuple(used),
        fully_filled=remaining <= ZERO,
    )


# ---------------------------------------------------------------------------
# Pembuatan order (paritas py-clob-client order_builder)
# ---------------------------------------------------------------------------

def round_order_amounts(
    side: Side, shares: Decimal, price: Decimal, tick: Decimal
) -> tuple[int, int]:
    """Return (maker_amount, taker_amount) sebagai integer 6 desimal.

    Aturan resmi (docs trading/place-orders + py-clob-client):
    1. harga dibulatkan normal ke price decimals;
    2. share dibulatkan TURUN ke size decimals;
    3. jumlah USD: jika desimal melebihi amount decimals -> bulatkan NAIK ke
       amount+4 dulu, lalu TURUN ke amount decimals;
    4. keduanya dikonversi ke integer 6 desimal.
    BUY:  maker = USD, taker = share. SELL: maker = share, taker = USD.
    """
    price_dec, size_dec, amount_dec = rounding_for_tick(tick)
    raw_price = round_half_up(price, price_dec)
    raw_shares = round_down(shares, size_dec)
    if raw_shares <= ZERO:
        raise ValueError("shares round to zero at size precision")
    usd = raw_shares * raw_price
    if _decimal_places(usd) > amount_dec:
        usd = round_up(usd, amount_dec + 4)
        if _decimal_places(usd) > amount_dec:
            usd = round_down(usd, amount_dec)

    def to_token_decimals(x: Decimal) -> int:
        scaled = x * Decimal(10) ** TOKEN_DECIMALS
        if _decimal_places(scaled) > 0:
            scaled = round_half_up(scaled, 0)
        return int(scaled)

    if side == Side.BUY:
        return to_token_decimals(usd), to_token_decimals(raw_shares)
    return to_token_decimals(raw_shares), to_token_decimals(usd)


def _decimal_places(x: Decimal) -> int:
    exp = x.normalize().as_tuple().exponent
    return abs(exp) if isinstance(exp, int) and exp < 0 else 0


# ---------------------------------------------------------------------------
# Gas
# ---------------------------------------------------------------------------

@dataclass
class GasModel:
    """Biaya gas Polygon untuk operasi on-chain user (bukan trading CLOB)."""

    enabled: bool = True
    gas_price_gwei: Decimal = D("100")
    pol_usd: Decimal = D("0.25")
    gas_units: dict = field(default_factory=lambda: {
        "approve": D("60000"),
        "split": D("150000"),
        "merge": D("150000"),
        "redeem": D("120000"),
        "convert_neg_risk": D("250000"),
    })
    amortize_approvals_over_trades: int = 20

    @staticmethod
    def from_config(cfg: dict) -> "GasModel":
        gu = {k: D(str(v)) for k, v in (cfg.get("gas_units") or {}).items()}
        model = GasModel(
            enabled=bool(cfg.get("enabled", True)),
            gas_price_gwei=D(str(cfg.get("gas_price_gwei_fallback", "100"))),
            pol_usd=D(str(cfg.get("pol_usd_fallback", "0.25"))),
            amortize_approvals_over_trades=int(cfg.get("amortize_approvals_over_trades", 20)),
        )
        if gu:
            model.gas_units.update(gu)
        return model

    def cost_usd(self, op: str) -> Decimal:
        if not self.enabled:
            return ZERO
        units = self.gas_units.get(op)
        if units is None:
            return ZERO
        return self._cost_for_units(units)

    def amortized_approval_cost(self) -> Decimal:
        """Biaya approval yang diamortisasi per trade (approvals jarang, bukan tiap order)."""
        if not self.enabled or self.amortize_approvals_over_trades <= 0:
            return ZERO
        approve = self._cost_for_units(self.gas_units.get("approve", ZERO))
        return approve / D(self.amortize_approvals_over_trades)

    def _cost_for_units(self, units: Decimal) -> Decimal:
        # gas_price_gwei * 1e9 (wei per gas) * units / 1e18 (POL) * pol_usd
        return (units * self.gas_price_gwei * D("1e-9")) * self.pol_usd


# ---------------------------------------------------------------------------
# Konfigurasi cost model
# ---------------------------------------------------------------------------

@dataclass
class CostConfig:
    safety_margin_usd: Decimal = D("0.005")
    safety_margin_pct: Decimal = ZERO
    min_net_profit_usd: Decimal = ZERO
    min_annualized_return: Decimal = D("0.15")
    leg_risk_haircut_pct: Decimal = D("0.002")
    latency_ms: int = 350
    max_book_age_ms: int = 3000
    resolution_haircut_pct_per_day: Decimal = D("0.0002")
    resolution_haircut_ambiguous_pct: Decimal = D("0.01")
    min_exit_hours: Decimal = D("1")          # floor untuk annualization (operasional)
    exit_hours_merge: Decimal = D("2")        # merge path: ±2 jam operasional
    exit_hours_immediate: Decimal = D("1")    # mint&sell: beberapa menit -> floor 1 jam
    max_capital_per_trade_usd: Decimal = D("50")
    default_exit_hours: Optional[Decimal] = None

    @staticmethod
    def from_config(cfg: dict, risk_cfg: Optional[dict] = None) -> "CostConfig":
        c = CostConfig()
        c.safety_margin_usd = D(str(cfg.get("safety_margin_usd", "0.005")))
        c.safety_margin_pct = D(str(cfg.get("safety_margin_pct", "0")))
        c.min_net_profit_usd = D(str(cfg.get("min_net_profit_usd", "0")))
        c.min_annualized_return = D(str(cfg.get("min_annualized_return", "0.15")))
        c.leg_risk_haircut_pct = D(str(cfg.get("leg_risk_haircut_pct", "0.002")))
        c.latency_ms = int(cfg.get("latency_ms", 350))
        c.max_book_age_ms = int(cfg.get("max_book_age_ms", cfg.get("stale_after_ms", 3000)))
        c.resolution_haircut_pct_per_day = D(str(cfg.get("resolution_haircut_pct_per_day", "0.0002")))
        c.resolution_haircut_ambiguous_pct = D(str(cfg.get("resolution_haircut_ambiguous_pct", "0.01")))
        if risk_cfg:
            c.max_capital_per_trade_usd = D(str(risk_cfg.get("max_capital_per_trade_usd", "50")))
        return c


# ---------------------------------------------------------------------------
# Input evaluasi
# ---------------------------------------------------------------------------

@dataclass
class LegInput:
    """Satu leg bundle. BUY = keluar kas (beli ask), SELL = masuk kas (jual bid)."""

    market: MarketMeta
    asset_id: str
    side: Side
    book: OrderBookSnapshot
    shares_per_bundle: Decimal = ONE
    label: str = ""


@dataclass
class BundleRequest:
    """Spesifikasi bundle untuk evaluasi generik (A1/A2/B1/B2/C).

    - ``fixed_payout_per_bundle``: kas pasti saat exit (merge/resolusi/redeem).
      1.00 untuk pasangan YES+NO / set YES pemenang; 0 bila semua leg dijual.
    - ``collateral_consumed_per_bundle``: pUSD yang dikonsumsi (mis. split 1 pUSD
      untuk mint&sell) — arus kas keluar per bundle.
    - ``exit_hours``: jam modal terkunci (untuk annualized return).
    """

    strategy: str
    legs: list[LegInput]
    fixed_payout_per_bundle: Decimal = ONE
    collateral_consumed_per_bundle: Decimal = ZERO
    exit_hours: Decimal = D("2")
    gas_op: Optional[str] = None            # merge | split | redeem | convert_neg_risk
    gas_op_count_per_bundle: Decimal = ZERO # operasi on-chain per bundle (0 = tidak ada)
    ambiguous_resolution: bool = False
    event_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    max_bundle_size: Optional[Decimal] = None
    meta: dict = field(default_factory=dict)


@dataclass
class EvalResult:
    opportunity: Opportunity
    # rincian tambahan untuk debug/test
    candidates_considered: int = 0


class CostModel:
    """Orkestrator perhitungan biaya & evaluasi peluang."""

    def __init__(
        self,
        cfg: Optional[CostConfig] = None,
        gas: Optional[GasModel] = None,
    ) -> None:
        self.cfg = cfg or CostConfig()
        self.gas = gas or GasModel()

    # -- fee ---------------------------------------------------------------

    def taker_fee(self, shares: Decimal, price: Decimal, fee_schedule: FeeSchedule) -> Decimal:
        return taker_fee(shares, price, fee_schedule)

    # -- sizing ------------------------------------------------------------

    def _bundle_candidates(
        self,
        req: BundleRequest,
        naive_buy: Decimal,
        naive_sell: Decimal,
    ) -> list[Decimal]:
        """Kandidat ukuran bundle: breakpoint depth tiap leg + batas modal.

        Optimum net profit terjadi di breakpoint depth atau tepat di batas
        modal (net_total konkaf per potong level) — keduanya dicoba.
        """
        cands: set[Decimal] = set()
        # breakpoint kumulatif per leg (dalam unit bundle)
        for leg in req.legs:
            depth = ZERO
            levels = leg.book.asks if leg.side == Side.BUY else leg.book.bids
            for lv in levels:
                depth += lv.size
                if leg.shares_per_bundle > ZERO:
                    cands.add(depth / leg.shares_per_bundle)
        if req.max_bundle_size is not None:
            cands.add(req.max_bundle_size)

        # batas modal: perkiraan capital per bundle di harga terbaik + kasar fee/gas
        approx_fees = naive_buy * D("0.07") * D("0.25")  # estimasi upper fee kasar
        approx_gas = self.gas.cost_usd(req.gas_op) if req.gas_op else ZERO
        approx_pb = naive_buy + req.collateral_consumed_per_bundle + approx_fees + approx_gas
        if approx_pb > ZERO and self.cfg.max_capital_per_trade_usd > ZERO:
            # buffer 5% agar estimasi kasar tidak melewati cap; clip presisi di loop
            cands.add(self.cfg.max_capital_per_trade_usd / (approx_pb * D("1.05")))

        out = sorted(s for s in cands if s > ZERO)
        return out

    def _aggregate(self, req: BundleRequest, legs_walk: dict) -> dict:
        """Agregat TOTAL (untuk ukuran penuh `size`) dari hasil walk per leg."""
        buy_notional = ZERO
        sell_notional = ZERO
        fees = ZERO
        slippage = ZERO
        for i, leg in enumerate(req.legs):
            walk, fee, slip = legs_walk[i]
            if leg.side == Side.BUY:
                buy_notional += walk.notional
            else:
                sell_notional += walk.notional
            fees += fee
            slippage += slip
        return {
            "buy_notional": buy_notional,
            "sell_notional": sell_notional,
            "fees": fees,
            "slippage": slippage,
        }

    def _gas_total(self, req: BundleRequest, size: Decimal) -> Decimal:
        per_bundle = ZERO
        if req.gas_op and req.gas_op_count_per_bundle > ZERO:
            per_bundle += self.gas.cost_usd(req.gas_op) * req.gas_op_count_per_bundle
        per_bundle += self.gas.amortized_approval_cost() * D(max(1, len(req.legs)))
        return per_bundle * size

    def _slippage(self, leg: LegInput, walk: WalkFill) -> Decimal:
        ref = leg.book.best_ask.price if leg.side == Side.BUY else (
            leg.book.best_bid.price if leg.book.best_bid else None
        )
        if ref is None or walk.filled_shares <= ZERO:
            return ZERO
        return walk.notional - (walk.filled_shares * ref)

    # -- evaluasi utama ----------------------------------------------------

    def evaluate(self, req: BundleRequest, now_ms: Optional[int] = None) -> EvalResult:
        """Evaluasi bundle -> Opportunity (valid atau ditolak dengan alasan)."""

        def build(
            valid: bool,
            reason: RejectReason,
            detail: str,
            bundle: Decimal = ZERO,
            legs_plan: Optional[list[LegPlan]] = None,
            cost: Optional[CostBreakdown] = None,
            candidates: int = 0,
            fill_prob: Decimal = ZERO,
        ) -> EvalResult:
            opp = Opportunity(
                opportunity_id=req.opportunity_id or _make_id(req),
                strategy=req.strategy,
                market_ids=tuple(leg.market.market_id for leg in req.legs),
                event_id=req.event_id,
                legs=legs_plan or [],
                payout_per_bundle=req.fixed_payout_per_bundle,
                bundle_size=bundle,
                cost=cost or CostBreakdown(),
                valid=valid,
                reject_reason=reason,
                reject_detail=detail,
                confidence=ONE if valid else ZERO,
                fill_probability=fill_prob,
                expected_net_profit=(cost.net_profit * fill_prob) if (valid and cost) else ZERO,
                meta=dict(req.meta),
            )
            return EvalResult(opportunity=opp, candidates_considered=candidates)

        # ---- validasi input dasar ----
        if not req.legs:
            return build(False, RejectReason.INVALID_INPUT, "no legs")
        for leg in req.legs:
            if leg.market.fee_schedule.source == "missing" or not leg.market.fee_schedule.available:
                return build(False, RejectReason.FEE_UNKNOWN, f"fee schedule unavailable for {leg.market.market_id}")
            if leg.book is None or leg.book.age_ms(now_ms) > self.cfg.max_book_age_ms:
                age = leg.book.age_ms(now_ms) if leg.book else -1
                return build(False, RejectReason.STALE_DATA, f"book age {age}ms > {self.cfg.max_book_age_ms}ms")
            side_levels = leg.book.asks if leg.side == Side.BUY else leg.book.bids
            if not side_levels:
                return build(False, RejectReason.THIN_BOOK, f"empty {'asks' if leg.side == Side.BUY else 'bids'} on {leg.asset_id[:16]}...")

        # ---- naive gross pada best price (per bundle) ----
        naive_buy = ZERO
        naive_sell = ZERO
        for leg in req.legs:
            best = leg.book.best_ask if leg.side == Side.BUY else leg.book.best_bid
            if best is None:
                return build(False, RejectReason.THIN_BOOK, "missing best price")
            if leg.side == Side.BUY:
                naive_buy += best.price * leg.shares_per_bundle
            else:
                naive_sell += best.price * leg.shares_per_bundle
        naive_gross = (req.fixed_payout_per_bundle + naive_sell) - (naive_buy + req.collateral_consumed_per_bundle)

        if naive_gross <= ZERO:
            return build(
                False,
                RejectReason.GROSS_NOT_POSITIVE,
                f"gross {naive_gross:.6f} <= 0 at top of book",
                cost=CostBreakdown(gross_edge=naive_gross),
            )

        # ---- minimal ukuran agar tiap order memenuhi min_order_notional (USDC) ----
        min_bundle = ZERO
        for leg in req.legs:
            best_px = leg.book.best_ask if leg.side == Side.BUY else leg.book.best_bid
            if best_px is None or best_px.price <= ZERO:
                return build(False, RejectReason.THIN_BOOK, "no price for min-order calc")
            need_shares = leg.market.min_order_notional / best_px.price
            need_bundle = need_shares / leg.shares_per_bundle if leg.shares_per_bundle > ZERO else need_shares
            min_bundle = dec_max(min_bundle, need_bundle)

        # ---- kandidat ukuran ----
        candidates = self._bundle_candidates(req, naive_buy, naive_sell)
        if not candidates:
            return build(False, RejectReason.THIN_BOOK, "no size candidates")
        if len(candidates) > 64:
            candidates = candidates[-64:]

        best: Optional[tuple] = None
        considered = 0

        def eval_size(size: Decimal) -> Optional[tuple]:
            """Hitung penuh untuk satu ukuran; None bila tidak feasible."""
            legs_plan: list[LegPlan] = []
            legs_walk: dict = {}
            for i, leg in enumerate(req.legs):
                shares = size * leg.shares_per_bundle
                walk = walk_the_book(leg.book, leg.side, shares)
                if not walk.fully_filled:
                    return None
                fee = fee_for_walk(walk, leg.market.fee_schedule)
                slip = self._slippage(leg, walk)
                legs_walk[i] = (walk, fee, slip)
                limit_px = walk.levels_used[-1][0] if walk.levels_used else walk.avg_price
                legs_plan.append(
                    LegPlan(
                        asset_id=leg.asset_id,
                        market_id=leg.market.market_id,
                        side=leg.side,
                        shares=walk.filled_shares,
                        limit_price=limit_px,
                        walk=walk,
                        fee=fee,
                        gas=ZERO,
                        label=leg.label,
                    )
                )

            agg = self._aggregate(req, legs_walk)
            gas_total = self._gas_total(req, size)

            # rounding cost: selisih encoding 6 desimal vs eksak (konservatif)
            rounding_cost = ZERO
            for i, leg in enumerate(req.legs):
                walk = legs_walk[i][0]
                tick = leg.book.tick_size or leg.market.tick_size
                try:
                    maker, taker = round_order_amounts(leg.side, walk.filled_shares, walk.avg_price, tick)
                    if leg.side == Side.BUY:
                        encoded = D(maker) / D(10) ** TOKEN_DECIMALS
                        rounding_cost += dec_max(ZERO, walk.notional - encoded)
                    else:
                        encoded = D(taker) / D(10) ** TOKEN_DECIMALS
                        rounding_cost += dec_max(ZERO, walk.notional - encoded)
                except ValueError:
                    pass

            payout_total = req.fixed_payout_per_bundle * size
            collateral_total = req.collateral_consumed_per_bundle * size

            capital_total = agg["buy_notional"] + agg["fees"] + gas_total + collateral_total
            leg_risk = capital_total * self.cfg.leg_risk_haircut_pct
            resolution_risk = ZERO
            if req.ambiguous_resolution:
                resolution_risk += payout_total * self.cfg.resolution_haircut_ambiguous_pct
            if payout_total > ZERO:
                days = dec_max(ZERO, req.exit_hours) / D(24)
                resolution_risk += payout_total * self.cfg.resolution_haircut_pct_per_day * days

            safety = dec_max(
                self.cfg.safety_margin_usd * size,
                capital_total * self.cfg.safety_margin_pct,
            )

            net_total = (
                payout_total
                + agg["sell_notional"]
                - agg["buy_notional"]
                - collateral_total
                - agg["fees"]
                - gas_total
                - leg_risk
                - resolution_risk
                - rounding_cost
                - safety
            )

            days_held = dec_max(self.cfg.min_exit_hours, req.exit_hours) / D(24)
            if capital_total > ZERO:
                annualized = (net_total / capital_total) * (D(365) / days_held)
            else:
                annualized = ZERO

            cost = CostBreakdown(
                gross_edge=naive_gross * size,
                notional=(agg["buy_notional"] + agg["sell_notional"]),
                trading_fees=agg["fees"],
                slippage_cost=agg["slippage"],
                gas_cost=gas_total,
                leg_risk_cost=leg_risk,
                resolution_risk_cost=resolution_risk,
                rounding_cost=rounding_cost,
                safety_margin=safety,
                total_costs=(agg["fees"] + agg["slippage"] + gas_total + leg_risk + resolution_risk + rounding_cost),
                net_profit=net_total,
                net_profit_pct=(net_total / capital_total * D(100)) if capital_total > ZERO else ZERO,
                capital_required=capital_total,
                annualized_return=annualized,
                days_to_resolution=days_held,
            )
            fill_prob = self._fill_probability(req, legs_walk)
            return (net_total * fill_prob, size, legs_plan, cost, fill_prob, capital_total)

        for size in candidates:
            if size < min_bundle:
                continue
            considered += 1
            result = eval_size(size)
            if result is not None and result[5] > self.cfg.max_capital_per_trade_usd:
                # clip presisi ke batas modal (capital linear terhadap size pada
                # komposisi level yang sama)
                clipped = round_down(
                    size * self.cfg.max_capital_per_trade_usd / result[5], 2
                )
                result = eval_size(clipped) if clipped >= min_bundle else None
            if result is None:
                continue
            score, eff_size, legs_plan, cost, fill_prob, _cap = result
            if best is None or score > best[0]:
                best = (score, eff_size, legs_plan, cost, fill_prob)

        if best is None:
            return build(
                False,
                RejectReason.BELOW_MIN_ORDER,
                f"no candidate size satisfies min_order_notional (min_bundle={min_bundle:.4f}) and capital cap",
                candidates=considered,
                cost=CostBreakdown(gross_edge=naive_gross),
            )

        _, size, legs_plan, cost, fill_prob = best

        # ---- gate akhir ----
        if cost.net_profit <= self.cfg.min_net_profit_usd:
            reason = (
                RejectReason.BELOW_SAFETY_MARGIN
                if self.cfg.safety_margin_usd > ZERO and cost.net_profit <= ZERO
                else RejectReason.NET_NOT_POSITIVE
            )
            return build(
                False,
                reason,
                f"net {cost.net_profit:.6f} <= min {self.cfg.min_net_profit_usd:.6f} after all costs",
                bundle=size,
                legs_plan=legs_plan,
                cost=cost,
                candidates=considered,
                fill_prob=fill_prob,
            )
        if cost.annualized_return < self.cfg.min_annualized_return:
            return build(
                False,
                RejectReason.ANNUALIZED_TOO_LOW,
                f"annualized {cost.annualized_return:.4f} < min {self.cfg.min_annualized_return}",
                bundle=size,
                legs_plan=legs_plan,
                cost=cost,
                candidates=considered,
                fill_prob=fill_prob,
            )
        return build(
            True,
            RejectReason.OK,
            "valid",
            bundle=size,
            legs_plan=legs_plan,
            cost=cost,
            candidates=considered,
            fill_prob=fill_prob,
        )

    # -- model probabilitas terisi ----------------------------------------

    def _fill_probability(self, req: BundleRequest, legs_walk: dict) -> Decimal:
        """Estimasi probabilitas semua leg terisi penuh (model konservatif)."""
        # parameter dari config default; di-override lewat meta bila ada
        base = D(str(req.meta.get("fill_base", "0.95")))
        depth_penalty = D(str(req.meta.get("fill_depth_penalty", "0.5")))
        staleness_per_ms = D(str(req.meta.get("fill_staleness_penalty_per_ms", "0.0002")))
        latency_per_ms = D(str(req.meta.get("fill_latency_penalty_per_ms", "0.00005")))
        min_p = D(str(req.meta.get("fill_min_prob", "0.05")))

        worst = ONE
        for i, leg in enumerate(req.legs):
            walk = legs_walk[i][0]
            top = leg.book.asks[0].size if leg.side == Side.BUY else leg.book.bids[0].size
            depth_frac = (walk.filled_shares / top) if top > ZERO else ONE
            # makin dekat ke depth top-of-book, makin kecil peluang terisi
            p = base - depth_penalty * dec_min(ONE, depth_frac)
            age = D(leg.book.age_ms())
            p -= staleness_per_ms * age
            p -= latency_per_ms * D(self.cfg.latency_ms)
            worst = dec_min(worst, p)
        # semua leg harus terisi: kalikan prob per leg secara konservatif (min)
        n = D(max(1, len(req.legs)))
        combined = worst  # konservatif: pakai terburuk
        if len(req.legs) > 1:
            combined = worst ** n
        return dec_max(min_p, dec_min(ONE, combined))


def _make_id(req: BundleRequest) -> str:
    parts = [req.strategy] + sorted(leg.asset_id[:12] for leg in req.legs)
    return "-".join(parts)


# ---------------------------------------------------------------------------
# Helper konversi MarketMeta ringkas (dipakai scanner & tests)
# ---------------------------------------------------------------------------

def make_market(
    market_id: str,
    *,
    fee_rate: Decimal,
    tick: Decimal = D("0.01"),
    min_notional: Decimal = D("5"),
    fees_enabled: bool = True,
    exponent: Decimal = ONE,
    neg_risk: bool = False,
    end_date=None,
) -> MarketMeta:
    return MarketMeta(
        market_id=market_id,
        slug=market_id,
        question=market_id,
        condition_id="0x" + market_id,
        event_id="evt-" + market_id,
        version="v1",
        yes_asset_id="yes-" + market_id,
        no_asset_id="no-" + market_id,
        neg_risk=neg_risk,
        neg_risk_augmented=False,
        tick_size=tick,
        min_order_notional=min_notional,
        fee_schedule=FeeSchedule(
            fees_enabled=fees_enabled,
            rate=fee_rate,
            exponent=exponent,
            taker_only=True,
            rebate_rate=ZERO,
            source="gamma",
        ),
        end_date=end_date,
    )
