# REVIEW — Santa Method × comprehensive-review × silent-failure-hunter

Method (affan `skills/santa-method`): **two independent reviewers, same rubric
(spec.md §5), both must PASS; fix-and-re-review convergence loop; human
escalation cap = 2 rounds.** Reviewer lenses taken from `comprehensive-review`
(agents) and `silent-failure-hunter` (affan). Rubric: 8 categories × 1–5,
PASS = every category ≥ 4 AND total ≥ 36/40.

Environment honesty (santa-method "hallucination-prone claims" clause):
this sandbox has **no MQL5 compiler and no broker feed**, so R1 (API
correctness) was verified by static cross-check against the MQL5 standard
library signatures, not by a compile. Round-2 PASS does NOT replace a
MetaEditor compile + Strategy Tester run.

---

## Round 1

### Reviewer A — lens: `code-reviewer` + `silent-failure-hunter` (affan agents)
**Verdict: FAIL (37/40, R4=3, R7=3)**

| # | Sev | Finding | Disposition |
|---|-----|---------|-------------|
| A1 | MAJOR | `OnInit`: if `iRSI`/`iATR` handle creation fails after `iMA` succeeded, already-created handles were not released → handle leak per failed init (MQL5 caps indicator handles) | **Fixed (F1)** — release all non-invalid handles before `INIT_FAILED` |
| A2 | MINOR | Unused standard-library includes (`PositionInfo.mqh`, `SymbolInfo.mqh`) — dead surface, reviewer noise | **Fixed (F2)** — removed, only `Trade.mqh` kept |
| A3 | INFO | Trailing ATR read at shift 0 (forming bar) — deliberate: exits use live volatility, **signals never do** | Accepted, documented in README §operational |
| A4 | INFO | Re-attach mid-trade: `g_r0`/`g_entryTime` are in-memory → BE/trailing disabled, SL/TP stay active, time-exit suppressed by `g_entryTime > 0` guard | Accepted (conservative), documented |
| — | — | All 8 `CTrade` calls checked + retcode logged; `EMPTY_VALUE` guards present; `ResetTradeState` on failed send and on close | PASS R4 (post-fix) |

Score: R1 4 · R2 5 · R3 5 · R4 3 · R5 5 · R6 5 · R7 3 · R8 4 = 37 — FAIL (R4, R7 < 4)

### Reviewer B — lens: `security-auditor` + `architect-review` (agents comprehensive-review)
**Verdict: FAIL (38/40, R7=3)**

| # | Sev | Finding | Disposition |
|---|-----|---------|-------------|
| B1 | MAJOR | Send-failure path silently had no *stated* retry policy — a future maintainer could add a blind re-send loop on REQUOTE (re-entry at worse price, unbounded). Policy must be explicit in code | **Fixed (F3)** — code comment: "No blind re-send by design; next bar re-evaluated fresh" on both Buy/Sell failure paths |
| B2 | MINOR | Two instances with same magic on same symbol would share position management (netting accounts: one shared net position) | Documented: **one instance per symbol** (README §operational) |
| B3 | MINOR | Risk composition not sanity-checked: `InpRiskPercent × InpMaxDailyTrades` can exceed sane daily risk (e.g. 2% × 10 = 20%) without warning | **Fixed (F4)** — `OnInit` warning when the product > 10% |
| B4 | INFO | Filling mode negotiated from `SYMBOL_FILLING_MODE` flags (FOK→IOC→RETURN) — correct for multi-broker portability | Accepted |
| — | — | No persistent secrets; all limits input-driven; magic isolation on symbol+magic; slippage bounded via `SetDeviationInPoints`; breaker evaluated per tick on live equity | PASS R3 |

Score: R1 5 · R2 5 · R3 4 · R4 4 · R5 4 · R6 5 · R7 3 · R8 4 = 38 — FAIL (R7 < 4)

### Fixes applied between rounds
- **F1** (A1): handle release on `OnInit` partial failure.
- **F2** (A2): removed unused includes.
- **F3** (B1): explicit no-re-send policy in code (both directions).
- **F4** (B3): `OnInit` warning for `risk% × maxDailyTrades > 10%`.
- **F5** (R7): `README.md` written — install, params, backtest protocol, operational notes, provenance, disclaimers.

## Round 2 (both reviewers, fresh pass over post-fix code + docs)

| R# | Category | Reviewer A | Reviewer B |
|----|----------|-----------|-----------|
| R1 | API correctness | 5 | 5 |
| R2 | No look-ahead | 5 | 5 |
| R3 | Risk enforcement | 5 | 5 |
| R4 | No silent failures | 5 | 5 |
| R5 | Metrics | 5 | 5 |
| R6 | Parameter discipline | 5 | 4 (22 inputs, but only 4 designated optimization targets; rest are risk/ops guards — acceptable, documented) |
| R7 | Documentation | 5 | 5 |
| R8 | Edge cases | 5 | 5 |
| | **Total** | **40/40 PASS** | **39/40 PASS** |

## Final verdict: **PASS (conditional)**

Condition: user must (1) compile in MetaEditor, (2) run the backtest protocol
(spec §6) and meet the go-live gates, (3) run ≥ 4 weeks demo before real money.
Remaining known limitations:

1. No compile verification in this environment (static API cross-check only).
2. Strategy expectancy unproven — v1 is a research artifact until backtest passes.
3. Broker-specific behavior (spreads, stops level, filling) varies; defaults assume a typical gold ECN account (2-digit XAUUSD, spread ≤ 45 points, FOK/IOC filling).
