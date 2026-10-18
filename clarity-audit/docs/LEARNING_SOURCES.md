# Learning Sources — the minimum reading to run this business

Curated for the owner's profile (strong copy/static sites; new to app frameworks, payments, deliverability).

## Operating this codebase
- Next.js App Router docs — routing, metadata, route handlers: https://nextjs.org/docs/app
- `next/og` ImageResponse (powers share images): https://nextjs.org/docs/app/api-reference/functions/image-response
- Tailwind CSS v4 (CSS-first config): https://tailwindcss.com/docs
- Supabase: SQL editor + RLS concepts: https://supabase.com/docs/guides/database/overview · RLS: https://supabase.com/docs/guides/database/postgres/row-level-security

## Payments (human-owned, launch blocker)
- Lemon Squeezy (merchant-of-record, simplest taxes for digital goods): https://docs.lemonsqueezy.com
- Stripe Payment Links / Checkout: https://docs.stripe.com/payments/checkout
- Webhook signature verification (must-do before fulfilling orders): https://docs.stripe.com/webhooks/signature

## Email (opt-in only)
- Resend or Buttondown for transactional + simple sequences: https://resend.com/docs · https://docs.buttondown.com
- CAN-SPAM / GDPR basics: double opt-in where required, physical address, one-click unsubscribe (RFC 8058), SPF/DKIM/DMARC on the sending domain before ANY sequence sends.

## Security (scanner-specific)
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- Our implementation notes + residual DNS-rebinding risk: `reports/RISK_LOG.md`

## Growth craft (compliant)
- Google Search Essentials (no doorway/thin pages): https://developers.google.com/search/docs/essentials
- FTC Endorsement Guides (affiliate disclosure rules): https://www.ftc.gov/legal-library/browse/federal-register-notices/guides-concerning-use-endorsements-testimonials-advertising
- The 5-second test tradition behind the rubric (usability.gov / NN/g first-impression research).
