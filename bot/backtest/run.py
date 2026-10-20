"""Runner backtest: replay fixture + parameter sweep -> laporan (misi §5d)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..config.loader import ROOT, load_config
from ..costs import CostConfig
from .replay import load_fixture_json, load_recording_db, markets_from_meta, run_replay
from .sweep import sweep


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Backtest replay (anti-lookahead) + parameter sweep")
    p.add_argument("--fixture", default=None, help="path fixture JSON atau recording.db")
    p.add_argument("--markets", default=None, help="path markets_meta.json")
    p.add_argument("--sweep", action="store_true", help="jalankan parameter sweep")
    p.add_argument("--report", default="report_out/backtest_report.json")
    args = p.parse_args(argv)

    cfg = load_config()
    fixture = Path(args.fixture) if args.fixture else ROOT / cfg.get("backtest", {}).get("fixture_path", "data/fixtures") / "synthetic_small.json"
    if not fixture.is_absolute():
        fixture = ROOT / fixture
    markets_path = Path(args.markets) if args.markets else fixture.parent / (fixture.stem + "_markets.json")
    if fixture.name.endswith(".db"):
        events = load_recording_db(fixture)
    else:
        events = load_fixture_json(fixture)
    meta = json.loads(markets_path.read_text(encoding="utf-8"))
    markets = markets_from_meta(meta)

    cost_cfg = CostConfig.from_config(cfg.get("costs", {}), cfg.get("risk", {}))
    result = run_replay(events, markets, cost_cfg=cost_cfg)
    report = {
        "fixture": str(fixture),
        "events": result.events,
        "scans": result.scans,
        "opportunities": result.opportunities,
        "valid": result.valid,
        "rejection_stats": result.rejection_stats,
        "avg_net_edge": sum(result.valid_net_edges) / len(result.valid_net_edges) if result.valid_net_edges else 0,
        "avg_lifetime_s": (sum(result.lifetimes_ms) / len(result.lifetimes_ms) / 1000) if result.lifetimes_ms else 0,
        "notes": result.notes,
    }
    if args.sweep:
        sw = sweep(events, markets, strategy_cfg=cfg.get("strategies", {}))
        report["sweep"] = sw.rows

    out = Path(args.report)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
