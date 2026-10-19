# polymarket-arb-bot

Polymarket arbitrage detector and (paper) executor, Python 3.11+ asyncio. Every cost that can erase an
edge is modelled in one place (`costs.py`). **Paper is the default mode. Live trading is locked and was not
enabled, tested against real funds, or used in any way.**

> Status: research and paper build. Not validated against live markets from this environment.
> See `REPORT.md` for evidence, limitations, and the pre-live checklist.

## What it does

| Strategy | Status | Notes |
|---|---|---|
| **A** intra-market binary, buy YES + NO on asks, merge | Implemented (backtest + paper) | Asks only. Exit is merge (no resolution risk). |
| **B1** neg-risk buy-all YES, redeem at resolution | Implemented (backtest + paper) | Exhaustive groups only; resolution haircut and UMA lock-up. |
| **B2** neg-risk convert (buy NO_j, convert, sell YES_i, i≠j) | Implemented (backtest + paper) | Mechanics from the official neg-risk docs. |
| **C** cross-market logical | Disabled, not implemented | Precision cannot be guaranteed. See DECISIONS.md #25. |
| **D** cross-venue | Disabled, default off | Needs identical resolution criteria and another venue's rules. |

Every strategy exposes `scan() -> list[Opportunity]`. Each opportunity records gross edge, each cost component,
net USDC and %, optimal size, capital required, annualised return, confidence, and a valid or rejected reason.

## Layout

```
src/polymarket_arb/
  costs.py          single source of truth for fees, gas, haircuts, margins, leg risk
  book.py           walk-the-book VWAP, tick and min-size checks
  domain.py         dataclasses (Opportunity, Leg, CostBreakdown, MarketInfo, ...)
  money.py          Decimal helpers and rounding (no float money)
  markets.py        Gamma market parsing (feeSchedule, neg-risk, resolution flags)
  universe.py       market selection, blacklist, ambiguity exclusion, liquidity cap
  strategies/       A (intra_binary), B (neg_risk), C/D (disabled)
  risk/             limits, exposure caps, daily-loss halt, rate limit, circuit breaker, kill switch
  data/             HTTP (throttled, retried), Gamma, CLOB REST, WebSocket book store, recorder
  execution/        paper executor (FOK-style, overlay), live executor (gated), L2 auth helpers
  state/            SQLite store, reconciliation
  monitoring/       JSON logs, counters
  engine.py         scan -> record -> risk -> execute, halts, reconciliation
  runner.py         record, replay, paper, live entry points
  cli.py            polymarket-arb {record,replay,paper,live,kill,report}
config/default.yaml all tunables (thresholds, risk, costs, data)
tests/              unit, property/fuzz, WS reconnect, replay determinism, IO paths
docs/               COST_MODEL.md, POLYMARKET_NOTES.md
```

## Setup

The project uses a local `.venv` with pinned dependencies (see DECISIONS.md #2 on `uv`).

```bash
cd polymarket-arb-bot
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest --cov          # full suite + coverage
.venv/bin/ruff check src tests && .venv/bin/ruff format --check src tests
.venv/bin/ty check src
```

No secrets are needed for `record`, `replay`, or `paper`. Copy `.env.example` to `.env` only if you need the
live-mode variables. `.env` is gitignored and must never be committed.

## Modes

```bash
.venv/bin/python -m polymarket_arb replay --input tests/fixtures/recordings/synthetic_replay.jsonl \
    --db /tmp/rp.sqlite --report reports/replay.json      # deterministic, offline
.venv/bin/python -m polymarket_arb paper --seconds 1800 --db state/bot.sqlite --report reports/paper.json
.venv/bin/python -m polymarket_arb record --seconds 600 --out data/recordings/session.jsonl
.venv/bin/python -m polymarket_arb kill {on|off|status}
.venv/bin/python -m polymarket_arb report --db state/bot.sqlite
```

- **backtest / replay**: runs the engine over a recorded feed on a virtual clock. Deterministic, test-verified.
- **paper** (default): live public market data, simulated fills. No order is ever sent.
- **live**: refused unless **both** `LIVE_TRADING=true` in the environment **and** the local file
  `config/LIVE_CONFIRMED.txt` exist. Even then no signer or order transport ships, so it raises `LiveNotArmed`.

Note: `paper` connects to Polymarket's public endpoints. The development sandbox could not run a live session
(see REPORT.md), so no live paper log is included.

## Risk controls

- Max trade notional, and exposure caps per market, per event, and in total.
- Daily-loss auto-halt until the next UTC day.
- Order rate limit and a circuit breaker after consecutive errors (with cooldown).
- Kill switch: a file (`state/KILL_SWITCH`) or the `kill on` command. It triggers cancel-all and halts scanning.
- Idempotent orders (client IDs are unique; duplicates are refused).
- Partial fill engages the kill switch. Periodic reconciliation mismatch engages the kill switch.
- Stale or skewed books, unknown fees, and off-tick prices reject candidates before they reach risk.

## Documentation

- `docs/COST_MODEL.md` — every cost component, formulas, defaults, and sources.
- `docs/POLYMARKET_NOTES.md` — API and market facts, with official source URLs.
- `DECISIONS.md` — ambiguities, judgement calls, and deviations from the brief.
- `REPORT.md` — evidence, key numbers, limitations, and the pre-live checklist.

## Not included

- Any live order placement, transaction signing, or wallet handling.
- Geo-restriction workarounds. Polymarket and Indonesian rules affect live use (see REPORT.md).
