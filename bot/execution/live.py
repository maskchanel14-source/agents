"""Live executor — TERKUNCI default (misi §5).

Eksekusi live HANYA aktif jika SEMUA syarat terpenuhi:
1. env LIVE_TRADING=true
2. file `live_trading.confirmed` ada di root repo
3. dependency `py-clob-client` terpasang (requirements-live.txt)

Sesi pengembangan ini TIDAK PERNAH menandatangani transaksi atau mengirim order
asli. Kelas ini menyediakan interface + guard; implementasi order signing memakai
client resmi Polymarket dan hanya dijalankan user secara sadar.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..models import Opportunity
from .simulator import ExecutionResult

log = logging.getLogger("bot.execution.live")

ROOT = Path(__file__).resolve().parents[2]


class LiveTradingNotPermitted(RuntimeError):
    pass


def live_trading_permitted() -> bool:
    import os
    if os.environ.get("LIVE_TRADING", "").strip().lower() != "true":
        return False
    return (ROOT / "live_trading.confirmed").exists()


class LiveExecutor:
    """Executor live — menolak semua aksi kecuali gate ganda terpenuhi."""

    def __init__(self, *, clob_client=None) -> None:
        self.clob_client = clob_client
        self.enabled = live_trading_permitted()
        if not self.enabled:
            log.warning("LiveExecutor dibuat dalam mode TERKUNCI (paper/simulation only)")

    def _require_live(self) -> None:
        if not live_trading_permitted():
            raise LiveTradingNotPermitted(
                "Live trading tidak diizinkan: butuh LIVE_TRADING=true + live_trading.confirmed"
            )
        if self.clob_client is None:
            try:
                import py_clob_client  # noqa: F401
            except ImportError as exc:
                raise LiveTradingNotPermitted(
                    "py-clob-client tidak terpasang (pip install -r requirements-live.txt)"
                ) from exc

    def execute(self, opp: Opportunity, now_ms: Optional[int] = None) -> ExecutionResult:
        self._require_live()
        # Implementasi live sesungguhnya: py_clob_client ClobClient.post_orders(...)
        # dengan order FOK/FAK yang sudah ditandatangani. TIDAK PERNAH dipanggil
        # selama sesi ini (misi §5: "kamu TIDAK boleh mengirim order asli").
        raise LiveTradingNotPermitted(
            "LiveExecutor.execute tidak aktif di sesi pengembangan ini — gunakan mode paper"
        )

    def cancel_all(self) -> None:
        self._require_live()
        raise LiveTradingNotPermitted("cancel_all live tidak aktif di sesi ini")
