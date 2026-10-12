# 01: Market research for XAUUSD (stage: market-researcher)

Version: v1. Scope: XAUUSD on MT5 retail CFD brokers.
Every number below is tagged **measured** (computed from the proxy samples in `../tools/`), **typical** (common for retail brokers), or **assumed** (a placeholder you must verify with your broker).

## 1. Drivers and how they show up intraday

| Driver | Mechanism | Intraday footprint |
|---|---|---|
| USD (DXY) | Gold is priced in USD, so a strong USD pushes gold down | Sharp moves when US data is released (12:30–14:00 GMT) |
| US real yields | Gold pays no yield, so higher real yields raise the opportunity cost of holding it | Trends that last for days. The H1/H4 regime catches them |
| Risk-off flows | Safe-haven bid | Gaps at the weekly open, spikes on geopolitical headlines |
| Central-bank and ETF demand | Structural bid | Shows up in the multi-month trend, so it matters for the regime filter and not for entries |

The structural trend is persistent. The samples show gold at about 2,280–2,760 (Apr–Oct 2024), about 4,275–5,285 (Dec 2025–Jan 2026) and about 4,130–4,700 (Aug–Sep 2026) (**measured**). Fixed-point thresholds go stale within months, so every distance in the EA must be expressed in ATR units.

## 2. Session map (GMT)

The hourly true-range profile is shown relative to the sample mean (**measured**, `tools/proxy_backtest.py` samples):

| Sample | Quiet hours (≤ 0.7×) | Hot hours (≥ 1.3×) |
|---|---|---|
| H1 Apr–Oct 2024 (GMT+3 broker, DST) | 04, 20–23 | 12–15 (NY open 12:30 GMT in summer) |
| M15 Dec 2025–Jan 2026 (GMT+2 broker) | 04, 10–11, 21 | 01, 13–15 (NY open 14:30 GMT in winter) |
| M15 Aug–Sep 2026 (UTC timestamps) | 01, 17 | 09–12, 22 |

- **Asia (00–07 GMT)** is mostly range-bound with thin liquidity. One exception is the 01 GMT burst around the Shanghai and Tokyo open.
- **London (07–12 GMT)** sets the direction for the day, and London-open breakouts are common.
- **London–NY overlap (12–16 GMT)** has the highest range of the day. US data lands here.
- **NY afternoon (16–20 GMT)** fades. Moves often reverse into the 19:30 GMT fix or close.
- **Rollover (about 20:45–23:15 GMT)** brings wide spreads (**typical**: 2–5× the normal spread), swap is charged, and price action is erratic.

## 3. Event risk

The high-impact USD events are NFP, CPI, FOMC (statement and press conference), PCE, ISM and retail sales (**typical**).
Around them, spreads widen 3–10× for seconds to minutes, gaps through stop orders are common, and the first move often reverses.
MT5 has a built-in economic calendar (`CalendarValueHistory`). It is **not available in the Strategy Tester**, so a news filter only works live, and backtests include the news bars.

## 4. Contract and cost model (verify with your broker)

| Item | Value | Tag |
|---|---|---|
| Digits | 2 (point = 0.01) or 3 (point = 0.001) | typical. **The EA must not hard-code points** |
| Contract | 100 oz per lot | typical. The EA uses `TICK_VALUE`/`TICK_SIZE` and never assumes the contract size |
| Spread (London/NY) | 0.15–0.45 USD | typical. The proxy uses 0.30–0.45 |
| Spread (rollover/news) | 1–3+ USD | typical |
| Median spread / M15 ATR | about 0.05 | measured, with the assumed spreads |
| Stops level / freeze level | 0–50 points | assumed. Read them at runtime |
| Swap | Usually negative on both sides | typical. Holding overnight costs money |

## 5. Volatility regime notes

- The mean M15 true range is about 9–10 USD at 2026 prices, against a mean H1 true range of about 6 USD in 2024 (**measured**). Volatility has roughly doubled with the price level.
- ATR clusters. Spikes after events can run 2–3× the 100-bar average, and dead holiday sessions run about 0.5×. A volatility band filter (`ATR / avgATR`) removes both extremes.

## 6. Hard constraints for the EA

1. Express every distance in ATR multiples. Never use fixed pips or points for a core rule.
2. Take new entries only from 07:00 to 20:00 GMT. That covers London and NY and skips Asia and the rollover.
3. The server GMT offset must be an input, because `TimeGMT()` equals server time in the tester. Auto-detect it live.
4. Block entries when spread is above k × ATR, which scales with the market better than fixed points do.
5. Block entries ±30 minutes around high-impact USD events (live). State clearly that this filter does nothing in the tester.
6. No new entries on Friday afternoon, and be flat before the weekend, to avoid the weekend gap.
7. Use a time exit so an intraday idea does not turn into a swap-paying swing trade.
