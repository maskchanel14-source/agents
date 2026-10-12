"""
Strategy iteration round (GAN loop, level 2): structural variants.
Protocol unchanged: rank on TRAIN, confirm on VAL/TEST.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import Cfg, run_backtest, split_metrics, atr_sma  # noqa: E402
from run_backtest import load_h1, load_d1, splits  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def band_for(df, lo, hi, period=14):
    c, h, l = df.c.to_numpy(), df.h.to_numpy(), df.l.to_numpy()
    a = atr_sma(h[lo:hi], l[lo:hi], c[lo:hi], period)
    a = a[~np.isnan(a)]
    return round(float(np.percentile(a, 10)), 2), round(float(np.percentile(a, 90)), 2)


def main():
    t0 = time.time()
    df = load_h1()
    n = len(df)
    s0, s1, s2, s3 = splits(n)
    lo, hi = band_for(df, s0, s1)

    V = {}
    V["V0 baseline (as-is)"] = Cfg(atr_min=lo, atr_max=hi)
    V["V1 +EMA200 trend filter"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200)
    V["V2 trend + TP 3.0xATR"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200, tp_mult=3.0)
    V["V3 trend + TP 3.5xATR"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200, tp_mult=3.5)
    V["V4 trend, no BE (pure SL/TP)"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200, use_be=False)
    V["V5 trend, no TP (trail after BE)"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200, tp_mult=0.0)
    V["V6 trend + SL 2.0 / TP 3.0 (wide)"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200,
                                                 sl_mult=2.0, tp_mult=3.0)
    V["V7 trend + SL 1.2 / TP 2.5 (tight)"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200,
                                                  sl_mult=1.2, tp_mult=2.5)
    V["V8 trend + 24h session"] = Cfg(atr_min=lo, atr_max=hi, trend_ema=200,
                                      session_start=0, session_end=23)
    V["V9 no trend, TP 3.0"] = Cfg(atr_min=lo, atr_max=hi, tp_mult=3.0)

    results = {}
    md = ["\n## Strategy iteration round — structural variants (H1)\n",
          "Ranked on TRAIN; VAL/TEST are confirm-only (no peeking). Same ATR band, same risk layer.\n"]
    md.append("| variant | TRAIN expR | VAL expR | TEST expR | TEST win% | TEST PF | TEST maxDD% | TEST trades |")
    md.append("|---|---|---|---|---|---|---|---|")

    for name, cfg in V.items():
        r = run_backtest(df, cfg)
        mt = split_metrics(r["trades"], r["equity"], s0, s1, cfg.starting_equity)
        mv = split_metrics(r["trades"], r["equity"], s1, s2, cfg.starting_equity)
        ms = split_metrics(r["trades"], r["equity"], s2, s3, cfg.starting_equity)
        results[name] = (cfg, r, mt, mv, ms)
        pf = "inf" if ms["profit_factor"] == float("inf") else f"{ms['profit_factor']:.2f}"
        md.append(f"| {name} | {mt['expectancy_R']:+.3f} | {mv['expectancy_R']:+.3f} "
                  f"| {ms['expectancy_R']:+.3f} | {ms['win_rate_pct']:.0f} | {pf} "
                  f"| {ms['max_dd_pct']:.1f} | {ms['trades']} |")
        print(f"{name:38s} TRAIN {mt['expectancy_R']:+.3f}R ({mt['trades']}) | "
              f"VAL {mv['expectancy_R']:+.3f}R | TEST {ms['expectancy_R']:+.3f}R "
              f"PF {pf} net ${ms['net_pnl']:+,.0f}")

    best = max((k for k in results if results[k][2]["trades"] >= 150),
               key=lambda k: results[k][2]["expectancy_R"], default=None)
    md.append(f"\nBest on train: **{best}**" if best else "\nNo variant met 150-trades min.")

    # D1 + trend filter (D1 was closest to breakeven)
    dfd = load_d1()
    nd = len(dfd)
    ds0, ds1, ds2, ds3 = splits(nd)
    dlo, dhi = band_for(dfd, ds0, ds1)
    dcfg = Cfg(atr_min=dlo, atr_max=dhi, trend_ema=200, tp_mult=3.0,
               session_start=0, session_end=23, friday_block_hour=0)
    rd = run_backtest(dfd, dcfg)
    dmt = split_metrics(rd["trades"], rd["equity"], ds0, ds1, dcfg.starting_equity)
    dmv = split_metrics(rd["trades"], rd["equity"], ds1, ds2, dcfg.starting_equity)
    dms = split_metrics(rd["trades"], rd["equity"], ds2, ds3, dcfg.starting_equity)
    md.append(f"\nD1 + EMA200 trend + TP 3.0 (ATR band [{dlo},{dhi}]): "
              f"TRAIN {dmt['expectancy_R']:+.3f}R ({dmt['trades']}) | "
              f"VAL {dmv['expectancy_R']:+.3f}R ({dmv['trades']}) | "
              f"TEST {dms['expectancy_R']:+.3f}R ({dms['trades']}) "
              f"PF {dms['profit_factor']:.2f} net ${dms['net_pnl']:+,.0f} "
              f"maxDD {dms['max_dd_pct']:.1f}%")
    print(f"{'D1+trend+TP3.0':38s} TRAIN {dmt['expectancy_R']:+.3f}R | VAL {dmv['expectancy_R']:+.3f}R | TEST {dms['expectancy_R']:+.3f}R")

    with open(os.path.join(OUT, "VARIANTS.md"), "w") as f:
        f.write("\n".join(md))
    # append to main report
    with open(os.path.join(OUT, "REPORT.md"), "a") as f:
        f.write("\n".join(md) + "\n")
    print(f"\ndone in {time.time() - t0:.0f}s -> out/VARIANTS.md (+ appended to REPORT.md)")


if __name__ == "__main__":
    main()
