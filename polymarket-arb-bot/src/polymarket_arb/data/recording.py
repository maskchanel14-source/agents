"""Record raw market data to JSONL and replay it deterministically (backtest).

Format (one JSON object per line):
  {"type":"meta","created_ms":..,"events":[<gamma event>...]}
  {"type":"ws","t":<recv_ms>,"msg":<raw ws event>}
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from ..config import Settings
from ..universe import build_universe
from .book_store import BookStore
from .gamma import GammaClient
from .http import JsonHttp
from .ws import MarketWsClient, parse_frame

log = logging.getLogger("polymarket_arb.recording")


def iter_records(path: Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


async def fetch_events(settings: Settings) -> list[dict[str, Any]]:
    http = JsonHttp(
        settings.data.gamma_base,
        timeout_s=settings.data.http_timeout_s,
        max_requests_per_10s=settings.data.max_requests_per_10s,
    )
    try:
        gamma = GammaClient(http, settings.data.cache_ttl_s)
        return await gamma.list_events(
            page_size=settings.data.events_page_size,
            max_events=settings.data.max_events,
        )
    finally:
        await http.aclose()


async def record(settings: Settings, seconds: float, out: Path) -> dict[str, int]:
    events = await fetch_events(settings)
    uni = build_universe(
        events,
        max_assets=settings.data.max_assets,
        exclude_ambiguous=settings.data.exclude_ambiguous,
        blacklist_condition_ids=settings.data.blacklist_condition_ids,
    )
    assets = uni.assets
    out.parent.mkdir(parents=True, exist_ok=True)
    counts = {"ws_messages": 0, "assets": len(assets)}
    store = BookStore()
    with out.open("w", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "type": "meta",
                    "created_ms": int(time.time() * 1000),
                    "events": events,
                }
            )
            + "\n"
        )

        def sink(msg: dict[str, Any]) -> None:
            counts["ws_messages"] += 1
            fh.write(
                json.dumps(
                    {"type": "ws", "t": int(time.time() * 1000), "msg": msg},
                    separators=(",", ":"),
                )
                + "\n"
            )

        client = MarketWsClient(settings.data.ws_url, store, lambda: assets, on_event=sink)
        stop = asyncio.Event()
        task = asyncio.create_task(client.run(stop))
        try:
            await asyncio.sleep(seconds)
        finally:
            stop.set()
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception) as exc:  # noqa: BLE001
                log.debug("recorder shutdown: %s", type(exc).__name__)
    return counts


def load_universe_from_recording(path: Path, **kwargs: Any):
    for rec in iter_records(path):
        if rec.get("type") == "meta":
            return build_universe(rec.get("events") or [], **kwargs)
    raise ValueError("recording has no meta record")


def ws_messages(path: Path) -> list[tuple[int, dict[str, Any]]]:
    out: list[tuple[int, dict[str, Any]]] = []
    for rec in iter_records(path):
        if rec.get("type") == "ws":
            for msg in parse_frame(json.dumps(rec["msg"])):
                out.append((int(rec["t"]), msg))
    out.sort(key=lambda x: x[0])
    return out
