"""Test endpoint dashboard (index, state, SSE, kontrol dengan token, export).

Ini adalah "test endpoint/stream data" untuk verifikasi dashboard (misi 5b),
dijalankan tanpa browser. Screenshot browser: lihat scripts/take_screenshots.py.
"""

from __future__ import annotations

import asyncio

from aiohttp.test_utils import TestClient, TestServer

from bot.costs import CostConfig, CostModel, GasModel, make_market
from bot.dashboard.server import DashboardServer
from bot.data.feed import MarketDataHub
from bot.decimal_utils import D
from bot.engine import BotEngine
from bot.models import OrderBookSnapshot
from bot.risk.limits import RiskConfig, RiskManager
from bot.scanner import Scanner
from bot.state.db import StateDB
from bot.strategies.intra_market import IntraMarketBinary

NOW = 1_792_464_000_000


class _FakeWs:
    def __init__(self):
        self.assets_per_connection = 400
        self.stats = {"shards": 0, "connected": 0, "assets": 0, "reconnects": 0}
        self.on_event = None

    async def subscribe(self, ids): pass
    async def unsubscribe(self, ids): pass
    async def start(self): pass
    async def stop(self): pass


class _FakeClob:
    async def get_books(self, asset_ids, *, batch_size=20):
        return {}


async def _make_engine(tmp_path):
    hub = MarketDataHub(_FakeClob(), _FakeWs(), stale_after_ms=10**9)
    m = make_market("m1", fee_rate=D("0.04"))
    hub.markets["m1"] = m
    hub.asset_to_market["yes-m1"] = "m1"
    hub.asset_to_market["no-m1"] = "m1"
    hub.books["yes-m1"] = OrderBookSnapshot.from_levels("yes-m1", [], [("0.40", "300")], recv_ms=NOW)
    hub.books["no-m1"] = OrderBookSnapshot.from_levels("no-m1", [], [("0.55", "300")], recv_ms=NOW)
    model = CostModel(
        CostConfig(min_annualized_return=D("0"), safety_margin_usd=D("0.001"), max_capital_per_trade_usd=D("50")),
        GasModel(enabled=False),
    )
    db = StateDB(tmp_path / "d.db")
    risk = RiskManager(RiskConfig(), root=tmp_path)
    scanner = Scanner(hub, [IntraMarketBinary(model, {"enabled": True})], model, db)
    from bot.execution.simulator import PaperExecutor
    ex = PaperExecutor(model, db, risk, seed=1)
    engine = BotEngine(
        {"monitoring": {"log_dir": "logs"}, "execution": {}},
        hub=hub, scanner=scanner, executor=ex, risk=risk, db=db,
        gamma=None, mode="paper", root=tmp_path,
    )
    return engine, db


def test_dashboard_endpoints(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        engine.scanner.scan(now_ms=NOW)  # isi data
        server = DashboardServer(engine, host="127.0.0.1", port=0)
        client = TestClient(TestServer(server.app))
        await client.start_server()

        # index html dengan token ter-inject
        resp = await client.get("/")
        assert resp.status == 200
        html = await resp.text()
        assert "ARC-TERMINAL" in html
        assert server.control_token in html

        # static assets
        for path in ("/static/css/style.css", "/static/js/app.js"):
            r = await client.get(path)
            assert r.status == 200, path

        # state
        resp = await client.get("/api/state")
        assert resp.status == 200
        state = await resp.json()
        assert state["mode"] == "paper"
        assert "risk" in state and "status" in state and "logs" in state and "health" in state
        assert "opportunities" in state

        # SSE stream: minimal satu event
        resp = await client.get("/api/stream")
        assert resp.status == 200
        assert resp.headers["Content-Type"].startswith("text/event-stream")
        chunk = await resp.content.read(200)
        assert b"data: " in chunk
        resp.close()

        # kontrol tanpa token -> 403
        resp = await client.post("/api/control/pause", json={})
        assert resp.status == 403
        # dengan token
        resp = await client.post(
            "/api/control/pause",
            json={},
            headers={"X-ARC-Token": server.control_token},
        )
        assert resp.status == 200
        assert (await resp.json())["paused"] is True
        # kill butuh konfirmasi dua langkah
        resp = await client.post("/api/control/kill", json={}, headers={"X-ARC-Token": server.control_token})
        assert resp.status == 400
        resp = await client.post(
            "/api/control/kill",
            json={"confirm": "CONFIRM"},
            headers={"X-ARC-Token": server.control_token},
        )
        assert resp.status == 200
        assert engine.risk.kill_switch

        # export csv
        resp = await client.get("/api/export/opportunities")
        assert resp.status == 200
        text = await resp.text()
        assert "opportunity" in text or text  # minimal kosong pun valid csv

        await client.close()
        db.close()

    asyncio.run(run())


def test_dashboard_survives_engine_errors(tmp_path):
    """Dashboard crash/error TIDAK mengganggu bot — state handler menangkap error."""

    async def run():
        engine, db = await _make_engine(tmp_path)

        class BrokenEngine:
            cfg = engine.cfg
            root = engine.root
            mode = "paper"

            def dashboard_state(self):
                raise RuntimeError("boom")

        server = DashboardServer(BrokenEngine(), host="127.0.0.1", port=0)
        state = server._safe_state()
        assert "error" in state
        db.close()

    asyncio.run(run())
