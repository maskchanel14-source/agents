# Gumroad — $49 Bundle Listing

*Skill: marketing-campaign (affan) · Audience: US wholesale brands + automation freelancers on non-Plus Shopify · Positioning: "the order-intake operating kit, not another app subscription" · Angle: buy once, save 15+ hrs/month*

---

## Product name
**PO Pilot Bundle — AI Wholesale Order Intake for Shopify**

## Subtitle (Gumroad "summary" field)
Stop retyping emailed POs into Shopify draft orders. The complete kit: MCP server source + 2 n8n automation templates + Loom walkthroughs + the 10-prompt wholesale desk pack. Free tier runs forever; Pro is $19/mo only if you scale.

## Price
**$49** (launch: first 50 buyers `$29` with code `EARLYPO`). Pay-what-you-want **above** $49 enabled — agencies grab it for client work.

## Cover text (for the thumbnail)
`20 min per order → 20 seconds.` / `Wholesale POs → Shopify draft orders, validated.`

---

## Description (paste into Gumroad)

**Your wholesale orders arrive the way they did in 2009: by email.**

A PDF from a retailer. An Excel line sheet. A photo of a handwritten list from a trade show. And then someone on your team spends 10–20 minutes per order:

- looking up each SKU in Shopify to check the wholesale price,
- retyping every line into a draft order,
- praying nobody ordered 25 units of a 12-pack,
- tracking net-30 payments in a spreadsheet,
- writing "just a friendly reminder" emails by hand on Mondays.

One distributor we talked to processes 60 POs a day. That's **5 hours a day of data entry**. Shopify Plus B2B starts at ~$2,000/month. Most wholesale apps are another $29–99/month subscription — per store, forever.

**PO Pilot is the one-time kit that puts the whole workflow inside the AI you already use.**

### What's inside ($49, one time)

1. **PO Pilot MCP server — full source (MIT).** TypeScript, 4 battle-tested tools: catalog validation with price-mismatch/case-pack/inventory flags, customer lookup, draft-order creation with PO-number dedupe + net terms + invoice send, and net-30 aging reports. Runs free forever via `npx po-pilot-mcp` in Claude Desktop, Claude Code, or Cursor. Your store token stays on your machine — no middleman, no per-order fees.
2. **Two done-for-you n8n templates (importable JSON).**
   - *PO Inbox → Draft Order:* IMAP watches your wholesale inbox, AI extracts the lines, Shopify lookup prices them, draft order created automatically. Fully hands-off intake.
   - *Monday Collections:* pulls overdue net-30 drafts and drafts reminder emails for your review.
3. **Loom walkthrough library (≈15 min total).** 60-second token setup, first PO end-to-end, the two n8n templates wired with your credentials, and the Monday collections routine.
4. **The Wholesale Desk prompt pack.** 10 copy-paste prompts: daily intake, trade-show batch entry, price-list audits, "who owes me" reports, polite dunning emails, reorder nudges to lapsed accounts.
5. **Hosted option, if you want zero local setup.** Free tier: 1,000 requests/mo on MCPize. Pro: $19/mo for 50,000 — only if you grow into it. The bundle you own either way.

### Who it's for
- US wholesale brands (apparel, food & bev, home goods, beauty, coffee roasters) doing 10–500 POs/month on a **regular Shopify plan**
- Ops managers drowning in draft orders and net-terms spreadsheets
- Freelancers/agencies: install it for clients in an afternoon, charge your own setup fee (the Upwork productized brief is included as a bonus)

### Why $49 and not $19/mo?
Because you should own your order desk. The source is MIT — modify it, self-host it, wire it to anything. If 15 hours a month of data entry is worth $300 at minimum wage, this pays for itself the first week. Subscriptions are for things that get better with updates; a workflow you own gets better with *your* updates.

### FAQ
- **Do I need Shopify Plus?** No — that's the point. Works on any plan with a free custom-app token.
- **Is my data safe?** The token grants only 4 scopes (read catalog/customers/drafts, write drafts). Nothing is stored or logged by the server. Draft orders don't touch inventory or payments until you send the invoice.
- **I'm not technical.** Watch the 60-second Loom, paste two values into Claude Desktop's config, done. The n8n templates are import-and-connect.
- **Will this keep working?** It uses Shopify's stable Admin GraphQL API (2026-10) and the Model Context Protocol — the same rails Shopify's own AI tools run on. Version pin included + update notes for buyers.
- **Refunds?** 14 days, no questions, Gumroad standard.

**Instant delivery. Free updates for life. Your order desk, owned.**

---

## Post-purchase upsell path (Gumroad offer settings)
- Order bump (+$30): "Done-with-you 30-min setup call (screen-share, we wire your store live)"
- Upsell to **Custom tier ($500–1,500)**: productized install via the Upwork brief (see `upwork-productized.md`) — for stores doing 500+ POs/mo or needing custom pricing rules/multi-store.

## Gumroad settings checklist
- [ ] Price $49, PWYW enabled above $49, coupon `EARLYPO` ($29, 50 uses, expires in 14 days)
- [ ] Files: `phase4/po-pilot-gumroad-bundle.zip` (source + both n8n templates + 10-prompt pack + Loom script), recorded Loom links/PDF, `upwork-productized.md` bonus
- [ ] Cover: 1280×720, big "20 min → 20 sec" + Shopify-green accent
- [ ] URL: `yourhandle.gumroad.com/l/po-pilot-bundle`
- [ ] Workflow: enable "Receive future updates" (update posts = re-engagement emails)
