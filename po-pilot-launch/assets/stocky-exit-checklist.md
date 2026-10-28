# The 12-Point Stocky Exit Checklist

*What to export, in what order, before Shopify's read-only window closes (~30 Nov 2026).*

You have a few weeks of export access left. After that, whatever is not in a CSV is gone — and the
thing most merchants forget is that **Stocky never had a "download suppliers" button**. Vendor lead
times, carton multiples and MOQs only exist inside historical purchase orders.

Do these in order. Total time: about 20 minutes for a normal store.

---

## Step 1 — Export the four files that actually matter

| # | Report | Where | Why |
|---|---|---|---|
| 1 | **Purchase orders** (full history) | Stocky → Purchase Orders → Export | The only source of vendor lead times and carton multiples |
| 2 | **Products / inventory** | Shopify Admin → Products → Export (all) | SKU, cost, barcode, current on-hand |
| 3 | **Sales by SKU, last 90–180 days** | Shopify Analytics → Reports → Sales by product variant | Daily velocity and ABC tiers |
| 4 | **Suppliers list** (screenshot or manual sheet) | Stocky → Suppliers | Name, email, currency, payment terms |

Name them `po_history.csv`, `products.csv`, `sales_by_sku.csv`, `suppliers.csv`. Do not rename the
columns yet — every parser in the world expects the original headers.

## Step 2 — Rebuild lead time from timestamps (nobody wrote it down)

For each vendor, take every historical PO and compute `received_date − created_date`. You want:

- **mean lead time** (use this for reorder points),
- **standard deviation** (this is your safety stock buffer),
- **max observed lead time** (this is what you plan the worst case around).

If a vendor has fewer than 3 historical POs, mark the lead time as "assumed" and revisit it after two
cycles. Do not silently average a single data point.

## Step 3 — Infer carton multiples from order quantities

Look at the quantities you ordered per SKU per PO. If every order is a multiple of 12 or 24, that is the
case pack. Round your future order quantities **up** to that multiple — ordering 47 units when the pack is
12 means you will be short, not clever.

## Step 4 — Capture MOQ twice: units and dollars

Vendors enforce two different minimums and merchants routinely satisfy one and forget the other:

- **MOQ units** — minimum pieces per SKU or per order,
- **Minimum order value** — often tied to free freight (e.g. "$500 for free shipping").

Write both down per vendor. The top-up rule that saves the most money is: if a PO is short of the free-freight
threshold by less than the freight cost, add A-tier fast movers to close the gap.

## Step 5 — Build the 12-column supplier sheet

This is the schema that replaces what Stocky stored:

```
vendor | vendor_email | currency | lead_time_days | lead_time_stdev_days
case_pack | moq_units | moq_dollars | free_freight_dollars
payment_terms | incoterm | sku_list
```

Fill it once. It is the single most valuable artifact in this whole exercise — more valuable than the app.

## Step 6 — Fix velocity for stockout days

Daily velocity computed as `units sold ÷ days` is wrong for any SKU that was out of stock, because the
sold-out days drag the average down and you end up under-ordering your best seller.

Correct formula: `units sold ÷ (days − stockout_days)`.

## Step 7 — Set safety stock by service level, not by vibes

`Safety stock = Z × σ_demand × √(lead time)`. For a 95% service level use Z = 1.65; for 98%, Z = 2.05.
Then `reorder point = (daily velocity × lead time) + safety stock`.

## Step 8 — Classify SKUs A/B/C by revenue

A-tier (top 80% of revenue): never stock out, top up POs to protect them.
B-tier: normal rules. C-tier: order only to fill a carton, never to fill a pallet.

## Step 9 — Generate a Draft PO and compare it to your own

Before you trust any tool (mine included), take one vendor and build the PO by hand. Then compare.
The differences will tell you exactly which rule was living only in your buyer's head.

## Step 10 — Put a receiving log in place now

3-way matching needs three documents: PO, dock receiving count, supplier invoice. You already have the
PO and the invoice. The receiving count is the one nobody keeps — a shared sheet with
`po_number | sku | qty_received | date | damaged` is enough to start.

## Step 11 — Audit one past invoice against its PO

Pick the largest invoice from the last 90 days and check three things: unit cost vs PO, quantity received
vs invoiced, freight vs agreed. Do this once and you will understand why AP teams care about this workflow.

## Step 12 — Keep the files offline, and back them up twice

Store the exports outside Shopify (local drive + one cloud copy). The read-only window closes; your
Google Drive does not.

---

## Want this automated?

The free engine is MIT-licensed: `npx -y po-pilot-mcp@1.0.0` (runs locally, demo mode included).
The paid kit adds unlimited SKUs, the 3 n8n workflows, and the exact CSV import recipes for Shopify
Admin, QuickBooks Online and Xero.

*Small Signal Studio — not affiliated with Shopify.*
