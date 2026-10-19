"""Command line: ``polymarket-arb {record,replay,paper,live,kill,report}``.

Default mode is paper. ``live`` is refused unless the env gate and confirmation file exist,
and even then no signer ships in this build (see docs/DECISIONS in DECISIONS.md).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from .config import LiveGateError, load_settings
from .monitoring import setup_logging


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="polymarket-arb")
    p.add_argument(
        "--config",
        type=Path,
        default=None,
        help="YAML config (default config/default.yaml)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="record live market data to JSONL (read-only)")
    rec.add_argument("--seconds", type=float, default=60)
    rec.add_argument("--out", type=Path, required=True)

    rep = sub.add_parser("replay", help="backtest: replay a recording through the paper engine")
    rep.add_argument("--input", type=Path, required=True)
    rep.add_argument("--db", type=Path, default=None)
    rep.add_argument("--report", type=Path, default=None)

    pap = sub.add_parser("paper", help="paper trading on live data (simulated fills only)")
    pap.add_argument("--seconds", type=float, default=60)
    pap.add_argument("--db", type=Path, default=None)
    pap.add_argument("--report", type=Path, default=None)

    sub.add_parser("live", help="live mode (gated; refused by default)")

    kill = sub.add_parser("kill", help="engage or clear the kill switch file")
    kill.add_argument("action", choices=["on", "off", "status"])

    rpt = sub.add_parser("report", help="summarise a state database")
    rpt.add_argument("--db", type=Path, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    setup_logging(logging.INFO)
    settings = load_settings(args.config)
    if args.cmd == "kill":
        from .risk import KillSwitch

        ks = KillSwitch(settings.kill_switch_path)
        if args.action == "on":
            ks.activate_file("cli")
        elif args.action == "off":
            ks.clear_file()
        print(json.dumps({"kill_switch_active": ks.is_active(), "reason": ks.reason()}))
        return 0
    if args.cmd == "report":
        from .state.store import StateStore

        store = StateStore(args.db, mode="paper")
        out = {
            "opportunities_valid": store.count("opportunities"),
            "executed": store.count("executed"),
            "orders": store.count("orders"),
            "pnl_by_kind": {k: str(v) for k, v in store.pnl_by_kind().items()},
            "rejections_note": "rejections are aggregated in run reports (stats), not stored per-scan",
        }
        store.close()
        print(json.dumps(out, indent=2))
        return 0
    if args.cmd == "live":
        from .runner import run_live

        try:
            asyncio.run(run_live(settings, dict(os.environ)))
        except LiveGateError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 - e.g. LiveNotArmed
            print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        return 0
    if args.cmd == "record":
        from .data.recording import record

        counts = asyncio.run(record(settings, args.seconds, args.out))
        print(json.dumps(counts))
        return 0
    if args.cmd == "replay":
        from .runner import run_replay

        db = args.db or (settings.db_path.parent / "replay.sqlite")
        summary = asyncio.run(run_replay(settings, args.input, db, args.report))
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0
    if args.cmd == "paper":
        from .runner import run_paper

        db = args.db or settings.db_path
        summary = asyncio.run(run_paper(settings, args.seconds, db, args.report))
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
