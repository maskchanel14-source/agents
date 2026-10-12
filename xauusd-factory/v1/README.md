# XAUUSD_AgentEA v1: Gold Session Trend-Pullback

The `xauusd-factory` orchestrator (`.claude/agents/xauusd-factory.md`) generated this MetaTrader 5 Expert Advisor for **XAUUSD**, using a 6-stage agent pipeline:
market-researcher → quant-analyst → trading-strategist → mql5-pro → security-auditor → backtest-analyst.

> ⚠️ **Risk disclaimer.** This is research software. It has **not** been compiled in this sandbox, it has **not** been validated on MT5 real-tick data, and it has **not been verified on a live account**. Leveraged gold CFDs can lose money quickly. Test on a demo account first. Nothing in this repository is financial advice.

## What it does

| Layer | Rule (detail in `pipeline/03-strategy-spec.md`) |
|---|---|
| Regime (H1) | `Close > EMA50 > EMA200`, EMA50 rising over 3 bars, ADX(14) ≥ 20. Shorts use the mirror image |
| Setup (M15) | Within the last 6 closed bars, price pulled back into the EMA20 zone (± 0.25 ATR) |
| Trigger | The bar closes back beyond EMA20 **and** beyond the prior bar's high (or low), with RSI on the right side of 50, and no more than 1 ATR from EMA20 |
| Filters | Entries only 07–20 GMT · spread ≤ 0.15 ATR · ATR/avgATR(100) between 0.6 and 2.5 · no entries ±30 minutes around high-impact USD news (live) · Friday cut-off |
| Exits | SL behind the pullback swing (+0.25 ATR buffer), clamped to 1.0–2.5 ATR · TP 2R · break-even at +1R · 1-ATR trail from +1.5R · time exit after 48 bars · flat on Friday 20 GMT |
| Risk | 0.5% of equity per trade (lot rounded **down**, and the trade is **skipped** if that is below the minimum lot) · 3 trades per day at most · daily loss cap 2% · equity kill switch at 15% drawdown from peak |
| Safety | No DLL, `#import`, WebRequest or file I/O · one position per magic number · no martingale, grid or averaging · restart-safe state |

## Files

| File | Purpose |
|---|---|
| `XAUUSD_AgentEA.mq5` | The EA, as a single file. It depends only on the standard `Trade\Trade.mqh` |
| `backtest-notes.md` | What has been measured so far (bar-level proxy), the caveats, and the exact MT5 tester plan |
| `pipeline/01…05-*.md` | The stage artefacts: research, quant analysis, the strategy spec with the Decision Record, build notes, and the security audit |
| `tools/proxy_backtest.py` | A stdlib-only bar-level proxy backtest. It fetches about 400 KB of public samples into `/tmp` on demand |
| `tools/proxy_results.json` | The output of the last proxy run |

## Install

1. Copy `XAUUSD_AgentEA.mq5` to `MQL5/Experts/` (in MT5: File → Open Data Folder).
2. Open it in MetaEditor and press **F7** to compile. You should get 0 errors. If you don't, paste the compiler log into the next factory run.
3. Attach it to an **XAUUSD M15** chart. The EA refuses to start on any symbol that does not contain XAU or GOLD.
4. Turn on **Algo Trading**. For the news filter to work, the terminal must be able to load the economic calendar (it is on by default).

## Key inputs

| Group | Input | Default | Notes |
|---|---|---|---|
| Session | `InpAutoGMTOffset` / `InpServerGMTOffset` | true / 2 | The offset is auto-detected live. **In the tester you must set it by hand** (usually 2 in winter and 3 in summer for EET brokers) |
| Risk | `InpRiskPercent` | 0.5 | Values from 0.1 to 1.0 are sensible. Validation rejects anything above 3 |
| Risk | `InpMaxLots` | 5.0 | A hard cap regardless of equity |
| Risk | `InpDailyLossPct` / `InpMaxTradesPerDay` | 2.0 / 3 | Daily circuit breakers, derived from the deal history |
| Risk | `InpKillSwitchDDPct` / `InpResetKillSwitch` | 15 / false | Once tripped, the switch stays tripped until you reset it, even after a restart |
| Exits | `InpTpRR`, `InpBeTriggerR`, `InpTrailStartR` | 2.0, 1.0, 1.5 | Set `InpTpRR = 0` to let the trail manage the exit |
| Execution | `InpMagic` | 26101201 | Use a different value for each chart or instance |
| Cost | `InpMaxSpreadATR`, `InpMaxSpreadPoints` | 0.15, 0 | The spread cap scales with ATR. The cap in points is optional |

## Strategy Tester quick start

Model **"Every tick based on real ticks"**, XAUUSD M15, 2021-01-01 → 2024-06-30 for in-sample, then a single out-of-sample run over 2024-07-01 → latest.
For optimisation, choose **Custom max**. This uses `OnTester()`, which rewards PF × √trades × recovery factor with a penalty for drawdown.
The full plan and the pass/fail thresholds are in `backtest-notes.md` §4.

## Known limitations (v1)

- **The news filter does not work in the Strategy Tester** (an MT5 calendar limitation), so backtests include news spikes.
- In the tester, the session filter relies on `InpServerGMTOffset`. It does not adjust for DST by itself, so sessions shift by 1 hour across DST changes.
- The proxy evidence is only 71 trades with an expectancy of about +0.01 R, which is **inconclusive**.
- "Today", for the daily caps, means the server day. Deposits and withdrawals shift the base for the daily loss cap and can trip the kill switch (in the safe direction).
- If you run several instances with the same magic number, they share state. Don't.

## Next version (v2)

The candidates (see `backtest-notes.md` §5) are: ADX threshold 25 (validated only out of sample), a second module that trades the London breakout of the Asian range, and a check on the short side.
Run `/xauusd-factory` in Claude Code, or start a session with `claude --agent xauusd-factory`, after adding your MT5 report to `xauusd-factory/v1/`.

## Ringkasan (ID)

v1 adalah EA *trend-pullback* untuk emas. Arah tren dibaca di H1 (EMA50/200 + ADX), entry di M15 saat harga pullback ke EMA20 lalu momentum lanjut, dan trading hanya jalan di sesi London–NY. Lot dihitung dari risiko 0,5% per trade, dengan batas loss harian 2% dan kill switch di drawdown 15%.
Hasil proxy backtest (71 trade) **belum membuktikan apa-apa**: kira-kira impas. Langkah berikutnya: compile dengan F7, lalu jalankan uji *real ticks* di MT5 sesuai `backtest-notes.md`. Jangan dipakai di akun live sebelum lolos semua kriteria di sana.
