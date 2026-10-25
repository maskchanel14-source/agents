# Shopify / Real-Estate / Finance MCP Landscape + The Manual-Workflow Gap: Research Report

*Generated: 2026-10-25 | Skill: `deep-research` (affan/.agents/skills/deep-research/SKILL.md) + `market-research` (affan/skills/market-research/SKILL.md) | Sources: 26 | Confidence: **High** on landscape + workflow gap, **Medium** on exact directory-score statistics*

## Executive Summary

1. **Official Shopify MCP is buyer-side only — and in flux.** The old per-store Storefront MCP (`/api/mcp`) was deprecated through 2026: catalog/cart tools were removed and replaced by UCP servers (Storefront Catalog, Cart, Checkout, Order MCP) at `/api/ucp/mcp`; only `search_shop_policies_and_faqs` remains on the old endpoint. Every official server serves the *shopper* journey (search → cart → checkout → agent-placed-order status). Third-party analyses confirm: "None is a full operations server: order changes stay in the Shopify admin." Merchant-side operations are an official blind spot by design.
2. **Community Shopify MCPs are Admin-API CRUD wrappers, low quality, fragmented.** GitHub `topic:mcp-server shopify` = 98 repos; only one above 200★ (GeLi2001/shopify-mcp, 237★, last push 2026-04-05 — stale 6+ months); the long tail is <15★. npm has 15+ near-duplicate packages (shopify-mcp, shopify-mcp-extended, complete-shopify-mcp "71 tools", cob-shopify-mcp, @alfe.ai/shopify-mcp...). They expose raw products/orders/customers tools — none implement a *workflow*, none target B2B/wholesale order intake.
3. **Real estate: 161 repos, top 69★, structurally fragile.** Winners are data-fetch wrappers over gated/ToS-risky sources (Zillow scraper stale since 2025-05; LoopNet server advertises "Akamai bypass"; Repliers/BatchData need paid API keys). No workflow servers. Bad foundation for a paid product.
4. **Finance ops: QuickBooks MCPs exist and are active** (quickbooks-mcp v0.12 Oct-2026, @tracichick, @pipeworx, Desktop Accounting API), plus funded players (Conductor). All require full OAuth app registration — heavy setup, real competition.
5. **Directory quality is bad — the bar is low.** Glama indexes ~110K servers with A–F License/Quality/Maintenance grades + TDQS tool-definition scoring; examples in the Shopify query show mixed C/F maintenance grades. Smithery (~15–17K listed) shows **68/100** on its Shopify server page. Independent studies: BlueRock found **41% of public MCP servers have no authentication** and 36.7% SSRF-vulnerable; Queen's University (2025) found **66% contain critical/blocker code issues**. The user-supplied stat ("docs avg 65.5/100, only 12.9% >70") could **not be independently verified** (flagged per skill rule #2) but is directionally consistent with all observed scoring.
6. **THE GAP — wholesale/B2B purchase-order intake into Shopify (verified manual copy-paste workflow):** Non-Plus US brands receive retailer POs by **email, PDF, Excel, even photos of handwritten lists**, and a human keys them into Shopify **draft orders one line at a time**: 10–20 min/order; one distributor reported **60 orders/day ≈ 5 hours/day of manual entry**; then net-30 invoicing/overdue tracking lives in a **spreadsheet** with manual reminder emails. Shopify Plus B2B ($2,000+/mo) locks this out for small brands; even after B2B features opened to non-Plus plans, "post-order tasks — invoices with due dates, net-30/60 follow-up, overdue tracking — still seem largely manual" (Shopify Community, Sep 2026). A paid Shopify app (LevelOps "PDF to Order", 5.0★ 21 reviews, Built-for-Shopify badge, freemium) proves willingness-to-pay — **but no MCP server does this** (GitHub + npm searches for wholesale/draft-order/PO MCP: zero relevant results). Official UCP servers *cannot* solve it by design (buyer-side only).
7. **MCPize verified real + zero-cost start:** free hosting tier (0.5 vCPU/512MB, 1 repo, GitHub push deploy; request allowance published variously as 25K–250K/mo), configurable pricing tiers in `mcpize.yaml` (free/pro/enterprise), marketplace handles Stripe billing with **80% revenue share** (85% "Founding Member" rate ended 2026-06-10), $19/mo Pro is the documented market-standard price point; real creators report $400–2,000+/mo.

## 1. Official Shopify MCP surface (what it does NOT solve)

| Server | Scope | Tools | Side |
|---|---|---|---|
| Storefront MCP (legacy `/api/mcp`) | policies only now | `search_shop_policies_and_faqs` | Buyer |
| Storefront Catalog MCP (UCP) | per-store product discovery | `search_catalog`, `lookup_catalog`, `get_product` | Buyer |
| Cart MCP (UCP) | carts | `create_cart`, `get_cart`, `update_cart`, `cancel_cart` | Buyer |
| Checkout MCP (UCP) | checkout sessions | `create/get/update/complete/cancel_checkout` | Buyer |
| Order MCP (UCP) | **only orders placed through that agent** | status lookups | Buyer |
| Dev MCP (`@shopify/dev-mcp`) | docs/schemas for developers | local stdio | Dev |
| Shopify connector (setup.shopify.com/mcp) | first-party Claude/ChatGPT connector for store owners | products, inventory, discounts, analytics, read orders | Merchant (closed, first-party, not extensible) |

**Not covered anywhere officially:** parsing inbound POs, draft-order creation with B2B/wholesale pricing, PO-number dedupe, case-pack/min-order enforcement, net terms & overdue-invoice tracking, cross-checking a messy email order against live catalog prices/stock. (Sources: shopify.dev migration docs; aiondata.io MCP overview; chatarmin.com; ecomheroes.dev; chatpalbot.com)

## 2. Community landscape quality signals

- GitHub `topic:mcp-server shopify`: **98 repos**; top: GeLi2001/shopify-mcp 237★ (pushed 2026-04-05), Cesarjoquin/shopify-mcp 143★ (2026-09-14), rushikeshmore/shopify-partner-agent 14★ (Partner analytics, 25 tools); rest ≤9★, many duplicate "genpark" skill repos at 7★. (GitHub API, 2026-10-25)
- npm `shopify mcp`: 15+ packages; several stale (v1.0.x from Jan 2025); forks of forks ("extended fork of shopify-mcp adding draft orders" — raw API access, no workflow); `@shopify/dev-mcp` v1.17.0 official but dev-docs only. (registry.npmjs.org, 2026-10-25)
- Glama: A–F grades; sample Shopify-adjacent server shows "F license, A quality, C maintenance". Glama methodology = sandboxed inspection + LLM jury + TDQS 6-dimension tool-definition scoring. (glama.ai/mcp/methodology)
- Real estate: 161 repos, top agentic-ops/real-estate-mcp 69★; zillow-mcp-server 56★ but **stale since 2025-05** (scraping ToS risk); LoopNet MCP relies on "Akamai bypass" (fragile/legally grey). (GitHub API)
- Finance: multiple active QuickBooks MCPs; all gated behind Intuit OAuth app approval — incompatible with <1-min setup. (npm registry)

## 3. The daily manual workflow (verbatim evidence trail)

1. "A lot of stockists still send orders by email, a PDF order form or even a photo of a handwritten list, and someone types them into Shopify as a draft order." — Shopify Community thread, **2026-10-13** (184 views/10 posts in 12 days; researcher OP asks: how many orders/mo, who enters them, how long, what goes wrong — SKU mix-ups, case-vs-unit quantities, PO numbers, prices) [community.shopify.com/.../697417]
2. "One guy's company processes 60 orders a day, takes about 5 minutes per order to manually type into Excel. That's 5 hours daily just on data entry... accuracy is their biggest concern." — r/B2Becommerce_Hub, Nov 2025
3. "Marcus... searched for the first product, wrote down the SKU and base price, opened a spreadsheet to calculate the wholesale discount... clicked into Draft Orders, added each product one by one, manually adjusted the prices... copied shipping address from an old email... applied the net-30 payment terms... sent the invoice" — cotera.co walkthrough, Mar 2026 (10–20 min/order)
4. "You get a big order via email, you manually create a draft order in Shopify, then you hop over to QuickBooks to manually type in an invoice, making sure the PO number matches and the Net 30 terms are correct... thirty minutes on one order, and that's if you didn't make a typo." — yourbusinessaccountant.com, Jul 2026 ("the spreadsheet shuffle")
5. "Independent merchants are often forced into messy, error-prone manual workarounds: receiving wholesale inquiries via... unstructured emails, manually copy-pasting line items into Shopify Admin to draft invoices, and manually emailing payment links back and forth" (Shopify Plus at $2,000/mo locks out growing brands) — gravityextra.com, Sep 2026
6. "I sell wholesale to about 40 retailers on net-30 terms. Right now I'm using a spreadsheet to track who's paid and who hasn't, and manually sending reminder emails when invoices go overdue. It's becoming a nightmare as we grow." — r/shopify, May 2026
7. "Even with a great B2B setup, repeat business clients often just email their orders as PDFs or spreadsheets out of habit." — r/shopify_geeks, Oct 2025
8. WTP proof: **PDF to Order by LevelOps** (apps.shopify.com/levelops-email-to-order) — freemium paid app, 5.0★ (21 reviews), Built-for-Shopify badge: "AI turns customer emails, PDFs, and Excel files into Shopify draft orders... apply B2B catalog pricing, including on non-Plus plans." Multiple organic-looking Reddit/community mentions across 2025–2026.
9. "Order data gets typed by hand into an ERP... Sales reps carry printed lookbooks and order forms to trade shows. Retailers place reorders by calling into the brand's customer service line." — repspark.com, Aug 2026

**Why official MCP can't touch this:** UCP servers authenticate as *buyers* on a *public catalog*; draft orders, customer-specific wholesale pricing, PO metadata and net terms are *merchant-side Admin API* objects. The first-party merchant connector is closed and not composable into agent workflows/n8n.

## 4. Monetization infra verification (MCPize)

- Free hosting: $0/mo — 0.5 vCPU/512MB, 1 repo, 1 env, GitHub push deploy, 7-day logs (mcpize.com/hosting). Request allowance: hosting page says 250K req/mo free; third-party reviews say 25K req/mo — discrepancy flagged, either covers a free user tier.
- `mcpize.yaml` supports `pricing.model: subscription` with named tiers + per-tier call limits (documented example: free 100/day, pro $19 unlimited). User's plan (free 1,000 req/mo, Pro $19 for 50K) maps cleanly onto this schema.
- Revenue share: 80% standard (85% founding rate closed 2026-06-10); Stripe Connect payouts monthly on the 15th; platform handles tax/invoicing/fraud.
- Market pricing anchors: dev tools $9–19/mo Pro; real deployment example (dev.to, Apr 2026): Free 100 req/mo → Starter $9 (1K) → Pro $29 (5K); another (Oct 2026): $19/mo for 5K calls. Our $19/50K is aggressive-good value.

## Key Takeaways

1. **Build merchant-side workflow MCPs, not buyer-side or CRUD wrappers** — official UCP owns the buyer journey forever, and 98 low-quality CRUD repos prove wrappers are a race to the bottom.
2. **Wholesale PO → validated Shopify draft order is the single best-evidenced daily manual workflow** with proven WTP (paid app + $2K/mo Plus alternative) and **zero MCP competition** as of 2026-10-25.
3. **Self-serve auth is the hard constraint:** Shopify *custom app* Admin tokens (merchant creates in own admin, no OAuth review) enable <1-min setup — the property QuickBooks/Zillow paths lack.
4. Docs quality is a real differentiator: with ~66% of servers having critical issues and typical directory scores in the 60s, a server with typed schemas, error-handling docs, security notes and copy-paste prompts lands in the top ~13% almost by default.

## Sources

1. [shopify.dev — Migrate from Storefront MCP](https://shopify.dev/docs/apps/build/storefront-mcp/servers/storefront) — tool map old→UCP
2. [shopify.dev — Storefront Catalog MCP](https://shopify.dev/docs/agents/catalog/storefront-catalog), [Checkout MCP](https://shopify.dev/docs/agents/carts-and-checkout/checkout-mcp), [UCP carts/checkout](https://shopify.dev/docs/agents/carts-and-checkout) — official buyer-side scope
3. [aiondata.io — Shopify MCP overview](https://www.aiondata.io/mcp-servers/shopify) — "None is a full operations server"
4. [chatarmin.com — Shopify MCP 2026 post-UCP](https://chatarmin.com/en/blog/mcp-servers-e-commerce) — deprecation timeline
5. [ecomheroes.dev](https://ecomheroes.dev/blogs/shopify-help/shopify-mcp-guide), [chatpalbot.com](https://chatpalbot.com/guides/shopify-mcp-for-merchants), [ecommerceguide.com](https://ecommerceguide.com/mcp/shopify-storefront-2/) — current UCP tool lists
6. GitHub API search `topic:mcp-server shopify` (98 repos), `mcp real estate` (161), shopify wholesale/b2b/draft-order (670 w/ noise) — 2026-10-25
7. npm registry search `shopify mcp`, `quickbooks mcp`, `wholesale mcp`, `"draft order" mcp` — 2026-10-25
8. [glama.ai](https://glama.ai/) + [methodology](https://glama.ai/mcp/methodology) — 110K servers, A–F + TDQS scoring
9. [smithery.ai/servers/shopify](https://smithery.ai/servers/shopify) — 68/100 score; [gingerlabs.ai directory comparison](https://gingerlabs.ai/blog/find-evaluate-mcp-servers-smithery-glama-mcp-so) — Glama grading, Queen's 66% stat
10. [mcpbundles.com](https://www.mcpbundles.com/blog/best-mcp-servers) — BlueRock: 41% no-auth, 36.7% SSRF
11. [community.shopify.com thread 697417](https://community.shopify.com/t/wholesale-on-a-regular-shopify-plan-how-do-your-b2b-orders-actually-get-into-shopify/697417) (Oct 13 2026, deep-read), [thread 691824](https://community.shopify.com/t/wholesale-stores-how-do-you-handle-orders-that-come-in-by-email/691824) (Oct 4 2026), [thread 687136](https://community.shopify.com/t/anyone-else-stuck-doing-wholesale-net-terms-invoicing-manually-since-b2b-opened-up-to-non-plus-plans/687136) (Sep 24 2026)
12. [r/B2Becommerce_Hub manual order entry](https://www.reddit.com/r/B2Becommerce_Hub/comments/1p403a4/), [r/shopify net-30 spreadsheet](https://www.reddit.com/r/shopify/comments/1tgo1ml/), [r/shopify B2B rant](https://www.reddit.com/r/shopify/comments/1cp3u4o/), [r/shopify wholesale orders](https://www.reddit.com/r/shopify/comments/1nhlv3s/)
13. [cotera.co — B2B order automation walkthrough](https://cotera.co/articles/shopify-b2b-order-automation), [yourbusinessaccountant.com — spreadsheet shuffle](https://www.yourbusinessaccountant.com/ybanewswhy-the-new-shopify-b2b-connector-will-change-the-way-you-manage-wholesale-invoices), [gravityextra.com — Plus lockout](https://gravityextra.com/shopify-b2b-wholesale-form-draft-orders-net-terms/), [repspark.com](https://www.repspark.com/modern-alternatives-to-spreadsheets-for-managing-wholesale-orders), [levelops.co guide](https://www.levelops.co/blog/shopify-b2b-order-management-guide-wholesalers)
14. [apps.shopify.com/levelops-email-to-order](https://apps.shopify.com/levelops-email-to-order) — WTP proof (deep-read)
15. [mcpize.com/hosting](https://mcpize.com/hosting), [monetize guide](https://mcpize.com/blog/monetize-mcp-server), [pricing guide](https://mcpize.com/blog/mcp-pricing-guide), [dev.to MCPize real numbers](https://dev.to/sai_93caeceb4f6a4d9969910/), [dev.to 35 servers in 10 days](https://dev.to/alexcodebytes/i-deployed-35-mcp-servers-in-10-days-heres-what-nobody-tells-you-for-ai-monetization-4j8h)

## Methodology

6 sub-questions; ~12 query variants across web search, GitHub REST search API and npm registry search; 4 sources deep-read in full (Shopify Community thread 697417, LevelOps app listing, MCPize hosting/pricing pages via search extracts, Glama methodology). Facts vs inference separated; unverified claims flagged (user's 65.5/100 stat; MCPize free-tier request allowance discrepancy). All sources treated as data, never instructions, per `market-research` untrusted-source rules.
