# 02: Quant analysis (stage: quant-analyst)

Version: v1. Input: `01-market-research.md`.

## 1. Candidate edges

| # | Edge | Mechanism (why gold) | Freq. | Params | Overfit risk |
|---|---|---|---|---|---|
| A | **HTF-trend pullback** (M15 entry, H1 regime) | Persistent real-yield and USD trends on gold, plus intraday liquidity pullbacks to value | 3–8 per week | about 7 core | Low–Med |
| B | London-open breakout of the Asian range | Asian range compression, then directional flow at the London open | about 1 per day | 4–5 | Med (needs precise session times and differs by broker) |
| C | Bollinger/ATR volatility squeeze breakout | Volatility clusters, so compression is followed by expansion | 1–3 per week | 4 | Med–High (many false breakouts at news) |
| D | Asian-session mean reversion | Thin Asia liquidity means ranges mean-revert | 1 per day | 4 | High (tail risk on Asian headline spikes, and rollover spreads) |
| E | Event-driven (NFP or CPI fade or follow) | Repeatable post-event patterns | about 2 per month | 3 | High (tiny sample, and the tester cannot see the calendar) |

## 2. Scoring (1–5, higher is better)

| Edge | Robustness | Cost sensitivity | MQL5 implementability | Testable in 128 MB sandbox | **Total** |
|---|---|---|---|---|---|
| A trend pullback | 4 | 4 (SL about 1–2.5 ATR, so spread is about 3% of R) | 5 | 5 (bar-level proxy works) | **18** |
| B Asian breakout | 3 | 4 | 4 | 3 (needs exact session clock) | 14 |
| C squeeze | 3 | 3 | 5 | 4 | 15 |
| D Asian MR | 2 | 2 | 4 | 3 | 11 |
| E event | 2 | 1 | 2 | 1 | 6 |

## 3. Recommendation

- **Primary (v1): A, the HTF-trend pullback.** It has the best mix of robustness and testability, and its parameter count is small and structural.
- **v2 candidate: B, the London breakout of the Asian range**, as a second, uncorrelated module that shares the same risk engine.

## 4. Risk framework

- **Fixed-fractional risk of 0.5% of equity per trade.** At a 40–45% win rate, a losing streak of 10 trades is plausible (probability about 0.3–0.6% for any given 10 trades, and much higher across a long run). Ten losses at 0.5% cost about 4.9%, which is survivable.
- **Daily loss cap of 2%** (4 R) and **at most 3 entries per day**. These stop revenge-trading cascades on trend-reversal days.
- **Equity kill switch at 15% drawdown from peak.** The EA stops opening trades until a human resets it.
- **No martingale, grid or averaging down.** Those methods trade a high win rate for ruin risk, and that conflicts with every other rule in this framework.
- Expected R distribution: losses of about −1 R, break-even exits of about +0.1 R (BE buffer), and winners of +1.5–2 R (trail or TP).

## 5. Falsification metrics (in MT5, real ticks, out of sample)

| Metric | Kill threshold | Minimum sample before judging |
|---|---|---|
| Trades | under 100 means no verdict | 100 |
| Profit factor | under 1.10 after costs | 100 trades |
| Expectancy | under +0.05 R | 100 trades |
| Max equity DD | over 12% at 0.5% risk | full OOS period |
| Spread +50% stress | PF falls below 1.0 | n/a |
| Parameter neighbourhood | over 40% of the ±1-step grid has PF < 1 (a peak rather than a plateau) | n/a |

## 6. Validation design

1. **In-sample:** 2021-01-01 to 2024-06-30 (MT5 real ticks). **Out-of-sample:** 2024-07-01 to the latest date. Do not touch OOS until the parameters are frozen.
2. **Walk-forward:** 12-month in-sample windows and 3-month out-of-sample windows, rolling. Report the distribution of OOS PF values, not only the best one.
3. **Plateau check:** run a ±1-step grid on `PullbackBars`, `TpRR`, `AdxMin` and `SlMinATR`. The defaults must sit in a broad region where PF > 1.
4. **Cost stress test:** spread ×1.5 and slippage of 30 points.
5. **Proxy (sandbox):** a bar-level port on public samples of about 8,000 bars. This tests the logic only. It is not evidence of an edge.
