# ScopeReply — validation asset, not the MVP

Cycle 001 for Small Signal Studio. This is a price-specific interest page for a proposed $19 one-time change-record generator. **The generator does not exist yet.** Do not build it until three qualified commitments are recorded in `studio/PREBUILD.md`.

## Run

```sh
npm ci
cp .env.example .env
npm run dev -- --port 5173
npm test
npm run build
npm run test:browser
```

The browser test starts its own Vite server, uses headless Chromium, checks mobile overflow and keyboard access, runs axe, and mocks submissions. It never writes synthetic prospects to the live database. Any live persistence check must use a clearly identified operational test, be deleted immediately, and never count as a commitment. See `studio/OPERATIONS.md` for the active database job versus the not-yet-active GitHub schedule.

## Backend

Supabase project `po-pilot-leads`, private schema `studio`, tables namespaced by experiment ID. Existing PO-PILOT data is not changed. The Edge Function has JWT verification disabled because it is a public form, but only the service role may call the private write RPC. No client read policy exists. Exact allowed origins are stored in the server-side `SCOPEREPLY_ALLOWED_ORIGINS` secret. Never put a service-role key in a `VITE_*` variable.

The database enforces buyer type, email shape, explicit $19 consent, unique email per experiment, five attempts/hour per hashed request source, and an experiment hard stop. Records expire after 60 days through the three-hour checkpoint job while the database is active. Hashing uses a server secret; raw IP addresses are not stored. Honeypot and origin checks reduce casual abuse, not determined attackers. There is no CAPTCHA or verified-email step; a form submission is a stated intention, not a verified buyer or payment.

## Honest metrics

- Interest != payment. There is no checkout.
- A fictional example is not a testimonial.
- A database job logs operational checkpoints; it does not post to Reddit or manufacture sales.
- Public outreach must follow the repository's `studio/LAUNCH.md`. No acquisition clock starts until a permitted post actually exists.
- No trademark, domain ownership, or legal enforceability claims.

Skills used: brand-landingpage, accessibility-compliance, avoid-ai-writing, javascript-testing-patterns, e2e-testing-patterns, api-design-principles, stripe-integration (payment audit only; no integration claimed).

## Verification status (2026-10-28)

- `npm test`: 11 passed; `npm run build`: passed; `npm audit`: zero vulnerabilities.
- `npm run test:browser`: passed at 320, 375, 768 and 1440 CSS pixels; axe WCAG A/AA checks reported zero violations. This is automated coverage, not a claim of full accessibility certification. All form requests in this suite are mocked.
- Database QA: invalid email, missing consent, wrong price, valid capture, normalized-email deduplication and rate limiting were exercised inside a rolled-back transaction. A follow-up query confirmed zero retained test prospects.
- Public aggregate status: verified through the Supabase connector. Direct sandbox-to-Supabase POST was blocked by the outbound network allowlist; it is not counted as a successful live submission test.
- GitHub heartbeat: implemented and unit-tested, but its schedule is inactive until the workflow reaches the default branch. The separate database checkpoint job is active.
