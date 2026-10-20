"""Interface strategi: `scan() -> list[Opportunity]` (misi §3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..costs import CostModel
from ..data.feed import MarketDataHub
from ..models import Opportunity


class Strategy(ABC):
    """Strategi arbitrase — memindai semua market yang memenuhi syarat."""

    name: str = "base"

    def __init__(self, cost_model: CostModel, config: Optional[dict] = None) -> None:
        self.cost_model = cost_model
        self.config = config or {}

    @abstractmethod
    def scan(self, hub: MarketDataHub, now_ms: Optional[int] = None) -> list[Opportunity]:
        """Pindai SEMUA market kandidat; kembalikan SEMUA hasil (valid & ditolak)."""

    @property
    def enabled(self) -> bool:
        return bool(self.config.get("enabled", True))
