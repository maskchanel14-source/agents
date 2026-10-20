"""Strategi D — cross-venue (default OFF, TIDAK aktif).

Misi §3D: hanya jika kriteria resolusi antar venue IDENTIK. Pada sesi ini tidak
ada venue eksternal dengan kriteria resolusi yang terverifikasi identik, dan
akses keluar sandbox dibatasi — modul disediakan sebagai interface + stub agar
bisa diisi nami TANPA mengubah arsitektur.

Keputusan: SKIP dengan alasan terdokumentasi (DECISIONS.md D4).
"""

from __future__ import annotations

import logging
from typing import Optional

from ..data.feed import MarketDataHub
from ..models import Opportunity
from .base import Strategy

log = logging.getLogger("bot.strategies.cross_venue")


class CrossVenue(Strategy):
    name = "D_cross_venue"

    def scan(self, hub: MarketDataHub, now_ms: Optional[int] = None) -> list[Opportunity]:
        if not self.enabled:
            return []
        # Tidak ada feed venue lain yang kriterianya terverifikasi identik.
        log.info(
            "D_cross_venue enabled but no venue with verifiably identical resolution "
            "criteria is configured — skipping (see DECISIONS.md D4)"
        )
        return []
