# Small Signal Studio — operating contract

## What is actually running

- **Active now:** Supabase `pg_cron` job `scopereply-three-hour-log`, schedule `5 */3 * * *` UTC. It records aggregate database checkpoints, enforces the creation-based hard stop, and removes expired interest records. It does not browse, post, sell, or edit Git files.
- **Implemented, not yet scheduled:** `.github/workflows/studio-heartbeat.yml` reads the aggregate-only status endpoint, validates the snapshot, and appends a row to `LOG.md`. GitHub only runs schedule events from the default branch. This file currently lives on `arena/1318282f-agents`; the schedule is not active until that workflow reaches the default branch. No merge to the default branch was performed.
- **Not running:** an indefinite autonomous sales agent. Agent execution is turn-based. A heartbeat can report no new evidence; it cannot invent a post, customer, or payment.

## Canonical experiment clock

Cycle 001 was created at **2026-10-28 21:05 UTC**. Its conservative database hard stop is **2026-10-30 21:05 UTC**, 48 hours after creation. This is earlier than a clock starting at first outreach and therefore does not extend the user's deadline. `outreach_started_at` remains null until a real permitted post exists. At the hard stop, fewer than three qualified commitments changes the experiment to `killed`; the reason must distinguish distribution failure from observed customer rejection.

The database is the enforcement source. This document and `LOG.md` explain it; they do not replace it. Changing the hard stop requires an explicit new experiment, not silently restarting the clock.

## Three-hour procedure

1. Read the aggregate status endpoint or query `studio.checkpoints` through the authorized connector.
2. Record Product, Who pays, Where you sold, $ collected, Skill used, and Why it lived/died. Use the actual snapshot time. Never infer revenue from interest.
3. If the experiment is killed, stop its product work. Retain the failure reason and select a different signal for the next cycle; do not add features to compensate for missing distribution.
4. If still validating, check the one selected channel's current rules and any genuine replies. Do not substitute email or another platform. A subreddit correction inside the same channel is allowed only when the original subreddit prohibits the offer (Cycle 001: r/web_design → r/sideprojects).
5. Count only distinct, explicit $19 commitments from the target buyer. Count payments only after provider verification. Operational tests and $0 downloads are excluded.
6. Update the work tracker and mirrors when there is a material change. A scheduled no-change checkpoint is not new market research.

## Connected-tool roles

- GitHub: source skills, versioned operating records, future default-branch heartbeat.
- Supabase: private interest ledger, write-only form endpoint, aggregate status, retention and hard-stop job.
- Vercel: validation-page hosting; no payment credentials.
- Linear: execution blockers and project status.
- Notion: human-readable operating log.
- Google Drive and Dropbox: private artifact mirrors, not acquisition channels.
- Gmail: internal studio correspondence only; not a second sales channel.

## Manual browser QA

`cd scope-reply && npm ci && npm run test:browser` runs mocked submissions only. A live operational test must use an `example.invalid` address, be deleted immediately, and be documented separately. Never count it as a commitment. The sandbox's outbound allowlist can block direct browser-to-Supabase POSTs even when connector GETs work; that is a test-environment limitation, not proof of a production outage.

## Skills used

Repository-local `before-you-build`, `competitive-landscape`, `api-design-principles`, `javascript-testing-patterns`, `e2e-testing-patterns`, accessibility and writing skills. The partial skill restoration and noisy router results are recorded in `PREBUILD.md`; no claim is made that every locked skill was restored.
