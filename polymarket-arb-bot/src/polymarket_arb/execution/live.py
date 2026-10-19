"""Live executor — IMPLEMENTED BUT NOT ARMED in this build.

Safety layers, in order (any failure => no order is ever sent):
  1. ``check_live_gate``: LIVE_TRADING=true AND config/LIVE_CONFIRMED.txt present.
  2. A ``Signer`` must be injected. This repository does NOT ship a signer; the
     default is ``None`` and execution raises ``LiveNotArmed``.
  3. Idempotency: each opportunity leg uses a deterministic client order id; a
     duplicate is refused before any network call.
  4. FOK per leg, with amounts derived from the worst walked price (limit price).

Tests exercise this path end-to-end against an in-memory mock transport/signer.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

from ..config import LIVE_CONFIRMATION_FILE, LiveGateError, check_live_gate
from ..domain import Opportunity, Side
from ..money import ZERO
from ..state.store import OrderRecord, StateStore
from .base import ExecutionResult, LegFill

MICRO = Decimal(1000000)


class LiveNotArmed(RuntimeError):
    """Live execution was requested but the system is not armed to send orders."""


class Signer(Protocol):
    """EIP-712 order signer. Implementations must never log key material."""

    address: str

    def sign_order(self, typed_order: Mapping[str, Any]) -> str: ...


class OrderTransport(Protocol):
    async def post_order(self, body: dict[str, Any]) -> dict[str, Any]: ...

    async def cancel_all(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class OrderDraft:
    client_order_id: str
    token_id: str
    side: Side
    shares: Decimal
    limit_price: Decimal
    maker_amount: int  # base units (6 dp)
    taker_amount: int  # base units (6 dp)


def build_order_draft(
    client_order_id: str,
    asset_id: str,
    side: Side,
    shares: Decimal,
    limit_price: Decimal,
) -> OrderDraft:
    """Derive maker/taker base-unit amounts exactly as the docs example does.

    BUY : maker = USDC spent (shares * price), taker = shares.
    SELL: maker = shares, taker = USDC received (shares * price).
    Rounding is conservative: BUY maker rounds UP, SELL taker rounds DOWN.
    """
    if shares <= ZERO or limit_price <= ZERO or limit_price >= 1:
        raise ValueError("invalid shares/limit price")
    share_units = shares * MICRO
    price_units = shares * limit_price * MICRO
    if share_units != share_units.to_integral_value() or price_units != price_units.to_integral_value():
        # Sub-micro amounts: round conservatively for the side.
        if side is Side.BUY:
            maker = int(price_units.to_integral_value(rounding="ROUND_UP"))
            taker = int(share_units.to_integral_value(rounding="ROUND_DOWN"))
        else:
            maker = int(share_units.to_integral_value(rounding="ROUND_DOWN"))
            taker = int(price_units.to_integral_value(rounding="ROUND_DOWN"))
    else:
        if side is Side.BUY:
            maker, taker = int(price_units), int(share_units)
        else:
            maker, taker = int(share_units), int(price_units)
    return OrderDraft(client_order_id, asset_id, side, shares, limit_price, maker, taker)


class LiveExecutor:
    mode = "live"

    def __init__(
        self,
        store: StateStore,
        transport: OrderTransport | None,
        signer: Signer | None,
        *,
        env: Mapping[str, str],
        mode: str = "live",
        confirmation_file: Path = LIVE_CONFIRMATION_FILE,
    ) -> None:
        check_live_gate(mode, env, confirmation_file)  # raises LiveGateError
        self.store = store
        self.transport = transport
        self.signer = signer

    def assert_armed(self) -> None:
        if self.signer is None or self.transport is None:
            raise LiveNotArmed("no signer/transport configured: this build does not sign or send orders")

    def _transport(self) -> OrderTransport:
        self.assert_armed()
        assert self.transport is not None  # narrowed by assert_armed
        return self.transport

    def _signer(self) -> Signer:
        self.assert_armed()
        assert self.signer is not None  # narrowed by assert_armed
        return self.signer

    async def cancel_all(self) -> int:
        self.assert_armed()
        resp = await self._transport().cancel_all()
        return int(resp.get("canceled", 0)) if isinstance(resp, dict) else 0

    async def execute(self, opp: Opportunity, now_ms: int) -> ExecutionResult:
        self.assert_armed()
        if not opp.valid:
            return ExecutionResult(status="refused", reason="opportunity_invalid")
        if not self.store.mark_executed(opp.opp_id):
            return ExecutionResult(status="skipped_duplicate", reason="already_executed")

        fills: list[LegFill] = []
        for i, leg in enumerate(opp.legs):
            cid = f"{opp.opp_id}#{i}"
            if self.store.order_exists(cid):
                return ExecutionResult(status="skipped_duplicate", reason="duplicate_client_order_id")
            limit = leg.worst_price
            draft = build_order_draft(cid, leg.asset_id, leg.side, leg.shares, limit)
            body = self._body(draft)
            typed = dict(body["order"])
            body["order"]["signature"] = self._signer().sign_order(typed)
            self.store.record_order(
                OrderRecord(
                    cid,
                    opp.opp_id,
                    leg.asset_id,
                    leg.side.value,
                    limit,
                    leg.shares,
                    "FOK",
                    "submitted",
                    ZERO,
                    ZERO,
                ),
                now_ms,
            )
            resp = await self._transport().post_order(body)
            if not resp.get("success"):
                self.store.log_event(
                    now_ms,
                    "error",
                    "order_rejected",
                    {
                        "opp_id": opp.opp_id,
                        "leg": i,
                        "error": str(resp.get("errorMsg", ""))[:200],
                    },
                )
                if fills:
                    # Earlier legs already filled: the position is UNHEDGED. Report it loudly;
                    # the engine must halt and flatten (see engine.py).
                    self.store.log_event(
                        now_ms,
                        "critical",
                        "unhedged_partial",
                        {"opp_id": opp.opp_id, "filled_legs": len(fills)},
                    )
                    return ExecutionResult(
                        status="partial",
                        reason="sibling_leg_rejected",
                        fills=tuple(fills),
                    )
                return ExecutionResult(status="cancelled", reason="order_rejected")
            fills.append(LegFill(leg.asset_id, leg.side, leg.shares, limit, leg.fee))
        return ExecutionResult(
            status="filled",
            fills=tuple(fills),
            gross_edge=opp.costs.gross_edge,
            fees=opp.costs.taker_fees,
            gas_usd=opp.costs.gas_usd,
        )

    @staticmethod
    def _body(d: OrderDraft) -> dict[str, Any]:
        return {
            "deferExec": False,
            "order": {
                "expiration": "0",
                "makerAmount": str(d.maker_amount),
                "takerAmount": str(d.taker_amount),
                "side": d.side.value,
                "tokenId": d.token_id,
                "signatureType": 3,
            },
            "orderType": "FOK",
        }


__all__ = [
    "LiveExecutor",
    "LiveGateError",
    "LiveNotArmed",
    "OrderDraft",
    "build_order_draft",
]
