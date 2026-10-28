# Batch 2 targets, ready to send

Prepared 29 October 2026. Not sent yet.

Ten firms, each with a public address taken from their own site, each domain
checked for a live MX record. No address was invented. Any firm whose address
could not be confirmed from their own pages was dropped, which is what happened
to Intrepid Advisory: their site publishes a form and a postal address, no email.

Send order and timing follow `SENDING-POLICY.md`. The rolling 24 hour window from
the batch 1 sends at 19:44 UTC on 28 October means the earliest permitted send is
19:44 UTC on 29 October, which is 02:44 WIB on 30 October. Ten emails over about
forty minutes, four minutes apart, lands them in the US afternoon and the UK
evening.

---

## The angle changes by segment

Batch 1 was all bookkeepers, so the pitch was invoice matching. Half of batch 2 is
fractional CFOs, and they do not run accounts payable. Leading with a three-way
match to a CFO wastes the first sentence.

For a CFO the pain is different: reorder points were a Stocky setting, and now
they are guesswork, which means free cash sits in the wrong SKUs. The offer is the
same work described from the cash side.

---

## CFO tier, cash and margin framing

**1. TYM Consulting** (Miami and Toronto) · `info@tymconsulting.cpa`
Their ecommerce page lists inventory accounting and cash forecasting, and then
draws a scope boundary in their own words: warehouse and inventory management
operations are not included, TYM audits and advises, the client executes. That
boundary is the opening, because the rebuild is exactly the part they leave out.

Subject: `the part your scope boundary leaves out`
Hook: quote their own exclusion line back to them, then describe the deliverable
as the execution half they deliberately do not do.

**2. Ascent CFO Solutions** (Boulder, Denver) · `info@ascentcfo.com`
Retail and ecommerce fractional CFO, inventory cash flow named on the page.

Subject: `cash sitting in the wrong SKUs`
Hook: reorder points lived in Stocky until 31 August. Anything built on them now
is a guess, and the cost of the guess shows up as inventory, not as an expense.

**3. CFO Lifeline** (Miami) · `info@cfolifeline.com`
Ecommerce accounting across Shopify, WooCommerce, Amazon, Walmart and eBay, with
inventory management listed as a service.

Subject: `five channels, one reorder point that no longer exists`
Hook: multi-channel means the same SKU has different velocity per channel, and
the single Stocky rule that reconciled them is gone.

**4. Mastery CFO** (Canada) · `info@masterycfo.com`
Case study on their site describes turning a retailer around partly through
inventory management.

Subject: `what the turnaround case study skipped`
Hook: their case study credits better inventory management. Ask what the reorder
rules behind it were built on, and what happens to that model without PO history.

**5. MT Bachani CPA** (Texas) · `info@mtbcpa.us`
Ecommerce plus import and wholesale, product costing, BOM and routing, Odoo and
QuickBooks.

Subject: `product costing when the PO lines are gone`
Hook: they already do costing for importers. Importers are the ones whose landed
cost has no purchase order behind it after a Stocky shutdown.

**6. Judith Hobdell** (Canada) · `hello@judithhobdell.com`
Fractional CFO working only with ecommerce brands between $3M and $100M.

Subject: `the $3M threshold and the Stocky export window`
Hook: brands at that size usually have a buyer, not a purchasing system. Ask who
now owns the reorder calculation after 31 August.

---

## Accountant tier, invoice and costing framing

**7. Elver Ecommerce Accountants** (Wigan, UK) · `enquiries@elverconsultancy.co.uk`
Chartered accountants, Shopify, Amazon and eBay, DTC and multichannel, VAT across
borders.

Subject: `stock flow is the part your clients can't answer for`
Hook: their page names tight margins and stock flow as the pressure. Stock flow
needs lead time, and lead time came from PO history.

**8. Custom CPA** (Canada) · `info@customcpa.ca`
Contribution margin by channel and SKU, plus inventory financing and
multi-platform reconciliation.

Subject: `contribution margin by SKU needs a cost per unit`
Hook: contribution margin per SKU is only as good as the unit cost under it, and
that cost lived in a system that was switched off.

**9. James Scott (Accounting)** (Oldham, UK) · `info@jamesscott.com`
Chartered certified accountants, ecommerce sector page, A2X and inventory sync
between Amazon and Xero.

Subject: `inventory sync, when there is nothing to sync from`
Hook: syncing quantity is easy. Syncing cost and receipts is what breaks, and A2X
does not carry that leg.

**10. EcomBalance tier is already covered in batch 1.** Do not re-contact.
This slot is intentionally left empty rather than filled with a weaker firm.

---

## Before any of these go out

- Run `python3 outreach/send-budget.py check --to <address>` for each one.
- Record every send with `send-budget.py record` in the same minute it is sent.
- Watch for bounces for the first hour. Two in twenty sends triggers the stop rule.
- If TYM or Judith Hobdell replies, answer them before working the rest of the
  list. They are the two most likely to have a client ready to hand over.

## What this batch tests

Batch 1 asked whether a bookkeeper will accept a subcontractor. Batch 2 asks
whether the cash framing beats the invoice framing, across six CFOs. Whichever
tier replies first sets the shape of batch 3, which is where the volume starts.
