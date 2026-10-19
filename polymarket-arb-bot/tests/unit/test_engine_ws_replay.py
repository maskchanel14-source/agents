"""Engine orchestration, WebSocket client (local server, reconnect), replay determinism."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
import websockets

from polymarket_arb.data.book_store import BookStore
from polymarket_arb.data.recording import load_universe_from_recording, ws_messages
from polymarket_arb.data.ws import MarketWsClient, parse_frame
from polymarket_arb.engine import Engine, utc_midnight_ms
from polymarket_arb.execution.book_view import PaperBookView
from polymarket_arb.execution.paper import PaperExecutor
from polymarket_arb.money import dec
from polymarket_arb.risk import KillSwitch
from polymarket_arb.runner import _register, run_replay
from polymarket_arb.state.store import StateStore
from tests.fixtures.synth import BASE_MS, initial_books, write_recording
from tests.unit.helpers import NOW, seeded, universe

ROOT = Path(__file__).resolve().parents[2]
RECORDING = ROOT / "tests" / "fixtures" / "recordings" / "synthetic_replay.jsonl"


def build_engine(settings, tmp_path, store, uni, kill_path=None):
    st = StateStore(tmp_path / "e.sqlite", mode="paper")
    view = PaperBookView(store)
    ex = PaperExecutor(st, view, uni.markets_by_asset(), settings.thresholds.max_book_age_ms)
    kill = KillSwitch(kill_path or tmp_path / "KILL")
    eng = Engine(settings=settings, universe=uni, books=view, store=st, executor=ex, kill_switch=kill)
    return eng, st, kill


class TestEngine:
    @pytest.mark.asyncio
    async def test_cycle_executes_valid_arb_and_records_candidates(self, settings, tmp_path):
        store, uni = seeded()
        eng, st, _ = build_engine(settings, tmp_path, store, uni)
        rep = await eng.cycle(NOW)
        assert rep.valid >= 1 and rep.executed >= 1
        assert st.count("opportunities") >= 1
        assert any("filled" in r for r in rep.results)
        st.close()

    @pytest.mark.asyncio
    async def test_kill_switch_blocks_and_cancels(self, settings, tmp_path):
        store, uni = seeded()
        eng, st, kill = build_engine(settings, tmp_path, store, uni)
        kill.trigger_manual("test")
        rep = await eng.cycle(NOW)
        assert rep.halted and rep.executed == 0
        assert st.count("orders") == 0
        assert eng.stats["cancel_all"] == 0  # paper cancel_all returns 0 but was invoked
        st.close()

    @pytest.mark.asyncio
    async def test_daily_loss_halts_cycle(self, settings, tmp_path):
        store, uni = seeded()
        eng, st, _ = build_engine(settings, tmp_path, store, uni)
        st.record_pnl(NOW, "old", "realized", -settings.limits.max_daily_loss)
        rep = await eng.cycle(NOW)
        assert "daily_loss_halt" in rep.halted and rep.executed == 0
        st.close()

    @pytest.mark.asyncio
    async def test_reconcile_mismatch_halts(self, settings, tmp_path):
        store, uni = seeded()
        eng, st, kill = build_engine(settings, tmp_path, store, uni)
        st.add_fill("tok-n0-yes", dec("3"))  # position with no backing order => mismatch
        diffs = eng.reconcile_positions(NOW)
        assert diffs and kill.is_active()
        assert st.count("events", "kind='reconcile_mismatch'") == 1
        st.close()

    @pytest.mark.asyncio
    async def test_reconcile_ok_when_consistent(self, settings, tmp_path):
        store, uni = seeded()
        eng, st, kill = build_engine(settings, tmp_path, store, uni)
        assert eng.reconcile_positions(NOW) == [] and not kill.is_active()
        st.close()

    def test_utc_midnight(self):
        assert utc_midnight_ms(BASE_MS + 3_600_000) == BASE_MS  # BASE is a UTC midnight

    @pytest.mark.asyncio
    async def test_rejections_counted_by_reason(self, settings, tmp_path):
        store, uni = seeded(received=BASE_MS - 10_000)  # all books stale
        eng, st, _ = build_engine(settings, tmp_path, store, uni)
        rep = await eng.cycle(NOW)
        assert rep.candidates >= 1 and rep.valid == 0
        assert rep.rejections["stale_book"] >= 1
        st.close()


class TestParseFrame:
    def test_list_and_dict_frames(self):
        assert parse_frame('{"event_type":"book"}') == [{"event_type": "book"}]
        assert len(parse_frame('[{"a":1},{"b":2}]')) == 2

    def test_heartbeats_ignored(self):
        assert parse_frame("PONG") == [] and parse_frame("") == []

    def test_scalar_ignored(self):
        assert parse_frame("123") == []


class TestWebSocket:
    @pytest.mark.asyncio
    async def test_snapshot_applied_and_disconnect_reconnects(self):
        """Local server: sends snapshots, drops the first connection, then serves again."""
        sessions = {"n": 0}
        subscriptions: list[dict] = []

        async def handler(ws):
            sessions["n"] += 1
            sub = json.loads(await ws.recv())
            subscriptions.append(sub)
            for m in initial_books(BASE_MS):
                if m["asset_id"] in sub["assets_ids"]:
                    await ws.send(json.dumps(m))
            if sessions["n"] == 1:
                await asyncio.sleep(0.2)
                return  # drop the connection to force a reconnect
            await asyncio.sleep(3)

        async with websockets.serve(handler, "127.0.0.1", 0) as server:
            port = server.sockets[0].getsockname()[1]
            store = BookStore()
            uni = universe()
            _register(store, uni)
            client = MarketWsClient(
                f"ws://127.0.0.1:{port}",
                store,
                lambda: uni.assets,
                backoff_base_s=0.05,
                backoff_max_s=0.2,
                idle_timeout_s=5,
            )
            stop = asyncio.Event()
            task = asyncio.create_task(client.run(stop))
            for _ in range(100):
                if sessions["n"] >= 2 and store.get("tok-b1-yes") is not None:
                    break
                await asyncio.sleep(0.05)
            stop.set()
            task.cancel()
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)  # reap; errors surface via assertions
        assert sessions["n"] >= 2, "client must reconnect after a drop"
        assert client.disconnects >= 1
        assert client.messages >= 1
        assert (
            store.counters.get("invalidated:session_end", 0) + store.counters.get("invalidated:disconnect", 0)
            >= 1
        )
        assert set(subscriptions[0]) == {"assets_ids", "type", "custom_feature_enabled"}
        assert subscriptions[0]["type"] == "market"


class TestReplay:
    @pytest.mark.asyncio
    async def test_replay_is_deterministic(self, settings, tmp_path):
        a = await run_replay(settings, RECORDING, tmp_path / "a.sqlite", None)
        b = await run_replay(settings, RECORDING, tmp_path / "b.sqlite", None)
        for key in ("executed_pairs", "opportunities_valid", "realized_pnl_usdc", "stats", "orders"):
            assert a[key] == b[key], key

    @pytest.mark.asyncio
    async def test_replay_expected_outcome_on_synthetic_recording(self, settings, tmp_path):
        s = await run_replay(settings, RECORDING, tmp_path / "r.sqlite", tmp_path / "rep.json")
        assert s["assets"] == 10
        assert s["executed_pairs"] >= 1
        assert float(s["realized_pnl_usdc"]) > 0
        assert float(s["expected_pending_resolution_pnl_usdc"]) > 0
        assert "universe_skipped" in s
        assert (tmp_path / "rep.json").exists()

    def test_recording_roundtrip(self, tmp_path):
        out = tmp_path / "rec.jsonl"
        n = write_recording(out)
        msgs = ws_messages(out)
        assert len(msgs) == n
        assert [t for t, _ in msgs] == sorted(t for t, _ in msgs)
        uni = load_universe_from_recording(out)
        assert uni.assets
