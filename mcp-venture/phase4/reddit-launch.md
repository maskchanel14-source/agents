# Reddit Launch Kit

*Skill: marketing-campaign (affan). Primary: r/shopify (~1M members, tools allowed with transparency; no link-dropping — links in comments only if asked). Secondary: r/smallbusiness, r/ecommerce, r/n8n (automation angle), r/ClaudeAI + r/mcp (builder angle). Timing: Tue–Thu, 8–11am ET. Account must have history in the sub — if yours doesn't, spend 3 days giving genuine answers in r/shopify threads first (the Oct-13 community.shopify.com thread 697417 and its Reddit mirrors are your warm entry).*

---

## Primary post — r/shopify

**Title:**
We cut wholesale order entry from ~15 min to ~30 sec per PO (no Plus, no $99/mo app) — here's the exact workflow, steal it even if you don't use my tool

**Body:**

I run ops for a small wholesale brand and for two years my mornings started the same way: open the orders@ inbox, find yesterday's POs — a PDF from one retailer, an Excel from another, one literal photo of a handwritten list — and retype every line into a Shopify draft order. Ten to fifteen minutes each. Check the wholesale price against a spreadsheet. Pray nobody ordered 25 units of something that only ships by the 12-pack. Then a second spreadsheet for who's paid their net-30.

Shopify Plus B2B would fix parts of this for ~$2,000/month. The app-store options are $29–99/month per store. Both fine if you're big. Neither made sense for us.

What actually changed for us: letting AI do the reading and typing, but **never** the deciding. The workflow, tool-agnostic:

1. **The AI reads the PO** (Claude/ChatGPT can read the PDF or the pasted email — extraction is genuinely solved, don't pay for it).
2. **Every line gets validated against the live catalog before anything is created**: exact SKU match, current price vs the PO's stated price, on-hand inventory, case-pack math. Mismatch = flag, not a silent order. This step is the whole game — it's what turns "AI made me a wrong order" into "AI caught that Dana typed 25 instead of 24."
3. **Draft order created with the PO number as a tag** — and deduped, so forwarding the same email twice can't double-key it. Net-30 goes in the note.
4. **Monday: list all drafts still unpaid past terms**, draft reminder emails. Spreadsheet #2 is dead.

Disclosure because it matters: I got tired of doing this by hand and built the piece that does steps 2–4 as a free open-source MCP server (po-pilot-mcp — that's the protocol Claude's integrations use), plus n8n templates for the fully hands-off version. It's MIT, the token it needs has 4 read/write-drafts scopes only, and there's a hosted free tier if you don't want to run anything locally. Happy to share links if mods allow / in comments if people want them — genuinely mostly here because I want to know:

- What breaks in YOUR PO intake that I haven't hit? (Per-customer price lists are next on my list)
- How are you handling the "buyer emails a photo of a handwritten list" case? Ours just… reads it. It's unsettling.

If you're on Plus already or happy with an app, ignore me — but if your order desk is still a human being with two spreadsheets, the pattern above works with any AI + any glue. Ask me anything about the setup.

**First comment (post immediately):**
Links since people asked by DM: the open-source server is `po-pilot-mcp` on npm/GitHub (MIT), setup guide is in the README — 60 seconds, needs a free Shopify custom-app token. The full bundle with the two n8n templates + Looms + prompt pack is $49 on Gumroad if you want the done-for-you version: [link]. I answer every reply here.

**Comment playbook:**
- Price objection → "the free self-host path is the real product; $49 is for people who want the templates + Looms, $19/mo hosted only if you outgrow 1,000 requests (≈100 POs/mo)."
- "Does it work with per-customer pricing?" → "not yet — it's #1 on the roadmap; today it flags the mismatch and you confirm the agreed price. Would love your format (price list CSV? tags?)" ← this is free product research, take every rep.
- Skeptic ("AI will mess up orders") → agree hard: "that's why it validates against the live catalog and refuses to create on ambiguity — drafts don't touch inventory or money until you send the invoice."
- Competitor app mentioned (LevelOps etc.) → be generous: "great app, use it if you want zero-setup in-Shopify; mine's for people who live in Claude/n8n and want to own the code."
- Mod removal → repost to r/smallbusiness + r/ecommerce with the same body; keep r/ClaudeAI builder-angle version ("I built an MCP server that…") for the dev crowd.

---

## Variant titles (other subs)

- **r/smallbusiness:** "My wholesale order entry took 5 hrs/day at peak. An AI workflow cut it to ~30 sec/order — breakdown inside (tool is free/open source)"
- **r/ecommerce:** "Shopify wholesale brands: your PO intake is the last manual thing in your stack. Here's the validation-first pattern that fixed ours"
- **r/n8n:** "PO email → AI extraction → Shopify draft order with price/case-pack validation — sharing both templates (IMAP intake + Monday net-30 chaser)"
- **r/ClaudeAI / r/mcp:** "I built an MCP server for the workflow Shopify's official MCPs don't cover: merchant-side wholesale PO intake (match_catalog_items → create_draft_order with PO dedupe). AMA + open source"
- **r/wholesalerealestate:** "Wholesale order desks still run on retyping emailed POs. We automated ours with AI + validation — the pattern applies to any back-office doc intake (supply orders, vendor invoices)"

---

## Launch-day sequence
1. **T-3 days:** 5 genuine helpful comments in r/shopify wholesale threads (including answering intake questions in threads like "Best Way to Enter Wholesale Orders into Shopify").
2. **T-day 08:30 ET:** primary post r/shopify + first comment with links.
3. **T+2h:** r/n8n variant (different body angle, never crosspost identical text).
4. **T+1 day:** r/ClaudeAI builder post; reply to every comment on all posts within 2h for the first 12h.
5. **T+3 days:** r/smallbusiness + r/ecommerce variants.
6. Track: post upvotes/comments → GitHub stars → npm installs (`npm-stat`) → MCPize free-tier signups → Gumroad sales. Screenshot the r/shopify thread for the Gumroad listing's social-proof section (with permission).
