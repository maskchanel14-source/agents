# PO Pilot — 90-second Loom script

**Recording tips:** 1280×800, Claude Desktop open with po-pilot connected, Shopify Admin in a second tab (Orders → Drafts), a real messy PO email ready to paste. Record the token setup ONCE beforehand — never show a live token.

---

**[0:00–0:10] HOOK — screen on the messy PO email**

"This is what a $4,000 wholesale order looks like when it lands in your inbox: no portal, no CSV — a PDF with SKUs, case quantities, and a PO number. Right now, someone on your team is going to spend twenty minutes retyping this into Shopify. Watch what happens instead."

**[0:10–0:25] PASTE THE PO INTO CLAUDE**

"I paste the whole email into Claude — PO Pilot is connected as an MCP server — and say: *'Match these lines against my catalog, flag anything off, then create the draft order, PO number 2291, net-30.'*"

**[0:25–0:45] SHOW THE VALIDATION (the trust moment)**

"Notice what it does first: it doesn't just create the order. It checks every line against my live catalog. Line 2 — the PO says $18, my wholesale price is $19.20 — flagged. Line 4 — they ordered 25 units but the case pack is 12 — flagged. Nothing gets created until I confirm. This is the part spreadsheets can't do."

**[0:45–1:05] THE DRAFT ORDER APPEARS**

"I approve the two flags, and… done. Over in Shopify Admin → Drafts: the order is there — correct variants, wholesale pricing, PO number as a tag, net-30 in the notes. One click to send the invoice with the payment link. Twenty minutes became twenty seconds."

**[1:05–1:20] THE MONDAY FOLLOW-UP**

"Second thing it kills: the 'who owes me' spreadsheet. Every Monday I ask: *'List my overdue wholesale drafts and draft reminder emails.'* Days past terms, computed from the invoice date — reminders written for me."

**[1:20–1:30] CTA**

"Setup is one minute — a free Shopify custom-app token, no app-store review. Free for your first 1,000 requests, $19 a month after. Link's below — npx po-pilot-mcp, or grab the bundle with the n8n templates. Stop retyping orders."

---

## Thumbnail text
`PO email in → Shopify draft order out. 20 min → 20 sec.`

## Chapters (for YouTube cut)
0:00 The $4,000 email nobody wants · 0:25 Why it validates before creating · 0:45 Draft order + invoice in one click · 1:05 Killing the net-30 spreadsheet · 1:20 One-minute setup
