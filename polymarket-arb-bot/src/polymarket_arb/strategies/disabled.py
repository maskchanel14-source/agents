"""Strategies C (cross-market logical) and D (cross-venue) — DISABLED by default.

Why they are not implemented here (see DECISIONS.md):
  * C requires word-by-word equivalence of resolution criteria across different
    markets. Without that equivalence the "arbitrage" can lose on one side. The
    precision requirement of this project cannot be guaranteed by a heuristic,
    so no C logic is shipped; a generic skip reason is logged instead.
  * D requires identical resolution criteria on another venue plus that venue's
    fees, settlement and access rules; none of that is verifiable from this sandbox.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..domain import Opportunity
from .common import StrategyContext


class DisabledStrategy:
    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.skip_reason = reason

    def scan(self, ctx: StrategyContext, universe: Sequence[object]) -> list[Opportunity]:
        ctx.stats[f"{self.name}:skipped:{self.skip_reason}"] += 1
        return []


def cross_logical() -> DisabledStrategy:
    return DisabledStrategy("cross_logical", "not_implemented_precision_unverifiable")


def cross_venue() -> DisabledStrategy:
    return DisabledStrategy("cross_venue", "disabled_default_off")
