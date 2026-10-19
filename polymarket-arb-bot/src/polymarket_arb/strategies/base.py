"""Strategy interface: every strategy exposes ``name`` and ``scan``."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..domain import EventGroup, MarketInfo, Opportunity
from .common import StrategyContext


class Strategy(Protocol):
    name: str

    def scan(
        self,
        ctx: StrategyContext,
        universe: Sequence[MarketInfo] | Sequence[EventGroup],
    ) -> list[Opportunity]:
        """Return evaluated candidates (valid and rejected) for this cycle."""
        ...
