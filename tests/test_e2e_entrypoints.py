"""End-to-end entrypoint: synthetic gen -> backtest CLI -> paper CLI; live gate."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_generate_deterministic(tmp_path):
    from bot.backtest.synthetic import generate

    a, am = tmp_path / "a.json", tmp_path / "a_markets.json"
    b, bm = tmp_path / "b.json", tmp_path / "b_markets.json"
    stats = generate(a, am, seed=3, minutes=0.5, tick_ms=1000)
    generate(b, bm, seed=3, minutes=0.5, tick_ms=1000)
    assert a.read_bytes() == b.read_bytes()
    assert am.read_bytes() == bm.read_bytes()
    assert stats["events"] > 0 and stats["markets"] == 4
    rows = json.loads(a.read_text())
    assert all(rows[i]["ts_ms"] <= rows[i + 1]["ts_ms"] for i in range(len(rows) - 1))


def test_backtest_cli_writes_report(tmp_path):
    from bot.backtest.run import main as bt_main

    out = tmp_path / "report.json"
    rc = bt_main([
        "--fixture", str(ROOT / "data/fixtures/synthetic_small.json"),
        "--report", str(out),
        "--sweep",
    ])
    assert rc == 0
    report = json.loads(out.read_text())
    assert report["events"] == 4800
    assert report["valid"] > 0
    assert report["rejection_stats"]
    assert len(report["sweep"]) == 36
    # semua sweep row harus punya field funnel yang konsisten
    for row in report["sweep"]:
        assert row["valid"] + row["rejected"] == report["opportunities"]


def test_paper_cli_writes_summary(tmp_path):
    from bot.paper_run import main as paper_main

    out = tmp_path / "paper.json"
    rc = paper_main([
        "--fixture", str(ROOT / "data/fixtures/synthetic_small.json"),
        "--out", str(out),
    ])
    assert rc == 0
    summary = json.loads(out.read_text())
    assert summary["opportunities_detected"] > 0
    assert summary["valid_opportunities"] > 0
    assert summary["executed"] >= 1
    from decimal import Decimal
    assert Decimal(summary["simulated_pnl_usd"]) > 0
    assert summary["risk_snapshot"]


def test_live_gate_requires_env_and_file(tmp_path, monkeypatch):
    from bot.config.loader import live_trading_enabled

    monkeypatch.delenv("LIVE_TRADING", raising=False)
    assert live_trading_enabled() is False
    monkeypatch.setenv("LIVE_TRADING", "true")
    # file live_trading.confirmed tidak ada di repo -> tetap terkunci
    assert not (ROOT / "live_trading.confirmed").exists()
    assert live_trading_enabled() is False
    monkeypatch.setenv("LIVE_TRADING", "false")
    assert live_trading_enabled() is False


def test_kill_switch_file_detection(tmp_path, monkeypatch):
    from bot.config.loader import kill_switch_active

    assert kill_switch_active(str(tmp_path / "KILL_SWITCH")) is False
    (tmp_path / "KILL_SWITCH").write_text("halt")
    assert kill_switch_active(str(tmp_path / "KILL_SWITCH")) is True
