"""Run modes: replay (backtest on a recording), paper (live data, simulated fills), live (gated)."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .config import LIVE_CONFIRMATION_FILE, Settings, check_live_gate
from .data.book_store import BookStore as _BookStore
from .data.recording import fetch_events, load_universe_from_recording, ws_messages
from .data.ws import MarketWsClient
from .engine import Engine
from .execution.book_view import PaperBookView
from .execution.paper import PaperExecutor
from .risk import KillSwitch
from .state.store import StateStore
from .universe import Universe, build_universe


def universe_kwargs(settings: Settings) -> dict[str, Any]:
    return {
        "max_assets": settings.data.max_assets,
        "exclude_ambiguous": settings.data.exclude_ambiguous,
        "blacklist_condition_ids": settings.data.blacklist_condition_ids,
    }


log = logging.getLogger("polymarket_arb.runner")


def _register(store: _BookStore, uni: Universe) -> None:
    for m in uni.binaries:
        for tok in (m.yes, m.no):
            store.register(tok.asset_id, m.tick_size, m.min_order_size, m.condition_id)
    for g in uni.groups:
        for m in g.markets:
            for tok in (m.yes, m.no):
                store.register(tok.asset_id, m.tick_size, m.min_order_size, m.condition_id)


def _summary(engine: Engine, store: StateStore, stats: Counter, extra: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": store.mode,
        "cycles": engine.cycles,
        "opportunities_recorded": store.count("opportunities"),
        "opportunities_valid": store.count("opportunities", "valid=1"),
        "executed_pairs": store.count("executed"),
        "orders": store.count("orders"),
        "realized_pnl_usdc": str(store.pnl_by_kind().get("realized", 0)),
        "expected_pending_resolution_pnl_usdc": str(
            store.pnl_by_kind().get("expected_pending_resolution", 0)
        ),
        "stats": {k: int(v) for k, v in sorted(stats.items())},
        **extra,
    }


def write_report(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")


async def run_replay(settings: Settings, recording: Path, db: Path, report: Path | None) -> dict[str, Any]:
    uni = load_universe_from_recording(recording, **universe_kwargs(settings))
    if db.exists():
        db.unlink()
    store = StateStore(db, mode="paper")
    stats: Counter = Counter()
    books = _BookStore()
    _register(books, uni)
    view = PaperBookView(books)
    executor = PaperExecutor(store, view, uni.markets_by_asset(), settings.thresholds.max_book_age_ms)
    kill = KillSwitch(Path(str(db) + ".KILL"))  # isolated per run
    engine = Engine(
        settings=settings,
        universe=uni,
        books=view,
        store=store,
        executor=executor,
        kill_switch=kill,
        stats=stats,
    )
    interval = settings.data.scan_interval_ms
    next_scan: int | None = None
    msgs = ws_messages(recording)
    for t, msg in msgs:
        # virtual clock: fire every scheduled scan that falls before this message
        while next_scan is not None and next_scan <= t:
            await engine.cycle(next_scan)
            next_scan += interval
        books.apply_message(msg, t)
        if next_scan is None:
            next_scan = t + interval
    stats["replay:messages"] = len(msgs)
    summary = _summary(
        engine,
        store,
        stats,
        {
            "recording": str(recording),
            "assets": len(uni.assets),
            "book_counters": dict(books.counters),
            "universe_skipped": dict(uni.skipped),
            "neg_risk_groups": len(uni.groups),
        },
    )
    store.close()
    if report is not None:
        write_report(report, summary)
    return summary


async def run_paper(settings: Settings, seconds: float, db: Path, report: Path | None) -> dict[str, Any]:
    events = await fetch_events(settings)
    uni = build_universe(events, **universe_kwargs(settings))
    assets = uni.assets
    store = StateStore(db, mode="paper")
    stats: Counter = Counter()
    books = _BookStore()
    _register(books, uni)
    view = PaperBookView(books)
    executor = PaperExecutor(store, view, uni.markets_by_asset(), settings.thresholds.max_book_age_ms)
    kill = KillSwitch(settings.kill_switch_path)
    engine = Engine(
        settings=settings,
        universe=uni,
        books=view,
        store=store,
        executor=executor,
        kill_switch=kill,
        stats=stats,
    )
    client = MarketWsClient(settings.data.ws_url, books, lambda: assets)
    stop = asyncio.Event()
    ws_task = asyncio.create_task(client.run(stop))
    engine_task = asyncio.create_task(
        engine.run(stop, settings.data.scan_interval_ms / 1000, lambda: int(time.time() * 1000))
    )
    started = time.time()
    try:
        while time.time() - started < seconds and not stop.is_set():
            await asyncio.sleep(1.0)
            if kill.is_active():
                log.critical("kill switch active; stopping paper run")
                break
    finally:
        stop.set()
        for t in (ws_task, engine_task):
            try:
                await asyncio.wait_for(t, timeout=15)
            except (TimeoutError, asyncio.CancelledError, Exception):  # noqa: BLE001
                t.cancel()
    summary = _summary(
        engine,
        store,
        stats,
        {
            "seconds": seconds,
            "assets": len(assets),
            "ws_connects": client.connects,
            "ws_disconnects": client.disconnects,
            "ws_messages": client.messages,
            "book_counters": dict(books.counters),
            "universe_skipped": dict(uni.skipped),
            "neg_risk_groups": len(uni.groups),
        },
    )
    store.close()
    if report is not None:
        write_report(report, summary)
    return summary


async def run_live(settings: Settings, env: dict[str, str]) -> None:
    """Live mode. Refuses unless the env gate AND the confirmation file are present.

    Even with the gate open, no signer is configured in this build, so the live
    executor raises LiveNotArmed before any order can be created.
    """
    from .execution.live import LiveExecutor, LiveNotArmed

    check_live_gate("live", env, LIVE_CONFIRMATION_FILE)
    store = StateStore(settings.db_path, mode="live")
    try:
        LiveExecutor(store, None, None, env=env).assert_armed()
    except LiveNotArmed:
        store.log_event(
            int(time.time() * 1000),
            "critical",
            "live_not_armed",
            {"reason": "no signer"},
        )
        raise
    finally:
        store.close()
