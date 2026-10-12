# 03: Strategy spec, the build contract (stage: trading-strategist)

Version: v1. Strategy name: **Gold Session Trend-Pullback (GSTP)**.

## Decision Record (orchestrator, not to be changed by stage agents)

- **Hypothesis.** Gold's intraday direction during London and NY is biased by its higher-timeframe trend, which is driven by real yields, the USD and safe-haven flows. A pullback to the M15 EMA20 "value" zone followed by a momentum resumption gives an entry with a favourable R-multiple, because the structural stop sits close behind it.
- **Why this edge and not the others.** It scored highest in `02` (18/25). It has few structural parameters, a natural stop location, and it can be tested at bar level without tick data. The Asian-range breakout comes in v2 as a second module.
- **What would falsify it.** On MT5 real ticks out of sample with at least 100 trades, PF < 1.10, or expectancy < +0.05 R, or max DD > 12%, or PF < 1 under spread ×1.5. Any one of these means the idea is dropped in v2 and does not get re-tuned.
- **Parameter budget.** 8 tunable parameters: `PullbackBars`, `TouchATR`, `AdxMin`, `SlMinATR`, `SlMaxATR`, `TpRR`, `BeTriggerR`, `TrailStartR`. The indicator periods (20/50/200/14) are market conventions and are deliberately **not** optimised.

## 1. Timeframes

- Signal TF = **M15**. Regime TF = **H1**. The regime TF must be higher than the signal TF.
- The entry logic runs **once per new signal bar** and only reads **closed bars**: shift 1 is the last closed bar.

## 2. Regime rules (regime TF, shift 1)

- `BULL` holds when `Close[1] > EMA50[1] > EMA200[1]` **and** `EMA50[1] > EMA50[1+3]` **and** `ADX14[1] ≥ 20`.
- `BEAR` is the mirror image: `Close[1] < EMA50[1] < EMA200[1]` **and** `EMA50[1] < EMA50[1+3]` **and** `ADX14[1] ≥ 20`.
- If neither holds, there is no trade.

## 3. Entry rules (signal TF; ATR = ATR14[1]; window W = shifts 1..6)

**Long** (requires `BULL`):
1. Touch: `min over W of (Low[i] − EMA20[i]) ≤ 0.25 × ATR`. Price came back to the EMA20 zone.
2. `Close[1] > EMA20[1]`
3. `Close[1] > High[2]`. Momentum resumes past the prior bar's high.
4. `RSI14[1] > 50`
5. No chasing: `Close[1] − EMA20[1] ≤ 1.0 × ATR`

**Short** (requires `BEAR`): the mirror image, using `EMA20[i] − High[i]`, `Close[1] < Low[2]` and `RSI < 50`.

## 4. Filters (all must pass)

| Filter | Rule |
|---|---|
| Session | GMT hour in [7, 20). No entries on Saturday or Sunday. On Friday, no entries from 18 GMT. GMT = server time − offset. The offset is auto-detected live; in the tester it comes from an input |
| Spread | `Ask − Bid ≤ 0.15 × ATR`. There is also an optional absolute cap in points (off by default) |
| Volatility band | `0.6 ≤ ATR[1] / mean(ATR[1..100]) ≤ 2.5` |
| News (live) | No entries from 30 minutes before to 30 minutes after a high-importance USD event in the MT5 calendar. Disabled in the tester |
| Daily caps | Fewer than 3 entries today **and** today's PnL (closed + floating, this magic) > −2% of the day-start balance |
| Kill switch | Equity must be above 85% of the peak equity (persisted in a terminal global variable) |
| Exposure | No open position for this symbol and magic. On netting accounts there must also be no foreign position on the symbol |
| Permissions | Terminal, program, account and expert trading must all be allowed. The symbol trade mode must allow the side |

## 5. Exits

- **Initial SL.** Long: `swing = min Low over W`, `raw = entry − (swing − 0.25 × ATR)`. Short: the mirror image. Then `SLdist = clamp(raw, 1.0 × ATR, 2.5 × ATR)`.
- **TP** = `entry ± 2.0 × SLdist`. TP = 0 disables it.
- **Break-even.** When `gain ≥ 1.0 R`, move the SL to `entry ± 0.1 R`.
- **Trailing.** When `gain ≥ 1.5 R`, trail the SL to `price ∓ 1.0 × ATR`, and only ever tighten it.
- **Time exit.** Close after 48 signal bars (12 hours).
- **Friday flat.** Close every position from 20 GMT on Friday.
- R is the **initial** SL distance. It is stored per ticket in a global variable, so it survives a restart.

## 6. Position sizing

`lots = floor( (equity × 0.5%) / (SLdist / tick_size × tick_value_loss) / step ) × step`, capped at `min(SYMBOL_VOLUME_MAX, InpMaxLots)`.
**Skip the trade** if `lots < SYMBOL_VOLUME_MIN`. Never round up. Also skip it if `OrderCalcMargin` is more than 90% of free margin.

## 7. Parameter table

| Input | Default | Range | Structural reason | Tunable |
|---|---|---|---|---|
| InpPullbackBars | 6 | 4–10 | About 1.5 hours of M15, one pullback swing | ✔ |
| InpTouchATR | 0.25 | 0.1–0.5 | Tolerance for "touched value" | ✔ |
| InpAdxMin | 20 | 15–30 | Classic trend/no-trend boundary | ✔ |
| InpSlMinATR | 1.0 | 0.8–1.5 | Keeps the SL outside the noise | ✔ |
| InpSlMaxATR | 2.5 | 2.0–3.5 | Caps R when the swing is far away | ✔ |
| InpTpRR | 2.0 | 1.5–3.0 | Trend-following payoff | ✔ |
| InpBeTriggerR | 1.0 | 0.8–1.5 | Protects open profit | ✔ |
| InpTrailStartR | 1.5 | 1.0–2.5 | Lets winners run past TP when TP is disabled | ✔ |
| EMA 20/50/200, RSI/ATR/ADX 14 | (fixed) | n/a | Market conventions, not optimised | ✘ |
| InpRiskPercent | 0.5 | 0.1–1.0 (validated ≤ 3) | Survives a streak of 10 losses | risk |
| InpDailyLossPct / InpKillSwitchDDPct | 2 / 15 | n/a | Circuit breakers | risk |

## 8. Edge cases

- **Gaps through the SL.** The broker fills at market. Sizing does not cover gaps, which is why the Friday-flat rule and the news filter exist.
- **Rejected orders.** Log the retcode and wait out a cooldown (default 60 s). There are no tight retry loops, and SL modifications have a 5 s cooldown.
- **EA restart with an open position.** R is recovered from the global variable. If it is missing and the SL has already moved, fall back to `SlMinATR × ATR`. Daily stats come from the deal history.
- **Netting accounts.** Never add to a net position that belongs to another magic number or to a manual trade.
- **Hedging accounts.** Only positions with this symbol and magic are counted or managed.
- **Wrong symbol.** Init fails unless the symbol contains XAU or GOLD. An override input exists.
