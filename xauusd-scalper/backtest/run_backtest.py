"""
H1 + D1 backtest pipeline for XauUsdScalper (Python mirror of the MQL5 EA).

Protocol (spec.md §6): train 60% / val 20% / test 20% (time-ordered),
ATR band chosen from TRAIN percentiles only, small grid on train,
confirm on val/test, Monte Carlo on test, cost sensitivity.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import Cfg, run_backtest, split_metrics, monte_carlo, fmt_metrics, atr_sma  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def load_h1():
    df = pd.read_csv(os.path.join(HERE, "data", "XAU_1h_data.csv"), sep=";")
    df["ts"] = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M")
    df = df.rename(columns={"Open": "o", "High": "h", "Low": "l", "Close": "c"})[
        ["ts", "o", "h", "l", "c"]].sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    return df


def load_d1():
    df = pd.read_csv(os.path.join(HERE, "data", "XAU_1d_data.csv"), sep=";")
    df["ts"] = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M")
    df = df.rename(columns={"Open": "o", "High": "h", "Low": "l", "Close": "c"})[
        ["ts", "o", "h", "l", "c"]].sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    return df


def splits(n):
    t = int(n * 0.6)
    v = int(n * 0.8)
    return 0, t, v, n


def atr_band(c, h, l, lo, hi, period=14, lo_q=0.10, hi_q=0.90):
    a = atr_sma(h[lo:hi], l[lo:hi], c[lo:hi], period)
    a = a[~np.isnan(a)]
    return round(float(np.percentile(a, 100 * lo_q)), 2), round(float(np.percentile(a, 100 * hi_q)), 2)


def report_splits(res, n, start_eq, label, md):
    s0, s1, s2, s3 = splits(n)
    rows = {
        "TRAIN": split_metrics(res["trades"], res["equity"], s0, s1, start_eq),
        "VAL":   split_metrics(res["trades"], res["equity"], s1, s2, start_eq),
        "TEST":  split_metrics(res["trades"], res["equity"], s2, s3, start_eq),
        "FULL":  split_metrics(res["trades"], res["equity"], 0, n, start_eq),
    }
    md.append(f"\n### {label}\n")
    md.append("| split | " + " | ".join(
        ["trades", "win%", "exp R", "net $", "PF", "maxDD%", "maxConsecLoss", "avgBars"]) + " |")
    md.append("|---" * 9 + "|")
    for k, m in rows.items():
        pf = "inf" if m["profit_factor"] == float("inf") else f"{m['profit_factor']:.2f}"
        md.append(f"| {k} | {m['trades']} | {m['win_rate_pct']:.1f} | {m['expectancy_R']:+.3f} "
                  f"| {m['net_pnl']:+,.0f} | {pf} | {m['max_dd_pct']:.1f} "
                  f"| {m['max_consec_losses']} | {m['avg_bars']:.1f} |")
    print(f"[{label}] " + " || ".join(f"{k}: {fmt_metrics(m)}" for k, m in rows.items()))
    return rows


def main():
    t0 = time.time()
    df = load_h1()
    n = len(df)
    c, h, l = df["c"].to_numpy(), df["h"].to_numpy(), df["l"].to_numpy()
    s0, s1, s2, s3 = splits(n)
    print(f"H1 data: {df.ts.iloc[0]} -> {df.ts.iloc[-1]} | bars={n} | "
          f"train[{s0}:{s1}] val[{s1}:{s2}] test[{s2}:{s3}]")
    bars_per_day = df.groupby(df["ts"].dt.date).size()
    print(f"bars/day: mean={bars_per_day.mean():.1f} min={bars_per_day.min()} max={bars_per_day.max()}")

    band_lo, band_hi = atr_band(c, h, l, s0, s1)
    print(f"ATR band (train p10-p90): [{band_lo}, {band_hi}]")

    base = Cfg(atr_min=band_lo, atr_max=band_hi)
    print("\n== BASELINE (EA defaults, H1-scaled) ==")
    res = run_backtest(df, base)
    md = []
    md.append("# Backtest Report — XauUsdScalper (Python mirror)\n")
    md.append(f"- Data: XAUUSD H1, {df.ts.iloc[0]} → {df.ts.iloc[-1]}, {n} bars "
              f"(source: github.com/FeziweMelvin/XAUUSD-Gold-Price)")
    md.append(f"- ATR band (train p10–p90): [{band_lo}, {band_hi}] | cost/oz round trip: ${base.cost_per_oz}")
    md.append("- Splits (time-ordered): train 60% / val 20% / test 20%")
    rows_base = report_splits(res, n, base.starting_equity, "BASELINE", md)

    res["trades_df"] = pd.DataFrame(res["trades"])
    res["trades_df"].to_csv(os.path.join(OUT, "trades_h1_baseline.csv"), index=False)
    pd.DataFrame({"ts": res["ts"], "equity": res["equity"]}).to_csv(
        os.path.join(OUT, "equity_h1_baseline.csv"), index=False)

    # ---- cost sensitivity -------------------------------------------
    md.append("\n## Cost sensitivity (baseline params)\n")
    md.append("| cost/oz | TEST exp R | TEST net $ | TEST maxDD% |")
    md.append("|---|---|---|---|")
    for cost in (0.25, 0.40, 0.55):
        r2 = run_backtest(df, Cfg(atr_min=band_lo, atr_max=band_hi, cost_per_oz=cost))
        m = split_metrics(r2["trades"], r2["equity"], s2, s3, base.starting_equity)
        md.append(f"| {cost:.2f} | {m['expectancy_R']:+.3f} | {m['net_pnl']:+,.0f} | {m['max_dd_pct']:.1f} |")
        print(f"cost {cost:.2f} TEST: {fmt_metrics(m)}")

    # ---- grid on train (4 params per spec) ---------------------------
    print("\n== GRID (train only) ==")
    grid = []
    for ef in (7, 9, 12):
        for es in (17, 21, 26):
            for slm in (1.2, 1.5):
                for tpm in (2.0, 2.5):
                    cfg = Cfg(ema_fast=ef, ema_slow=es, sl_mult=slm, tp_mult=tpm,
                              atr_min=band_lo, atr_max=band_hi)
                    r = run_backtest(df, cfg)
                    m = split_metrics(r["trades"], r["equity"], s0, s1, base.starting_equity)
                    grid.append((cfg, m, r))
    grid_df = pd.DataFrame([{
        "ef": g[0].ema_fast, "es": g[0].ema_slow, "sl": g[0].sl_mult, "tp": g[0].tp_mult,
        **{k: g[1][k] for k in ("trades", "expectancy_R", "profit_factor", "max_dd_pct", "win_rate_pct")},
    } for g in grid])
    grid_df = grid_df[grid_df.trades >= 150]
    grid_df = grid_df.sort_values("expectancy_R", ascending=False)
    grid_df.to_csv(os.path.join(OUT, "grid_train_results.csv"), index=False)
    print(grid_df.head(10).to_string(index=False))

    best_cfg, best_m, best_res = None, None, None
    if len(grid_df):
        top = grid_df.iloc[0]
        for g in grid:
            if (g[0].ema_fast == top.ef and g[0].ema_slow == top.es
                    and g[0].sl_mult == top.sl and g[0].tp_mult == top.tp):
                best_cfg, best_m, best_res = g
                break
    if best_cfg is not None:
        print(f"\n== GRID-BEST (ef={best_cfg.ema_fast} es={best_cfg.ema_slow} "
              f"sl={best_cfg.sl_mult} tp={best_cfg.tp_mult}) ==")
        report_splits(best_res, n, base.starting_equity, "GRID-BEST", md)
        best_res["trades_df"] = pd.DataFrame(best_res["trades"])
        best_res["trades_df"].to_csv(os.path.join(OUT, "trades_h1_gridbest.csv"), index=False)
    else:
        md.append("\nGRID: no combination met the 150-trades/train minimum.")

    # ---- Monte Carlo on TEST ----------------------------------------
    md.append("\n## Monte Carlo (test-set trades, 1000 shuffles)\n")
    md.append("| config | P(final < 90%) | P(min < 90%) | final min $ | final median $ |")
    md.append("|---|---|---|---|---|")
    mc_results = {}
    runs = [("BASELINE", res)]
    if best_res is not None:
        runs.append(("GRID-BEST", best_res))
    for label, r in runs:
        test_trades = [t for t in r["trades"] if s2 <= t["entry_i"] < s3]
        mc = monte_carlo(test_trades, base.starting_equity)
        mc_results[label] = mc
        md.append(f"| {label} | {mc['p_final_below_90']*100:.1f}% | {mc['p_min_below_90']*100:.1f}% "
                  f"| {mc['final_min']:,.0f} | {mc['final_median']:,.0f} |")
        print(f"MC {label}: {mc}")

    # ---- go-live gates (spec §6) -------------------------------------
    md.append("\n## Go-live gates (test set, spec §6)\n")
    md.append("| gate | threshold | BASELINE | GRID-BEST |")
    md.append("|---|---|---|---|")
    tb = rows_base["TEST"]
    tg = (split_metrics(best_res["trades"], best_res["equity"], s2, s3, base.starting_equity)
          if best_res is not None else None)
    def gate(name, thr, ok_b, ok_g):
        return f"| {name} | {thr} | {'PASS' if ok_b else 'FAIL'} | " \
               f"{'PASS' if ok_g else 'FAIL' if ok_g is not None else '—'} |"
    md.append(gate("expectancy", "> 0", tb["expectancy_R"] > 0,
                   tg["expectancy_R"] > 0 if tg else None))
    md.append(gate("max drawdown", "< 10%", tb["max_dd_pct"] > -10.0,
                   tg["max_dd_pct"] > -10.0 if tg else None))
    md.append(gate("profit factor", "> 1.3", tb["profit_factor"] > 1.3,
                   tg["profit_factor"] > 1.3 if tg else None))
    md.append(gate("MC P(final<90%)", "< 10%", mc_results["BASELINE"]["p_final_below_90"] < 0.10,
                   mc_results.get("GRID-BEST", {}).get("p_final_below_90", 99) < 0.10 if "GRID-BEST" in mc_results else None))

    # ---- equity chart --------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        eq = res["equity"]
        tsv = res["ts"]
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(tsv, eq, lw=0.8, color="#1f77b4")
        for x, lbl in ((tsv[s1], "val start"), (tsv[s2], "test start")):
            ax.axvline(x, color="red", ls="--", lw=0.8)
            ax.text(x, ax.get_ylim()[0], f" {lbl}", rotation=90, fontsize=8)
        ax.set_title(f"XauUsdScalper (H1, Python mirror) — equity, start ${base.starting_equity:,.0f}")
        ax.set_ylabel("Equity ($)")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, "equity_h1.png"), dpi=110)
        print("\nchart -> out/equity_h1.png")
    except Exception as e:  # chart is optional
        print("chart failed:", e)

    # ---- D1 sanity -----------------------------------------------------
    print("\n== D1 sanity (daily bars, same engine) ==")
    dfd = load_d1()
    nd = len(dfd)
    cd, hd, ld = dfd["c"].to_numpy(), dfd["h"].to_numpy(), dfd["l"].to_numpy()
    ds0, ds1, ds2, ds3 = splits(nd)
    d_lo, d_hi = atr_band(cd, hd, ld, ds0, ds1)
    dcfg = Cfg(atr_min=d_lo, atr_max=d_hi, time_exit_bars=12,
               session_start=0, session_end=23, friday_block_hour=0)
    resd = run_backtest(dfd, dcfg)
    md.append(f"\n## D1 sanity (daily, ATR band [{d_lo},{d_hi}], no session filter)\n")
    report_splits(resd, nd, dcfg.starting_equity, "D1 SANITY", md)

    with open(os.path.join(OUT, "REPORT.md"), "w") as f:
        f.write("\n".join(md))
    print(f"\ndone in {time.time() - t0:.0f}s -> {OUT}/REPORT.md")


if __name__ == "__main__":
    main()
