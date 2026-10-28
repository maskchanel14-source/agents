# PO Pilot — 30-Day Revenue Plan ($1,500)

**Owner:** Galeka / Small Signal Studio
**Start:** 29 Oct 2026 · **Deadline hook:** Stocky read-only export window closes ~30 Nov 2026
**Goal:** $1,500 in 30 days from the PO Pilot product line (Polar one-time + MCPize subscription)

This plan replaces the "post once and hope" approach. It is a number-first plan: every channel has a
target, and every day has a scoreboard.

---

## 1. The arithmetic behind $1,500

| Line | Unit price | Units needed | Revenue |
|---|---|---|---|
| Solo Kit (Polar) | $49 | 20 | $980 |
| Agency Kit (Polar) | $249 | 2 | $498 |
| Hosted Cloud (MCPize, 80% to you) | $29/mo | 3 subs × 1 month | $70 |
| **Total** | | | **~$1,548** |

So the real target is **22 paying customers**, not 31. That changes the plan: the Agency tier is
worth chasing even at low volume, because two $249 sales equal five $49 sales.

### Funnel assumption (conservative)

| Stage | Rate | Notes |
|---|---|---|
| Targeted visitor → email capture | 8–15% | landing page is checklist-first, not buy-first |
| Visitor → purchase (cold social) | 1–2% | self-serve dev tool, no sales call |
| Email → purchase within 14 days | 5–10% | only if the follow-up sequence actually sends |

Conclusion: **you need roughly 1,200–2,000 qualified visitors in 30 days**, or far fewer if the
Agency/email track lands. Organic-only traffic means the post quality matters more than volume.

---

## 2. What must be fixed in the first 48 hours (blockers, not marketing)

1. **Gumroad payouts** — two emails say "we need more information from you to process your payouts."
   Until that is completed, any Gumroad sale is stuck. Fix: `gumroad.com/settings/payments`.
2. **Polar payout reachability from Indonesia** — confirm on the Polar dashboard that a payout method
   is set and that the account is verified. A $49 sale you cannot withdraw is a vanity metric.
3. **The $0.00 test order** — leave it, but never quote "we have sales" anywhere.
4. **MCPize listing copy** — make sure the $29 and $79 tiers show the same Stocky-deadline hook as the
   landing page. Commission is 80%, so a $29 sub nets ~$23.
5. **Refund policy** — the landing page promises 14-day refund on the kit. Honor it; a chargeback on a
   new Polar account is much worse than a refund.

---

## 3. Channel plan with targets

| # | Channel | Effort | Expected units | Why it works |
|---|---|---|---|---|
| 1 | **r/shopify** value-first post (GitHub link only in body, store links in comments) | 45 min/post | 2–5 Solo | Exact audience mid-migration, high intent |
| 2 | **Shopify Community Forum** (Shopify Discussions + Retail and POS) | 30 min | 1–3 Solo | Long-tail SEO, stays indexed for months |
| 3 | **r/Bookkeeping + r/Operations** (3-way match angle) | 40 min | 1–3 Solo/Agency | Finance ops buyers have budget authority |
| 4 | **Show HN / Indie Hackers** ("I rebuilt Stocky's purchasing engine as an MCP") | 30 min | 3–10 (high variance) | Technical credibility, npm/GitHub traffic spike |
| 5 | **MCP directories** — claim Glama, submit Smithery, mcp.so, PulseMCP, awesome-mcp-servers PR | 90 min once | 2–5 | Compounding, zero marginal cost per click |
| 6 | **Direct 1:1 email to 30 Shopify agencies / 3PLs / fractional CFOs** (manual, personalized, no blasts) | 20 min/day | 1–3 Agency | Agency tier is $249 and they resell to clients |
| 7 | **npm + GitHub README banner** pointing to the landing page and $49 checkout | 20 min once | assist | Every `npx` user sees it |
| 8 | **Cross-sell to the 12-Point AI Ops Audit buyers** (Gumroad) | 30 min | 0–2 | Warm list, already paid for ops content |

Total expected: **10–31 units**. The low end is what happens if only posting happens; the high end
requires the email track and at least one post that lands.

---

## 4. The 30-day calendar

**Week 1 — credibility & plumbing (days 1–7)**
- Day 1: fix Gumroad payout + Polar payout. Claim Glama listing. Deploy the landing page.
- Day 2: update GitHub README + npm description with the landing page link and deadline banner.
- Day 3: post Shopify Community Forum (most forgiving channel, no karma requirement).
- Day 4: post r/shopify. Answer every comment within 2 hours for the first 6 hours.
- Day 5: send 10 personalized agency emails.
- Day 6: submit to Smithery, mcp.so, PulseMCP, awesome-mcp-servers.
- Day 7: review numbers, rewrite the weakest section of the landing page.

**Week 2 — second wave (days 8–14)**
- Day 8: post r/Bookkeeping (3-way match angle, no hard sell).
- Day 9: Show HN or Indie Hackers post.
- Day 10: 10 more agency emails + follow-up #1 to non-openers.
- Day 11: publish the free checklist as a public GitHub gist → link from Reddit comments.
- Day 12: post a short teardown ("what 3 years of Stocky POs taught me about MOQ rounding") on Medium/LinkedIn.
- Day 13: nudge every email lead with the worked example email.
- Day 14: mid-month review. If < 3 sales, change the offer before changing the channel.

**Week 3 — urgency (days 15–21)**
- Deadline messaging: "export window closes in ~3 weeks". Countdown is already on the page.
- Post r/shopify follow-up only if the first post did well (don't double-post the same angle).
- Email all leads: "the CSV export window is closing, here is the 20-minute version."
- Contact 10 more agencies; offer a free 30-min "PO audit" call (this is what converts to $249).

**Week 4 — close & raise (days 22–30)**
- Days 22–26: 1:1 follow-ups only. No new channels.
- Day 27: announce price move: $49 early-bird → $99 Solo after the export window closes. This is honest
  (it is in the pricing doc) and creates a real deadline.
- Day 28–30: collect two testimonials (ask buyers directly), publish them on the landing page.

---

## 5. Daily scoreboard (5 minutes/day)

| Metric | Where | Target/day |
|---|---|---|
| Landing page visits | Vercel Analytics or a simple counter | 40–70 |
| Email leads captured | Supabase `leads` table | 3–6 |
| Checkout clicks | Polar dashboard | 3–8 |
| Sales | Gmail (Polar notification) | 0–2 |
| Comments/DMs answered | Reddit/Shopify | 100% same day |

Track these in one note. If visits are fine but checkouts are near zero, the offer is wrong.
If checkouts are fine but sales are zero, the checkout page is leaking (pricing, trust, payment method).

---

## 6. Honest risks

- **Zero social proof.** No testimonials, no case study, no revenue screenshot. The landing page leans
  on verifiability (MIT code, npm provenance, live demo) instead — that is the strongest card you have,
  and it only works if you actually answer questions in public, fast.
- **The deadline is real but you are late.** The Stocky shutdown was 31 Aug; the window closes ~30 Nov.
  Interest peaked in September. You are selling into the tail, so lead with "still haven't rebuilt your
  supplier rules?" rather than "Stocky just died".
- **Reddit will punish promotion.** Link the free GitHub repo in the body, put checkout links in comments
  only when asked. One removed post can cost you the account's ability to post in r/shopify at all.
- **Payment friction for Indonesian sellers.** Polar is merchant of record, which helps with US sales tax,
  but confirm payout rails before promising anything to yourself about revenue timing.
- **Do not buy ads yet.** $49 AOV with no testimonials means paid traffic burns cash at this stage.

---

## 7. Files in this folder

| File | Purpose |
|---|---|
| `site/index.html` | The landing page (deployed on Vercel, lead form → Supabase `leads`) |
| `supabase/migrations/001_leads.sql` | Lead table + insert-only RLS for the anon key |
| `emails/` | Email templates for the checklist delivery, follow-up, and agency outreach |
| `LAUNCH-PLAN.md` | This document |
