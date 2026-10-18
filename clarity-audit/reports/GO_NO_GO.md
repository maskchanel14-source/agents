# Go / No-Go — launch gates

## Current verdict: **LIVE (free scanner) · NO-GO for taking money** until payment + legal gates clear. (Updated 2026-10-18 post-deploy.)

### Free-scanner soft launch — GO when:
- [x] Scanner works end-to-end (verified live: real URL → score → result → OG/badge/share)
- [x] SSRF guards + rate limiting verified (metadata IP + localhost rejected)
- [x] Unit tests pass (scoring, weight sum = 100, SSRF) · typecheck · lint (0 errors) · production build green (43 routes)
- [x] Methodology, sample report, privacy/terms/refund/support pages live
- [x] Deployed to human-owned Vercel project — https://clarity-audit-five.vercel.app (`NEXT_PUBLIC_SITE_URL` set; custom domain optional)
- [x] Supabase connected (project yckbkpaqlwcfblgiqmno; migration applied; persistence verified in production)
- [x] Real support inbox set (owner's Gmail; swap to custom-domain support@ when ready)
- [ ] Lighthouse + axe pass on production URL (targets: Perf/SEO/A11y ≥95 marketing pages; fix regressions before promotion)

### Taking money — NO-GO until ALL clear:
- [ ] Human connects payment account (Lemon Squeezy recommended as MoR, or Stripe) — checkout links wired, `SITE.paymentsConnected = true`
- [ ] Webhook endpoint w/ signature verification + idempotent order fulfillment (schema ready)
- [ ] Report delivery email verified end-to-end with a provider test order
- [ ] Legal review of privacy/terms/refund drafts (human/lawyer)
- [ ] Email auth (SPF/DKIM/DMARC) on sending subdomain; sequences loaded in provider
- [ ] Refund path rehearsed (who clicks what, SLA) — final decisions stay human

### Promotion — NO-GO until:
- [ ] Human approves each community/partnership draft in `growth/` (no auto-posting, ever)
- [ ] First data-study batch run + methodology date-stamped (aggregate-only publishing)
