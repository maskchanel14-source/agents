# Batch 3 targets, verified and ready

Prepared 29 October 2026. Nothing sent. Every address below was read off the
firm's own site and its domain returns a live MX record.

The pool problem from batch 2 is now the binding constraint, not Gmail. Twenty
sends took a third of the ecommerce-accountant pool that actually qualifies. This
batch widens into a second segment rather than lowering the bar on the first.

---

## Segment A: inventory-specialist accountants, four

**1. Unloop** (New York and Markham, ON) · `hello@unloop.com`
The strongest single fit found so far. Their own positioning: the only accounting
firm exclusively serving ecommerce and inventory businesses in the US and Canada,
with COGS and inventory accounting as the core of the work.
Subject: `the cost history your inventory clients just lost`
Hook: they already own inventory accounting. The one input they cannot produce
from a client's current data is cost history, because it left with Stocky.

**2. Fusion CPA** (Atlanta, Puerto Rico, Park City) · `info@fusiontaxes.com`
Their ecommerce page names the exact problem in their own words: products sitting
in Amazon warehouses, in transit from suppliers, at 3PL locations and returned by
customers all need tracking. Inventory and COGS is a named service line.
Subject: `in transit from suppliers, with no PO to prove it`
Hook: quote that sentence. In-transit inventory needs purchase order lines, and
Stocky was where a lot of their clients kept them.

**3. The Ecommerce Accountants** (CPA-led, US) · `info@theecommerceaccountants.com`
CPA-led, built only for ecommerce: Amazon FBA, Shopify, dropship, agencies.
Subject: `books that close cleanly start with a cost per unit`
Hook: their pitch is clean books and tax strategy. Clean books need COGS, COGS
needs receipts, receipts came from Stocky.

**4. Irvine Bookkeeping** (Irvine, CA) · `support@irvinebookkeeping.com`
Local firm with a dedicated ecommerce service page, AP and AR included.
Subject: `your ecommerce clients' AP has nothing to match against`
Hook: they offer accounts payable. AP without purchase orders is a payment
approval, not a control.

Those four are the whole segment. MT Bachani, Elver, Custom CPA and Judith Hobdell
were already contacted in batch 2, so they do not appear here.

Three further candidates were researched and rejected:

- **Finaloop** (`hello@finaloop.com`): sells inventory accounting with FIFO COGS
  and a 3PL sync. They are the product that replaces the problem, not a buyer of
  the repair.
- **Whiz Consulting** (`info@whizconsulting.net`): overseas outsourced accounting
  at a scale where a $250 audit is below their minimum and would read as
  competition for their own delivery team.
- **E2E Accounting** (`support@e2eaccounting.com`): generic multi-industry firm,
  Shopify is one page among dental and restaurants. No specific hook available,
  and a hook is the whole method.

---

## Segment B: 3PLs, three, and an honest caveat

This segment is a test, not a conviction. A 3PL receives cartons and reconciles
them against an inbound notice, which is the same data the audit rebuilds. But
they bill per order and per pallet, so a $250 advisory is unfamiliar territory for
them. Expect a lower reply rate than the accountants, and treat any reply as
information rather than as revenue.

**1. Encore Fulfillment** (Tulsa, OK) · `info@encore3pl.com`
Their site describes receiving precisely: UPC scanning at inbound, then
reconciliation of received inventory against expected inbounds.
Subject: `receiving reconciliation, when the brand has no PO`
Hook: they reconcile against what the brand declares. After 31 August, what the
brand declares is often a guess.

**2. ShipCalm** (Los Angeles and Indianapolis) · `help@shipcalm.com`
Shopify-native 3PL, two warehouses, named account management, no lock-in minimums.
Subject: `your Shopify brands onboard with no purchasing history`
Hook: onboarding a brand means asking for SKU data and expected inbounds. The
purchasing history that would make that accurate does not exist any more.

**3. SHIPHYPE** (US and Canada, five locations) · `support@shiphype.com`
Publicly targets Shopify brands shipping 1,000+ orders a month, and publishes a
48 hour receiving SLA.
Subject: `the 48 hour receiving SLA depends on clean inbound data`
Hook: their SLA is a promise about data quality arriving with the pallet.

---

## Follow-ups already queued

Day 3 lands on 31 October and day 7 on 4 November. Both texts are in
`SENT-2026-10-29.md`. Before sending day 7 to anyone, check whether they replied.
A reply cancels the sequence for that address permanently.

## Send order

Segment A first, because the reply rate evidence so far is stronger on
accountants. If the four in segment A land before segment B is touched, that is
useful information about which segment to spend the next hundred sends on.

Rate limits unchanged: 20 per day, 3 minute gap, 15 per hour. Check the budget
before each send:

```bash
python3 outreach/send-budget.py check --to hello@unloop.com
```

## The arithmetic this pool supports

Seven verified firms in this batch, four accountants and three 3PLs. At 20 per day
that is a third of one day's budget, which is the point: the pool is the constraint
now, not the ceiling.

Realistically this market holds somewhere between 60 and 90 firms worth
contacting in English-speaking markets. At 20 a day that is four days of sending,
after which the choice is to widen geographically, lower the fit bar, or stop
prospecting and start working the replies. The third option is the one that
produces revenue, and it needs to happen before the pool is empty, not after.
