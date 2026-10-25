# PO Pilot 🧾✈️ — wholesale purchase orders → validated Shopify draft orders

**An MCP server that ends the 10–20-minute-per-order copy-paste grind for wholesale brands on Shopify.**

Your retail buyers email you POs — PDFs, Excel files, plain text, even photos of handwritten lists. Today someone on your team retypes every line into a Shopify draft order, checks prices against a spreadsheet, and tracks net-30 payments by hand. PO Pilot plugs that workflow into Claude (or any MCP client): **the AI reads the messy PO, PO Pilot validates every line against your live catalog, and the draft order is created with PO dedupe, net terms, tags, and an optional invoice email — in seconds.**

[![npm version](https://img.shields.io/npm/v/po-pilot-mcp.svg)](https://www.npmjs.com/package/po-pilot-mcp)
[![Node](https://img.shields.io/node/v/po-pilot-mcp.svg)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![MCP](https://img.shields.io/badge/MCP-stdio%20%2B%20MCPize-blueviolet.svg)](https://modelcontextprotocol.io)
[![API](https://img.shields.io/badge/Shopify%20Admin%20GraphQL-2026--10-95BF47.svg)](https://shopify.dev/docs/api/admin-graphql)

---

## Why this exists

- Non-Plus Shopify brands get wholesale orders **by email/PDF/Excel** and key them in manually: 10–20 min per order. A distributor processing 60 orders/day spends **~5 hours/day on data entry alone**.
- Shopify's official MCP servers (Storefront Catalog / Cart / Checkout / Order MCP, UCP) are **buyer-side only** — they cannot create draft orders, apply wholesale pricing, or track net terms. That's merchant-side Admin API territory.
- Shopify Plus B2B starts around **$2,000/month**. Existing apps solve pieces; **no MCP server owned this workflow** when PO Pilot shipped (checked Smithery, Glama, GitHub `topic:mcp-server`, npm — Oct 2026).

## What it does / doesn't do

| ✅ Does | ❌ Doesn't |
|---|---|
| Validate PO lines against your **live catalog** (SKU + title search) | Parse PDFs itself — your AI client reads the document, PO Pilot validates & writes |
| Flag **price mismatches**, low inventory, case-pack errors **before** ordering | Silently create wrong orders — every mismatch needs review |
| Create **draft orders** with custom wholesale prices, net terms, PO tags | Take payments (Shopify's invoice link does that) |
| **Refuse duplicate PO numbers** (no more double-keying) | Sync to QuickBooks (roadmap) |
| **Net-30/60 aging**: list unpaid drafts, flag overdue | Manage more than one store per server instance (run one per store) |
| Optionally **email the invoice** + payment link to the buyer | Require OAuth/app review — uses your own custom-app token |

## Architecture (the division of labor is the product)

```
 Retailer's PO (email/PDF/Excel/handwritten photo)
        │
        ▼
 Your AI client (Claude Desktop / Claude Code / Cursor / ChatGPT)
   reads the document, extracts line items           ← LLM is great at this
        │
        ▼
 PO Pilot MCP server
   match_catalog_items  → exact SKU/title match, live price, inventory, warnings
   find_customer        → resolve or create the B2B account
   create_draft_order   → PO dedupe + net terms + tags + invoice send
   list_draft_orders    → net-terms aging, overdue flags
        │
        ▼
 Shopify Admin GraphQL API (2026-10)  →  Draft order ready for review
```

## Setup (< 1 minute, no OAuth, no app store review)

### 1. Create a Shopify custom app token (30 s)

1. Shopify Admin → **Settings → Apps and sales channels → Develop apps → Create app** (name: `PO Pilot`).
2. App → **Configuration → Admin API integration** → grant exactly these scopes → **Save**:
   `read_products` · `read_customers` · `read_draft_orders` · `write_draft_orders`
3. **API credentials** tab → **Install app** → **Admin API access token** → *Reveal token once* → copy it (starts with `shpat_`).

### 2. Connect your MCP client (20 s)

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "po-pilot": {
      "command": "npx",
      "args": ["-y", "po-pilot-mcp"],
      "env": {
        "SHOPIFY_STORE_DOMAIN": "your-store.myshopify.com",
        "SHOPIFY_ADMIN_TOKEN": "shpat_xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add po-pilot \
  -e SHOPIFY_STORE_DOMAIN=your-store.myshopify.com \
  -e SHOPIFY_ADMIN_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxx \
  -- npx -y po-pilot-mcp
```

**Remote/hosted (MCPize):** deploy once with `mcpize deploy` and connect clients to the hosted URL — see [Pricing & hosting](#pricing--hosting).

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SHOPIFY_STORE_DOMAIN` | ✅ | — | Your `*.myshopify.com` domain (no `https://`, no trailing slash) |
| `SHOPIFY_ADMIN_TOKEN` | ✅ | — | Custom-app Admin API token (`shpat_…`) |
| `PO_PILOT_DISCOUNT_PCT` | — | `0` | Default wholesale discount % off catalog price, used for *suggested* pricing and mismatch checks |
| `PO_PILOT_TAGS` | — | `wholesale` | Comma-separated tags applied to every created draft order |
| `PO_PILOT_API_VERSION` | — | `2026-10` | Admin GraphQL version (fall back to `2025-10` if your store is pinned) |

## Tools

### 1. `match_catalog_items`

Validates extracted PO lines against the live catalog. **Always call this first.**

| Param | Type | Notes |
|---|---|---|
| `items[].sku` | string? | Exact (case-insensitive) SKU match attempted first |
| `items[].title` | string? | Full-text product search when SKU is missing/unmatched |
| `items[].variant_title` | string? | Disambiguates size/color ("Large / Navy", "12oz") |
| `items[].quantity` | int > 0 | Convert cases→units first ("4 cases of 12" → 48) |
| `items[].unit_price` | number? | PO-stated price → compared vs catalog & wholesale price |
| `items[].case_pack` | int? | Qty not divisible by it → warning |

Returns per line: `status` = `matched` \| `ambiguous` \| `not_found` \| `error`, the matched variant (`variant_id`, `catalog_price`, `suggested_wholesale_price`, `inventory_available`), and `warnings` (price mismatch, oversell, case-pack). Ambiguous lines return up to 5 candidates for the user to pick.

### 2. `find_customer`

Search customers by email/name/company; returns `customer_id`, contacts, tags, addresses. `create_if_missing: true` (+ `email`) creates a minimal customer for new wholesale accounts — **search-only by default** for privacy.

### 3. `create_draft_order`

Creates the draft order from **matched variant ids only**.

| Param | Type | Notes |
|---|---|---|
| `line_items[]` | array | `{variant_id (GID), quantity, unit_price?}` — `unit_price` overrides catalog price with the agreed wholesale price |
| `po_number` | string? | Enables **dedupe** + `po-<NUMBER>` tracking tag |
| `customer_id` / `customer_email` | string? | `customer_id` preferred; email-only drafts supported |
| `payment_terms` | `net-15` \| `net-30` \| `net-60` \| `due-on-receipt` | Recorded in note + note attributes (default `net-30`) |
| `send_invoice` | bool? | Emails invoice + payment link to buyer, returns `invoice_url` |
| `tags` / `note` | array? / string? | Merged with `PO_PILOT_TAGS` |
| `allow_duplicate_po` | bool? | Escape hatch for genuinely repeated PO numbers (default `false` = refuse) |

Returns: draft `id`, `name`, `status`, `total_price`, `invoice_url`, applied tags/terms — or a structured `duplicate_po` error listing the existing drafts.

### 4. `list_draft_orders`

Net-terms aging without the spreadsheet: the 50 most recent drafts with `days_open`, parsed `payment_terms`, and computed `overdue` flag. Filters: `status`, `tag`, `po_number`, `days`, `overdue_only`.

## 3 copy-paste prompts

**① Daily PO intake**

> Here's a wholesale order that just came in by email:
> ```
> <paste the email body / PDF text / CSV rows>
> ```
> Use PO Pilot to match every line against my catalog. Show me anything that doesn't match or has a price mismatch. If everything is clean, create a draft order for PO #[number], net-30, tagged `wholesale`, and don't send the invoice yet.

**② Monday collections run**

> Use PO Pilot to list all overdue wholesale draft orders. For each one, draft a short, polite reminder email to the buyer mentioning their PO number, the invoice total, and how many days past terms it is.

**③ Trade-show batch**

> I collected 6 paper orders at the trade show. I'll paste them one at a time. For each: validate the lines, find or create the customer, and create a net-30 draft order tagged `trade-show-2026`. At the end, give me one summary table of everything needing my review.

## Error handling — it never crashes, it explains

Every failure is a structured payload the AI can act on, never a stack trace:

| Situation | You get |
|---|---|
| Missing/invalid env vars | `ok:false, error:"not_configured"` + the exact 60-second setup checklist |
| Bad/revoked token, missing scopes | HTTP 401/403 mapped to "regenerate token, add scopes …" |
| Wrong domain / API version | HTTP 404 → "check `.myshopify.com` domain / try `2025-10`" |
| Shopify rate limit | HTTP 429 → "wait and retry; batch lines into one call" |
| Network failure | Per-line `error` + hint; other lines still processed |
| Fabricated variant ids | Refused up-front: "run `match_catalog_items` first" |
| Duplicate PO number | Refused with the existing draft(s) listed; `allow_duplicate_po` to override |
| Shopify `userErrors` | Passed through verbatim with common-cause hints |

## Security

- **Least privilege:** 4 scopes, no `write_products`, no `write_orders`, no customer-data export scopes. The token can only *read* catalog/customers/drafts and *write* draft orders.
- **No storage, no telemetry:** PO data flows client → this server → Shopify per request. Nothing is written to disk or logged (except a startup line on stderr).
- **Token hygiene:** token lives in your MCP client's env config. Rotate anytime by reinstalling the custom app. Never commit it — `.env` is gitignored.
- **Human in the loop:** draft orders are *not* real orders — nothing charges, nothing decrements inventory until you (or the buyer, via invoice) complete them.

## Pricing & hosting

Self-host free forever (MIT, `npx po-pilot-mcp`). Or use the hosted remote server via MCPize:

| Tier | Price | Requests | Notes |
|---|---|---|---|
| **Free** | $0 | 1,000/mo | Full workflow — enough for ~50–100 POs/mo (4 calls each) |
| **Pro** | $19/mo | 50,000/mo | Priority support, invoice-send at volume |

Developers: `mcpize deploy` (see `mcpize.yaml`) — MCPize handles hosting, Stripe billing, and pays 80% revenue share.

## Deploy checklist (maintainer)

```bash
npm install && npm run build      # typecheck + dist/
npm publish --access public       # registry name: po-pilot-mcp
mcpize deploy                     # hosted remote endpoint + metered billing per mcpize.yaml
```

## Troubleshooting

- **"access denied" GraphQL errors** → the custom app is missing a scope, or wasn't re-installed after scope changes. Fix scopes → Save → Install app again → new token.
- **`products(query:"sku:…")` returns nothing** → some stores have SKUs only on variants of archived products; try the `title` field instead (the tool falls back automatically).
- **Older store pinned to an older API** → set `PO_PILOT_API_VERSION=2025-10`.
- **Inspect locally:** `npm run inspect` (MCP Inspector) or pipe JSON-RPC into `node dist/index.js`.

## Roadmap

QuickBooks invoice sync · multi-store · Shopify Flow trigger on draft completion · case-pack rules from product metafields · PO parsing evals suite.

## License

MIT © 2026 maskchanel14. Not affiliated with Shopify Inc. "Shopify" is a trademark of Shopify Inc.
