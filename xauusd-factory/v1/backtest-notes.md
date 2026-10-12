# Backtest notes for XAUUSD_AgentEA v1 (stage: backtest-analyst)

> **Bottom line:** v1 is **inconclusive and close to break-even** on a small bar-level proxy: 71 trades and a pooled expectancy of **+0.01 R**.
> That is not evidence of an edge, and it is not evidence against one either. The real test is the MT5 real-tick plan in §4.
> Nothing here has been verified on a live account.

## 1. Evidence status

| Item | Measured (proxy, this sandbox) | Measured (MT5) | Not yet measured |
|---|---|---|---|
| Logic produces trades in both directions, filters engage | ✅ | n/a | n/a |
| Rough performance on about 8,000 bars over 3 periods | ✅ (below) | n/a | n/a |
| Compile in MetaEditor | n/a | n/a | ❌ user action (F7) |
| Real-tick performance 2021→present, walk-forward | n/a | n/a | ❌ |
| Spread/slippage stress on real ticks | partial (proxy spread ×1.5) | n/a | ❌ |
| News filter effect | n/a | n/a | ❌ (only works live) |

## 2. Proxy simulation

Reproduce it with `python3 tools/proxy_backtest.py --stress --json tools/proxy_results.json`. The script uses only the stdlib, fetches about 400 KB of data into `/tmp`, and takes about 1 second.

**Method.** The script ports `03-strategy-spec.md` 1:1 at bar level. Signals use closed bars. Entries fill at the next bar's open, with buys at the ask (open + spread). When the SL and the TP are both inside one bar, **the SL is assumed to fill**. A gap through the SL fills at the open. BE and the trail are updated at bar close. Risk is 0.5% of equity per trade, compounded. The daily caps and kill switch are included. Commission, swap and slippage are **not** modelled.

**Data.** Three small public samples are fetched on demand from GitHub and are **not committed** (see `SAMPLES` in the script). Timezones were inferred from the hourly range profile: the NY-open volatility peak must fall at 12–15 GMT. While writing these notes, sample 3 turned out to use UTC timestamps, not GMT+3. That was corrected **before** any parameter was looked at, and the correction made its result worse.

| Sample | Bars | Period | Signal / regime TF | Spread | GMT offset |
|---|---|---|---|---|---|
| h1_2024 | 2,923 | 2024-04-30 → 2024-10-25 | H1 / H4 (not the EA default) | 0.30 | +3 |
| m15_2025_12 | 2,048 | 2025-12-24 → 2026-01-28 | M15 / H1 | 0.40 | +2 |
| m15_2026_08 | 3,000 | 2026-08-05 → 2026-09-18 | M15 / H1 | 0.45 | 0 |

### Results with the default parameters (fixed before the first run)

| Sample | Trades | Win | PF | Exp (R) | Net | Max DD |
|---|---|---|---|---|---|---|
| h1_2024 | 31 (31L/0S) | 45.2% | 1.02 | +0.011 | +0.12% | 3.08% |
| m15_2025_12 | 20 (20L/0S) | 45.0% | 1.12 | +0.065 | +0.61% | 2.48% |
| m15_2026_08 | 20 (7L/13S) | 40.0% | 0.92 | −0.046 | −0.50% | 1.99% |
| **Pooled** | **71** | n/a | n/a | **+0.010** | n/a | n/a |

Exit mix (default): about 79% of trades ended at the SL. That count includes break-even and trailed exits, which is why the win rate is above the TP rate. About 20% hit the TP.

### Robustness neighbourhood (±1 step, **not** used to pick parameters)

| Variant | h1_2024 PF | m15_2025_12 PF | m15_2026_08 PF |
|---|---|---|---|
| default | 1.02 | 1.12 | 0.92 |
| spread ×1.5 | 1.01 | 1.12 | 0.85 |
| pullback_bars 4 / 8 | 1.14 / 1.08 | 1.12 / 1.05 | 0.94 / 0.91 |
| tp_rr 1.5 / 2.5 | 1.09 / 0.95 | 0.97 / 1.08 | 0.88 / 0.90 |
| adx_min 15 / 25 | 1.07 / 1.34 | 0.95 / 1.29 | 0.74 / 1.01 |

**Reading.**
- The neighbourhood is **flat around PF ≈ 1**. There is no sharp peak, which is a sign the defaults are not curve-fit, but there is no clear edge either.
- Spread sensitivity is low, because the SL is ≥ 1 ATR and spread is about 5% of ATR.
- `adx_min 25` comes out better in all three samples. That is a **hypothesis for v2 only**. It was found in sample, and 13–27 trades per sample is far too few to adopt it.
- The 2024 and Dec 2025 samples were strong uptrends, so only longs fired there. The short logic has been exercised in only one sample.

## 3. Caveats

1. **Sample size.** 71 trades is noise-dominated. The standard error of the mean R is about ±0.15 R, which is much larger than the measured +0.01 R.
2. **Bar-level fills.** The proxy assumes the SL fills on ties (pessimistic) and models no slippage, commission or swap (optimistic). The EA's per-tick BE and trail will differ.
3. **Indicator differences.** The ATR (SMA of TR), RSI (Wilder) and ADX (EMA-smoothed DI) in the proxy approximate MT5's built-in versions. EMA warm-up differs too.
4. **Sample 1 runs on H1/H4**, not on the EA's default M15/H1, so it tests the logic's behaviour when the timeframes are scaled.
5. **Data provenance.** These are third-party samples with unknown broker feeds, and the timezones were inferred.

## 4. MT5 Strategy Tester plan (the real validation)

| Setting | Value |
|---|---|
| Model | **Every tick based on real ticks** |
| Symbol / TF | XAUUSD (your broker's symbol). Chart M15. Inputs: signal M15, regime H1 |
| Deposit / leverage | 10,000 USD / 1:100 (match your real account) |
| Spread | Real-tick spread from history. Repeat the run with a fixed spread at 1.5× the broker's typical value |
| Delays | "Random delay" on the second run |
| `InpServerGMTOffset` | Your broker's winter offset (usually 2). Note that DST moves the session by 1 hour in summer: run once with 2 and once with 3 |
| In-sample | 2021-01-01 → 2024-06-30 |
| Out-of-sample | 2024-07-01 → latest. Run it **once**, after the parameters are frozen |
| Walk-forward | Use the tester's "Forward" option with 1/4 forward. Also do rolling 12-month in-sample / 3-month out-of-sample windows done by hand |
| Optimisation criterion | "Custom max" (uses `OnTester()`) |
| Optimisation grid (in-sample only, coarse) | `InpPullbackBars` 4–10 step 2 · `InpAdxMin` 15–30 step 5 · `InpTpRR` 1.5–3.0 step 0.5 · `InpSlMinATR` 0.8–1.4 step 0.2. That is 256 combinations. Use the genetic optimiser if it is slow |
| Selection rule | Pick the centre of the widest plateau where PF > 1.1, **not** the single best pass |

**Pass/fail thresholds** (from `pipeline/02-quant-analysis.md`): out of sample with at least 100 trades, PF ≥ 1.10, expectancy ≥ +0.05 R, max equity DD ≤ 12%, and PF ≥ 1.0 under spread ×1.5.
A failure on any one means **drop the idea in v2. Do not re-tune it.**

Check the Journal for the log lines `Entry failed`, `Modify failed`, `Close failed`, `Skip:` and `KILL SWITCH`. If any of them occurs more than once per 100 trades, it needs investigating.

## 5. Hypotheses for v2

1. **ADX 25 regime threshold.** It was better in all three proxy samples. Validate it only on the MT5 out-of-sample period.
2. **Add module B (London breakout of the Asian range)** as an uncorrelated second setup, using the same risk engine and a separate magic-number offset.
3. **Short-side behaviour.** It has been exercised in only one sample. Check the MT5 results separately for longs and shorts. If the shorts are negative, consider a long-only regime when the price is above the D1 EMA200.
