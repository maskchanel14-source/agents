# PO Pilot launch kit

Everything needed to sell the PO Pilot MCP kit, kept in one folder so it survives across sessions.

| Path | What it is |
|---|---|
| `site/index.html` | Landing page. Static, no build step. Lead form posts to Supabase. |
| `supabase/migrations/001_leads.sql` | `leads` table with insert-only RLS for the anon key. |
| `supabase/migrations/002_audit_requests.sql` | `audit_requests` table for the paid-audit service (insert-only for anon). |
| `assets/stocky-exit-checklist.md` | The free lead magnet (12 points). Send as-is or export to PDF. |
| `emails/sequences.md` | Four emails: checklist delivery, 2 follow-ups, agency outreach. Copy-paste ready. |
| `DISTRIBUTION.md` | Canonical URLs, per-channel tracked links, analytics, Search Console steps. |
| `LAUNCH-PLAN.md` | The 30-day plan with channel targets and the honest risk list. |
| `video/` | 24s HyperFrames promo composition (lint-clean; render it on a machine with Chrome). |

## Live

- **Landing page:** https://po-pilot-henna.vercel.app (canonical)
- **Comparison page:** https://po-pilot-henna.vercel.app/stocky-alternative/
- **Free guide:** https://po-pilot-henna.vercel.app/stocky-export-guide/
- **Paid service:** https://po-pilot-henna.vercel.app/audit/ (fixed-scope audit $250 / $450 / $750)
- **Social card:** https://po-pilot-henna.vercel.app/og.png (1200×630, wired into OG + Twitter tags)
- **Free checklist (public Google Doc):** https://docs.google.com/document/d/1SSHvIUlbnQCBS5EnOAsNIsCwR5mw6WDjuT0L5qtQJQE/edit
- **Measurement:** Vercel Web Analytics + Speed Insights on all three pages; leads land in Supabase `leads`

See `DISTRIBUTION.md` for tracked links per channel, what is measurable, and the list of things that
cannot be automated from this workspace.

Note: raw `*.vercel.app` build URLs (`po-pilot-nflb31tfs-...`) are behind Vercel Authentication because the
project uses the "all deployments except custom domains" protection setting. Always share the project domain
or the alias above, never a deployment URL.

## Infra

- **Landing page:** Vercel project `po-pilot` (`prj_FHdhrV5yQDyFPBG71siBQcMFw4Do`), root directory
  `po-pilot-launch/site`. Framework preset: Vite (needed because the Vercel API rejects file-based deploys
  for projects without a framework). Deploy by pushing to the branch, then creating a deployment from the
  commit SHA.
- **Database:** Supabase project `po-pilot-leads` (`tkoerwqgpzwxcbbqzbwg`, ap-southeast-1).
  The anon key embedded in `index.html` can only `insert` into `public.leads`; reads require the dashboard
  or the service role.
- **Checkout:** Polar (merchant of record, handles US sales tax) — $49 Solo, $249 Agency.
  Hosted cloud tier lives on MCPize.

## Reading the leads

Supabase dashboard → SQL editor:

```sql
select created_at, email, first_name, store_url, sku_range, source, referrer
from public.leads
order by created_at desc;
```

Export to CSV and work the sequence in `emails/sequences.md` from Gmail.

## Editing the page

`site/index.html` is self-contained — no framework, no build. Change the copy, commit, and the deploy
from the branch picks it up. The countdown banner computes days left from `2026-11-30` in JavaScript,
so it will read "0 days left" after the export window closes; update the copy at that point.

## What this folder deliberately does not do

- No automatic email sending. Form submissions are stored; you decide who gets an email.
- No analytics tracker beyond what Vercel provides for the project.
- No scraping and no bulk cold email. The agency template is for 1:1 outreach only — see the compliance
  notes at the bottom of `emails/sequences.md`.
