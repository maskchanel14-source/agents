"""Test unit data layer (Gamma/CLOB/HTTP/WS/Feed), engine lifecycle, CLI, monitoring.

Network diganti fake — tidak ada egress nyata.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import pytest

from bot.data.clob import ClobClient, parse_book
from bot.data.feed import MarketDataHub
from bot.data.gamma import GammaClient, parse_fee_schedule, parse_market
from bot.data.http import HttpClient, RateLimiter
from bot.data.ws_feed import MarketWsFeed, WsShard, apply_price_change
from bot.models import FeeSchedule, OrderBookSnapshot
from bot.decimal_utils import D

NOW = 1_792_464_000_000


# ---------------------------------------------------------------- fixtures --

class FakeHttp:
    """Pengganti HttpClient untuk GammaClient/ClobClient."""

    def __init__(self, responses: dict) -> None:
        self.responses = responses  # (method, url-substr) -> list hasil per panggilan
        self.calls: list = []

    async def get_json(self, url, *, params=None, limiter=None, timeout=None):
        self.calls.append(("GET", url, params))
        for key, val in self.responses.items():
            if key in url:
                if isinstance(val, list):
                    return val.pop(0)
                return val
        raise RuntimeError(f"unexpected url {url}")

    async def post_json(self, url, *, json=None, limiter=None, headers=None, timeout=None):
        self.calls.append(("POST", url, json))
        for key, val in self.responses.items():
            if key in url:
                if isinstance(val, list):
                    return val.pop(0)
                return val
        return []


class FakeResp:
    def __init__(self, status, payload=None, headers=None):
        self.status = status
        self._payload = payload or {}
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self, content_type=None):
        return self._payload

    async def text(self):
        return json.dumps(self._payload)


class FakeSession:
    def __init__(self, queue):
        self.queue = list(queue)  # daftar FakeResp
        self.requests: list = []

    def request(self, method, url, **kw):
        self.requests.append((method, url, kw))
        return self.queue.pop(0)


class FakeWs:
    def __init__(self):
        self.assets_per_connection = 400
        self.subscribed = []
        self.stats = {"connected": True, "shards": 1, "assets": 0, "reconnects": 0}

    async def subscribe(self, ids):
        self.subscribed.extend(ids)
        self.stats["assets"] = len(self.subscribed)

    async def unsubscribe(self, ids):
        for i in ids:
            if i in self.subscribed:
                self.subscribed.remove(i)
        self.stats["assets"] = len(self.subscribed)

    async def start(self):
        pass

    async def stop(self):
        pass


# ------------------------------------------------------------------ gamma --

def test_parse_fee_schedule_variants():
    # bentuk ternormalisasi
    fs = parse_fee_schedule({"feeSchedule": {"rate": 0.04, "exponent": 1, "takerOnly": True, "rebateRate": 0}})
    assert fs.rate == D("0.04") and fs.exponent == 1 and fs.taker_only
    # bentuk mentah Gamma (baseFee/takerBaseFee + expScalar)
    fs2 = parse_fee_schedule({
        "feeSchedule": {"baseFee": "0.05", "makerBaseFee": "0", "takerBaseFee": "0.07",
                        "expVersion": 0, "expBase": 2, "expScalar": 10000000000000000},
    })
    assert fs2.rate == D("0.07") and fs2.exponent == 1 and fs2.taker_only
    # exponent 2 via expScalar=2e16
    fs3 = parse_fee_schedule({"feeSchedule": {"baseFee": "0.02", "expScalar": 20000000000000000}})
    assert fs3.exponent == 2 and fs3.rate == D("0.02")
    # bentuk fee lama
    fs4 = parse_fee_schedule({"fee": {"baseFee": "0.04", "expScalar": 10000000000000000}})
    assert fs4.rate == D("0.04") and fs4.taker_only
    # feesEnabled=false eksplisit -> fee 0 valid
    fs5 = parse_fee_schedule({"feesEnabled": False})
    assert fs5.fees_enabled is False and fs5.rate == 0 and fs5.available
    # kosong -> missing (fail-closed)
    assert not parse_fee_schedule({}).available


def test_parse_market_variants():
    raw = {
        "id": "m1", "slug": "s", "question": "Q?", "conditionId": "0xabc",
        "outcomes": "[\"Yes\", \"No\"]", "outcomePrices": "[\"0.4\", \"0.6\"]",
        "clobTokenIds": "[\"t1\", \"t2\"]", "orderPriceMinTickSize": "0.01",
        "orderMinSize": "5", "endDate": "2026-10-25T00:00:00Z",
        "events": [{"id": "e1"}],
    }
    m = parse_market(raw)
    assert m is not None and m.yes_asset_id == "t1" and m.no_asset_id == "t2"
    assert m.event_id == "e1" and m.tick_size == D("0.01")

    # v2 positionIds
    raw2 = dict(raw, positionIds='["p1","p2"]', version="v2", clobTokenIds=None)
    m2 = parse_market(raw2)
    assert m2 is not None and m2.version == "v2" and m2.yes_asset_id == "p1"

    # tanpa token -> None
    raw3 = dict(raw, clobTokenIds="[]", positionIds=None)
    assert parse_market(raw3) is None

    # neg-risk augmented dari event
    raw4 = dict(raw, events=[{"id": "e2", "trading": {"negRiskAugmented": True}, "enableNegRisk": True}])
    m4 = parse_market(raw4)
    assert m4.neg_risk and m4.neg_risk_augmented

    # field list JSON asli (bukan string)
    raw5 = dict(raw, outcomes=["Yes", "No"], outcomePrices=["0.3", "0.7"], clobTokenIds=["t1", "t2"])
    assert parse_market(raw5).yes_asset_id == "t1"

    # tags -> category
    raw6 = dict(raw, tags=[{"label": "Crypto"}])
    assert parse_market(raw6).category == "Crypto"


@pytest.mark.parametrize("fn", ["iter_markets", "iter_markets_keyset"])
def test_gamma_pagination(fn):
    async def run():
        page1 = [{"id": "1"}, {"id": "2"}]
        page2 = [{"id": "3"}]
        if fn == "iter_markets":
            http = FakeHttp({"/markets/keyset": [], "/markets": [page1, page2]})
        else:
            http = FakeHttp({"/markets/keyset": [
                {"data": page1, "next_cursor": "abc="},
                {"data": page2, "next_cursor": "LTE="},
            ]})
        client = GammaClient(http, "https://gamma/")  # type: ignore[arg-type]
        got = [m["id"] async for m in getattr(client, fn)(page_size=2)]
        assert got == ["1", "2", "3"]
    asyncio.run(run())


def test_gamma_discover_all_stats_and_skip(tmp_path):
    async def run():
        good = {
            "id": "m1", "slug": "s", "question": "Q?", "conditionId": "0x1",
            "outcomes": ["Yes", "No"], "outcomePrices": ["0.5", "0.5"],
            "clobTokenIds": ["t1", "t2"], "fee": {"baseFee": "0.04"},
        }
        bad = {"id": "m2"}  # parse gagal
        nofee = {
            "id": "m3", "slug": "s3", "question": "Q3?", "conditionId": "0x3",
            "outcomes": ["Yes", "No"], "outcomePrices": ["0.5", "0.5"],
            "clobTokenIds": ["t3", "t4"],  # tanpa fee -> skip jika diminta
        }
        http = FakeHttp({"/markets": [[good, bad, nofee]]})
        client = GammaClient(http, "https://gamma/")  # type: ignore[arg-type]
        markets, stats = await client.discover_all(skip_if_missing_fee=True, fetch_events_for_neg_risk=False)
        assert stats["raw"] == 3 and stats["parsed"] == 1 and stats["skipped"] == 2
        assert set(markets) == {"m1"}
        assert stats["skip_reasons"].get("parse_failed") == 1
        assert stats["skip_reasons"].get("fee_unknown") == 1
    asyncio.run(run())


# ------------------------------------------------------------------- clob --

def test_parse_book_sorts_levels_defensively():
    raw = {
        "asset_id": "a1", "timestamp": str(NOW),
        "bids": [{"price": "0.3", "size": "5"}, {"price": "0.4", "size": "2"}],  # tidak terurut
        "asks": [{"price": "0.7", "size": "3"}, {"price": "0.6", "size": "4"}],
        "tick_size": "0.01", "min_order_size": "5",
    }
    snap = parse_book(raw)
    assert [lv.price for lv in snap.bids] == [D("0.4"), D("0.3")]
    assert [lv.price for lv in snap.asks] == [D("0.6"), D("0.7")]
    assert snap.tick_size == D("0.01")


def test_clob_get_books_batches():
    async def run():
        calls = []

        class H:
            async def post_json(self, url, *, json=None, limiter=None, headers=None, timeout=None):
                calls.append(json)
                return [{"asset_id": item["token_id"], "bids": [], "asks": []} for item in json]
        client = ClobClient(H(), "https://clob/")  # type: ignore[arg-type]
        books = await client.get_books([f"a{i}" for i in range(5)], batch_size=2)
        assert len(books) == 5 and len(calls) == 3  # 2+2+1
    asyncio.run(run())


# -------------------------------------------------------------------- http --

def test_rate_limiter_token_bucket():
    rl = RateLimiter(calls_per_10s=10)  # 1 token/detik, kapasitas 1
    assert rl.tokens >= 1.0

    async def run():
        await rl.acquire()  # langsung
        t0 = time.monotonic()
        await rl.acquire()  # harus menunggu refill
        return time.monotonic() - t0
    waited = asyncio.run(run())
    assert waited > 0.05  # benar-benar throttle


def test_http_client_429_retry_then_success():
    async def run():
        sess = FakeSession([
            FakeResp(429, headers={"Retry-After": "0.01"}),
            FakeResp(200, {"ok": 1}),
        ])
        http = HttpClient(session=sess, backoff_base=0.01)
        out = await http.get_json("https://x/y")
        assert out == {"ok": 1}
        assert http.stats["errors_429"] == 1 and http.stats["retries"] == 1
    asyncio.run(run())


def test_http_client_4xx_raises_and_5xx_retries():
    async def run():
        sess = FakeSession([FakeResp(404, {"err": "nope"})])
        http = HttpClient(session=sess, backoff_base=0.01)
        with pytest.raises(RuntimeError, match="HTTP 404"):
            await http.get_json("https://x/y")

        sess2 = FakeSession([FakeResp(500), FakeResp(500), FakeResp(200, [1])])
        http2 = HttpClient(session=sess2, backoff_base=0.01, max_retries=3)
        assert await http2.get_json("https://x/z") == [1]
        assert http2.stats["retries"] == 2
    asyncio.run(run())


# ------------------------------------------------------------------ ws_feed --

def test_apply_price_change_set_and_delete():
    snap = OrderBookSnapshot.from_levels("a1", [("0.4", "2"), ("0.3", "5")], [("0.6", "4")], ts_ms=NOW, recv_ms=NOW)
    s2 = apply_price_change(snap, {"price": "0.35", "size": "7", "side": "BUY", "asset_id": "a1"})
    assert any(lv.price == D("0.35") and lv.size == D("7") for lv in s2.bids)
    s3 = apply_price_change(snap, {"price": "0.3", "size": "0", "side": "BUY", "asset_id": "a1"})
    assert all(lv.price != D("0.3") for lv in s3.bids)
    s4 = apply_price_change(snap, {"price": "0.55", "size": "1", "side": "SELL", "asset_id": "a1"})
    assert any(lv.price == D("0.55") for lv in s4.asks)


def test_ws_feed_dispatch_and_sharding():
    async def run():
        received = []

        async def on_event(etype, data):
            received.append((etype, data))

        feed = MarketWsFeed("wss://x", assets_per_connection=2, on_event=on_event)

        async def _fake_run_shard(shard):
            return None  # jangan buka koneksi nyata di test

        feed._run_shard = _fake_run_shard  # type: ignore[assignment]
        # dispatch langsung (tanpa koneksi nyata)
        await feed._dispatch({"type": "book", "market": "m", "asset_id": "a1",
                              "bids": [{"price": "0.4", "size": "1"}], "asks": []})
        assert received and received[0][0] == "book"
        # sharding subscribe
        await feed.subscribe([f"a{i}" for i in range(5)])
        assert len(feed.shards) >= 3  # 5 asset / 2 per shard
        stats = feed.stats
        assert "shards" in stats and "reconnects" in stats
        await feed.stop()
    asyncio.run(run())


# -------------------------------------------------------------------- feed --

def test_feed_hub_books_staleness_coverage():
    async def run():
        hub = MarketDataHub(ClobClient(FakeHttp({}), "https://clob/"), FakeWs(), stale_after_ms=1000)  # type: ignore[arg-type]
        await hub._on_ws_event("book", {
            "asset_id": "a1", "timestamp": str(NOW),
            "bids": [{"price": "0.4", "size": "2"}], "asks": [{"price": "0.6", "size": "2"}],
        })
        # paksa recv_ms ke NOW agar staleness deterministik
        b = hub.get_book("a1")
        hub.books["a1"] = OrderBookSnapshot.from_levels(
            b.asset_id, [(lv.price, lv.size) for lv in b.bids], [(lv.price, lv.size) for lv in b.asks],
            ts_ms=NOW, recv_ms=NOW,
        )
        snap = hub.get_book("a1")
        assert snap is not None and snap.bids[0].price == D("0.4")
        assert hub.is_fresh("a1", now_ms=NOW + 500)
        assert not hub.is_fresh("a1", now_ms=NOW + 5000)  # stale setelah 1s

        await hub._on_ws_event("price_change", {"price_changes": [
            {"asset_id": "a1", "price": "0.45", "size": "3", "side": "BUY"},
        ]})
        assert any(lv.price == D("0.45") for lv in hub.get_book("a1").bids)

        await hub._on_ws_event("last_trade_price", {"asset_id": "a1", "price": "0.41"})
        assert hub.get_book("a1").last_trade_price == D("0.41")

        cov = hub.coverage_snapshot()
        assert cov.stale_assets >= 0 and cov.ws_subscribed_assets == 0
        await hub._on_ws_event("market_resolved", {"id": "m-none"})
    asyncio.run(run())


def test_feed_register_and_remove_markets():
    from bot.models import MarketMeta

    def meta(mid, yes, no):
        return MarketMeta(
            market_id=mid, slug=mid, question="q", condition_id="0x1", event_id="e1",
            version="v1", yes_asset_id=yes, no_asset_id=no,
            neg_risk=False, neg_risk_augmented=False, tick_size=D("0.01"),
            min_order_notional=D("5"), fee_schedule=FeeSchedule(True, D("0"), D("1"), True, D("0")), end_date=None,
            category="Other", resolution_criteria="c",
        )

    async def run():
        hub = MarketDataHub(ClobClient(FakeHttp({}), "https://clob/"), FakeWs(), stale_after_ms=10**9)  # type: ignore[arg-type]
        await hub.register_markets([meta("m1", "y1", "n1"), meta("m2", "y2", "n2")])
        assert set(hub.markets) == {"m1", "m2"}
        assert hub.market_for_asset("y1").market_id == "m1"
        assert set(hub.ws.subscribed) == {"y1", "n1", "y2", "n2"}
        await hub.remove_markets(["m1"])
        assert set(hub.markets) == {"m2"}
        assert "y1" not in hub.ws.subscribed
    asyncio.run(run())


# ------------------------------------------------------------------- engine --

def test_engine_lifecycle_and_dashboard_state(tmp_path):
    from bot.costs import CostModel, GasModel
    from bot.engine import BotEngine
    from bot.execution.fill_model import FillModel, FillModelConfig
    from bot.execution.simulator import PaperExecutor
    from bot.risk.limits import RiskConfig, RiskManager
    from bot.scanner import Scanner
    from bot.state.db import StateDB
    from bot.strategies.intra_market import IntraMarketBinary
    from bot.models import MarketMeta, FeeSchedule

    cfg = {
        "discovery": {"refresh_seconds": 300, "page_size": 100},
        "monitoring": {"scan_interval_seconds": 0.05},
        "execution": {"cancel_on_shutdown": True},
    }
    hub = MarketDataHub(ClobClient(FakeHttp({}), "https://clob/"), FakeWs(), stale_after_ms=10**9)  # type: ignore[arg-type]
    model = CostModel()
    model.gas = GasModel(enabled=False)
    strat_cfg = {"A_intra_binary": {"enabled": True}}
    scanner = Scanner(hub, [IntraMarketBinary(model, strat_cfg["A_intra_binary"])], model, db=None)
    db = StateDB(tmp_path / "t.db")
    risk = RiskManager(RiskConfig(), root=tmp_path)
    executor = PaperExecutor(model, db, risk, FillModel(FillModelConfig()), seed=1)
    engine = BotEngine(cfg, hub=hub, scanner=scanner, executor=executor, risk=risk, db=db, mode="paper", root=tmp_path)

    async def run():
        await engine.run_for(0.25)
    asyncio.run(run())
    assert engine.status.running is False
    state = engine.dashboard_state()
    for key in ("status", "risk", "opportunities", "rejection_stats", "positions", "mode"):
        assert key in state
    assert state["mode"] == "paper"
    db.close()


def test_engine_survives_scanner_error(tmp_path):
    """Scan loop tidak boleh mati saat scanner melempar exception."""
    from bot.engine import BotEngine
    from bot.execution.fill_model import FillModel, FillModelConfig
    from bot.execution.simulator import PaperExecutor
    from bot.risk.limits import RiskConfig, RiskManager
    from bot.costs import CostModel, GasModel
    from bot.state.db import StateDB

    class BoomScanner:
        def scan(self):
            raise ValueError("boom")

    cfg = {"monitoring": {"scan_interval_seconds": 0.02}, "execution": {"cancel_on_shutdown": True}}
    hub = MarketDataHub(ClobClient(FakeHttp({}), "https://clob/"), FakeWs(), stale_after_ms=10**9)  # type: ignore[arg-type]
    db = StateDB(tmp_path / "t2.db")
    risk = RiskManager(RiskConfig(), root=tmp_path)
    model = CostModel()
    model.gas = GasModel(enabled=False)
    executor = PaperExecutor(model, db, risk, FillModel(FillModelConfig()), seed=1)
    engine = BotEngine(cfg, hub=hub, scanner=BoomScanner(), executor=executor, risk=risk, db=db, mode="paper", root=tmp_path)

    async def run():
        await engine.run_for(0.15)
    asyncio.run(run())
    assert any("boom" in e for e in engine.status.errors)
    db.close()


# ---------------------------------------------------------------------- cli --

def test_cli_parse_args_defaults_and_flags():
    from bot.cli import parse_args
    args = parse_args([])
    assert args.mode == "paper" and args.no_dashboard is False and args.duration is None
    args2 = parse_args(["--mode", "live", "--no-dashboard", "--port", "9999", "--duration", "5", "--no-open-browser"])
    assert args2.mode == "live" and args2.port == 9999 and args2.duration == 5 and args2.no_open_browser


# --------------------------------------------------------------- monitoring --

def test_monitoring_metrics_logging_notify(tmp_path):
    from bot.monitoring import Metrics, JsonFormatter, setup_logging, send_notification
    import logging

    m = Metrics()
    m.inc("orders", 3)
    m.set_gauge("cpu", 1.5)
    m.event("halt", "daily loss", level=2)
    snap = m.snapshot()
    assert snap["counters"]["orders"] == 3 and snap["gauges"]["cpu"] == 1.5 and snap["recent_events"]

    logger = setup_logging(tmp_path / "logs", level="INFO", max_bytes=1000, backups=1)
    logger.info("hello %s", "world")
    for h in logger.handlers:
        h.flush()
    log_files = list((tmp_path / "logs").glob("*.log*"))
    assert log_files and "hello world" in log_files[0].read_text(encoding="utf-8")

    fmt = JsonFormatter()
    rec = logging.LogRecord("n", logging.INFO, "p", 1, "msg %s", ("x",), None)
    assert json.loads(fmt.format(rec))["msg"] == "msg x"

    assert send_notification("x") is False  # default OFF


# ---------------------------------------------------------------- record/db --

def test_recorder_db_save_and_readback(tmp_path):
    from bot.record import RecorderDB
    db = RecorderDB(tmp_path / "rec.db")
    snap = OrderBookSnapshot.from_levels("a1", [("0.4", "1")], [("0.6", "2")], ts_ms=NOW)
    db.save_book(snap, market_id="m1")
    db.save_book(snap, market_id="m1")  # idempotent
    row = db._conn.execute("SELECT COUNT(*) FROM orderbook_snapshots").fetchone()
    assert row[0] == 2
    db.close()
