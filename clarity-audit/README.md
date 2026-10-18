# Clarity Audit — Instant Website Clarity Audit

**Paste a public landing page URL → get a free, evidence-based clarity score (25 checks / 100 points), your top issues with fixes, and an optional paid deep-dive.** Built for coaches, course creators, consultants, and small service businesses. Aggressive growth, zero dark patterns: public rubric, no fake proof, no email wall on the free score.

## What's inside
- **Free scanner** (`/`, `/api/scan`) — SSRF-hardened fetcher (private/metadata IP blocking, redirect re-validation, 10s/1.5MB caps) + deterministic rubric engine (`src/lib/scanner.ts`)
- **Result pages** (`/scan/[id]`) — score ring, quick win, top issues, full evidence table, share links, dynamic OG images (`/api/og/[id]`), embeddable SVG badge (`/api/badge/[id].svg`)
- **Conversion paths** — pricing ($19/$39/$79/$49 + bundles) with honest pre-launch waitlist mode, full sample report, methodology, opt-in captures (consent-gated), 5-Day Clarity Challenge, affiliate applications
- **Traffic assets** — 10 resource guides, 3 niche pages, 2 micro-tools (headline/CTA checkers), live data-study page, widget docs, sitemap/robots/JSON-LD
- **Ops** — operator dashboard (`/dashboard`, `/api/stats`), Supabase schema (`supabase/migrations/`), batch study runner (`scripts/`), open-source core (`open-source/clarity-score`, MIT)
- **War-room files** — `docs/` (skill graph, stack decision), `reports/` (morning report, experiments, risk log, go/no-go), `growth/` (keywords, email sequences, community/partnership/newsletter drafts, marketplace kit, cold-outreach HUMAN-APPROVAL pack)

## Run locally
```bash
npm install
npm run dev          # http://localhost:3000
npm run test         # scanner + SSRF unit tests
npm run typecheck && npm run lint && npm run build   # pre-push gate
```

## Deploy (human steps, ~30 min)
1. **Vercel:** import this repo/subdirectory → framework Next.js → set `NEXT_PUBLIC_SITE_URL=https://your-domain`.
2. **Supabase:** create project → run `supabase/migrations/0001_init.sql` → set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` env vars (server-only). App works without it; with it, leads/scans persist.
3. **Support inbox:** replace `support@example.com` in `src/lib/site.ts`.
4. **Payments (when ready):** connect Lemon Squeezy/Stripe, wire checkout links, add signed webhook → flip `SITE.paymentsConnected`. See `reports/GO_NO_GO.md` — do not skip gates.
5. **Email:** connect provider (SPF/DKIM/DMARC first), load `growth/email-sequences/SEQUENCES.md`.

## Guardrails encoded in the product
No fake testimonials/counts/scarcity · averages hidden until n≥10 real scans · result pages noindex · aggregates are counts-only · scanner never logs in/submits forms · outreach assets are drafts requiring human approval · final refund/chargeback/legal decisions stay human.
