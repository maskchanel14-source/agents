"""Execution interface and result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol

from ..domain import Opportunity, Side
from ..money import ZERO


@dataclass(frozen=True)
class LegFill:
    asset_id: str
    side: Side
    shares: Decimal
    price: Decimal
    fee: Decimal


@dataclass(frozen=True)
class ExecutionResult:
    status: str  # "filled" | "cancelled" | "skipped_duplicate" | "refused"
    reason: str = ""
    fills: tuple[LegFill, ...] = ()
    gross_edge: Decimal = ZERO
    fees: Decimal = ZERO
    gas_usd: Decimal = ZERO
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def net_profit(self) -> Decimal:
        return self.gross_edge - self.fees - self.gas_usd


class Executor(Protocol):
    mode: str

    async def execute(self, opp: Opportunity, now_ms: int) -> ExecutionResult: ...

    async def cancel_all(self) -> int: ...
