"""SQLite persistence: opportunities, orders (idempotent), fills, positions, PnL, events.

Decimals are stored as TEXT to keep exact precision. Mode ('paper'/'live') is a column,
so paper and live history never mix.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from ..domain import Opportunity
from ..money import ZERO

SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
    opp_id TEXT NOT NULL,
    ts_ms INTEGER NOT NULL,
    mode TEXT NOT NULL,
    strategy TEXT NOT NULL,
    group_id TEXT NOT NULL,
    valid INTEGER NOT NULL,
    shares TEXT NOT NULL,
    gross_edge TEXT NOT NULL,
    taker_fees TEXT NOT NULL,
    gas_usd TEXT NOT NULL,
    leg_risk TEXT NOT NULL,
    haircut TEXT NOT NULL,
    safety TEXT NOT NULL,
    net_profit TEXT NOT NULL,
    net_pct TEXT NOT NULL,
    annualized_pct TEXT NOT NULL,
    capital TEXT NOT NULL,
    reasons TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS executed (
    opp_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    PRIMARY KEY (opp_id, mode)
);
CREATE TABLE IF NOT EXISTS orders (
    client_order_id TEXT PRIMARY KEY,
    opp_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    side TEXT NOT NULL,
    price TEXT NOT NULL,
    shares TEXT NOT NULL,
    order_type TEXT NOT NULL,
    status TEXT NOT NULL,
    filled_shares TEXT NOT NULL,
    fee TEXT NOT NULL,
    created_ms INTEGER NOT NULL,
    updated_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS positions (
    asset_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    shares TEXT NOT NULL,
    PRIMARY KEY (asset_id, mode)
);
CREATE TABLE IF NOT EXISTS pnl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_ms INTEGER NOT NULL,
    mode TEXT NOT NULL,
    opp_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    amount TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_ms INTEGER NOT NULL,
    mode TEXT NOT NULL,
    level TEXT NOT NULL,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class OrderRecord:
    client_order_id: str
    opp_id: str
    asset_id: str
    side: str
    price: Decimal
    shares: Decimal
    order_type: str
    status: str
    filled_shares: Decimal
    fee: Decimal


class StateStore:
    def __init__(self, path: Path | str, mode: str) -> None:
        self.mode = mode
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # ---- opportunities ----------------------------------------------------------
    def record_opportunity(self, opp: Opportunity, ts_ms: int) -> None:
        c = opp.costs
        self._conn.execute(
            "INSERT INTO opportunities VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                opp.opp_id,
                ts_ms,
                self.mode,
                opp.strategy,
                opp.group_id,
                int(opp.valid),
                str(opp.shares),
                str(c.gross_edge),
                str(c.taker_fees),
                str(c.gas_usd),
                str(c.leg_risk_expected_loss),
                str(c.resolution_haircut),
                str(c.safety_margin),
                str(opp.net_profit),
                str(opp.net_pct),
                str(opp.annualized_pct),
                str(opp.capital_required),
                ";".join(opp.reasons),
            ),
        )
        self._conn.commit()

    def mark_executed(self, opp_id: str) -> bool:
        """Idempotency: return False if this opportunity was already executed."""
        try:
            self._conn.execute("INSERT INTO executed (opp_id, mode) VALUES (?, ?)", (opp_id, self.mode))
        except sqlite3.IntegrityError:
            return False
        self._conn.commit()
        return True

    # ---- orders & fills ---------------------------------------------------------
    def record_order(self, rec: OrderRecord, ts_ms: int) -> None:
        try:
            self._conn.execute(
                "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    rec.client_order_id,
                    rec.opp_id,
                    self.mode,
                    rec.asset_id,
                    rec.side,
                    str(rec.price),
                    str(rec.shares),
                    rec.order_type,
                    rec.status,
                    str(rec.filled_shares),
                    str(rec.fee),
                    ts_ms,
                    ts_ms,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"duplicate client_order_id {rec.client_order_id}") from exc
        self._conn.commit()

    def order_exists(self, client_order_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM orders WHERE client_order_id=?", (client_order_id,)
        ).fetchone()
        return row is not None

    def add_fill(self, asset_id: str, signed_shares: Decimal) -> None:
        """Apply a fill: BUY adds shares, SELL subtracts (signed_shares carries the sign)."""
        cur = self.position(asset_id)
        new = cur + signed_shares
        self._conn.execute(
            "INSERT INTO positions (asset_id, mode, shares) VALUES (?,?,?) "
            "ON CONFLICT(asset_id, mode) DO UPDATE SET shares=excluded.shares",
            (asset_id, self.mode, str(new)),
        )
        self._conn.commit()

    def position(self, asset_id: str) -> Decimal:
        row = self._conn.execute(
            "SELECT shares FROM positions WHERE asset_id=? AND mode=?",
            (asset_id, self.mode),
        ).fetchone()
        return Decimal(row["shares"]) if row else ZERO

    def positions(self) -> dict[str, Decimal]:
        rows = self._conn.execute(
            "SELECT asset_id, shares FROM positions WHERE mode=?", (self.mode,)
        ).fetchall()
        return {r["asset_id"]: Decimal(r["shares"]) for r in rows}

    # ---- pnl & events -----------------------------------------------------------
    def record_pnl(self, ts_ms: int, opp_id: str, kind: str, amount: Decimal) -> None:
        self._conn.execute(
            "INSERT INTO pnl (ts_ms, mode, opp_id, kind, amount) VALUES (?,?,?,?,?)",
            (ts_ms, self.mode, opp_id, kind, str(amount)),
        )
        self._conn.commit()

    def realized_pnl_since(self, since_ms: int) -> Decimal:
        rows = self._conn.execute(
            "SELECT amount FROM pnl WHERE mode=? AND ts_ms>=?", (self.mode, since_ms)
        ).fetchall()
        return sum((Decimal(r["amount"]) for r in rows), ZERO)

    def pnl_by_kind(self) -> dict[str, Decimal]:
        """Sums per PnL kind: ``realized`` (merge/sell) vs ``expected_pending_resolution`` (redeem)."""
        out: dict[str, Decimal] = {}
        for r in self._conn.execute("SELECT kind, amount FROM pnl WHERE mode=?", (self.mode,)).fetchall():
            out[r["kind"]] = out.get(r["kind"], ZERO) + Decimal(r["amount"])
        return out

    def total_pnl(self) -> Decimal:
        rows = self._conn.execute("SELECT amount FROM pnl WHERE mode=?", (self.mode,)).fetchall()
        return sum((Decimal(r["amount"]) for r in rows), ZERO)

    def log_event(self, ts_ms: int, level: str, kind: str, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO events (ts_ms, mode, level, kind, payload) VALUES (?,?,?,?,?)",
            (
                ts_ms,
                self.mode,
                level,
                kind,
                json.dumps(payload, sort_keys=True, default=str),
            ),
        )
        self._conn.commit()

    def count(self, table: str, where: str = "", args: tuple[Any, ...] = ()) -> int:
        if table not in {"opportunities", "orders", "pnl", "events", "executed"}:
            raise ValueError("unknown table")
        sql = f"SELECT COUNT(*) AS n FROM {table} WHERE mode=?"
        if where:
            sql += f" AND {where}"
        return int(self._conn.execute(sql, (self.mode, *args)).fetchone()["n"])

    def rows(self, sql: str, args: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        return [dict(r) for r in self._conn.execute(sql, args).fetchall()]
