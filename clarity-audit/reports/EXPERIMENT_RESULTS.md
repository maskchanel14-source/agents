# Experiment Results

No live-traffic results yet (site not yet deployed to a public domain; see MORNING_REPORT). This file only records measured outcomes — never projections dressed as results.

## Baseline instrumentation (Day 0 — 2026-10-18, updated post-deploy)
- Funnel events: scan completed, opt-in (consented), affiliate application — `/api/stats` (Supabase-backed) + `/dashboard`.
- PRODUCTION verification: live scan of github.com = 73/100 on Vercel; result page hydrated from Supabase across deployments (durability proven); badge/OG/stats endpoints healthy.
- Data-study pilot (REAL market data): 8 public coach/course pages attempted, 6 scanned via production. Median 80.5. Failure frequencies: audience-named 100% · email-capture 83% · cta-above-fold 83% · outcome-language 67%. 2/8 sites blocked automated fetching. Method + limits on /data/coach-landing-pages-2026.
- Security: SSRF probes (169.254.169.254, localhost) rejected; rate limit + consent error paths friendly.

## Won
- (none yet — first real cohort decides)

## Lost / killed
- (none yet)

## Next three (once deployed)
1. E1 baseline read at 200 scans. 2. E3 share-rate read at 150 scans. 3. E5 batch-study publish + link watch.
