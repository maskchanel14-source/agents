"""Position reconciliation: local ledger vs. the venue's view.

In paper mode the venue view is the simulator's own ledger (self-consistency check).
In live mode it must come from the authenticated positions endpoint. Any mismatch is
a hard failure: the caller should halt trading and page the operator.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ..money import ZERO


@dataclass(frozen=True)
class Diff:
    asset_id: str
    local: Decimal
    remote: Decimal

    @property
    def delta(self) -> Decimal:
        return self.remote - self.local


def reconcile(
    local: dict[str, Decimal],
    remote: dict[str, Decimal],
    tolerance: Decimal = Decimal("0.000001"),
) -> list[Diff]:
    diffs: list[Diff] = []
    for aid in sorted(set(local) | set(remote)):
        l_ = local.get(aid, ZERO)
        r_ = remote.get(aid, ZERO)
        if abs(l_ - r_) > tolerance:
            diffs.append(Diff(aid, l_, r_))
    return diffs
