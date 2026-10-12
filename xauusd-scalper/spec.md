# XAUUSD Scalper — Spec (GAN-PLANNER output)

> Brief (user): "EA MQL5 XAUUSD scalping"
> Date: 2026-10-12
> Pipeline: `before-you-build` (agents) → `intent-driven-development` (affan) →
> `council` (affan) → `gan-planner` (affan) → `gan-generator` (affan) →
> `verification-loop` (affan, adapted) → `santa-method` (affan) × `comprehensive-review` (agents) ×
> `silent-failure-hunter` (affan)

## 1. Before You Build (pre-mortem)

- **Risk verdict: HIGH** — this is trading software; a defect costs real money, not just a bad product.
- **Main assumption:** EMA-cross momentum on M5 gold has positive expectancy AFTER spread + commission. Unverified until backtested.
- **Evidence to find first:** real-tick backtest with realistic spread (protocol in §6). If expectancy ≤ 0R on the test set → iterate the strategy (GAN loop), do NOT deploy.
- **Do next:** build v1 EA + backtest protocol.
- **Delay:** live/paper trading, parameter optimization, multi-timeframe variants, news integration, hedging/martingale.

## 2. Acceptance Criteria (intent-driven-development)

| # | Criterion | How verified |
|---|-----------|--------------|
| AC1 | Uses only stable MQL5 standard-library APIs (`CTrade`, iMA/iRSI/iATR, history) | Static API cross-check (no compiler available in this env) |
| AC2 | No look-ahead: signals use closed bars only (shift ≥ 1); entry evaluated once per new bar | Code review (rubric R2) |
| AC3 | Risk layer enforces: %-risk sizing w/ clamps, daily-loss halt, consecutive-loss halt, max trades/day, max spread, ATR gate, session filter, pre-send margin simulation | Code review (R3) + tester behavior |
| AC4 | Every `CTrade` call checks return value and logs retcode — no silent failures | `silent-failure-hunter` pass (R4) |
| AC5 | Performance tracked in R-multiples: win rate, expectancy (R), max consecutive losses; exposed via chart comment + `OnTester()` | Code review (R5) |
| AC6 | Defaults are conservative: 0.5%/trade, 2% daily halt, 4 consec-loss halt, 10 trades/day, max-1-position | Code review (R3) |
| AC7 | Backtest protocol documented: train/val/test split, walk-forward, every-tick real data, spread modeling, MC stress | README §backtest |

## 3. Council deliberations (4 voices, affan `council` skill)

### D1 — Entry logic: pure EMA cross vs pullback vs breakout?
- **Skeptic:** EMA cross on M5 gold is late; whipsaws in chop; RSI(7) adds little. Pullback logic adds params → overfitting risk.
- **Pragmatist:** Cross is the simplest form to backtest and explain. V1 should be simple; iterate after feedback.
- **Critic:** The real killer on gold is cost, not entry. If TP < ~1.5×SL after spread, any entry logic is negative-EV. Size SL/TP by ATR so RR scales with volatility.
- **DECISION:** EMA(9/21) cross + RSI(7) confirm, both on closed bars; SL = 1.5×ATR, TP = 2.25×ATR (1.5R). Session + spread + ATR gates.

### D2 — Default risk parameters?
- **Skeptic:** 1%/trade × 10 trades/day = 10% potential daily loss — too much for a scalp.
- **Pragmatist:** 0.5%/trade, 2% daily halt, 4-consec halt, 10/day — tight, boring, survivable.
- **Critic:** Breaker must evaluate EVERY TICK on current equity vs day-start equity (not per trade), or the halt lags by one losing trade.
- **DECISION:** 0.5%/trade, 2% daily loss halt, 4 consecutive-loss halt, max 10 entries/day, max 1 position. Breaker evaluated on every tick.

### D3 — Time exit (stale trades)?
- **Skeptic:** Forced close can realize losses a trailing stop would have avoided.
- **Pragmatist:** A scalp that hasn't moved in N bars is dead money; cap exposure.
- **Critic:** If break-even was reached, the position is risk-free — let TP/SL/trailing decide. Time-exit only for stuck, not-yet-BE trades.
- **DECISION:** Close after 12 bars (M5 = 60 min) **only if break-even has not been reached** (`!g_beDone`).

### D4 — Timeframe default?
- **Skeptic:** M1 gold scalping dies from spread.
- **DECISION:** default `PERIOD_CURRENT`, README recommends **M5**; ATR gate defaults tuned for M5 gold.

## 4. System design

**File:** `XauUsdScalper.mq5` (single self-contained EA, MQL5).

**Layers**
1. **Gate layer (every tick):** day rollover → circuit breakers → position management → new-bar check.
2. **Entry gates (new bar only):** halted? max trades? weekend? session? Friday block? spread? ATR band? indicator ready?
3. **Signal (closed bars only):** up-cross + RSI>level → BUY at ask; down-cross + RSI<level → SELL at bid.
4. **Sizing:** `lots = equity × risk% / loss-per-lot(SL distance)`; floor to lot step; clamp to [min, max∩InpMaxLot]; skip if below min lot; warn if capped (actual risk > target).
5. **Pre-send simulation** (llm-trading-agent-security): trade mode FULL, terminal+EA trade allowed, `OrderCalcMargin` ≤ 50% free margin, SL/TP respect stops level, lot within broker limits.
6. **Exits:** ATR SL/TP at entry; break-even at +1R (preserves TP); ATR trailing only after BE; time exit (12 bars) only before BE.
7. **Metrics:** R-multiple tracking per trade, win rate, expectancy (R), max consecutive losses → chart comment + `OnTester()` returns expectancy.

**Non-goals (explicit):** no martingale, no averaging down, no hedging, no multi-symbol, no news-feed/external API, no partial closes, no trailing before break-even.

**State:** `g_dayKey`, `g_dayStartEquity`, `g_dayTrades`, `g_consecLosses`, `g_haltedToday`/`g_haltReason`, `g_lastBarTime`, `g_entryTime`, `g_r0` (initial SL distance), `g_riskAmount` (currency), `g_beDone`, stats (`g_totalClosed`, `g_wins`, `g_sumWinR`, `g_sumLossR`, `g_maxConsecLoss`).

## 5. Evaluation rubric (for the ruthless evaluator)

Score 1–5 each (max total 40). PASS = every category ≥ 4 AND total ≥ 36/40.

| R# | Category | Checks |
|----|----------|--------|
| R1 | API correctness | Only stable MQL5 APIs; correct signatures; handles released; no MQL4-isms |
| R2 | No look-ahead | All signal reads at shift ≥ 1; one entry eval per new bar |
| R3 | Risk enforcement | All gates present; breaker per-tick; sizing clamped; defaults conservative |
| R4 | No silent failures | Every CTrade call checked + retcode logged; EMPTY_VALUE guards; state reset on failed send |
| R5 | Metrics | R-multiples tracked; expectancy via OnTester; comment dashboard |
| R6 | Parameter discipline | ≤ 4 recommended optimization params; rest fixed |
| R7 | Documentation | README: install, backtest protocol, params, honest disclaimers |
| R8 | Edge cases | BE modify preserves TP; time-exit state guard; multi-EA magic isolation; weekend; wrap-around session |

## 6. Backtest protocol (agents `backtesting-frameworks` skill)

1. Strategy Tester: XAUUSD, M5, **"Every tick based on real ticks"**, 2–3 years, realistic spread + commission.
2. Split: **train 60% / validation 20% / test 20%**. Optimize on train only; validate on validation; confirm on test (no peeking).
3. Walk-forward: 6-month windows, re-optimize each window on its preceding 6 months.
4. **Go-live gates (test set):** expectancy > 0; max drawdown < 10%; profit factor > 1.3; Monte Carlo (1000 shuffles of trade order): P(final equity < 90% of start) < 10%.
5. Optimize **at most 4 params** (EMA fast/slow, SL/TP ATR multipliers). Everything else stays at spec defaults.
6. Then: demo account ≥ 4 weeks before any real money. This EA is a research artifact until it passes.

## 7. Provenance (skills & agents used, by repo)

| Source | Skill / Agent | Contribution |
|--------|---------------|--------------|
| agents | `plugins/quantitative-trading/agents/quant-analyst.md` | Strategy approach: closed-bar data quality, realistic costs, risk-adjusted returns, out-of-sample discipline |
| agents | `plugins/quantitative-trading/agents/risk-manager.md` | %-risk sizing, R-multiple tracking, expectancy formula, systematic stops |
| agents | `plugins/quantitative-trading/skills/backtesting-frameworks` | §6 protocol: biases table → train/val/test, walk-forward, no overfit, cost modeling |
| agents | `plugins/quantitative-trading/skills/risk-metrics-calculation` | Multi-metric dashboard (win rate, expectancy R, max consec loss, drawdown note) |
| agents | `plugins/before-you-build` (§skill + risk-checklist) | §1 pre-mortem: verdict, main assumption, evidence-first, delay list |
| agents | `plugins/comprehensive-review` (architect-review, code-reviewer, security-auditor roles) | Reviewer lenses for santa-method round 2 |
| affan (ECC) | `skills/llm-trading-agent-security` | Circuit breakers, hard spend limits, pre-send simulation, slippage control, audit-log-every-decision |
| affan (ECC) | `skills/intent-driven-development` | §2 acceptance criteria before coding |
| affan (ECC) | `skills/council` | §3 four-voice deliberations D1–D4 |
| affan (ECC) | `agents/gan-planner`, `gan-generator`, `gan-evaluator` | Spec → build → ruthless-rubric loop (this doc = planner output) |
| affan (ECC) | `skills/santa-method` | 2 independent reviewers, both must pass, fix-and-re-review loop (REVIEW.md) |
| affan (ECC) | `skills/verification-loop` | 6-phase verification, adapted (no MQL5 compiler in env → static phases) |
| affan (ECC) | `agents/silent-failure-hunter` | Rubric R4 + dedicated review pass (REVIEW.md round 1-B) |

**Deliberately skipped:** `taste` (music-video aesthetic), `council-multi-model` (requires external model send + consent), `recursive-decision-ledger` (overkill for one file), `ship-mate`/`conductor` (role overlap with GAN harness).
