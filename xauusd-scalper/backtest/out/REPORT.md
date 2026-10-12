# Backtest Report — XauUsdScalper (Python mirror)

- Data: XAUUSD H1, 2004-06-11 07:00:00 → 2025-06-06 06:00:00, 122028 bars (source: github.com/FeziweMelvin/XAUUSD-Gold-Price)
- ATR band (train p10–p90): [1.14, 5.52] | cost/oz round trip: $0.4
- Splits (time-ordered): train 60% / val 20% / test 20%

### BASELINE

| split | trades | win% | exp R | net $ | PF | maxDD% | maxConsecLoss | avgBars |
|---|---|---|---|---|---|---|---|---|
| TRAIN | 857 | 18.0 | -0.347 | -7,469 | 0.37 | -75.1 | 32 | 2.8 |
| VAL | 330 | 21.2 | -0.311 | -892 | 0.45 | -36.6 | 28 | 3.2 |
| TEST | 265 | 14.0 | -0.378 | -507 | 0.34 | -31.0 | 23 | 2.5 |
| FULL | 1452 | 18.0 | -0.345 | -8,868 | 0.38 | -88.9 | 32 | 2.8 |

## Cost sensitivity (baseline params)

| cost/oz | TEST exp R | TEST net $ | TEST maxDD% |
|---|---|---|---|
| 0.25 | -0.365 | -704 | -34.7 |
| 0.40 | -0.378 | -507 | -31.0 |
| 0.55 | -0.418 | -374 | -27.8 |

### GRID-BEST

| split | trades | win% | exp R | net $ | PF | maxDD% | maxConsecLoss | avgBars |
|---|---|---|---|---|---|---|---|---|
| TRAIN | 762 | 17.5 | -0.306 | -6,679 | 0.43 | -67.5 | 27 | 2.9 |
| VAL | 309 | 21.4 | -0.289 | -1,086 | 0.46 | -33.4 | 25 | 3.3 |
| TEST | 284 | 15.1 | -0.374 | -742 | 0.36 | -33.7 | 21 | 2.6 |
| FULL | 1355 | 17.9 | -0.316 | -8,508 | 0.43 | -85.3 | 27 | 2.9 |

## Monte Carlo (test-set trades, 1000 shuffles)

| config | P(final < 90%) | P(min < 90%) | final min $ | final median $ |
|---|---|---|---|---|
| BASELINE | 0.0% | 0.0% | 9,493 | 9,493 |
| GRID-BEST | 0.0% | 0.0% | 9,258 | 9,258 |

## Go-live gates (test set, spec §6)

| gate | threshold | BASELINE | GRID-BEST |
|---|---|---|---|
| expectancy | > 0 | FAIL | FAIL |
| max drawdown | < 10% | FAIL | FAIL |
| profit factor | > 1.3 | FAIL | FAIL |
| MC P(final<90%) | < 10% | PASS | PASS |

## D1 sanity (daily, ATR band [6.54,27.5], no session filter)


### D1 SANITY

| split | trades | win% | exp R | net $ | PF | maxDD% | maxConsecLoss | avgBars |
|---|---|---|---|---|---|---|---|---|
| TRAIN | 97 | 32.0 | -0.116 | -438 | 0.77 | -7.4 | 14 | 5.7 |
| VAL | 34 | 38.2 | -0.179 | -193 | 0.71 | -4.3 | 7 | 6.0 |
| TEST | 30 | 30.0 | -0.026 | -22 | 0.95 | -2.5 | 8 | 4.9 |
| FULL | 161 | 32.9 | -0.113 | -653 | 0.78 | -10.6 | 14 | 5.6 |
## Strategy iteration round — structural variants (H1)

Ranked on TRAIN; VAL/TEST are confirm-only (no peeking). Same ATR band, same risk layer.

| variant | TRAIN expR | VAL expR | TEST expR | TEST win% | TEST PF | TEST maxDD% | TEST trades |
|---|---|---|---|---|---|---|---|
| V0 baseline (as-is) | -0.347 | -0.311 | -0.378 | 14 | 0.34 | -31.0 | 265 |
| V1 +EMA200 trend filter | -0.305 | -0.261 | -0.416 | 15 | 0.33 | -27.7 | 182 |
| V2 trend + TP 3.0xATR | -0.285 | -0.266 | -0.443 | 13 | 0.29 | -29.5 | 182 |
| V3 trend + TP 3.5xATR | -0.279 | -0.257 | -0.442 | 13 | 0.29 | -29.5 | 182 |
| V4 trend, no BE (pure SL/TP) | -0.013 | -0.068 | -0.202 | 36 | 0.71 | -16.6 | 182 |
| V5 trend, no TP (trail after BE) | -0.218 | -0.180 | -0.205 | 0 | 0.00 | -15.9 | 187 |
| V6 trend + SL 2.0 / TP 3.0 (wide) | -0.177 | -0.163 | -0.369 | 20 | 0.34 | -25.2 | 178 |
| V7 trend + SL 1.2 / TP 2.5 (tight) | -0.358 | -0.310 | -0.480 | 9 | 0.25 | -31.6 | 185 |
| V8 trend + 24h session | -0.270 | -0.261 | -0.302 | 22 | 0.47 | -25.1 | 255 |
| V9 no trend, TP 3.0 | -0.343 | -0.309 | -0.389 | 12 | 0.33 | -31.9 | 272 |

Best on train: **V4 trend, no BE (pure SL/TP)**

D1 + EMA200 trend + TP 3.0 (ATR band [6.54,27.5]): TRAIN +0.036R (54) | VAL -0.134R (20) | TEST -0.047R (21) PF 0.96 net $-11 maxDD -1.9%

## FINAL VERDICT (iteration round complete)

1. **V1 (EA as shipped) — FAIL.** Negative expectancy on train, val, and test
   (−0.35R / −0.31R / −0.38R on H1); all 36 grid combinations negative;
   cost-insensitive (negative at $0.25–$0.55/oz). The account curve collapsed
   (maxDD −89% over 21 years).
2. **Structural iteration findings (H1):**
   - **Break-even at +1R is the #1 destroyer** (−0.30R with BE vs −0.01R
     without, all else equal). Gold H1 pullbacks routinely retrace >1R; the BE
     layer converts would-be winners into breakevens and adds churn.
   - **EMA200 trend filter helps modestly** (+0.04R) but does not fix the core.
   - Wider TP (3.0–3.5x) does NOT help — the issue is entry quality in ranges,
     not exit distance.
   - Best H1 variant (trend + no BE) still −0.20R on TEST.
3. **D1 + trend + TP3.0**: +0.036R on train but NEGATIVE on val (−0.13R) and
   test (−0.05R) → does not survive out-of-sample. Not an edge.
4. **Conclusion: DO NOT DEPLOY.** The EMA-cross + RSI entry family, as
   specified, has no robust positive expectancy on 21y of real XAUUSD data.
   Per spec §6, a negative result means iterate the strategy — not the
   parameters, not the risk layer (which behaved correctly: breakers, sizing,
   and caps all worked as designed).

### Honest limitations of this backtest
- Bar-based Python mirror of the MQL5 logic — NOT the MT5 Strategy Tester with
  real ticks; intra-bar exit ambiguity resolved conservatively (SL before TP).
- Data timezone is the source's local time (hour-of-day semantics approximate;
  server-time session filter may be shifted by a few hours).
- Flat cost model; no variable spread, commission is inside the $0.40/oz.
- The EA was *designed* for M5; this ran it on H1 (no M5 data reachable in the
  sandbox). H1 is a harsher-cost proxy for M5 (lower ATR per bar would make
  the same $0.40 cost a larger fraction of R) — treat this as a red flag, and
  still run the M5 Strategy Tester (README protocol) before any deployment.

### Next steps (ranked)
1. **Re-spec the strategy** (new council + spec round): promising directions
   from this data — (a) trend-following bias with pullback entries instead of
   raw crosses; (b) daily-regime filter driving H1 entries; (c) drop the BE
   layer entirely. Each needs its own spec + review before code.
2. **Get M5 data from the user's broker** (MT5: Tools → History Center, or
   CSV export) and rerun the M5 protocol in Strategy Tester.
3. If a variant ever passes ALL gates on test (expR>0, DD<10%, PF>1.3,
   MC P<10%) → 4 weeks demo first.
