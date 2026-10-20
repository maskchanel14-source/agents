"""Test recorder end-to-end (network difake), CLI async_main, WS shard reconnect."""

from __future__ import annotations

import asyncio
import json

import aiohttp
import pytest

from bot.costs import make_market
from bot.decimal_utils import D


# ---------------------------------------------------------------- recorder --

class _FakeHttp:
    @classmethod
    async def create(cls, **kw):
        return cls()

    async def close(self):
        pass


class _FakeGamma:
    def __init__(self, http, base):
        pass

    async def discover_all(self, **kw):
        m = make_market("m1", fee_rate=D("0.04"))
        return {"m1": m}, {"raw": 1, "parsed": 1, "skipped": 0, "skip_reasons": {}}


class _FakeClob:
    def __init__(self, http, base):
        pass

    async def get_books(self, ids, **kw):
        return {}


class _FakeWsFeed:
    last = None

    def __init__(self, url, assets_per_connection=400, on_event=None):
        self.on_event = on_event
        self.subscribed = []
        _FakeWsFeed.last = self

    async def start(self):
        # simulasikan satu event book masuk saat start
        await self.on_event("book", {
            "event_type": "book", "asset_id": "yes-m1", "timestamp": "1792464000000",
            "bids": [{"price": "0.4", "size": "10"}], "asks": [{"price": "0.6", "size": "10"}],
        })

    async def subscribe(self, ids):
        self.subscribed = list(ids)

    async def stop(self):
        pass

    @property
    def stats(self):
        return {"shards": 1, "connected": 0, "assets": len(self.subscribed), "reconnects": 0}


def test_record_end_to_end_fake_network(tmp_path, monkeypatch):
    import bot.record as rec

    monkeypatch.setattr(rec, "HttpClient", _FakeHttp)
    monkeypatch.setattr(rec, "GammaClient", _FakeGamma)
    monkeypatch.setattr(rec, "ClobClient", _FakeClob)
    monkeypatch.setattr(rec, "MarketWsFeed", _FakeWsFeed)

    cfg = {"endpoints": {}, "discovery": {"page_size": 10}, "ws": {"assets_per_connection": 10}}
    summary = asyncio.run(rec.record(0, tmp_path, cfg))

    assert summary["markets"] == 1
    assert summary["books_saved"] == 1
    assert summary["ws_events"] == 1
    assert (tmp_path / "recording.db").exists()
    meta = json.loads((tmp_path / "markets_meta.json").read_text())
    assert meta["m1"]["yes"] == "yes-m1"
    saved = json.loads((tmp_path / "run_summary.json").read_text())
    assert saved["books_saved"] == 1


def test_record_main(monkeypatch, tmp_path):
    import bot.record as rec

    async def fake_record(minutes, out_dir, cfg):
        return {"minutes": minutes, "markets": 0, "books_saved": 0}

    monkeypatch.setattr(rec, "record", fake_record)
    assert rec.main(["--minutes", "0", "--out", str(tmp_path)]) == 0


# --------------------------------------------------------------------- cli --

class _FakeEngine:
    def __init__(self):
        self.started = False
        self.stopped = False

    async def start(self):
        self.started = True

    async def stop(self):
        self.stopped = True


def test_cli_live_rejected_falls_back_to_paper(monkeypatch):
    import bot.cli as cli

    captured = {}
    engine = _FakeEngine()

    async def fake_build(cfg, mode="paper", root=None):
        captured["mode"] = mode
        return engine

    monkeypatch.setattr(cli, "build_engine_async", fake_build)
    monkeypatch.setattr(cli, "live_trading_enabled", lambda: False)
    monkeypatch.delenv("LIVE_TRADING", raising=False)

    args = cli.parse_args(["--mode", "live", "--no-dashboard", "--duration", "0.1"])
    rc = asyncio.run(cli.async_main(args))
    assert rc == 0
    assert captured["mode"] == "paper"  # live DITOLAK -> fallback paper
    assert engine.started and engine.stopped


def test_cli_paper_short_run(monkeypatch):
    import bot.cli as cli

    engine = _FakeEngine()

    async def fake_build(cfg, mode="paper", root=None):
        assert mode == "paper"
        return engine

    monkeypatch.setattr(cli, "build_engine_async", fake_build)
    args = cli.parse_args(["--mode", "paper", "--no-dashboard", "--duration", "0.05"])
    assert asyncio.run(cli.async_main(args)) == 0
    assert engine.started and engine.stopped


# ------------------------------------------------------------------ ws_feed --

def test_ws_dispatch_swallows_handler_errors_and_unsubscribe():
    from bot.data.ws_feed import MarketWsFeed

    async def run():
        calls = []

        async def bad_handler(etype, data):
            calls.append(etype)
            raise RuntimeError("handler boom")

        feed = MarketWsFeed("wss://x", assets_per_connection=2, on_event=bad_handler)
        await feed._dispatch({"event_type": "book", "asset_id": "a1"})  # tidak boleh raise
        assert calls == ["book"]

        await feed.subscribe(["a1", "a2", "a3"])
        assert feed.stats["assets"] == 3 and len(feed.shards) == 2
        await feed.unsubscribe(["a1", "a3"])
        assert feed.stats["assets"] == 1
    asyncio.run(run())


class _FakeMsg:
    def __init__(self, data):
        self.type = aiohttp.WSMsgType.TEXT
        self.data = data


class _FakeWsConn:
    def __init__(self, feed):
        self.feed = feed
        self.sent = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def send_json(self, payload):
        self.sent.append(payload)

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        yield _FakeMsg(json.dumps({"event_type": "book", "asset_id": "a1", "bids": [], "asks": []}))
        yield _FakeMsg("bukan-json")  # JSON rusak harus di-skip, bukan crash


class _FakeSession:
    def __init__(self, feed=None, fail=False):
        self.feed = feed
        self.fail = fail
        self.attempts = 0

    def ws_connect(self, url, heartbeat=None):
        self.attempts += 1
        if self.fail:
            raise RuntimeError("connect gagal")
        return _FakeWsConn(self.feed)


def test_ws_shard_processes_messages_then_stops():
    from bot.data.ws_feed import MarketWsFeed, WsShard

    async def run():
        received = []
        feed = MarketWsFeed("wss://x", reconnect_min=0.01, reconnect_max=0.02, on_event=None)

        async def on_event(etype, data):
            received.append(etype)
            feed._running = False  # hentikan setelah event pertama

        feed.on_event = on_event
        feed._running = True
        feed._session = _FakeSession(feed)
        shard = WsShard(shard_id=0, asset_ids={"a1"})
        await asyncio.wait_for(feed._run_shard(shard), timeout=5)
        assert received == ["book"]
        assert shard.connected is False
    asyncio.run(run())


def test_ws_shard_reconnects_with_backoff_on_failure():
    from bot.data.ws_feed import MarketWsFeed, WsShard

    async def run():
        feed = MarketWsFeed("wss://x", reconnect_min=0.01, reconnect_max=0.02)
        feed._running = True
        session = _FakeSession(feed, fail=True)
        feed._session = session
        shard = WsShard(shard_id=0, asset_ids={"a1"})
        task = asyncio.create_task(feed._run_shard(shard))
        # beri waktu beberapa percobaan reconnect
        for _ in range(100):
            await asyncio.sleep(0.05)
            if shard.reconnects >= 2:
                break
        feed._running = False
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert shard.reconnects >= 2
        assert session.attempts >= 2
    asyncio.run(run())
