# PO Pilot — 10 prompts for your wholesale order desk

Copy/paste into Claude with PO Pilot connected. Review every draft order in Shopify before sending an invoice. The server validates catalog facts; you remain the approver.

## 1. Turn this PO into a draft order

> Read the purchase order below. First call `match_catalog_items` for every line using the exact SKU, description, quantity, and any stated unit price. Show me all matches and warnings. Do not create an order if any line is ambiguous, not found, or has an unresolved price/case-pack warning. If everything is clean, find the customer by the buyer's email, then create a Shopify draft order with the PO number, payment terms, and the matched variant IDs. Summarize the draft-order URL and any assumptions. PO: [paste PO]

## 2. Process a PDF PO I uploaded

> Extract the buyer name, email, PO number, payment terms, ship-to address, and each line's SKU/description/quantity/unit price from the attached PO. Quote the extracted fields back to me first. Then validate every line against Shopify with `match_catalog_items`. Ask me about anything that does not match exactly; do not guess. Only after I confirm, find the customer and create a draft order. Never send the invoice yet.

## 3. Check a retailer's order before entry

> Validate this order against the live Shopify catalog. For every line, report: requested SKU, matched product/variant, quantity, available inventory, catalog price, PO price, case-pack divisibility, and status. Do not create a draft order. Order: [paste lines]

## 4. Find this customer without creating anyone

> Search Shopify for the wholesale customer [buyer name or email]. Use search-only mode. Show the customer ID, email, tags, and relevant shipping addresses. If there are multiple likely matches, list them and ask me to choose. Do not create or update a customer.

## 5. Safely create a draft order

> The PO has been reviewed and approved. Create a draft order for customer [email], PO number [PO number], payment terms Net-30, with these already-validated Shopify variant IDs and quantities: [variant GIDs + quantities]. Before creating, check whether this PO number already exists. If it is a duplicate, stop and show me the existing draft instead of creating another. Do not send an invoice.

## 6. Send the invoice after approval

> Find draft order [draft name or ID]. Confirm its customer, PO number, total, and payment terms. If they match [expected details], send the invoice email with a clear subject that includes the Shopify draft name and PO number. If anything differs, stop and ask me. Report the invoice URL and send result.

## 7. Monday collections review

> List open wholesale draft orders with payment terms. Show PO number, customer, total, days open, net terms, and whether overdue. Sort most overdue first. Do not email anyone. Flag records missing terms or buyer email so I can fix them.

## 8. Draft overdue reminders (human review)

> Find wholesale drafts overdue by at least [N] days. For each one, verify customer email and invoice URL, then write a polite, non-accusatory reminder that includes the PO number, amount, due date, and payment link. Show me the messages as drafts for review; do not send them automatically.

## 9. Investigate a duplicate PO

> Check whether PO [number] has already been entered. If found, compare the existing draft's customer, line items, quantities, total, and status with this PO: [paste PO]. Explain whether it is a true duplicate or a correction/revision. Do not create or modify anything until I decide.

## 10. End-of-week exception report

> Review these orders using `list_draft_orders` and catalog validation where useful. Give me an exception-only report grouped by: overdue payment, missing PO number, duplicate PO, unmatched SKU, price mismatch, inventory shortfall, and case-pack violation. Include the Shopify link or identifier and a recommended next action. Do not modify orders or send emails.

---

### Safety rules
- A match is not approval: review warnings and source PO before creating.
- Never invent variant IDs; obtain them from catalog matching.
- Keep invoices and payment reminders human-approved.
- Use the least-privilege Shopify custom-app scopes described in the server README.
