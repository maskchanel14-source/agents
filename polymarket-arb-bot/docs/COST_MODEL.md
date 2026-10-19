# Cost model

`src/polymarket_arb/costs.py` is the single source of truth for every cost that can erase an
arbitrage edge. Strategies call into it; nothing else computes fees, gas, haircuts or margins.
All money is `decimal.Decimal`. Parameters live in `config/default.yaml` under `costs:` and
are loaded into `CostParams`. Official sources are listed in `docs/POLYMARKET_NOTES.md`.

## Output

Every candidate `Opportunity` (valid or rejected) carries a `CostBreakdown`:

| Field | Meaning |
|---|---|
| `gross_edge` | Strategy-specific gross edge in USDC (e.g. `1 - (ask_yes + ask_no)` times shares, walked on depth). |
| `taker_fees` | Sum of per-leg taker fees (runtime `feeSchedule`). |
| `gas_usd` | On-chain operation cost (merge, convert or redeem), USDC. |
| `leg_risk_expected_loss` | Expected unhedged loss if one sibling leg fails. |
| `resolution_haircut` | Resolution-risk haircut; non-zero only when holding to resolution (`redeem`). |
| `safety_margin` | Fixed 10 bps of capital, always deducted. |
| `capital_opportunity_cost` | Forgone return on idle USDC while capital is locked. |

Derived: `net_usdc = gross_edge - sum(costs)`, `net_pct = net_usdc / capital_required`,
`annualized_pct`, `confidence` (reporting only), and `valid` / `reject reasons`.
Thresholds (`min_net_profit_usdc`, `min_net_pct`, `min_annualized_pct`) are applied to these values.

## 1. Taker fees (runtime, never hardcoded)

Source: Polymarket fee docs (`docs.polymarket.com/trading/fees`). Per market, the Gamma
`feeSchedule` gives `rate` and `exponent`, plus `feesEnabled`.

    fee = shares × rate × p × (1 − p)        rounded UP to 5 dp (conservative)

- Fetched at runtime from Gamma market data and cached with TTL (`data.cache_ttl_s`, default 300 s).
- `feesEnabled` missing → `FeeUnknown` → opportunity **INVALID** (`fee_unknown`).
- `feesEnabled=false` with a non-zero rate → conflict → **INVALID**.
- `feeSchedule` missing while fees are enabled → **INVALID**.
- `exponent != 1` → `FeeModelUnverified` → **INVALID**. The docs describe only exponent 1.
- Legacy `takerBaseFee` fields are not used; they did not match `feeSchedule` when checked.
- The bot is taker-only. Makers pay no fee and are not modelled.

## 2. Gas (Polygon)

    gas_usd = units × gas_price_gwei × 1e-9 × POL_usd        rounded UP to 1e-6 USDC

- `units` per operation from `costs.gas_units` (merge 250k, split 250k, convert 500k, redeem 250k). These are conservative
  estimates. Replace them with `eth_estimateGas` in live mode.
- `gas_price_gwei` and `POL_usd` use a configured fallback (200 gwei, 1.0 USD) because no RPC is available
  in the development sandbox. The `GasEstimate.source` field records `config_fallback`. This is a documented limitation.
- `gasless_relayer: true` sets gas to zero. It is `false` by default, which is conservative. No relayer is configured.
- The sizing step reserves the largest gas cost from `max_notional_per_trade` before dividing capital per share.

## 3. Walk-the-book VWAP and depth

For a target size, the book is walked level by level (`book.walk_book`). A leg
is priced at the volume-weighted average price of the levels it consumes. Only the depth that
actually exists is used. A leg that cannot fill the requested size in full is rejected (`insufficient_depth`).
Book ordering is normalised (bids descending, asks ascending) because the docs' examples are inconsistent.

## 4. Tick and minimum size

- Every leg price must be an exact multiple of `tick_size`. An off-tick price is rejected, not rounded silently.
- Shares must be ≥ `min_order_size` (market) and ≥ `thresholds.min_shares`.
- USDC notional must also be ≥ `min_order_size` (conservative interpretation; logged in DECISIONS.md).
- Share sizes are floored to 0.01 shares.

## 5. Staleness

- Book age is `now_ms - book.timestamp_ms`. A book older than `thresholds.max_book_age_ms` (default 1500 ms) is rejected (`stale_book`).
- Two legs whose book timestamps differ by more than `max_book_skew_ms` (default 1000 ms) are rejected (`book_skew`).
- Books are invalidated on disconnect and after a top-of-book mismatch (see `data/book_store.py`).

## 6. Leg risk (FOK / FAK)

Orders are fill-or-kill style. Multi-leg arbitrage can still leave one leg unfilled.

    unwind_loss(BUY leg)  = max(0, notional − (shares × unwind_price − unwind_fee))
    unwind_loss(SELL leg) = max(0, shares × unwind_price + unwind_fee − notional)
    leg_risk_expected_loss = p_fail × Σ unwind_loss(leg)        p_fail = leg_fail_probability (default 0.05)

If no unwind price exists, the worst case for that leg is used. Leg risk is only applied to multi-leg
positions. This is pessimistic: every leg may be the one that fails.

## 7. Resolution haircut (UMA dispute and resolution)

Applies only when holding to resolution (`redeem`). Merge and sell exits carry no resolution exposure, so the haircut is zero.

    rate = base_resolution_haircut + per_day_resolution_haircut × days_to_end
           (+ ambiguous_resolution_haircut if the market is flagged ambiguous)
    resolution_haircut = payout_notional × rate + capital × p_unknown_resolution

- `base` 0.001, `per_day` 0.0002, `ambiguous` 0.01, `p_unknown_resolution` 0.005.
- The last term covers the rare 50/50 or unknown outcome. The whole capital is treated as at risk in that tail.
- Ambiguous-resolution markets are excluded from the universe by default (`data.exclude_ambiguous: true`).

## 8. Capital opportunity cost and annualised threshold

    holding_hours: merge 0.25 h, sell 0.1 h, redeem = days_to_end × 24 + uma_resolution_hours (48)
    capital_opportunity_cost = capital × opportunity_cost_annual_rate × holding_hours / 8760
    annualized_pct = net_pct × 8760 / max(holding_hours, 0.01)

- `opportunity_cost_annual_rate` defaults to 4%. This is an assumption about idle USDC, not a market quote.
- Simple (non-compounding) interest throughout.
- An opportunity is rejected if `annualized_pct < min_annualized_pct` (default 20%). This is what rejects long-dated redemptions whose capital is locked for months.

## 9. Safety margin

    safety_margin = capital × safety_margin_rate        (default 0.001 = 10 bps, always deducted)

## 10. Confidence (reporting only)

    confidence = 1 − 0.3 (ambiguous) − 0.2 (book age ≥ half of max_age) − 0.3 (incomplete group), clamped to [0, 1]

Confidence never makes a trade pass or fail. It is reported so the user can review candidates.

## 11. Blacklist

`data.blacklist_condition_ids` is a manual blacklist. Markets with unclear resolution criteria are excluded
by `exclude_ambiguous`. Blacklisted or ambiguous events are counted separately in the universe summary.

## Known gaps

- Gas units and gas price are estimates, not measurements. They must be replaced in live mode.
- Realised paper PnL excludes the safety margin and leg risk, as recorded in REPORT.md.
- Fee exponent other than 1 is unsupported and rejected, not modelled.
- Capital opportunity cost uses an assumed rate, so `annualized_pct` depends on that assumption.
