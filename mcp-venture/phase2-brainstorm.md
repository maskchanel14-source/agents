# Phase 2 — Deep Thinking & Brainstorming Artifact

*Skills invoked: `brainstorming` (obra/skills/brainstorming/SKILL.md), `product-lens` (affan/skills/product-lens/SKILL.md), `before-you-build` (agents/plugins/before-you-build/skills/before-you-build/SKILL.md)*
*Date: 2026-10-25 · Input: phase1-research-report.md*

## Private ideation — dropped ideas (brainstorming skill: think wide, drop weak)

| Idea | Why dropped |
|---|---|
| QuickBooks invoice-chaser MCP | Intuit OAuth app review = weeks; violates <1-min setup; active npm competition |
| Zillow/MLS real-estate data MCP | ToS fragility (stale scrapers, "Akamai bypass"), gated paid keys |
| Stripe dispute/refund MCP | Official free Stripe MCP exists → dies to free clone (constraint violation) |
| Shopify review-responder MCP | $5 apps solve it; weak agentic-workflow fit |
| n8n-templates-only product | No server → no metered MCPize revenue; templates kept as bundle component instead |

## Finalists scored (1–10; Competition & Build high = favorable)

| Criterion | A. PO Pilot (wholesale PO → validated draft orders) | B. Net-Terms AR Copilot | C. RE Deal Intake |
|---|---|---|---|
| Demand | 9 | 7 | 6 |
| WTP | 9 | 6 | 5 |
| Competition | 8 | 7 | 5 |
| Build (<100 core lines) | 9 | 8 | 3 |
| Monetization fit | 9 | 7 | 5 |
| **Total** | **44** | 35 | 24 |

Evidence anchors: A — Shopify Community 697417 (Oct 13 2026), r/B2Becommerce_Hub (60 orders/day × 5 min = 5 hrs/day), cotera.co 10–20 min/order walkthrough, LevelOps 5.0★ paid app, Plus $2,000/mo lockout (gravityextra). B — r/shopify net-30 spreadsheet thread (May 2026), community 687136 (Sep 2026). C — 161 repos, top 69★, fragile data sources.

## Winner + tradeoff

**A — PO Pilot.** B is subsumed (its product = A's tool #4 `list_draft_orders`; becomes a Pro feature, not a separate build). C has weakest WTP + licensing swamp. A's tradeoff: narrow ICP (US wholesale brands on non-Plus Shopify, 10–500 POs/mo) instead of finance-ops mega-TAM — narrow enough to have zero MCP competition, broad enough for hundreds × $19/mo.

## before-you-build pre-mortem (winner)

- **Highest-risk assumption:** merchants paste POs into Claude instead of buying the turnkey app.
- **Smallest validation step:** free tier live on MCPize + reply in community thread 697417 + r/shopify launch post; measure draft orders created via server in first 14 days (target: ≥10 real POs from ≥3 stores).
- **Anti-goal:** a silently-wrong draft order (bad SKU/price). Every mismatch MUST surface as a structured warning. Trust is the product.
- **Delay until evidence:** QuickBooks sync, multi-store, hosted email ingestion, PDF parsing server-side (client LLM already reads PDFs — division of labor: LLM extracts, MCP validates against live catalog + creates).

## product-lens ICE

Reach 7 · Impact 9 · Confidence 8 · Ease 9 → **GO** (ICE ≈ 8.25/10)

## How-it-gets-made choices (my call, per brainstorming skill)

- **Stack:** TypeScript + @modelcontextprotocol/sdk + Zod (per `mcp-server-patterns` skill; npm-first; MCPize node runtime).
- **Auth:** Shopify custom-app Admin token (`shpat_`) via env — merchant self-issues in own admin; scopes `read_products`, `read_customers`, `write_draft_orders`, `read_draft_orders`. No OAuth review, no app-store listing.
- **API:** Admin GraphQL `2026-10` (matches local `shopify-product-operations` skill).
- **Tools (4):** `match_catalog_items`, `find_customer`, `create_draft_order` (PO-dedupe + net terms + tags + optional invoice send), `list_draft_orders` (net-30 aging).
- **Division of labor (the moat):** client LLM does fuzzy extraction from messy PO text; server does authoritative validation (SKU match, live price, inventory, case/min-qty warnings, PO dedupe) and the write. A free CRUD-wrapper clone can't copy the validation rules + docs + templates.
