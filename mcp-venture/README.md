# mcp-venture — PO Pilot: research → build → launch

Zero-cost MCP product sprint (Surabaya → US wholesale Shopify brands). Every phase ran on skills from the owner's repos:

| Phase | Artifact | Skills invoked (path) |
|---|---|---|
| 0 Inventory | (chat deliverable) | scanned `agents/plugins/*/skills/` (187), `affan/.agents/skills/` + `affan/skills/` (~250), `obra/skills/` |
| 1 Deep research | [phase1-research-report.md](./phase1-research-report.md) | `deep-research` (affan), `market-research` (affan) |
| 2 Brainstorm + score | [phase2-brainstorm.md](./phase2-brainstorm.md) | `brainstorming` (obra), `product-lens` (affan), `before-you-build` (agents) |
| 3 MVP build | [po-pilot-mcp/](./po-pilot-mcp/) | `mcp-server-patterns` (affan), `shopify-product-operations` (agents) |
| 4 Sales packaging | [phase4/](./phase4/) | `marketing-campaign` (affan), `opensource-pipeline` (affan) — no gumroad skill exists |

## The product

**PO Pilot** (`po-pilot-mcp`) — MCP server turning emailed wholesale POs into *validated* Shopify draft orders: live SKU matching, price-mismatch/case-pack/inventory flags, PO dedupe, net-15/30/60 terms, invoice send, net-terms aging. Merchant-side workflow the official buyer-side UCP servers can't touch; zero MCP competition found (2026-10-25).

## Definition of Done — run these

```bash
# 1) Publish the server (npm account: maskchanel14; name verified available 2026-10-25)
cd mcp-venture/po-pilot-mcp
npm ci && npm run build && npm run smoke
npm publish --access public

# 2) Deploy hosted + metered billing (free 1,000 req/mo, Pro $19 / 50K — see mcpize.yaml)
npm i -g mcpize   # or per mcpize.com docs
mcpize deploy

# 3) Gumroad $49 bundle — upload: source zip, n8n templates (phase4/n8n-templates/*.json),
#    prompt pack + Loom script are in phase4/po-pilot-gumroad-bundle.zip; listing = phase4/gumroad-listing.md

# 4) Upwork productized project $500/$950/$1,500 — copy = phase4/upwork-productized.md
# 5) Reddit launch (r/shopify first) — copy + sequence = phase4/reddit-launch.md
```

## Status

- [x] MVP built, typechecked (tsc strict), smoke-tested: handshake, 4 tools listed, unconfigured→setup-guide, bad-GID guard, network-failure → structured errors (server never crashed)
- [ ] npm publish (owner) · [ ] mcpize deploy (owner) · [ ] Gumroad live (owner) · [ ] Upwork listing (owner) · [ ] Reddit launch (owner)
- [x] Offline CI workflow + `npm run smoke` added; `npm pack --dry-run` verified the npm artifact contains only the built runtime, README, and license.
- [x] Gumroad upload zip generated at `phase4/po-pilot-gumroad-bundle.zip`; rebuild with `python3 package-bundle.py` after edits. Includes source, both n8n templates, prompt pack, and Loom script; excludes dependencies/build outputs/secrets.
- [ ] Optional discovery setup: create the dedicated GitHub repo `maskchanel14-source/po-pilot-mcp` from this package (package.json already points there), then submit to Smithery + Glama for backlinks.
