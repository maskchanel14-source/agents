"""Parameter sweep — sensitivitas threshold (misi §5d: jangan cherry-pick)."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Optional

from ..costs import CostConfig
from ..decimal_utils import D
from .replay import ReplayEvent, ReplayResult, run_replay


@dataclass
class SweepResult:
    rows: list = field(default_factory=list)

    def summary(self) -> str:
        lines = ["params | valid | rejected | avg_net | avg_lifetime_s"]
        for r in self.rows:
            lines.append(
                f"{r['params']} | {r['valid']} | {r['rejected']} | {r['avg_net']:.4f} | {r['avg_lifetime_s']:.1f}"
            )
        return "\n".join(lines)


def sweep(
    events: list[ReplayEvent],
    markets: dict,
    *,
    safety_margin_usd: Optional[list] = None,
    min_annualized_return: Optional[list] = None,
    max_capital_per_trade_usd: Optional[list] = None,
    strategy_cfg: Optional[dict] = None,
) -> SweepResult:
    safety_margin_usd = safety_margin_usd or ["0.002", "0.005", "0.01", "0.02"]
    min_annualized_return = min_annualized_return or ["0.05", "0.15", "0.30"]
    max_capital_per_trade_usd = max_capital_per_trade_usd or ["25", "50", "100"]

    out = SweepResult()
    for s, a, c in itertools.product(safety_margin_usd, min_annualized_return, max_capital_per_trade_usd):
        cfg = CostConfig(
            safety_margin_usd=D(s),
            min_annualized_return=D(a),
            max_capital_per_trade_usd=D(c),
        )
        res: ReplayResult = run_replay(events, markets, cost_cfg=cfg, strategy_cfg=strategy_cfg)
        total = sum(res.rejection_stats.values())
        rejected = total - res.rejection_stats.get("ok", 0)
        avg_net = sum(res.valid_net_edges) / len(res.valid_net_edges) if res.valid_net_edges else 0.0
        avg_life = (sum(res.lifetimes_ms) / len(res.lifetimes_ms) / 1000.0) if res.lifetimes_ms else 0.0
        out.rows.append({
            "params": {"safety": s, "min_ann": a, "max_cap": c},
            "valid": res.valid,
            "rejected": rejected,
            "avg_net": avg_net,
            "avg_lifetime_s": avg_life,
        })
    return out
