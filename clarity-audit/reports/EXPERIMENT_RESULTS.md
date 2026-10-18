# Experiment Results

No live-traffic results yet (site not yet deployed to a public domain; see MORNING_REPORT). This file only records measured outcomes — never projections dressed as results.

## Baseline instrumentation (Day 0 — 2026-10-18)
- Funnel events available today: scan completed, opt-in (consented), affiliate application — via `/api/stats` aggregates and `/dashboard`.
- QA-session sanity data (sandbox only, not market signal): github.com scored 73/100 ("Nearly there"); illustrative sample coach page 56/100 ("Foggy"); unit fixtures: strong page ≥75, weak page <35.
- Verified mechanics: scan → result → share/badge/OG → opt-in → stats increment. SSRF probes (169.254.169.254, localhost) rejected. Rate-limit + consent error paths return friendly messages.

## Won
- (none yet — first real cohort decides)

## Lost / killed
- (none yet)

## Next three (once deployed)
1. E1 baseline read at 200 scans. 2. E3 share-rate read at 150 scans. 3. E5 batch-study publish + link watch.
