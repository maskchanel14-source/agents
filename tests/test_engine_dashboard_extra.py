"""Test discovery loop engine + endpoint dashboard export/kontrol lanjutan (T19)."""

from __future__ import annotations

import asyncio
import json

from aiohttp.test_utils import TestClient, TestServer

from bot.costs import make_market
from bot.dashboard.server import DashboardServer
from bot.decimal_utils import D
from test_dashboard_http import NOW, _make_engine


# ------------------------------------------------------------------ engine --

class _FakeGamma:
    def __init__(self, markets=None, boom=False):
        self._markets = markets or {}
        self.boom = boom

    async def discover_all(self, **kw):
        if self.boom:
            raise RuntimeError("gamma down")
        return self._markets, {"raw": len(self._markets), "parsed": len(self._markets),
                               "skipped": 0, "skip_reasons": {}}


def test_discovery_loop_registers_and_removes_markets(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        m_new = make_market("m-new", fee_rate=D("0.04"))
        engine.gamma = _FakeGamma({"m-new": m_new})
        task = asyncio.create_task(engine._discovery_loop())
        await asyncio.sleep(0.3)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert "m-new" in engine.hub.markets
        assert engine.status.api_ok is True
        assert engine.status.markets_total == 1

        # market hilang dari discovery berikutnya -> dibuang dari hub
        engine.gamma = _FakeGamma({})
        task = asyncio.create_task(engine._discovery_loop())
        await asyncio.sleep(0.3)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert "m-new" not in engine.hub.markets
        await engine.stop()
        db.close()
    asyncio.run(run())


def test_discovery_loop_failure_marks_api_down(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        engine.gamma = _FakeGamma(boom=True)
        task = asyncio.create_task(engine._discovery_loop())
        await asyncio.sleep(0.3)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert engine.status.api_ok is False
        assert any("gamma down" in e for e in engine.status.errors)
        await engine.stop()
        db.close()
    asyncio.run(run())


def test_health_loop_updates_ws_status(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        engine.hub.ws.stats["connected"] = 3
        task = asyncio.create_task(engine._health_loop())
        await asyncio.sleep(0.15)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await engine.stop()
        db.close()
    asyncio.run(run())


# --------------------------------------------------------------- dashboard --

def test_dashboard_token_export_and_unknowns(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        engine.scanner.scan(now_ms=NOW)
        server = DashboardServer(engine, host="127.0.0.1", port=0)
        client = TestClient(TestServer(server.app))
        await client.start_server()
        try:
            resp = await client.get("/api/token")
            assert resp.status == 200
            assert (await resp.json())["token"] == server.control_token

            # export opportunities CSV (ada header dari scan)
            resp = await client.get("/api/export/opportunities")
            assert resp.status == 200
            assert "text/csv" in resp.headers["Content-Type"]
            assert "opportunities.csv" in resp.headers["Content-Disposition"]
            text = await resp.text()
            assert "strategy" in text.splitlines()[0]

            # trades kosong tetap 200
            resp = await client.get("/api/export/trades")
            assert resp.status == 200

            # pnl JSON list
            resp = await client.get("/api/export/pnl")
            assert resp.status == 200
            assert isinstance(await resp.json(), list)

            resp = await client.get("/api/export/apapun")
            assert resp.status == 404

            # kontrol: aksi tak dikenal dengan token valid -> 400
            resp = await client.post("/api/control/terbang", json={},
                                     headers={"X-ARC-Token": server.control_token})
            assert resp.status == 400

            # resume: pause -> resume biasa
            await client.post("/api/control/pause", json={}, headers={"X-ARC-Token": server.control_token})
            resp = await client.post("/api/control/resume", json={}, headers={"X-ARC-Token": server.control_token})
            assert (await resp.json())["paused"] is False
        finally:
            await client.close()
            db.close()
    asyncio.run(run())


def test_dashboard_kill_then_resume_after_kill_cycle(tmp_path):
    """Gap T19: resume_after_kill dulu diiklankan (wajib CONFIRM) tapi tak diimplementasikan."""
    async def run():
        engine, db = await _make_engine(tmp_path)
        server = DashboardServer(engine, host="127.0.0.1", port=0)
        client = TestClient(TestServer(server.app))
        await client.start_server()
        hdr = {"X-ARC-Token": server.control_token}
        try:
            # kill tanpa konfirmasi -> 400
            resp = await client.post("/api/control/kill", json={}, headers=hdr)
            assert resp.status == 400
            # kill dengan konfirmasi -> risk halted + file kill switch ada
            resp = await client.post("/api/control/kill", json={"confirm": "CONFIRM"}, headers=hdr)
            assert (await resp.json())["killed"] is True
            assert engine.risk.is_halted()

            # resume tanpa konfirmasi -> 400, masih halted
            resp = await client.post("/api/control/resume_after_kill", json={}, headers=hdr)
            assert resp.status == 400
            assert engine.risk.is_halted()

            # resume dengan konfirmasi -> bersih, tidak halted lagi
            resp = await client.post("/api/control/resume_after_kill",
                                     json={"confirm": "CONFIRM"}, headers=hdr)
            body = await resp.json()
            assert resp.status == 200 and body["resumed"] is True
            assert not engine.risk.is_halted()
            assert not engine.risk.kill_switch

            # resume tetap butuh token
            resp = await client.post("/api/control/resume_after_kill", json={"confirm": "CONFIRM"})
            assert resp.status == 403
        finally:
            await client.close()
            db.close()
    asyncio.run(run())


def test_dashboard_log_tail_and_safe_state_error(tmp_path):
    async def run():
        engine, db = await _make_engine(tmp_path)
        # tulis log terstruktur + baris rusak
        log_dir = tmp_path / "logs"
        log_dir.mkdir(exist_ok=True)
        (log_dir / "bot.log").write_text(
            json.dumps({"level": "INFO", "msg": "halo", "ts": "t"}) + "\nbaris rusak\n",
            encoding="utf-8",
        )
        server = DashboardServer(engine, host="127.0.0.1", port=0)
        tail = server._log_tail(10)
        assert tail[0]["msg"] == "halo"
        assert tail[1]["msg"] == "baris rusak"  # JSON rusak -> fallback teks

        # engine.dashboard_state meledak -> _safe_state tidak ikut meledak
        class Boom:
            root = tmp_path
            cfg = {}
            def dashboard_state(self):
                raise RuntimeError("state boom")
        server2 = DashboardServer(Boom(), host="127.0.0.1", port=0)  # type: ignore[arg-type]
        assert server2._safe_state()["error"] == "state boom"
        db.close()
    asyncio.run(run())


def test_risk_resume_clears_halt_but_keeps_error_history(tmp_path):
    from bot.risk.limits import RiskConfig, RiskManager
    risk = RiskManager(RiskConfig(), root=tmp_path)
    risk.record_error()
    risk.trigger_kill_switch("manual test")
    assert risk.is_halted() and risk.kill_switch
    risk.resume()
    assert not risk.is_halted() and not risk.kill_switch
    snap = risk.snapshot()
    assert snap["kill_switch"] is False
