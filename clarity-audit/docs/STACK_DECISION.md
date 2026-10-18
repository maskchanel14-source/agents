# Stack Decision

## Decision
**Next.js 16 (App Router) + React 19 + TypeScript (strict) + Tailwind CSS 4**, with **Supabase** as the (optional-at-launch) system of record, deploying to **Vercel** (or any Node host).

## Why not the brief's default (Astro + React islands + Cloudflare Pages)?
The repos show **no prior Astro or Next experience** — so familiarity doesn't break the tie. What breaks it:
- The product's center of gravity is *server work*: SSRF-safe URL fetching, rate limiting, dynamic OG images, SVG badges, API routes, webhooks later. Next puts pages + APIs + OG generation in one deployable with first-class Node runtime.
- One framework to learn with AI assistance beats two mental models (Astro + islands + separate functions).
- `metadata`, `sitemap.ts`, `robots.ts`, and `next/og` remove whole categories of hand-rolled SEO code the owner previously wrote manually.

## Why this stays true to owner patterns
- Design tokens in CSS variables (same approach as Nudgely), zero webfonts (system stack → fast, no FOUT), static prerendering for all marketing/content pages (Pages-like economics), dynamic only where needed (scan results, APIs).
- The app runs **fully without Supabase** (in-memory store anchored on `globalThis`) so nothing blocks launch; setting `SUPABASE_URL` + service key lights up persistence with the provided migration.

## Consequences / watch-items
- Node runtime required (scanner uses `node:dns`) → Vercel/Node host, not static Pages. Cloudflare would need Workers + a DNS-over-HTTPS resolver; documented as future work, not launch path.
- In-memory rate limits/scans reset on redeploy — acceptable pre-launch; Supabase + Upstash-style limits are the scale path.
- Next 16 Cache Components strictness (no `new Date()` in prerenders, `connection()` for request-time pages) is handled and noted in code.
