"""Test backtest replay (anti-lookahead) + synthetic fixture + sweep."""

from __future__ import annotations

import json
from pathlib import Path

from bot.backtest.replay import (
    ReplayEvent,
    load_fixture_json,
    markets_from_meta,
    run_replay,
)
from bot.backtest.sweep import sweep
from bot.backtest.synthetic import generate
from bot.costs import CostConfig
from bot.decimal_utils import D


def test_synthetic_fixture_and_replay(tmp_path: Path):
    fx = tmp_path / "syn.json"
    meta_p = tmp_path / "syn_markets.json"
    stats = generate(fx, meta_p, seed=7, minutes=3.0, tick_ms=1000)
    assert stats["events"] > 1000

    events = load_fixture_json(fx)
    # urutan waktu (anti lookahead)
    ts = [e.ts_ms for e in events]
    assert ts == sorted(ts)

    meta = json.loads(meta_p.read_text())
    markets = markets_from_meta(meta)
    assert set(markets.keys()) == {"m-alpha", "m-beta-1", "m-beta-2", "m-beta-3"}

    cfg = CostConfig(
        safety_margin_usd=D("0.005"),
        min_annualized_return=D("0.15"),
        max_capital_per_trade_usd=D("50"),
    )
    res = run_replay(events, markets, cost_cfg=cfg)
    assert res.events == len(events)
    assert res.scans > 0
    assert res.opportunities > 0
    # planted arb (ask sum 0.95 / 0.93) harus menghasilkan minimal satu valid
    assert res.valid > 0, res.rejection_stats
    assert "ok" in res.rejection_stats


def test_replay_no_lookahead_semantics():
    """Scan pada t hanya melihat event dengan ts <= t (bucket pertama tidak
    boleh memanfaatkan 'peluang' yang baru muncul di bucket berikutnya)."""
    from bot.backtest.replay import ReplayHub
    from bot.costs import make_market

    m = make_market("m1", fee_rate=D("0"))
    hub = ReplayHub({"m1": m})
    # event masa depan belum diterapkan
    assert hub.get_book("yes-m1") is None
    hub.apply(ReplayEvent(ts_ms=1, asset_id="yes-m1", market_id="m1", bids=[], asks=[("0.4", "10")]))
    assert hub.get_book("yes-m1") is not None
    snap = hub.get_book("yes-m1")
    assert snap.best_ask.price == D("0.4")


def test_sweep_runs_and_reports(tmp_path: Path):
    fx = tmp_path / "syn.json"
    meta_p = tmp_path / "syn_markets.json"
    generate(fx, meta_p, seed=3, minutes=1.5, tick_ms=1000)
    events = load_fixture_json(fx)
    markets = markets_from_meta(json.loads(meta_p.read_text()))
    sw = sweep(
        events,
        markets,
        safety_margin_usd=["0.005", "0.01"],
        min_annualized_return=["0.15"],
        max_capital_per_trade_usd=["50"],
    )
    assert len(sw.rows) == 2
    assert "valid" in sw.rows[0]
    assert sw.summary()
