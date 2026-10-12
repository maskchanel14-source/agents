---
description: Run the xauusd-factory pipeline (6 stages) to produce the next XAUUSD EA version.
argument-hint: "[optional focus, e.g. 'v2: test Asian-range breakout module']"
---

Act as the `xauusd-factory` orchestrator defined in `.claude/agents/xauusd-factory.md`. Follow it exactly:
make every strategy decision yourself, delegate the six stages in order with the Agent tool
(market-researcher → quant-analyst → trading-strategist → mql5-pro → security-auditor → backtest-analyst),
enforce the release gate, and deliver `XAUUSD_AgentEA.mq5`, `README.md` and `backtest-notes.md` under
`xauusd-factory/v<N>/`.

Extra focus from the user (optional): $ARGUMENTS
