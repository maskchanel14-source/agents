"""Scanner menyeluruh — pipeline bertahap, ranking net profit, dedup (misi §3b).

Pipeline:
1. filter murah (top-of-book gross > 0) — dilakukan di tiap strategi;
2. hitung kasar (kandidat);
3. hitung penuh (walk-the-book + SEMUA biaya) via CostModel — hanya kandidat.

SEMUA peluang (valid & ditolak) disimpan ke SQLite. Peringkat berdasarkan
expected net profit (net x fill probability), lalu annualized.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Sequence

from .costs import CostModel
from .data.feed import MarketDataHub
from .models import CoverageReport, Opportunity
from .state.db import StateDB
from .strategies.base import Strategy

log = logging.getLogger("bot.scanner")


@dataclass
class ScanResult:
    opportunities: list[Opportunity] = field(default_factory=list)
    ranked_valid: list[Opportunity] = field(default_factory=list)
    coverage: Optional[CoverageReport] = None
    duration_ms: int = 0
    per_strategy: dict = field(default_factory=dict)
    rejection_stats: dict = field(default_factory=dict)


class Scanner:
    def __init__(
        self,
        hub: MarketDataHub,
        strategies: Sequence[Strategy],
        cost_model: CostModel,
        db: Optional[StateDB] = None,
    ) -> None:
        self.hub = hub
        self.strategies = list(strategies)
        self.cost_model = cost_model
        self.db = db
        self._seen: set[str] = set()

    def scan(self, now_ms: Optional[int] = None) -> ScanResult:
        t0 = time.time()
        result = ScanResult()
        all_opps: list[Opportunity] = []

        for strat in self.strategies:
            if not strat.enabled:
                continue
            try:
                opps = strat.scan(self.hub, now_ms=now_ms)
            except Exception:
                log.exception("strategy %s failed", strat.name)
                continue
            result.per_strategy[strat.name] = len(opps)
            all_opps.extend(opps)

        # ---- dedup: satu market/event tidak dieksekusi ganda ----
        deduped: list[Opportunity] = []
        best_by_market: dict[tuple, Opportunity] = {}
        for opp in all_opps:
            key = tuple(sorted(opp.market_ids))
            prev = best_by_market.get(key)
            if prev is None:
                best_by_market[key] = opp
            else:
                # simpan yang paling mendekati valid / net terbesar untuk ranking;
                # keduanya tetap dicatat ke SQLite (SEMUA peluang)
                if (opp.valid, opp.cost.net_profit) > (prev.valid, prev.cost.net_profit):
                    best_by_market[key] = opp
        deduped = list(best_by_market.values())

        # ---- statistik penolakan ----
        for opp in all_opps:
            reason = opp.reject_reason.value
            result.rejection_stats[reason] = result.rejection_stats.get(reason, 0) + 1

        # ---- persist SEMUA peluang (valid & ditolak) ----
        if self.db is not None:
            self.db.save_opportunities(all_opps)

        # ---- ranking peluang valid ----
        valid = [o for o in deduped if o.valid]
        valid.sort(key=lambda o: (o.expected_net_profit, o.cost.annualized_return), reverse=True)
        result.opportunities = all_opps
        result.ranked_valid = valid
        result.coverage = self.hub.coverage_snapshot()
        result.duration_ms = int((time.time() - t0) * 1000)

        if self.db is not None and result.coverage is not None:
            self.db.record_scan_run(
                markets_total=result.coverage.total_active_markets or len(self.hub.markets),
                markets_monitored=result.coverage.markets_monitored,
                candidates=len(all_opps),
                valid=len(valid),
                rejected=len(all_opps) - sum(1 for o in all_opps if o.valid),
                coverage=result.coverage.as_dict(),
            )
        return result

    def execute_top(
        self,
        result: ScanResult,
        executor,
        *,
        max_trades: int = 1,
        now_ms: Optional[int] = None,
    ) -> list:
        """Eksekusi peluang teratas yang lolos semua gate (risk + ranking)."""
        results = []
        for opp in result.ranked_valid[:max_trades]:
            res = executor.execute(opp, now_ms=now_ms)
            results.append((opp, res))
            if not res.executed:
                log.info("top opportunity %s not executed: %s", opp.opportunity_id, res.reason)
        return results
