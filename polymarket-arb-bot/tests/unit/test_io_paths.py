"""I/O paths tested without the network: HTTP retry/throttle, Gamma/CLOB clients,
L2 auth helpers, live executor with FAKE signer/transport, CLI, paper/record runners."""

from __future__ import annotations

import json
import logging

import httpx
import pytest

from polymarket_arb import cli
from polymarket_arb.config import LiveGateError
from polymarket_arb.data import recording as rec_mod
from polymarket_arb.data.clob import ClobClient
from polymarket_arb.data.gamma import GammaClient
from polymarket_arb.data.http import JsonHttp, TokenBucket
from polymarket_arb.domain import Side
from polymarket_arb.execution.clob_auth import ApiCredentials, l2_headers, l2_signature
from polymarket_arb.execution.live import LiveExecutor, LiveNotArmed
from polymarket_arb.execution.paper import ExecutionResult  # noqa: F401 (import smoke)
from polymarket_arb.money import dec
from polymarket_arb.monitoring import JsonFormatter, setup_logging
from polymarket_arb.monitoring.metrics import summarize_counters
from polymarket_arb.runner import run_live, run_paper, run_replay
from polymarket_arb.state.store import StateStore
from tests.fixtures.synth import universe_events
from tests.unit.helpers import NOW, seeded
from tests.unit.test_execution_state import arb_opp

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
RECORDING = ROOT / "tests" / "fixtures" / "recordings" / "synthetic_replay.jsonl"


def mock_client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


class TestJsonHttp:
    @pytest.mark.asyncio
    async def test_success_returns_json(self):
        http = JsonHttp("https://x.example", client=mock_client(lambda r: httpx.Response(200, json={"a": 1})))
        assert await http.get_json("/p") == {"a": 1}

    @pytest.mark.asyncio
    async def test_429_then_success_retries(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            return httpx.Response(429) if calls["n"] == 1 else httpx.Response(200, json=[1])

        http = JsonHttp("https://x.example", client=mock_client(handler), retries=2)
        assert await http.get_json("/p") == [1]
        assert calls["n"] == 2

    @pytest.mark.asyncio
    async def test_client_error_not_retried(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            return httpx.Response(404)

        http = JsonHttp("https://x.example", client=mock_client(handler), retries=3)
        with pytest.raises(httpx.HTTPStatusError):
            await http.get_json("/p")
        assert calls["n"] == 1

    @pytest.mark.asyncio
    async def test_transport_error_exhausts_retries(self):
        def handler(req):
            raise httpx.ConnectError("boom", request=req)

        http = JsonHttp("https://x.example", client=mock_client(handler), retries=1)
        with pytest.raises(Exception):  # noqa: B017 - surfaces the last transport error
            await http.get_json("/p")
        await http.aclose()

    @pytest.mark.asyncio
    async def test_token_bucket_throttles(self):
        b = TokenBucket(rate=2, per_s=10.0)
        await b.acquire()
        await b.acquire()
        assert b.tokens < 1.0  # third acquire must wait for refill


class TestClients:
    @pytest.mark.asyncio
    async def test_gamma_paginates_and_caches(self):
        pages = {"0": [{"id": str(i)} for i in range(2)], "2": []}
        calls = []

        def handler(req):
            off = req.url.params.get("offset")
            calls.append(off)
            return httpx.Response(200, json=pages.get(off, []))

        g = GammaClient(JsonHttp("https://g.example", client=mock_client(handler)), cache_ttl_s=300)
        out = await g.list_events(page_size=2, max_events=10)
        assert [e["id"] for e in out] == ["0", "1"]
        await g.list_events(page_size=2, max_events=10)  # served from cache
        assert calls == ["0", "2"]

    @pytest.mark.asyncio
    async def test_gamma_non_list_page_stops(self):
        g = GammaClient(JsonHttp("https://g", client=mock_client(lambda r: httpx.Response(200, json={}))))
        assert await g.list_events() == []

    @pytest.mark.asyncio
    async def test_clob_book(self):
        c = ClobClient(
            JsonHttp("https://c", client=mock_client(lambda r: httpx.Response(200, json={"bids": []})))
        )
        assert await c.get_book("tok") == {"bids": []}

    @pytest.mark.asyncio
    async def test_clob_non_dict_rejected(self):
        c = ClobClient(JsonHttp("https://c", client=mock_client(lambda r: httpx.Response(200, json=[1]))))
        with pytest.raises(TypeError):
            await c.get_book("tok")


class TestAuth:
    def test_signature_deterministic_and_urlsafe(self):
        secret = "c2VjcmV0LWtleS1mb3ItdGVzdHM="  # test vector only, not a real credential
        s1 = l2_signature(secret, "1700000000", "GET", "/orders", "")
        s2 = l2_signature(secret, "1700000000", "GET", "/orders", "")
        assert s1 == s2 and "+" not in s1 and "/" not in s1
        assert s1 != l2_signature(secret, "1700000001", "GET", "/orders", "")

    def test_headers_have_all_l2_fields(self):
        creds = ApiCredentials(api_key="k", secret="c2VjcmV0", passphrase="p", address="0xabc")
        h = l2_headers(creds, "1", "post", "/order", "{}")
        assert set(h) == {
            "POLY_ADDRESS",
            "POLY_SIGNATURE",
            "POLY_TIMESTAMP",
            "POLY_API_KEY",
            "POLY_PASSPHRASE",
        }

    def test_credentials_repr_masked(self):
        creds = ApiCredentials(api_key="SECRETKEY", secret="SECRETVALUE", passphrase="PHRASE", address="0x1")
        text = repr(creds)
        assert "SECRETVALUE" not in text and "PHRASE" not in text and "SECRETKEY" not in text


class FakeSigner:
    def sign_order(self, typed):
        return "0xfake-signature"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.posted = []

    async def post_order(self, body):
        self.posted.append(body)
        return self.responses.pop(0)

    async def cancel_all(self):
        return {"canceled": 0}


@pytest.fixture
def armed(tmp_path):
    conf = tmp_path / "LIVE_CONFIRMED.txt"
    conf.write_text("operator confirmed (test)")
    store = StateStore(tmp_path / "live.sqlite", mode="live")
    yield store, conf
    store.close()


class TestLiveWithFakes:
    @pytest.mark.asyncio
    async def test_fake_transport_fills_both_legs(self, armed, tmp_path):
        store, conf = armed
        su, uni = seeded()
        opp = arb_opp(su, uni)
        t = FakeTransport([{"success": True}, {"success": True}])
        ex = LiveExecutor(store, t, FakeSigner(), env={"LIVE_TRADING": "true"}, confirmation_file=conf)
        res = await ex.execute(opp, NOW)
        assert res.status == "filled" and len(t.posted) == 2
        body = t.posted[0]
        assert body["orderType"] == "FOK"
        assert body["order"]["signature"] == "0xfake-signature"
        assert "opp_id" not in body["order"]  # no client-only fields leak into the payload

    @pytest.mark.asyncio
    async def test_first_leg_rejected_cancels_cleanly(self, armed):
        store, conf = armed
        su, uni = seeded()
        opp = arb_opp(su, uni)
        t = FakeTransport([{"success": False, "errorMsg": "no liquidity"}])
        ex = LiveExecutor(store, t, FakeSigner(), env={"LIVE_TRADING": "true"}, confirmation_file=conf)
        res = await ex.execute(opp, NOW)
        assert res.status == "cancelled" and res.reason == "order_rejected"
        assert res.fills == ()

    @pytest.mark.asyncio
    async def test_sibling_rejected_after_fill_is_partial(self, armed):
        store, conf = armed
        su, uni = seeded()
        opp = arb_opp(su, uni)
        t = FakeTransport([{"success": True}, {"success": False, "errorMsg": "x"}])
        ex = LiveExecutor(store, t, FakeSigner(), env={"LIVE_TRADING": "true"}, confirmation_file=conf)
        res = await ex.execute(opp, NOW)
        assert res.status == "partial" and len(res.fills) == 1
        assert store.count("events", "kind='unhedged_partial'") == 1

    @pytest.mark.asyncio
    async def test_live_refuses_without_gate(self, armed):
        store, conf = armed
        with pytest.raises(LiveGateError):
            LiveExecutor(store, FakeTransport([]), FakeSigner(), env={}, confirmation_file=conf)

    @pytest.mark.asyncio
    async def test_cancel_all_delegates(self, armed):
        store, conf = armed
        ex = LiveExecutor(
            store, FakeTransport([]), FakeSigner(), env={"LIVE_TRADING": "true"}, confirmation_file=conf
        )
        assert await ex.cancel_all() == 0

    @pytest.mark.asyncio
    async def test_unarmed_cancel_all_raises(self, armed):
        store, conf = armed
        ex = LiveExecutor(store, None, None, env={"LIVE_TRADING": "true"}, confirmation_file=conf)
        with pytest.raises(LiveNotArmed):
            await ex.cancel_all()


def test_engine_partial_result_engages_kill_switch(settings, tmp_path):
    from polymarket_arb.engine import CycleReport, Engine
    from polymarket_arb.execution.base import ExecutionResult as ER
    from polymarket_arb.execution.book_view import PaperBookView
    from polymarket_arb.risk import KillSwitch

    su, uni = seeded()
    st = StateStore(tmp_path / "p.sqlite", mode="paper")
    kill = KillSwitch(tmp_path / "KILL")
    eng = Engine(
        settings=settings, universe=uni, books=PaperBookView(su), store=st, executor=None, kill_switch=kill
    )
    opp = arb_opp(su, uni)
    eng._after_execution(opp, ER(status="partial", reason="x"), "m", "e", NOW, CycleReport(now_ms=NOW))
    assert kill.is_active()
    st.close()


def test_engine_repeated_order_failures_open_circuit(settings, tmp_path):
    from polymarket_arb.engine import CycleReport, Engine
    from polymarket_arb.execution.base import ExecutionResult as ER
    from polymarket_arb.execution.book_view import PaperBookView
    from polymarket_arb.risk import KillSwitch

    su, uni = seeded()
    st = StateStore(tmp_path / "p.sqlite", mode="paper")
    eng = Engine(
        settings=settings,
        universe=uni,
        books=PaperBookView(su),
        store=st,
        executor=None,
        kill_switch=KillSwitch(tmp_path / "KILL"),
    )
    opp = arb_opp(su, uni)
    for _ in range(settings.limits.max_consecutive_errors):
        eng._after_execution(
            opp, ER(status="cancelled", reason="order_rejected"), "m", "e", NOW, CycleReport(now_ms=NOW)
        )
    assert eng.risk.circuit.is_open(NOW)
    assert st.count("events", "kind='circuit_open'") == 1
    st.close()


class TestRunnersAndCli:
    def test_json_formatter_emits_valid_json(self):
        rec = logging.LogRecord("polymarket_arb.x", logging.INFO, "f", 1, "hello %s", ("w",), None)
        rec.fields = {"k": 1}
        line = JsonFormatter().format(rec)
        data = json.loads(line)
        assert data["msg"] == "hello w" and data["k"] == 1 and data["level"] == "info"

    def test_setup_logging_idempotent(self):
        setup_logging()
        setup_logging()
        assert len(logging.getLogger("polymarket_arb").handlers) == 1

    def test_summarize_counters(self):
        from collections import Counter

        out = summarize_counters(Counter({"rejected:x": 2, "rejected:y": 1}))
        assert out["counters"]["rejected"] == {"x": 2, "y": 1}

    def test_cli_kill_status_and_report(self, tmp_path, capsys):
        assert cli.main(["kill", "status"]) == 0
        db = tmp_path / "r.sqlite"
        StateStore(db, mode="paper").close()
        assert cli.main(["report", "--db", str(db)]) == 0
        assert "pnl_by_kind" in capsys.readouterr().out

    def test_cli_live_refused_by_default(self, capsys, monkeypatch):
        monkeypatch.delenv("LIVE_TRADING", raising=False)
        assert cli.main(["live"]) == 2
        assert "REFUSED" in capsys.readouterr().err

    def test_cli_replay(self, tmp_path, capsys):
        rc = cli.main(
            [
                "replay",
                "--input",
                str(RECORDING),
                "--db",
                str(tmp_path / "c.sqlite"),
                "--report",
                str(tmp_path / "rep.json"),
            ]
        )
        assert rc == 0 and (tmp_path / "rep.json").exists()

    @pytest.mark.asyncio
    async def test_run_live_refuses(self, settings, monkeypatch):
        monkeypatch.delenv("LIVE_TRADING", raising=False)
        with pytest.raises(LiveGateError):
            await run_live(settings, {})

    @pytest.mark.asyncio
    async def test_run_paper_with_fake_feed(self, settings, tmp_path, monkeypatch):
        from tests.fixtures.synth import recording_messages

        async def fake_events(_settings):
            return universe_events()

        class FakeWs:
            instances = 0

            def __init__(self, url, store, asset_ids, **kw):
                self.store = store
                self.connects = 1
                self.disconnects = 0
                self.messages = 0
                FakeWs.instances += 1

            async def run(self, stop):
                for t, msg in recording_messages():
                    self.store.apply_message(msg, t)
                    self.messages += 1
                await stop.wait()

        monkeypatch.setattr("polymarket_arb.runner.fetch_events", fake_events)
        monkeypatch.setattr("polymarket_arb.runner.MarketWsClient", FakeWs)
        monkeypatch.setattr("polymarket_arb.runner.time.time", __import__("time").time)
        summary = await run_paper(
            settings, seconds=2, db=tmp_path / "p.sqlite", report=tmp_path / "paper.json"
        )
        assert summary["mode"] == "paper" and summary["seconds"] == 2
        assert (tmp_path / "paper.json").exists()

    @pytest.mark.asyncio
    async def test_record_with_fake_feed(self, settings, tmp_path, monkeypatch):
        async def fake_events(_settings):
            return universe_events()

        class FakeWs:
            def __init__(self, url, store, asset_ids, **kw):
                self.on_event = kw.get("on_event")

            async def run(self, stop):
                from tests.fixtures.synth import initial_books

                for m in initial_books(0):
                    self.on_event(m)
                await stop.wait()

        monkeypatch.setattr(rec_mod, "fetch_events", fake_events)
        monkeypatch.setattr(rec_mod, "MarketWsClient", FakeWs)
        counts = await rec_mod.record(settings, 0.05, tmp_path / "rec.jsonl")
        assert counts["ws_messages"] >= 1 and counts["assets"] == 10
        assert len(rec_mod.ws_messages(tmp_path / "rec.jsonl")) == counts["ws_messages"]

    def test_run_replay_sync_wrapper(self, settings, tmp_path):
        import asyncio

        s = asyncio.run(run_replay(settings, RECORDING, tmp_path / "x.sqlite", None))
        assert s["executed_pairs"] >= 1


def test_side_enum_values_used_by_overlay():
    assert Side.BUY.value == "BUY" and Side.SELL.value == "SELL"
    assert dec("1") == dec("1.0")
