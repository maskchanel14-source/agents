"""Recorder data orderbook live -> SQLite/NDJSON untuk replay & FEASIBILITY.

Jalankan dari mesin dengan akses jaringan Polymarket:

    python -m bot.record --minutes 120 --out data/recordings

Output:
- `orderbook_snapshots` di SQLite (timestamp, asset, bids, asks)
- `markets_meta.json` (metadata market hasil discovery)
- `run_summary.json` (statistik: market dipantau, event WS, dsb.)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from pathlib import Path

from .config.loader import ROOT, load_config, load_env
from .data.clob import ClobClient
from .data.gamma import GammaClient
from .data.http import HttpClient
from .data.ws_feed import MarketWsFeed
from .models import OrderBookSnapshot
from .monitoring import setup_logging
from .state.db import StateDB

log = logging.getLogger("bot.record")


class RecorderDB(StateDB):
    SCHEMA_EXTRA = """
    CREATE TABLE IF NOT EXISTS orderbook_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_ms INTEGER NOT NULL,
        asset_id TEXT NOT NULL,
        market_id TEXT,
        bids TEXT, asks TEXT, hash TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_ob_asset_ts ON orderbook_snapshots(asset_id, ts_ms);
    """

    def __init__(self, path):
        super().__init__(path)
        self._conn.executescript(self.SCHEMA_EXTRA)
        self._conn.commit()

    def save_book(self, snap: OrderBookSnapshot, market_id: str = "") -> None:
        import json as _json
        with self._lock:
            self._conn.execute(
                "INSERT INTO orderbook_snapshots (ts_ms, asset_id, market_id, bids, asks, hash) VALUES (?,?,?,?,?,?)",
                (
                    snap.recv_ms,
                    snap.asset_id,
                    market_id,
                    _json.dumps([[str(lv.price), str(lv.size)] for lv in snap.bids]),
                    _json.dumps([[str(lv.price), str(lv.size)] for lv in snap.asks]),
                    snap.hash,
                ),
            )
            self._conn.commit()


async def record(minutes: float, out_dir: Path, cfg: dict) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    db = RecorderDB(out_dir / "recording.db")
    http = await HttpClient.create()
    endpoints = cfg.get("endpoints", {})
    gamma = GammaClient(http, endpoints.get("gamma", "https://gamma-api.polymarket.com"))
    clob = ClobClient(http, endpoints.get("clob", "https://clob.polymarket.com"))

    markets, stats = await gamma.discover_all(
        closed=False,
        page_size=int(cfg.get("discovery", {}).get("page_size", 100)),
        skip_if_missing_fee=True,
    )
    (out_dir / "markets_meta.json").write_text(
        json.dumps(
            {
                mid: {
                    "slug": m.slug, "question": m.question, "event_id": m.event_id,
                    "neg_risk": m.neg_risk, "tick": str(m.tick_size),
                    "min_notional": str(m.min_order_notional),
                    "fee_rate": str(m.fee_schedule.rate), "end_date": str(m.end_date),
                    "yes": m.yes_asset_id, "no": m.no_asset_id,
                    "criteria": m.resolution_criteria[:500],
                }
                for mid, m in markets.items()
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    log.info("discovered %d markets (raw=%d skipped=%d)", len(markets), stats["raw"], stats["skipped"])

    asset_to_market = {}
    for mid, m in markets.items():
        asset_to_market[m.yes_asset_id] = mid
        asset_to_market[m.no_asset_id] = mid

    saved = {"books": 0, "ws_events": 0}

    async def on_event(etype: str, data: dict) -> None:
        saved["ws_events"] += 1
        if etype == "book":
            from .data.clob import parse_book
            try:
                snap = parse_book(data)
                if snap.asset_id:
                    db.save_book(snap, asset_to_market.get(snap.asset_id, ""))
                    saved["books"] += 1
            except Exception:
                pass

    ws = MarketWsFeed(
        endpoints.get("ws_market", "wss://ws-subscriptions-clob.polymarket.com/ws/market"),
        assets_per_connection=int(cfg.get("ws", {}).get("assets_per_connection", 400)),
        on_event=on_event,
    )
    await ws.start()
    await ws.subscribe(list(asset_to_market.keys()))

    t_end = time.time() + minutes * 60
    last_rest = 0.0
    while time.time() < t_end:
        await asyncio.sleep(5)
        # REST snapshot berkala sebagai cadangan (hash compare)
        if time.time() - last_rest > 60:
            last_rest = time.time()
            try:
                books = await clob.get_books(list(asset_to_market.keys())[:400])
                for snap in books.values():
                    db.save_book(snap, asset_to_market.get(snap.asset_id, ""))
                    saved["books"] += 1
            except Exception as exc:
                log.warning("rest snapshot failed: %s", exc)

    await ws.stop()
    summary = {
        "minutes": minutes,
        "markets": len(markets),
        "discovery_stats": stats,
        "books_saved": saved["books"],
        "ws_events": saved["ws_events"],
        "ws_stats": ws.stats,
    }
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    db.close()
    await http.close()
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Rekam orderbook live Polymarket untuk replay/feasibility")
    p.add_argument("--minutes", type=float, default=60)
    p.add_argument("--out", default="data/recordings")
    args = p.parse_args(argv)
    load_env()
    cfg = load_config()
    setup_logging(ROOT / "logs", level="INFO")
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    summary = asyncio.run(record(args.minutes, out, cfg))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
