"""Soak dashboard (loop request berulang) + uji skala scanner (500 market)."""

from __future__ import annotations

import asyncio
import time

from aiohttp.test_utils import TestClient, TestServer

from bot.costs import CostConfig, CostModel, GasModel, make_market
from bot.dashboard.server import DashboardServer
from bot.data.feed import MarketDataHub
from bot.decimal_utils import D
from bot.models import OrderBookSnapshot
from bot.scanner import Scanner
from bot.strategies.intra_market import IntraMarketBinary
from test_dashboard_http import _FakeClob, _FakeWs, _make_engine

NOW = 1_792_464_000_000


def test_dashboard_soak_200_state_requests(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        server = DashboardServer(engine, host="127.0.0.1", port=0)
        client = TestClient(TestServer(server.app))
        await client.start_server()
        errors = 0
        t0 = time.monotonic()
        try:
            for i in range(200):
                engine.scanner.scan(now_ms=NOW)  # state berubah tiap iterasi
                resp = await client.get("/api/state")
                if resp.status != 200:
                    errors += 1
                    continue
                state = await resp.json()
                assert state["mode"] == "paper"
        finally:
            elapsed = time.monotonic() - t0
            await client.close()
            db.close()
        assert errors == 0
        # 200 request + scan harus jauh di bawah ambang soak (biasanya <5s)
        assert elapsed < 30
        return elapsed
    asyncio.run(run())


def test_dashboard_sse_multiple_events(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        server = DashboardServer(engine, host="127.0.0.1", port=0)
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            resp = await client.get("/api/stream")
            assert resp.status == 200
            chunks = b""
            async def _read():
                nonlocal chunks
                while chunks.count(b"data: ") < 3:
                    chunk = await resp.content.read(4096)
                    if not chunk:
                        break
                    chunks += chunk
            await asyncio.wait_for(_read(), timeout=20)
            resp.close()
            assert chunks.count(b"data: ") >= 3
        finally:
            await client.close()
            db.close()
    asyncio.run(run())


def test_scanner_scale_500_markets():
    hub = MarketDataHub(_FakeClob(), _FakeWs(), stale_after_ms=10**9)
    model = CostModel(
        CostConfig(min_annualized_return=D("0"), safety_margin_usd=D("0.001"), max_capital_per_trade_usd=D("50")),
        GasModel(enabled=False),
    )
    n = 500
    for i in range(n):
        m = make_market(f"mkt-{i}", fee_rate=D("0.04"))
        hub.markets[m.market_id] = m
        hub.asset_to_market[m.yes_asset_id] = m.market_id
        hub.asset_to_market[m.no_asset_id] = m.market_id
        # setengah market punya arb (Σ ask < 1), setengah tidak
        yes_ask, no_ask = ("0.40", "0.55") if i % 2 == 0 else ("0.48", "0.55")
        hub.books[m.yes_asset_id] = OrderBookSnapshot.from_levels(m.yes_asset_id, [], [(yes_ask, "300")], recv_ms=NOW)
        hub.books[m.no_asset_id] = OrderBookSnapshot.from_levels(m.no_asset_id, [], [(no_ask, "300")], recv_ms=NOW)

    scanner = Scanner(hub, [IntraMarketBinary(model, {"enabled": True})], model, db=None)
    t0 = time.monotonic()
    result = scanner.scan(now_ms=NOW)
    elapsed = time.monotonic() - t0
    assert len(result.opportunities) >= n // 2  # minimal separuh terdeteksi
    valid = len(result.ranked_valid)
    assert valid > 0
    assert elapsed < 10, f"scan 500 market terlalu lambat: {elapsed:.2f}s"
    # scan kedua (dedup/_seen) tetap berfungsi & cepat
    t0 = time.monotonic()
    result2 = scanner.scan(now_ms=NOW)
    assert time.monotonic() - t0 < 10
    assert len(result2.opportunities) == len(result.opportunities)
