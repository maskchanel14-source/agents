# 04: Build notes (stage: mql5-pro)

Version: v1. File: `../XAUUSD_AgentEA.mq5`, about 870 lines. It is a single file and depends only on `Trade\Trade.mqh` (standard library).

## Spec-to-code map

| Spec section | Function(s) |
|---|---|
| §1 new-bar gating, closed bars | `IsNewSignalBar()`, `OnTick()`. Every `CopyBuffer` call starts at shift 1 |
| §2 regime | `EvaluateSignal()` (regime block) |
| §3 entry rules | `EvaluateSignal()` (bull/bear blocks) |
| §4 session | `InEntrySession()`, `GmtNow()`, `ServerGMTOffsetSeconds()` |
| §4 spread | `SpreadOk()` |
| §4 volatility band | `EvaluateSignal()` (ATR / avgATR) |
| §4 news | `RefreshNews()` (cached for 15 minutes), `InNewsBlackout()` |
| §4 daily caps | `TodayStats()` (deal history), `FloatingPnl()`, `DailyLimitsHit()` |
| §4 kill switch | `KillSwitchTripped()` (global variables `XAEA_<magic>_<login>_PEAK` / `_KILL`) |
| §4 exposure and permissions | `CountMyPositions()`, `ForeignPositionOnSymbol()`, `TradingPermitted()`, `SideAllowedBySymbol()` |
| §5 SL/TP and stops level | `TryEnter()` |
| §5 BE, trailing, time exit, Friday flat | `ManagePositions()`, `ModifySL()` (freeze/stops checks, 5 s failure cooldown), `InitialRisk()` |
| §6 sizing | `LotsForRisk()` (floored, skips below the minimum lot, margin check) |
| §8 restart safety | `InitialRisk()` global variables, `TodayStats()`, `CleanupRiskVars()` |
| Validation | `ValidateInputs()` → `INIT_PARAMETERS_INCORRECT` |
| Optimisation criterion | `OnTester()`: `PF × √trades × RecoveryFactor / (1 + DD%/10)`. Returns 0 when there are fewer than 30 trades or PF ≤ 1 |

## Deviations from the spec

- Break-even and trailing are evaluated **every tick** in the EA. The Python proxy evaluates them once at bar close, so the EA protects profit slightly sooner.
- The spread filter is checked after the signal, which lets the EA log skipped signals. The result is the same.
- An SL modification is only sent when the new SL improves on the old one by at least `max(tick, 0.10 × ATR)` (audit M-1). The proxy tightens on any improvement.
- Changes made after the stage-5 audit: a 10 s close-failure cooldown (H-1), and a warning when the news filter is fail-open (M-2).

## Compile status: NOT COMPILED IN THIS SANDBOX

The sandbox runs Linux with no MetaEditor or Wine, so the file was **not** compiled with `metaeditor64.exe`.
Mitigations:
- A static check confirmed balanced braces, parentheses and brackets, that every input is used, and that every called function is either defined in the file or is a standard MQL5 or CTrade API.
- APIs relied on (MQL5 build ≥ 3000): `iMA`, `iATR`, `iRSI`, `iADX`, `CopyBuffer`, `CopyHigh/Low/Close`, `iTime`, `iClose`, `iBarShift`, `CalendarValueHistory`, `CalendarEventById`, `OrderCalcMargin`, `HistorySelect`, `HistoryDeal*`, `GlobalVariable*`, `TesterStatistics(STAT_TRADES|STAT_PROFIT_FACTOR|STAT_RECOVERY_FACTOR|STAT_EQUITY_DDREL_PERCENT)`, and the CTrade methods `Buy`, `Sell`, `PositionModify`, `PositionClose`, `SetTypeFillingBySymbol`, `SetMarginMode`, `LogLevel`, `ResultRetcode`, `ResultRetcodeDescription`.
- **Action for the user:** open the file in MetaEditor and press F7. Expect 0 errors. If anything fails, paste the compiler output into the next factory run (`/xauusd-factory fix compile: ...`).
