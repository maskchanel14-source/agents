"""Paper executor — eksekusi simulasi terhadap data live dengan fill model.

FOK = semua atau tidak sama sekali (default, minimalkan leg risk).
FAK = isi yang bisa, sisa dibatalkan (partial fill dihitung sebagai risiko).
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..costs import CostModel
from ..decimal_utils import D, ZERO
from ..models import LegPlan, Opportunity
from ..risk.limits import RiskManager
from ..state.db import StateDB
from .fill_model import FillModel, FillModelConfig

log = logging.getLogger("bot.execution.paper")


@dataclass
class ExecutionResult:
    executed: bool
    reason: str
    filled_shares: Decimal = ZERO
    paid_notional: Decimal = ZERO
    fees: Decimal = ZERO
    partial: bool = False
    trade_ids: Optional[list] = None


class PaperExecutor:
    """Simulator eksekusi: menulis trade ke SQLite, memperbarui posisi & risk."""

    def __init__(
        self,
        cost_model: CostModel,
        db: StateDB,
        risk: RiskManager,
        fill_model: Optional[FillModel] = None,
        *,
        order_type_primary: str = "FOK",
        order_type_fallback: str = "FAK",
        seed: Optional[int] = None,
    ) -> None:
        self.cost_model = cost_model
        self.db = db
        self.risk = risk
        self.fill_model = fill_model or FillModel(FillModelConfig(latency_ms=cost_model.cfg.latency_ms))
        self.order_type_primary = order_type_primary
        self.order_type_fallback = order_type_fallback
        self.rng = random.Random(seed)

    def execute(self, opp: Opportunity, now_ms: Optional[int] = None) -> ExecutionResult:
        allowed, reason = self.risk.check_opportunity(opp)
        if not allowed:
            log.info("risk rejected %s: %s", opp.opportunity_id, reason)
            return ExecutionResult(False, f"risk: {reason}")

        order_type = self.order_type_primary
        trade_ids: list = []
        total_filled = ZERO
        total_notional = ZERO
        total_fees = ZERO
        partial = False

        for leg in opp.legs:
            # estimasi peluang terisi tiap leg (book asli tidak tersedia di sini;
            # pakai probabilitas dasar dari konfigurasi fill model)
            p = self.fill_model.cfg.base_fill_prob
            if order_type == "FOK":
                # FOK: kalau simulasi gagal penuh, order dibatalkan seluruhnya
                if self.rng.random() > float(p):
                    log.info("FOK fill simulation failed for leg %s", leg.asset_id[:12])
                    self._record(opp, leg, ZERO, ZERO, ZERO, status="fok_unfilled", now_ms=now_ms)
                    return ExecutionResult(
                        False, "FOK not filled (fill model)", partial=partial, trade_ids=trade_ids
                    )
                filled, notional, fee = self._fill_leg(opp, leg, full=True)
            else:
                filled, notional, fee = self._fill_leg(opp, leg, full=self.rng.random() < float(p))
                if filled < leg.shares:
                    partial = True

            total_filled += filled
            total_notional += notional
            total_fees += fee
            tid = self._record(opp, leg, filled, notional, fee, status="filled" if filled == leg.shares else "partial", now_ms=now_ms)
            trade_ids.append(tid)

            if filled > ZERO:
                self.db.upsert_position(leg.market_id, leg.asset_id, leg.label or "", filled, (notional / filled) if filled else ZERO)

        if order_type == "FOK" and partial:
            return ExecutionResult(False, "FOK partial (should not happen)", partial=True, trade_ids=trade_ids)

        self.risk.commit_exposure(opp)
        log.info(
            "PAPER EXECUTED %s: %d legs, notional=%.4f fees=%.5f",
            opp.opportunity_id, len(opp.legs), total_notional, total_fees,
        )
        return ExecutionResult(
            True, "executed", filled_shares=total_filled, paid_notional=total_notional,
            fees=total_fees, partial=partial, trade_ids=trade_ids,
        )

    def _fill_leg(self, opp: Opportunity, leg: LegPlan, *, full: bool):
        if full:
            filled = leg.shares
        else:
            frac = D(str(round(self.rng.uniform(0.2, 0.9), 4)))
            filled = leg.shares * frac
        if filled <= ZERO:
            return ZERO, ZERO, ZERO
        notional = leg.limit_price * filled
        # fee proporsional terhadap plan (plan dihitung per level pada harga yang sama)
        fee = leg.fee * (filled / leg.shares) if leg.shares > ZERO else ZERO
        return filled, notional, fee

    def _record(self, opp, leg, filled, notional, fee, status, now_ms=None) -> int:
        return self.db.record_trade(
            opportunity_id=opp.opportunity_id,
            mode="paper",
            market_id=leg.market_id,
            asset_id=leg.asset_id,
            label=leg.label,
            side=leg.side.value,
            shares=filled,
            price=leg.limit_price,
            fee=fee,
            notional=notional,
            status=status,
            order_id=f"paper-{opp.opportunity_id}-{leg.asset_id[:10]}",
            fill_probability=opp.fill_probability,
            meta={"order_type": self.order_type_primary},
        )
