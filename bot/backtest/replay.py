"""Replay data orderbook (rekaman live ATAU fixture) — TANPA lookahead bias.

Keputusan di waktu t hanya memakai data dengan timestamp <= t (misi §5d, §7.3).
Sumber data:
- SQLite rekaman `bot.record` (tabel orderbook_snapshots)
- Fixture JSON: [{"ts_ms", "asset_id", "market_id", "bids", "asks"}, ...]
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from ..costs import CostConfig, CostModel, GasModel, make_market
from ..decimal_utils import D, ONE
from ..models import FeeSchedule, MarketMeta, OrderBookSnapshot
from ..scanner import Scanner
from ..state.db import StateDB
from ..strategies.intra_market import IntraMarketBinary
from ..strategies.multi_outcome import MultiOutcomeNegRisk


@dataclass
class ReplayEvent:
    ts_ms: int
    asset_id: str
    market_id: str
    bids: list
    asks: list


@dataclass
class ReplayResult:
    events: int = 0
    scans: int = 0
    opportunities: int = 0
    valid: int = 0
    rejection_stats: dict = field(default_factory=dict)
    valid_net_edges: list = field(default_factory=list)
    lifetimes_ms: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def load_fixture_json(path: Path, markets_meta: Optional[dict] = None) -> list[ReplayEvent]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    events = []
    for row in raw:
        events.append(ReplayEvent(
            ts_ms=int(row["ts_ms"]),
            asset_id=str(row["asset_id"]),
            market_id=str(row.get("market_id", "")),
            bids=[tuple(x) for x in row.get("bids", [])],
            asks=[tuple(x) for x in row.get("asks", [])],
        ))
    events.sort(key=lambda e: e.ts_ms)  # urutan waktu — anti lookahead
    return events


def load_recording_db(path: Path) -> list[ReplayEvent]:
    conn = sqlite3.connect(str(path))
    cur = conn.execute(
        "SELECT ts_ms, asset_id, market_id, bids, asks FROM orderbook_snapshots ORDER BY ts_ms"
    )
    events = []
    for ts_ms, asset_id, market_id, bids, asks in cur.fetchall():
        events.append(ReplayEvent(
            ts_ms=int(ts_ms), asset_id=asset_id, market_id=market_id or "",
            bids=[tuple(x) for x in json.loads(bids)],
            asks=[tuple(x) for x in json.loads(asks)],
        ))
    conn.close()
    return events


class ReplayHub:
    """Hub orderbook minimal untuk replay (implementasi subset interface MarketDataHub)."""

    def __init__(self, markets: dict[str, MarketMeta], stale_after_ms: int = 10**9) -> None:
        self.markets = markets
        self.asset_to_market: dict[str, str] = {}
        for mid, m in markets.items():
            self.asset_to_market[m.yes_asset_id] = mid
            self.asset_to_market[m.no_asset_id] = mid
        self.books: dict[str, OrderBookSnapshot] = {}
        self.stale_after_ms = stale_after_ms
        self.coverage = None

    def get_book(self, asset_id: str) -> Optional[OrderBookSnapshot]:
        return self.books.get(asset_id)

    def coverage_snapshot(self):
        return None

    def apply(self, ev: ReplayEvent) -> None:
        self.books[ev.asset_id] = OrderBookSnapshot.from_levels(
            ev.asset_id, ev.bids, ev.asks, ts_ms=ev.ts_ms, recv_ms=ev.ts_ms
        )


def markets_from_meta(meta: dict) -> dict[str, MarketMeta]:
    """Konversi markets_meta.json (dari recorder / fixture) ke MarketMeta."""
    out: dict[str, MarketMeta] = {}
    for mid, m in meta.items():
        out[mid] = make_market(
            mid,
            fee_rate=D(m.get("fee_rate", "0")),
            tick=D(m.get("tick", "0.01")),
            min_notional=D(m.get("min_notional", "5")),
            end_date=None,
        )
        object.__setattr__(out[mid], "slug", m.get("slug", mid))
        object.__setattr__(out[mid], "question", m.get("question", mid))
        object.__setattr__(out[mid], "event_id", m.get("event_id", ""))
        object.__setattr__(out[mid], "neg_risk", bool(m.get("neg_risk", False)))
        object.__setattr__(out[mid], "yes_asset_id", m.get("yes", f"yes-{mid}"))
        object.__setattr__(out[mid], "no_asset_id", m.get("no", f"no-{mid}"))
        object.__setattr__(out[mid], "resolution_criteria", m.get("criteria", ""))
        fs = out[mid].fee_schedule
        object.__setattr__(out[mid], "fee_schedule", FeeSchedule(
            fees_enabled=True, rate=fs.rate, exponent=ONE, taker_only=True,
            rebate_rate=D("0"), source="gamma",
        ))
        # asset mapping ulang setelah asset id diganti
    return out


def run_replay(
    events: list[ReplayEvent],
    markets: dict[str, MarketMeta],
    *,
    scan_every_ms: int = 1000,
    cost_cfg: Optional[CostConfig] = None,
    strategy_cfg: Optional[dict] = None,
) -> ReplayResult:
    """Replay event berurutan waktu; scan periodik HANYA dengan data <= t."""
    result = ReplayResult()
    if not events:
        result.notes.append("no events")
        return result

    cfg = cost_cfg or CostConfig(min_annualized_return=D("0.15"))
    model = CostModel(cfg, GasModel(enabled=False))
    hub = ReplayHub(markets)
    scanner = Scanner(
        hub,
        [
            IntraMarketBinary(model, (strategy_cfg or {}).get("A_intra_binary", {"enabled": True})),
            MultiOutcomeNegRisk(model, (strategy_cfg or {}).get("B_multi_outcome", {"enabled": True, "require_exhaustive": True})),
        ],
        model,
        db=None,
    )

    last_scan = events[0].ts_ms
    active_valid: dict[str, int] = {}  # opportunity_id -> ts pertama valid (lifetime)

    for ev in events:
        result.events += 1
        hub.apply(ev)  # hanya data dengan ts <= sekarang yang sudah diterapkan
        if ev.ts_ms - last_scan >= scan_every_ms:
            last_scan = ev.ts_ms
            result.scans += 1
            scan_res = scanner.scan(now_ms=ev.ts_ms)
            result.opportunities += len(scan_res.opportunities)
            for opp in scan_res.opportunities:
                reason = opp.reject_reason.value
                result.rejection_stats[reason] = result.rejection_stats.get(reason, 0) + 1
                if opp.valid:
                    result.valid += 1
                    result.valid_net_edges.append(float(opp.cost.net_profit))
                    if opp.opportunity_id not in active_valid:
                        active_valid[opp.opportunity_id] = ev.ts_ms
            # peluang yang hilang -> lifetime tercatat
            now_valid = {o.opportunity_id for o in scan_res.opportunities if o.valid}
            for oid in list(active_valid.keys()):
                if oid not in now_valid:
                    result.lifetimes_ms.append(ev.ts_ms - active_valid.pop(oid))
    for oid, t0 in active_valid.items():
        result.lifetimes_ms.append(events[-1].ts_ms - t0)

    total_candidates = sum(result.rejection_stats.values())
    if total_candidates:
        rejected = total_candidates - result.rejection_stats.get("ok", 0)
        result.notes.append(
            f"gross candidates={total_candidates}, valid={result.rejection_stats.get('ok', 0)}, "
            f"rejected after costs={rejected} ({100 * rejected / total_candidates:.1f}%)"
        )
    return result
