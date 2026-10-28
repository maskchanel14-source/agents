# Cycle 001 verification ledger

Checked 2026-10-28. This file distinguishes executed checks from remaining blockers.

## Product checks

- `npm test`: **11 passed**.
- `npm run build`: **passed** after switching to bundled, locally served fonts.
- `npm run test:browser`: **passed** at 320, 375, 768, and 1440 CSS pixels. Covers mocked success/failure, explicit consent payload, duplicate-submit guard, sample choices, FAQ, keyboard focus, horizontal overflow, and axe WCAG A/AA rules. A contrast defect was found and fixed before the passing run. Automated checks are not full accessibility certification.
- `npm audit`: **zero reported vulnerabilities**.
- Local preview: HTTP 200 with the Arena preview Host header after the Vite host configuration fix.
- Screenshot review: desktop and mobile layouts inspected; no claim of testing every browser/device.

## Repository gates

The sandbox initially lacked uv and Python 3.12. uv was bootstrapped and CPython 3.12.12/zlib built from source because the managed Python release asset host was outside the network allowlist. The resulting gates were actually run, not marked passed by assumption:

- `make validate STRICT=1`: **passed**, six harnesses.
- `make garden`: **passed with eight existing oversized-skill warnings**, zero errors. Those unrelated skills were not rewritten.
- `make test` under Python 3.12: **732 passed, 30 skipped, one failed**: the unchanged `ui-design/mobile-android-design` skill's static score changed bronze → silver. The source and snapshot have no local diff. We did not rewrite the snapshot to conceal this environment-dependent failure.
- The same main test suite under system Python 3.11 with locked application dependencies supplied through uv: **733 passed, 30 skipped**. This is a supplementary result, not a claim that the repository's required Python 3.12 gate passed.
- `make smoke-test`: **four passed, 13 skipped** because external CLI binaries are absent. Generation completed; no tracked generated-file changes remained.
- `studio/scripts` unit tests: **three passed**.
- `make lint`: **passed** after installing the repository’s declared optional `llm` extra. Ruff check, formatting check, and ty all passed. New studio scripts were separately formatted and linted.

## Backend checks

- Private write and aggregate snapshot RPCs: anon/authenticated EXECUTE **false**, service_role **true**.
- A transactional QA block exercised invalid email, missing consent, wrong price, valid synthetic capture, normalized-email deduplication, and the attempt limit, then deliberately raised an exception to roll everything back. The expected rollback exception was returned. A separate query confirmed **zero retained operational-test rows**.
- Public aggregate status endpoint: **verified by connector GET**, returning zero commitments, zero paid customers, zero cents, and outreach_started_at=null. It returns no prospect rows.
- Direct sandbox-to-Supabase POST: **blocked by the outbound network allowlist** (`ERR_CONNECTION_CLOSED`). This is not counted as a live form success or a production outage. Mocked browser tests and rolled-back database tests are separate evidence.
- `scopereply-three-hour-log`: database job **active**, `5 */3 * * *` UTC.
- GitHub LOG.md workflow: implemented; **schedule not active on this non-default branch**. No indefinite autonomous sales loop is claimed.

## Commercial truth

- Public Reddit posts: **0**.
- Qualified $19 commitments: **0 / 3**.
- Paying customers: **0 / 3**.
- Customer money collected: **$0.00**.
- Full generator: **not built**, pending the commitment gate.
- Checkout: **not enabled or verified**.
- Hard stop: **2026-10-30 21:05 UTC**, creation-based and conservative. Distribution has not started; this is not evidence of customer rejection.
