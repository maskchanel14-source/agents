#!/usr/bin/env python3
"""
Win-rate / drawdown reality check for the XAUScalperEA backtests.

Standard-library only (no numpy/scipy needed). Answers four questions that
every "high win rate EA" claim has to survive:

  Q1. I measured a win rate of W over N trades. How wide is the real interval?
  Q2. How many trades do I need before W is distinguishable from a coin flip?
  Q3. How many trades do I need before my average R is distinguishable from 0?
  Q4. Given my win rate and payoff shape, what drawdown should I EXPECT to
      see (not hope to see) over N trades?

Usage:
    python3 winrate_power.py                # run the built-in report
    python3 winrate_power.py --wr 62 --n 150 --avg-win 1.6 --avg-loss 1.0
                             --risk 0.5 --trades 500
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
from statistics import NormalDist

ND = NormalDist()


# --------------------------------------------------------------------------
# Q1. confidence interval around an observed win rate (Wilson score interval)
# --------------------------------------------------------------------------
def wilson_interval(wins: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = ND.inv_cdf(1 - (1 - conf) / 2)
    p = wins / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


# --------------------------------------------------------------------------
# Q2. how many trades to distinguish a win rate from a coin flip
# --------------------------------------------------------------------------
def n_for_winrate(p1: float, p0: float = 0.5, alpha: float = 0.05,
                  power: float = 0.80) -> int:
    """Two-sided one-sample proportion test, normal approximation."""
    za = ND.inv_cdf(1 - alpha / 2)
    zb = ND.inv_cdf(power)
    num = za * math.sqrt(p0 * (1 - p0)) + zb * math.sqrt(p1 * (1 - p1))
    den = abs(p1 - p0)
    if den == 0:
        return -1
    return math.ceil((num / den) ** 2)


# --------------------------------------------------------------------------
# Q3. how many trades to prove expectancy > 0 (mean R different from zero)
# --------------------------------------------------------------------------
def n_for_expectancy(mean_r: float, sd_r: float, alpha: float = 0.05,
                     power: float = 0.80) -> int:
    if mean_r <= 0 or sd_r <= 0:
        return -1
    za = ND.inv_cdf(1 - alpha / 2)
    zb = ND.inv_cdf(power)
    return math.ceil(((za + zb) * sd_r / mean_r) ** 2)


# --------------------------------------------------------------------------
# Q3b. is an observed win rate plausibly just luck? (binomial upper tail)
# --------------------------------------------------------------------------
def luck_probability(wins: int, n: int, p0: float = 0.5) -> float:
    """P(observe >= wins | true rate = p0). Large value = could be luck."""
    if n == 0:
        return 1.0
    # survival function of the binomial, computed in log space
    total = 0.0
    for k in range(wins, n + 1):
        logp = (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                + k * math.log(p0) + (n - k) * math.log(1 - p0))
        total += math.exp(logp)
    return min(1.0, total)


# --------------------------------------------------------------------------
# Q4. Monte-Carlo the drawdown you should EXPECT (not hope for)
# --------------------------------------------------------------------------
def simulate_dd(wr: float, avg_win_r: float, avg_loss_r: float,
                risk_pct: float, n_trades: int, sims: int = 4000,
                seed: int = 7) -> dict:
    rng = random.Random(seed)
    equity = 100.0
    finals, maxdds = [], []
    for _ in range(sims):
        eq = 100.0
        peak = 100.0
        dd = 0.0
        for _t in range(n_trades):
            if rng.random() < wr:
                r = avg_win_r
            else:
                r = -avg_loss_r
            # add realistic dispersion around the average R
            r = r * rng.gauss(1.0, 0.35)
            eq *= 1 + risk_pct / 100.0 * r
            if eq > peak:
                peak = eq
            dd = max(dd, (peak - eq) / peak * 100.0)
        finals.append(eq)
        maxdds.append(dd)
    finals.sort()
    maxdds.sort()

    def q(sorted_list, p):
        idx = min(len(sorted_list) - 1, max(0, int(p * len(sorted_list))))
        return sorted_list[idx]

    return {
        "all_maxdd": maxdds,
        "median_final": q(finals, 0.50),
        "p05_final": q(finals, 0.05),
        "p95_final": q(finals, 0.95),
        "median_maxdd": q(maxdds, 0.50),
        "p95_maxdd": q(maxdds, 0.95),
        "worst_maxdd": q(maxdds, 0.999),
        "pct_losing": sum(1 for f in finals if f < 100.0) / sims * 100.0,
        "start_equity": equity,
    }


def expectancy_r(wr: float, avg_win_r: float, avg_loss_r: float) -> float:
    return wr * avg_win_r - (1 - wr) * avg_loss_r


def pct_paths_over_dd(maxdds: list, limit: float) -> float:
    if not maxdds:
        return 0.0
    return sum(1 for d in maxdds if d > limit) / len(maxdds) * 100.0


def report(wr: float, n: int, avg_win_r: float, avg_loss_r: float,
           risk_pct: float, horizon: int, dd_limit: float = 6.0) -> None:
    wins = round(wr * n)
    exp_r = expectancy_r(wr, avg_win_r, avg_loss_r)
    lo, hi = wilson_interval(wins, n)

    print("=" * 68)
    print(" XAUScalperEA - backtest reality check")
    print("=" * 68)
    print(f" Observed win rate      : {wr:.1%}  ({wins}/{n} trades)")
    print(f" 95% CI (Wilson)        : {lo:.1%} .. {hi:.1%}")
    print(f" Average win / loss     : {avg_win_r:.2f}R / {avg_loss_r:.2f}R")
    print(f" Expectancy per trade   : {exp_r:+.3f}R   "
          f"({risk_pct * exp_r:+.3f}% of equity per trade)")
    print()
    print(" Q2 - trades needed before the win rate is NOT a coin flip")
    print("      (two-sided, alpha=0.05, power=0.80, H0: p = 0.50)")
    for target in (0.55, 0.58, 0.60, 0.65, 0.70):
        need = n_for_winrate(target)
        flag = "OK" if n >= need else f"need {need - n} more"
        print(f"      true WR {target:.0%} -> n = {need:5d}   (you have {n:5d})  {flag}")
    print()
    print(" Q3 - trades needed before expectancy is provably > 0")
    sd_r = math.sqrt(wr * (avg_win_r - exp_r) ** 2 + (1 - wr) * (-avg_loss_r - exp_r) ** 2)
    need = n_for_expectancy(exp_r, sd_r)
    print(f"      per-trade R std.dev = {sd_r:.3f}")
    print(f"      n = {need}  (you have {n})  "
          f"{'OK' if n >= need else f'need {need - n} more'}")
    print(f"      luck probability of your win count: "
          f"{luck_probability(wins, n):.4f}"
          f"{'  <-- WARNING: indistinguishable from chance' if luck_probability(wins, n) > 0.05 else ''}")
    print()
    print(f" Q4 - Monte-Carlo over {horizon} trades at {risk_pct}% risk "
          f"(4000 paths, seed 7)")
    res = simulate_dd(wr, avg_win_r, avg_loss_r, risk_pct, horizon)
    print(f"      median final equity : {res['median_final']:.1f} "
          f"(5th pct {res['p05_final']:.1f} / 95th pct {res['p95_final']:.1f})")
    print(f"      median max DD       : {res['median_maxdd']:.1f}%")
    print(f"      95th pct max DD     : {res['p95_maxdd']:.1f}%   "
          f"<-- size your InpMaxDrawdownPct above this")
    print(f"      worst of 4000 paths : {res['worst_maxdd']:.1f}%")
    print(f"      paths ending red    : {res['pct_losing']:.1f}%")
    print(f"      paths breaching DD guard of {dd_limit:.1f}% : "
          f"{pct_paths_over_dd(res['all_maxdd'], dd_limit):.1f}%"
          f"   <-- the guard WILL fire on healthy systems too")
    print("=" * 68)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wr", type=float, default=0.60, help="observed win rate, e.g. 0.60")
    ap.add_argument("--n", type=int, default=150, help="number of backtest trades")
    ap.add_argument("--avg-win", type=float, default=1.45, help="average winner in R")
    ap.add_argument("--avg-loss", type=float, default=1.00, help="average loser in R")
    ap.add_argument("--risk", type=float, default=0.5, help="risk per trade, %% of equity")
    ap.add_argument("--trades", type=int, default=1000, help="Monte-Carlo horizon in trades")
    ap.add_argument("--dd-limit", type=float, default=6.0,
                    help="your InpMaxDrawdownPct, to measure how often it fires")
    a = ap.parse_args()
    report(a.wr, a.n, a.avg_win, a.avg_loss, a.risk, a.trades, a.dd_limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
