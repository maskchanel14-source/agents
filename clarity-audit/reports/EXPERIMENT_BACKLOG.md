# Experiment Backlog

Format per experiment: hypothesis · channel · metric · min sample · scale/kill thresholds · next action.
Rule: one primary experiment at a time pre-launch-traffic; never change price and promise simultaneously.

## E1 — Quick-win-first result layout
- Hypothesis: Leading the result with "Your quick win" increases email opt-in ≥15% vs score-only.
- Channel: on-site (result page) · Metric: opt-ins / completed scan · Min sample: 200 scans
- Scale: opt-in +15% with no drop in share rate · Kill: no lift at 200 scans → test score + top-issue-first variant.
- Status: SHIPPED as default (baseline being measured).

## E2 — $9 tripwire "ExpressFix"
- Hypothesis: A $9 one-fix deep-dive increases total paid orders enough to offset AOV dilution.
- Channel: pricing/result upgrade · Metric: revenue per 100 scans, refund rate · Min sample: 100 upgrade views
- Scale: revenue/100 scans up, refunds <5% · Kill: revenue flat/down or support load up.
- Status: QUEUED — needs payments live (human). Do not run until E4 baseline exists.

## E3 — Share text with top issue
- Hypothesis: Including the top issue in prewritten share text increases shares/scan ≥20%.
- Channel: viral loop · Metric: share clicks + referred scans (?ref) · Min sample: 150 scans
- Scale: shares/scan +20% · Kill: no lift → try before/after improvement framing.
- Status: SHIPPED (ShareBar includes top issue); measuring.

## E4 — Full Audit $39 vs $29 anchor
- Hypothesis: $29 → more orders but lower AOV; $39 with bundle anchor wins on revenue/scan.
- Metric: revenue per 100 result views · Min sample: 300 result views per arm (sequential, dated cohorts)
- Status: QUEUED post-payments. Human approves any >20% price move.

## E5 — Data-study backlink engine
- Hypothesis: The open-methods coach-page study earns ≥5 referring domains in 60 days.
- Channel: SEO/PR · Metric: referring domains, study→scan conversions · Kill: 0 links after batch publish + 10 compliant mentions → pivot study format to embeddable chart widget.
- Status: RUNNING (live-finding chart live; batch protocol documented; runner script ready).

## E6 — Niche page vs generic landing (ads-free test via community drafts)
- Hypothesis: /niche/coaches converts referred coaches to scans ≥25% better than homepage.
- Metric: scan-start rate per landing · Min sample: 100 visits each
- Status: QUEUED — needs first approved community posts.

## E7 — Challenge email → rescan loop
- Hypothesis: Day-5 rescan reminder produces ≥30% rescans among challenge opt-ins, rescans share 2× more.
- Metric: rescan rate, shares per rescan · Status: QUEUED — needs email provider (human connects).

## E8 — Badge embed loop
- Hypothesis: ≥3% of scanned users embed the badge; each embed yields ≥2 scans/month.
- Metric: badge copies, badge-origin scans · Status: SHIPPED (badge + widget docs live).
