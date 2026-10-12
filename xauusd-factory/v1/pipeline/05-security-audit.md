# 05: Security and operational-safety audit (stage: security-auditor)

Version: v1. Reviewed: `XAUUSD_AgentEA.mq5`, against spec `03-strategy-spec.md` v1.
Method: manual line-by-line review plus a static grep for forbidden APIs. Assume the account is live.

## Checklist

| # | Check | Result |
|---|---|---|
| 1 | No `#import`, DLL, `WebRequest`, sockets, file writes or hard-coded credentials | ✅ PASS. The only include is `Trade\Trade.mqh`, and the only I/O is `Print` |
| 2 | Every input is range-checked and init fails on bad values | ✅ PASS. `ValidateInputs()` covers every numeric, timeframe and string input (bools need no check) and returns `INIT_PARAMETERS_INCORRECT`. Risk is capped at 3% |
| 3 | SL is set at send time and is outside the stops level | ✅ PASS. The SL is passed to `Buy`/`Sell`, and the trade is skipped if the SL or TP is inside `SYMBOL_TRADE_STOPS_LEVEL` |
| 4 | Lot floored, capped by the user maximum and the broker maximum, skipped below the minimum, margin checked | ✅ PASS. `LotsForRisk()`. Margin must be ≤ 90% of free margin |
| 5 | No martingale, grid, averaging down, or unbounded position count | ✅ PASS. One position per symbol and magic. Size depends only on equity and SL distance |
| 6 | Daily loss cap and kill switch survive a restart | ✅ PASS. Daily stats come from the deal history, and peak and kill state are stored in terminal global variables |
| 7 | Retcodes checked, retries on a cooldown, no spam loop | ✅ PASS after fix H-1. Entries use a 60 s cooldown, modifications 5 s, and closes 10 s |
| 8 | Spread, session and news guards, with tester behaviour documented | ✅ PASS. The news guard is live-only and is documented in the README and backtest notes |
| 9 | Magic-number isolation | ✅ PASS. Every position and deal loop filters on symbol and magic |
| 10 | Netting and hedging accounts | ✅ PASS. On netting accounts the EA refuses to enter when a foreign position exists on the symbol |
| 11 | Freeze level, and no division by zero | ✅ PASS. `ModifySL` checks the freeze level. ATR, avgATR, tick size, step, R and loss-per-lot are all guarded with `> 0` |
| 12 | Wrong-symbol protection | ✅ PASS. Init fails unless the symbol contains XAU or GOLD, with an explicit override input |

## Findings

| ID | Severity | Location | Issue | Status |
|---|---|---|---|---|
| H-1 | **High** | `ManagePositions()`, hard-exit branch | `PositionClose` was retried on **every tick** after a failure. During a Friday close or a disconnect, this could flood the broker with requests and get the account flagged | **Fixed**: 10 s close-failure cooldown, and the retcode description is logged |
| M-1 | Medium | `ManagePositions()` trailing | A minimum SL step of 0.02 × ATR (about $0.15) could send dozens of modify requests per minute in fast markets | **Fixed**: the minimum step is now 0.10 × ATR |
| M-2 | Medium | `RefreshNews()` | If the calendar is unavailable, the news filter silently does nothing (fail-open) | **Fixed (mitigated)**: an hourly warning is logged. Fail-open is kept on purpose, because fail-closed would stop all trading whenever the calendar is down. Documented |
| L-1 | Low | `KillSwitchTripped()` | A withdrawal lowers equity relative to the stored peak and can trip the kill switch | Accepted. This is fail-safe (it stops trading and never adds risk). Reset with `InpResetKillSwitch=true` |
| L-2 | Low | `DailyLimitsHit()` | Day-start balance = balance − this EA's closed PnL today. A deposit, a withdrawal, or another EA's PnL shifts the base | Accepted. The error is small and the approach is restart-safe. Documented |
| L-3 | Low | `InitialRisk()` | If the EA restarts after a BE move and the global variable is lost, R falls back to `SlMinATR × ATR` | Accepted. Only the BE/trail trigger points move; the broker-side SL stays in place |
| L-4 | Low | Time exit / Friday flat | A forced close can happen while the spread is wide | Accepted. It is bounded by `InpSlippagePoints`, and weekend-gap risk is the bigger danger |
| I-1 | Info | Build | Not compiled in this sandbox (no MetaEditor) | The user must compile with F7. See `04-build-notes.md` |
| I-2 | Info | Day boundary | "Today" is the server day, not the GMT day | Documented |
| I-3 | Info | Magic number | The default magic `26101201` can collide with another EA that uses the same number | Change it per chart if you run several instances |

## Verdict

**PASS.** There are no open Critical or High findings. H-1 was sent back to `mql5-pro` once and the fix was verified.
This verdict covers code safety only. It says **nothing** about profitability. See `../backtest-notes.md`.
