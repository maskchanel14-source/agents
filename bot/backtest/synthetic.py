"""Generator fixture orderbook SINTETIS (jelas ditandai) untuk uji replay.

Bukan data live — dipakai untuk menguji pipeline end-to-end dari rekaman ->
scan -> statistik FEASIBILITY saat data live belum tersedia (lihat
docs/FEASIBILITY.md; angka live harus direkam via `python -m bot.record`).
"""

from __future__ import annotations

import json
import random
from pathlib import Path


def generate(
    path: Path,
    markets_meta_path: Path,
    *,
    seed: int = 7,
    minutes: float = 10.0,
    tick_ms: int = 1000,
) -> dict:
    rng = random.Random(seed)
    t0 = 1_792_464_000_000  # 2026-10-20T00:00:00Z
    n_ticks = int(minutes * 60 * 1000 / tick_ms)

    markets_meta = {
        # event 1: binary market dengan peluang A1 sesekali
        "m-alpha": {
            "slug": "will-x-happen", "question": "Will X happen?",
            "event_id": "evt-1", "neg_risk": False, "tick": "0.01",
            "min_notional": "5", "fee_rate": "0.04",
            "yes": "yes-alpha", "no": "no-alpha",
            "criteria": "Resolves Yes if X happens.",
        },
        # event 2: neg-risk 3 outcome dengan peluang B1 sesekali
        "m-beta-1": {
            "slug": "winner-a", "question": "Will A win?", "event_id": "evt-2",
            "neg_risk": True, "tick": "0.01", "min_notional": "5", "fee_rate": "0.04",
            "yes": "yes-beta-1", "no": "no-beta-1", "criteria": "Resolves Yes if A wins.",
        },
        "m-beta-2": {
            "slug": "winner-b", "question": "Will B win?", "event_id": "evt-2",
            "neg_risk": True, "tick": "0.01", "min_notional": "5", "fee_rate": "0.04",
            "yes": "yes-beta-2", "no": "no-beta-2", "criteria": "Resolves Yes if B wins.",
        },
        "m-beta-3": {
            "slug": "winner-c", "question": "Will C win?", "event_id": "evt-2",
            "neg_risk": True, "tick": "0.01", "min_notional": "5", "fee_rate": "0.04",
            "yes": "yes-beta-3", "no": "no-beta-3", "criteria": "Resolves Yes if C wins.",
        },
    }

    def book(best_bid: float, best_ask: float, size: float = 200.0):
        bids = [[f"{best_bid:.2f}", f"{size:.1f}"], [f"{best_bid - 0.02:.2f}", f"{size * 2:.1f}"]]
        asks = [[f"{best_ask:.2f}", f"{size:.1f}"], [f"{best_ask + 0.02:.2f}", f"{size * 2:.1f}"]]
        return bids, asks

    events = []
    for i in range(n_ticks):
        ts = t0 + i * tick_ms
        # m-alpha: harga normal 0.45/0.50; sesekali (15% tick) ask turun -> A1 muncul
        if rng.random() < 0.15:
            ya, na = 0.40, 0.55   # Σ ask = 0.95 -> gross arb
        else:
            ya, na = 0.48, 0.55   # Σ ask = 1.03 -> tidak ada
        for asset, bid, ask in (
            ("yes-alpha", ya - 0.03, ya),
            ("no-alpha", na - 0.03, na),
        ):
            bids, asks = book(bid, ask)
            events.append({"ts_ms": ts, "asset_id": asset, "market_id": "m-alpha", "bids": bids, "asks": asks})

        # event beta: Σ ask YES biasanya 1.02; sesekali 0.93 -> B1
        if rng.random() < 0.12:
            ys = [0.30, 0.33, 0.30]  # Σ = 0.93
        else:
            ys = [0.34, 0.34, 0.34]  # Σ = 1.02
        for k, (mid, aid) in enumerate(
            [("m-beta-1", "yes-beta-1"), ("m-beta-2", "yes-beta-2"), ("m-beta-3", "yes-beta-3")]
        ):
            bids, asks = book(ys[k] - 0.03, ys[k])
            events.append({"ts_ms": ts, "asset_id": aid, "market_id": mid, "bids": bids, "asks": asks})
            nb, na_ = book(0.60, 0.68)
            events.append({
                "ts_ms": ts, "asset_id": aid.replace("yes-", "no-"), "market_id": mid,
                "bids": nb, "asks": na_,
            })

    events.sort(key=lambda e: e["ts_ms"])
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(events), encoding="utf-8")
    Path(markets_meta_path).write_text(json.dumps(markets_meta, indent=1), encoding="utf-8")
    return {"events": len(events), "markets": len(markets_meta), "ticks": n_ticks}


if __name__ == "__main__":
    import sys
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/fixtures/synthetic_small.json")
    meta = Path(str(out).replace(".json", "_markets.json"))
    print(generate(out, meta))
