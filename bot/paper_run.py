"""Paper-run session: eksekusi simulasi penuh (scanner -> risk -> paper executor).

Dua sumber data:
- fixture/rekaman (replay dipercepat) — bisa dijalankan di sandbox/offline;
- live feed via `python -m bot --mode paper` (butuh jaringan Polymarket).

Output: `logs/paper_run_summary.json` — peluang terdeteksi, ditolak per alasan,
PnL simulasi setelah semua biaya.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .backtest.replay import ReplayEvent, load_fixture_json, load_recording_db, markets_from_meta
from .config.loader import ROOT, load_config
from .costs import CostConfig, CostModel, GasModel
from .data.feed import MarketDataHub
from .decimal_utils import ZERO
from .execution.fill_model import FillModel, FillModelConfig
from .execution.simulator import PaperExecutor
from .risk.limits import RiskConfig, RiskManager
from .scanner import Scanner
from .state.db import StateDB
from .strategies.cross_market import CrossMarketLogical
from .strategies.intra_market import IntraMarketBinary
from .strategies.multi_outcome import MultiOutcomeNegRisk


class _FakeWs:
    def __init__(self):
        self.stats = {"shards": 0, "connected": 0, "assets": 0, "reconnects": 0}
        self.on_event = None

    async def subscribe(self, ids): pass
    async def unsubscribe(self, ids): pass
    async def start(self): pass
    async def stop(self): pass


class _FakeClob:
    async def get_books(self, asset_ids, *, batch_size=20):
        return {}


def run_paper_session(
    events: list[ReplayEvent],
    markets_meta: dict,
    *,
    db_path: Path,
    scan_every_ms: int = 1000,
    max_trades: int = 8,
    cfg: dict | None = None,
) -> dict:
    cfg = cfg or {}
    markets = markets_from_meta(markets_meta)
    hub = MarketDataHub(_FakeClob(), _FakeWs(), stale_after_ms=10**9)
    hub.markets = markets
    for m in markets.values():
        hub.asset_to_market[m.yes_asset_id] = m.market_id
        hub.asset_to_market[m.no_asset_id] = m.market_id

    cost_cfg = CostConfig.from_config(cfg.get("costs", {}), cfg.get("risk", {}))
    model = CostModel(cost_cfg, GasModel.from_config(cfg.get("costs", {}).get("gas", {})))
    strategies_cfg = cfg.get("strategies", {})
    scanner = Scanner(
        hub,
        [
            IntraMarketBinary(model, strategies_cfg.get("A_intra_binary", {"enabled": True})),
            MultiOutcomeNegRisk(model, strategies_cfg.get("B_multi_outcome", {"enabled": True, "require_exhaustive": True})),
            CrossMarketLogical(model, strategies_cfg.get("C_cross_market", {"enabled": False})),
        ],
        model,
        db=None,
    )
    db = StateDB(db_path)
    risk = RiskManager(RiskConfig.from_config(cfg.get("risk", {})), root=ROOT)
    executor = PaperExecutor(model, db, risk, FillModel(FillModelConfig.from_config(
        cfg.get("fill_model", {}), latency_ms=cost_cfg.latency_ms
    )), seed=42)

    rejection: dict[str, int] = {}
    detected = 0
    valid = 0
    executed = 0
    simulated_pnl = ZERO
    trades = 0
    last_scan = events[0].ts_ms if events else 0

    for ev in events:
        snap_bids, snap_asks = ev.bids, ev.asks
        from .models import OrderBookSnapshot
        hub.books[ev.asset_id] = OrderBookSnapshot.from_levels(
            ev.asset_id, snap_bids, snap_asks, ts_ms=ev.ts_ms, recv_ms=ev.ts_ms
        )
        if ev.ts_ms - last_scan < scan_every_ms:
            continue
        last_scan = ev.ts_ms
        result = scanner.scan(now_ms=ev.ts_ms)
        detected += len(result.opportunities)
        for opp in result.opportunities:
            rejection[opp.reject_reason.value] = rejection.get(opp.reject_reason.value, 0) + 1
        valid += len(result.ranked_valid)
        for opp, res in scanner.execute_top(result, executor, max_trades=max_trades, now_ms=ev.ts_ms):
            if res.executed:
                executed += 1
                trades += len(opp.legs)
                simulated_pnl += opp.cost.net_profit
                risk.record_realized_pnl(opp.cost.net_profit)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "replay (paper executor, fill model aktif)",
        "events_processed": len(events),
        "markets": len(markets),
        "opportunities_detected": detected,
        "valid_opportunities": valid,
        "executed": executed,
        "simulated_trades_legs": trades,
        "rejection_stats": rejection,
        "simulated_pnl_usd": str(simulated_pnl),
        "note": (
            "PnL simulasi = Σ net profit termodel pada harga fill (setelah SEMUA biaya: "
            "fee, slippage walk-the-book, gas, haircut risiko, safety margin). "
            "Untuk angka live-paper, jalankan `python -m bot --mode paper` dengan "
            "akses jaringan Polymarket (lihat docs/FEASIBILITY.md)."
        ),
        "risk_snapshot": risk.snapshot(),
    }
    db.kv_set("paper_run_summary", summary)
    db.close()
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Paper run dari fixture/rekaman")
    p.add_argument("--fixture", default=str(ROOT / "data/fixtures/synthetic_small.json"))
    p.add_argument("--markets", default=None)
    p.add_argument("--out", default=str(ROOT / "logs/paper_run_summary.json"))
    args = p.parse_args(argv)
    cfg = load_config()

    fixture = Path(args.fixture)
    if fixture.name.endswith(".db"):
        events = load_recording_db(fixture)
        markets_path = Path(args.markets) if args.markets else fixture.parent / "markets_meta.json"
    else:
        events = load_fixture_json(fixture)
        markets_path = Path(args.markets) if args.markets else fixture.parent / (fixture.stem + "_markets.json")
    meta = json.loads(markets_path.read_text(encoding="utf-8"))

    summary = run_paper_session(events, meta, db_path=ROOT / "logs/paper_run.db", cfg=cfg)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
