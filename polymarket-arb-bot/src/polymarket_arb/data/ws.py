"""CLOB market-channel WebSocket client with heartbeat, idle watchdog and reconnect.

On every (re)connect: subscribe to all assets, expect a fresh ``book`` snapshot per
asset (``initial_dump`` defaults to true), and invalidate all books on disconnect so
stale data is never used for trading decisions.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Any

import websockets

from .book_store import BookStore

log = logging.getLogger("polymarket_arb.ws")


def now_ms() -> int:
    return int(time.time() * 1000)


def parse_frame(text: str) -> list[dict[str, Any]]:
    """Parse one text frame into a list of event dicts (ignores PONG/heartbeats)."""
    if not text or text.strip().upper() in ("PONG", "PING"):
        return []
    data = json.loads(text)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    return []


class MarketWsClient:
    def __init__(
        self,
        url: str,
        store: BookStore,
        asset_ids: Callable[[], list[str]],
        *,
        ping_interval_s: float = 10.0,
        idle_timeout_s: float = 30.0,
        backoff_base_s: float = 1.0,
        backoff_max_s: float = 60.0,
        clock_ms: Callable[[], int] = now_ms,
        on_event: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.url = url
        self.store = store
        self._asset_ids = asset_ids
        self.ping_interval_s = ping_interval_s
        self.idle_timeout_s = idle_timeout_s
        self.backoff_base_s = backoff_base_s
        self.backoff_max_s = backoff_max_s
        self.clock_ms = clock_ms
        self.on_event = on_event
        self.connects = 0
        self.disconnects = 0
        self.messages = 0

    def _subscribe_payload(self) -> str:
        return json.dumps(
            {
                "assets_ids": self._asset_ids(),
                "type": "market",
                "custom_feature_enabled": True,
            }
        )

    async def run(self, stop: asyncio.Event) -> None:
        attempt = 0
        while not stop.is_set():
            try:
                await self._session(stop)
                attempt = 0
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - reconnect on any transport error
                self.disconnects += 1
                self.store.invalidate_all("disconnect")
                delay = min(self.backoff_max_s, self.backoff_base_s * (2**attempt))
                attempt += 1
                log.warning("ws disconnected: %s; retry in %.1fs", type(exc).__name__, delay)
                try:
                    await asyncio.wait_for(stop.wait(), timeout=delay)
                except TimeoutError:
                    pass

    async def _session(self, stop: asyncio.Event) -> None:
        async with websockets.connect(self.url, ping_interval=None, open_timeout=10, max_size=2**23) as ws:
            self.connects += 1
            await ws.send(self._subscribe_payload())
            heartbeat = asyncio.create_task(self._heartbeat(ws, stop))
            try:
                while not stop.is_set():
                    try:
                        frame = await asyncio.wait_for(ws.recv(), timeout=self.idle_timeout_s)
                    except TimeoutError as exc:
                        raise ConnectionError("idle timeout") from exc
                    text = frame if isinstance(frame, str) else frame.decode("utf-8", "replace")
                    try:
                        msgs = parse_frame(text)
                    except ValueError:  # malformed JSON frame: count and keep the session
                        self.store.count_external("malformed_frame")
                        continue
                    for msg in msgs:
                        self.messages += 1
                        try:
                            self.store.apply_message(msg, self.clock_ms())
                        except (ValueError, TypeError, KeyError, ArithmeticError):
                            # one bad event must not drop the session; the asset is invalidated
                            self.store.invalidate(str(msg.get("asset_id", "")), "malformed_event")
                            self.store.count_external("malformed_event")
                            continue
                        if self.on_event is not None:
                            self.on_event(msg)
            finally:
                heartbeat.cancel()
                self.store.invalidate_all("session_end")

    async def _heartbeat(self, ws: Any, stop: asyncio.Event) -> None:
        while not stop.is_set():
            await asyncio.sleep(self.ping_interval_s)
            await ws.send("PING")
