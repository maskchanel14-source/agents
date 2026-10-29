# Harvey, vendored

Source: `github.com/ethanplusai/harvey` at commit `4237f07`, v0.3.0, MIT licence.
Cloned and inspected 29 October 2026. 3,204 stars. Autonomous cold-email agent.

## What is here

| Path | What it is |
| --- | --- |
| `skills/` | All 10 sales knowledge files, verbatim. Plain Markdown, edited to change behaviour. |
| `prompts/` | `writer.md`, `scout.md`, `handler.md`, `system.md`, verbatim. |
| `harvey/gate.py` | The deterministic pre-send gate, unmodified. This is the part actually executed. |
| `HARVEY-README.md` | Upstream README, kept for the deliverability and compliance sections. |
| `LICENSE` | MIT, upstream. |

## What was left out, and why

- `harvey/` modules other than `gate.py` (18 MB is mostly docs screenshots). The
  collection pipeline, dashboard, and brain all need a `claude` or `codex` CLI,
  Playwright, and mailbox OAuth. None of that exists in this sandbox, so vendoring
  the code would only create files that cannot run.
- `tests/` (1.3 MB), `docs/` (7.3 MB of images).

## What is used, and how

`po-pilot-launch/outreach/pre_send_gate.py` imports `harvey.gate.pre_send_check`
directly and wraps it with the rules from `prompts/writer.md` that the gate does
not itself enforce (em dashes, vague CTAs, opening with I/We, question count,
the 75-word target). Every draft passes through it before a send.

Full writeup of what changed as a result: `po-pilot-launch/outreach/HARVEY-AUDIT.md`.

## Updating

```bash
git clone --depth 1 https://github.com/ethanplusai/harvey.git /tmp/harvey
cp -r /tmp/harvey/skills /tmp/harvey/prompts vendor/harvey/
cp /tmp/harvey/harvey/gate.py vendor/harvey/harvey/
```

Then re-run the audit, because the gate's rules may have changed.
