"""SQLite persistence — semua peluang (valid & ditolak), trade, posisi, PnL.

Schema dipertahankan dengan migrasi sederhana (CREATE TABLE IF NOT EXISTS).
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Optional

from ..models import Opportunity

SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    strategy TEXT NOT NULL,
    market_ids TEXT NOT NULL,
    event_id TEXT,
    valid INTEGER NOT NULL,
    reject_reason TEXT NOT NULL,
    reject_detail TEXT,
    gross_edge TEXT, notional TEXT, trading_fees TEXT, slippage_cost TEXT,
    gas_cost TEXT, leg_risk_cost TEXT, resolution_risk_cost TEXT,
    rounding_cost TEXT, safety_margin TEXT, total_costs TEXT,
    net_profit TEXT, net_profit_pct TEXT, capital_required TEXT,
    annualized_return TEXT, bundle_size TEXT,
    fill_probability TEXT, expected_net_profit TEXT,
    meta TEXT
);
CREATE INDEX IF NOT EXISTS idx_opps_created ON opportunities(created_at);
CREATE INDEX IF NOT EXISTS idx_opps_strategy ON opportunities(strategy);
CREATE INDEX IF NOT EXISTS idx_opps_valid ON opportunities(valid);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    opportunity_id TEXT,
    mode TEXT NOT NULL,
    market_id TEXT,
    asset_id TEXT,
    label TEXT,
    side TEXT,
    shares TEXT,
    price TEXT,
    fee TEXT,
    notional TEXT,
    status TEXT,
    order_id TEXT,
    fill_probability TEXT,
    meta TEXT
);
CREATE INDEX IF NOT EXISTS idx_trades_ts ON trades(ts);

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    label TEXT,
    shares TEXT NOT NULL,
    avg_price TEXT NOT NULL,
    realized_pnl TEXT NOT NULL DEFAULT '0',
    opened_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    closed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pnl_snapshots (
    ts TEXT PRIMARY KEY,
    equity TEXT, realized TEXT, unrealized TEXT, daily TEXT,
    open_positions INTEGER, trades INTEGER
);

CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    markets_total INTEGER, markets_monitored INTEGER,
    candidates INTEGER, valid INTEGER, rejected INTEGER,
    coverage TEXT
);
"""


def _dec(v: Optional[Decimal]) -> Optional[str]:
    return format(v, "f") if v is not None else None


class StateDB:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- opportunities -----------------------------------------------------

    def save_opportunity(self, opp: Opportunity) -> None:
        c = opp.cost
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO opportunities (
                    id, created_at, strategy, market_ids, event_id, valid,
                    reject_reason, reject_detail,
                    gross_edge, notional, trading_fees, slippage_cost, gas_cost,
                    leg_risk_cost, resolution_risk_cost, rounding_cost,
                    safety_margin, total_costs, net_profit, net_profit_pct,
                    capital_required, annualized_return, bundle_size,
                    fill_probability, expected_net_profit, meta
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    opp.opportunity_id,
                    opp.created_at.astimezone(timezone.utc).isoformat(),
                    opp.strategy,
                    json.dumps(list(opp.market_ids)),
                    opp.event_id,
                    1 if opp.valid else 0,
                    opp.reject_reason.value,
                    opp.reject_detail,
                    _dec(c.gross_edge), _dec(c.notional), _dec(c.trading_fees),
                    _dec(c.slippage_cost), _dec(c.gas_cost), _dec(c.leg_risk_cost),
                    _dec(c.resolution_risk_cost), _dec(c.rounding_cost),
                    _dec(c.safety_margin), _dec(c.total_costs), _dec(c.net_profit),
                    _dec(c.net_profit_pct), _dec(c.capital_required),
                    _dec(c.annualized_return), _dec(opp.bundle_size),
                    _dec(opp.fill_probability), _dec(opp.expected_net_profit),
                    json.dumps(opp.meta, default=str),
                ),
            )
            self._conn.commit()

    def save_opportunities(self, opps: Iterable[Opportunity]) -> int:
        n = 0
        for opp in opps:
            self.save_opportunity(opp)
            n += 1
        return n

    def opportunity_stats(self) -> dict:
        with self._lock:
            cur = self._conn.execute(
                """SELECT reject_reason, COUNT(*) as n, SUM(valid) as v
                   FROM opportunities GROUP BY reject_reason"""
            )
            rows = cur.fetchall()
        return {r["reject_reason"]: {"count": r["n"], "valid": r["v"] or 0} for r in rows}

    def recent_opportunities(self, limit: int = 100) -> list[dict]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM opportunities ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            return [dict(r) for r in cur.fetchall()]

    # -- trades ------------------------------------------------------------

    def record_trade(
        self,
        *,
        opportunity_id: str,
        mode: str,
        market_id: str,
        asset_id: str,
        label: str,
        side: str,
        shares: Decimal,
        price: Decimal,
        fee: Decimal,
        notional: Decimal,
        status: str,
        order_id: str = "",
        fill_probability: Optional[Decimal] = None,
        meta: Optional[dict] = None,
    ) -> int:
        with self._lock:
            cur = self._conn.execute(
                """INSERT INTO trades (ts, opportunity_id, mode, market_id, asset_id, label,
                   side, shares, price, fee, notional, status, order_id, fill_probability, meta)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(), opportunity_id, mode, market_id,
                    asset_id, label, side, _dec(shares), _dec(price), _dec(fee), _dec(notional),
                    status, order_id, _dec(fill_probability), json.dumps(meta or {}, default=str),
                ),
            )
            self._conn.commit()
            return int(cur.lastrowid)

    def trades(self, limit: int = 200) -> list[dict]:
        with self._lock:
            cur = self._conn.execute("SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

    # -- positions ---------------------------------------------------------

    def upsert_position(self, market_id: str, asset_id: str, label: str, shares: Decimal, price: Decimal) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM positions WHERE asset_id=? AND closed=0", (asset_id,)
            )
            row = cur.fetchone()
            if row is None:
                self._conn.execute(
                    """INSERT INTO positions (market_id, asset_id, label, shares, avg_price,
                       realized_pnl, opened_at, updated_at, closed) VALUES (?,?,?,?,?,'0',?,?,0)""",
                    (market_id, asset_id, label, _dec(shares), _dec(price), now, now),
                )
            else:
                old_shares = Decimal(row["shares"])
                old_avg = Decimal(row["avg_price"])
                new_shares = old_shares + shares
                if new_shares > 0:
                    new_avg = (old_shares * old_avg + shares * price) / new_shares
                else:
                    new_avg = old_avg
                self._conn.execute(
                    "UPDATE positions SET shares=?, avg_price=?, updated_at=? WHERE id=?",
                    (_dec(new_shares), _dec(new_avg), now, row["id"]),
                )
            self._conn.commit()

    def open_positions(self) -> list[dict]:
        with self._lock:
            cur = self._conn.execute("SELECT * FROM positions WHERE closed=0")
            return [dict(r) for r in cur.fetchall()]

    # -- pnl / kv / scan ----------------------------------------------------

    def snapshot_pnl(self, equity: Decimal, realized: Decimal, unrealized: Decimal, daily: Decimal, open_positions: int, trades: int) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO pnl_snapshots (ts, equity, realized, unrealized, daily,
                   open_positions, trades) VALUES (?,?,?,?,?,?,?)""",
                (datetime.now(timezone.utc).isoformat(), _dec(equity), _dec(realized),
                 _dec(unrealized), _dec(daily), open_positions, trades),
            )
            self._conn.commit()

    def pnl_history(self, limit: int = 500) -> list[dict]:
        with self._lock:
            cur = self._conn.execute("SELECT * FROM pnl_snapshots ORDER BY ts DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

    def kv_set(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?,?)", (key, json.dumps(value, default=str))
            )
            self._conn.commit()

    def kv_get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            cur = self._conn.execute("SELECT value FROM kv WHERE key=?", (key,))
            row = cur.fetchone()
        if row is None:
            return default
        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:
            return row["value"]

    def record_scan_run(self, *, markets_total: int, markets_monitored: int, candidates: int, valid: int, rejected: int, coverage: dict) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO scan_runs (ts, markets_total, markets_monitored, candidates,
                   valid, rejected, coverage) VALUES (?,?,?,?,?,?,?)""",
                (datetime.now(timezone.utc).isoformat(), markets_total, markets_monitored,
                 candidates, valid, rejected, json.dumps(coverage, default=str)),
            )
            self._conn.commit()
