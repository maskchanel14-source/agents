"""Deterministic SYNTHETIC market data in the documented Gamma / CLOB WS schemas.

Used for tests and the offline replay/backtest. Not captured from Polymarket: the
sandbox cannot reach Polymarket hosts, so these fixtures test the code paths, not
real-market economics. Field names follow docs.polymarket.com (see POLYMARKET_NOTES).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_MS = 1_792_368_000_000  # 2026-10-17T00:00:00Z (fixed clock for reproducibility)
END_DATE = "2027-06-01T00:00:00Z"
NEG_RISK_END = "2026-11-15T00:00:00Z"  # near resolution so the B annualized test is meaningful


def fee_schedule(rate: str = "0.04") -> dict[str, Any]:
    return {"rate": rate, "exponent": "1", "takerOnly": True, "rebateRate": "0.25"}


def gamma_market(
    cid: str,
    yes: str,
    no: str,
    *,
    neg_risk: bool,
    liquidity: str = "5000",
    tick: str = "0.001",
    min_size: str = "5",
    fees: bool = True,
    end_date: str = END_DATE,
) -> dict[str, Any]:
    return {
        "conditionId": cid,
        "slug": f"synthetic-{cid[-6:]}",
        "question": f"Synthetic question {cid[-6:]}?",
        "description": "Synthetic market for offline tests. Resolves YES if the synthetic oracle reports the event, otherwise NO, using a fixed rule.",
        "resolutionSource": "synthetic-oracle",
        "outcomes": json.dumps(["Yes", "No"]),
        "clobTokenIds": json.dumps([yes, no]),
        "active": True,
        "closed": False,
        "acceptingOrders": True,
        "negRisk": neg_risk,
        "negRiskOther": False,
        "version": "v1",
        "orderPriceMinTickSize": tick,
        "orderMinSize": min_size,
        "feesEnabled": fees,
        "feeSchedule": fee_schedule() if fees else None,
        "endDate": end_date,
        "liquidity": liquidity,
    }


def gamma_event(event_id: str, markets: list[dict[str, Any]], *, neg_risk: bool) -> dict[str, Any]:
    return {
        "id": event_id,
        "title": f"Synthetic event {event_id}",
        "enableNegRisk": neg_risk,
        "negRiskAugmented": False,
        "markets": markets,
    }


def universe_events() -> list[dict[str, Any]]:
    """Two binaries (one arbitrage, one fair) and one 3-outcome neg-risk event (arb)."""
    binary_arb = gamma_market("0x" + "a1" * 32, "tok-b1-yes", "tok-b1-no", neg_risk=False)
    binary_fair = gamma_market("0x" + "a2" * 32, "tok-b2-yes", "tok-b2-no", neg_risk=False)
    nr = [
        gamma_market(
            "0x" + ("b" + str(i)) * 32,
            f"tok-n{i}-yes",
            f"tok-n{i}-no",
            neg_risk=True,
            end_date=NEG_RISK_END,
        )
        for i in range(3)
    ]
    return [
        gamma_event("ev-binary-1", [binary_arb], neg_risk=False),
        gamma_event("ev-binary-2", [binary_fair], neg_risk=False),
        gamma_event("ev-neg-1", nr, neg_risk=True),
    ]


def book_msg(asset: str, bids: list[tuple[str, str]], asks: list[tuple[str, str]], ts: int) -> dict[str, Any]:
    return {
        "event_type": "book",
        "asset_id": asset,
        "market": "synthetic",
        "timestamp": str(ts),
        "bids": [{"price": p, "size": s} for p, s in bids],
        "asks": [{"price": p, "size": s} for p, s in asks],
        "tick_size": "0.001",
        "min_order_size": "5",
    }


def initial_books(ts: int) -> list[dict[str, Any]]:
    msgs = [
        # binary arb: YES ask 0.45 + NO ask 0.45 = 0.90 < 1
        book_msg("tok-b1-yes", [("0.44", "300")], [("0.45", "200"), ("0.47", "500")], ts),
        book_msg("tok-b1-no", [("0.44", "300")], [("0.45", "200"), ("0.47", "500")], ts),
        # binary fair: 0.50 + 0.52 > 1 -> nothing to do
        book_msg("tok-b2-yes", [("0.49", "400")], [("0.50", "400")], ts),
        book_msg("tok-b2-no", [("0.49", "400")], [("0.52", "400")], ts),
    ]
    # neg-risk: buy-all of YES at 0.30 each = 0.90 < 1
    for i in range(3):
        msgs.append(
            book_msg(
                f"tok-n{i}-yes",
                [("0.29", "300")],
                [("0.30", "300"), ("0.33", "400")],
                ts,
            )
        )
        msgs.append(book_msg(f"tok-n{i}-no", [("0.60", "300")], [("0.62", "300")], ts))
    return msgs


def recording_messages() -> list[tuple[int, dict[str, Any]]]:
    """(recv_ms, ws_event) in order. Includes a delta, a non-arb update and a re-snapshot."""
    out: list[tuple[int, dict[str, Any]]] = []
    t = BASE_MS
    for m in initial_books(BASE_MS):
        out.append((t, m))
        t += 1
    # tick 1: the arb binary's YES ask improves size via price_change (size 0 removes level)
    ts1 = BASE_MS + 2_000
    out.append(
        (
            ts1,
            {
                "event_type": "price_change",
                "timestamp": str(ts1),
                "market": "synthetic",
                "price_changes": [
                    {
                        "asset_id": "tok-b2-no",
                        "price": "0.52",
                        "size": "0",
                        "side": "SELL",
                        "best_bid": "0.49",
                        "best_ask": "0.50",
                    }
                ],
            },
        )
    )
    # tick 2: neg-risk asks move up (arb disappears), then fresh snapshot at t=10s
    ts2 = BASE_MS + 10_000
    for i in range(3):
        out.append((ts2, book_msg(f"tok-n{i}-yes", [("0.29", "300")], [("0.36", "300")], ts2)))
    out.append((ts2 + 1, book_msg("tok-b1-yes", [("0.44", "300")], [("0.45", "200")], ts2)))
    out.append((ts2 + 2, book_msg("tok-b1-no", [("0.44", "300")], [("0.45", "200")], ts2)))
    return out


def write_recording(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    msgs = recording_messages()
    with path.open("w", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "type": "meta",
                    "created_ms": BASE_MS,
                    "synthetic": True,
                    "events": universe_events(),
                }
            )
            + "\n"
        )
        for t, msg in msgs:
            fh.write(json.dumps({"type": "ws", "t": t, "msg": msg}, separators=(",", ":")) + "\n")
    return len(msgs)


if __name__ == "__main__":  # pragma: no cover
    here = Path(__file__).resolve().parent / "recordings" / "synthetic_replay.jsonl"
    print(write_recording(here), here)
