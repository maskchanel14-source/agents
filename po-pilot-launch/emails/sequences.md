# Email sequence (copy ready)

> **Kirim atas nama Small Signal Studio.** Sejak 29 Oktober 2026 semua email keluar
> dengan display name `Small Signal Studio` (lewat parameter `from_address`, sudah
> diuji) dan tanda tangan di bawah. Batas kirim harian, aturan stop, dan larangan
> duplikat domain ada di [`../outreach/SENDING-POLICY.md`](../outreach/SENDING-POLICY.md).
> Teks di bawah masih memakai tanda tangan lama; ganti saat menyalin.


All four emails are written for you to paste into Gmail — nothing is sent automatically.
Send from `smallsignalstudiolife@gmail.com` (the verified address on the account).

Read the compliance note at the bottom before sending the agency outreach.

---

## 1. `01-checklist-delivery.md` — send within 5 minutes of a form submission

**Subject:** Your Stocky exit checklist (+ the 4 exports to pull first)

Hey {first_name | there},

Here's the checklist: {LINK_TO_CHECKLIST}

The short version, if you only do three things this week:

1. Export **purchase order history** from Stocky. It is the only place your vendor lead times and carton
   multiples exist, and the read-only window closes around the end of November.
2. Grab **sales by SKU for the last 90–180 days** so velocity has something to calculate from.
3. Write down **MOQ units AND minimum order dollars** per vendor. Most stores track one and forget the other.

The checklist walks through all 12 points, including the formula for stockout-corrected velocity and the
12-column supplier sheet that replaces what Stocky stored.

If you want it automated instead of done in a spreadsheet: the free tool is
`npx -y po-pilot-mcp@1.0.0` (MIT, demo mode, read the code first — genuinely).
The $49 kit adds unlimited SKUs plus 3 pre-built n8n workflows: {LANDING_PAGE_URL}

Either way, get the exports before the window closes.

Small Signal Studio
Purchasing data for Shopify brands
https://po-pilot-henna.vercel.app/audit/

---

## 2. `02-followup-day3.md` — day 3, only to people who opened #1

**Subject:** Re: Your Stocky exit checklist — the MOQ trap

Quick follow-up with the part people get wrong.

Vendors enforce two minimums, not one:

- **MOQ units** — minimum pieces per SKU or per order
- **Minimum order value** — usually tied to free freight, e.g. $500

A store satisfies the unit MOQ, ships a $420 order, pays $60 freight, and thinks it saved money. The fix
is to top up with A-tier fast movers until the order clears the free-freight line — same cash out, no
freight, more cover on your best sellers.

Worked example from the checklist: 18 SKUs across a 12-pack vendor, rounded to 3 cartons, plus a 4-unit
top-up to clear the vendor minimum. That's the whole trick.

{LANDING_PAGE_URL}

Small Signal Studio
Purchasing data for Shopify brands
https://po-pilot-henna.vercel.app/audit/

---

## 3. `03-followup-day7-deadline.md` — day 7, to everyone who has not bought

**Subject:** ~3 weeks of export access left

No pitch, just the timing.

The Stocky read-only CSV window closes around the end of November. After that:

- vendor lead times can no longer be reconstructed from order history,
- carton multiples have to be guessed,
- and running POs the Monday way means rebuilding all of it by hand from invoices.

If the checklist is still sitting in your inbox, block 20 minutes this week and pull the four exports.
That part is free and it's the part that actually expires.

If you'd rather not build the sheet: the $49 kit gives you the deterministic version of all four tools
plus the n8n automations, and the MIT core is free to test first.

{CHECKLIST_LINK} · {LANDING_PAGE_URL}

Small Signal Studio
Purchasing data for Shopify brands
https://po-pilot-henna.vercel.app/audit/

---

## 4. `04-agency-outreach.md` — 1:1 only, never a blast

Send one at a time, always after reading something real about the agency (a case study, a client niche,
a recent post). Ten per day maximum. If you cannot name something specific about them, skip them.

**Subject:** For {agency} clients still running POs in spreadsheets post-Stocky

Hi {first_name},

I saw {specific thing — e.g. "your case study on the outdoor gear brand doing 4,000 orders/month"}.

Since Stocky went read-only on Aug 31, the purchasing side of Shopify has been the messy part for stores
in that range: native POs store drafts but don't compute reorder points, don't round to carton multiples,
and don't audit supplier invoices.

I built a small MCP server for it (MIT core, `po-pilot-mcp`): it reconstructs vendor lead times from
exported Stocky POs, generates Shopify Draft PO CSVs, and runs a 3-way match that outputs verified-only
QuickBooks/Xero bill CSVs.

The Agency licence is $249 one-time for up to 10 client stores with commercial use rights — priced so an
agency can use it on two clients and still be ahead of a $99/month app.

If it's useful, I can run one of your client's PO exports through it and send you the before/after for free.
No obligation; a worked example on real data is better than my marketing page.

{AGENCY_CHECKOUT_URL}

Small Signal Studio
Purchasing data for Shopify brands
https://po-pilot-henna.vercel.app/audit/

---

## Compliance & deliverability notes

- **Do not use these as a cold blast.** Agency email (#4) is 1:1 outreach, max 10/day, with a real reason
  for contacting that specific person. Bulk-importing a scraped list into Gmail will get the account
  rate-limited or suspended, and it is illegal in the EU/UK without a lawful basis.
- Form leads (#1–#3) consented by submitting the form, and the footer on the landing page states exactly
  how many emails they will get. Honor the unsubscribe immediately.
- Keep plain text, one link per paragraph, no image-only emails. New Gmail accounts sending HTML with
  several links land in promotions or spam.
- If a lead replies, stop the sequence. The sequence exists to earn a reply, not to finish itself.
