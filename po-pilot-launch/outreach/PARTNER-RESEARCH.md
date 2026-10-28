# Partner outreach: research behind the first send

Written 29 October 2026. Covers what was researched, what was concluded, who was
contacted, and what the numbers actually say.

---

## 1. The decision this research changed

The first instinct was to email Shopify design agencies. That is the wrong buyer.
A design-and-build shop hands the store back at launch and never touches a
purchase order again. Someone who does not own the inventory workflow has no
reason to pay for an inventory audit.

The buyer is the person who has to reconcile supplier invoices at month end and
who cannot, because the purchase order history went away with Stocky. That means
ecommerce bookkeepers and ecommerce accountants, not web studios.

Second correction: the pitch is not "hire me". A bookkeeper with 40 clients will
not hand a stranger their client list. The pitch is a fixed-fee subcontract behind
their existing engagement, where they keep the client, keep the relationship, and
bill the output as their own work. That is a decision they can make in one reply
without exposing anything.

## 2. Market facts used in every email

All sourced, none inferred.

| Fact | Source |
| --- | --- |
| Stocky was fully retired on 31 August 2026 | Shopify Help Center, migrating from Stocky |
| Read-only export stays open "for at least 90 days" after that date, with no published end date, so the earliest possible close is 29 November 2026 | Same page |
| Suppliers were never exportable from Stocky | Same page |
| Historical purchase orders and stocktakes do not transfer into Shopify's native inventory tools | Shopify Help Center; ApparelMagic's own FAQ says the same |
| Shopify's native tools track quantity well but not average cost, landed cost, or detailed receiving history | Woodard Report, 23 July 2026 (Rachel Dauchy) |
| Stocky's API stopped on 31 August 2026 | Shopify Help Center |

The 90-day line matters because it is the only claim on the audit page with a
deadline attached, and it is the one a bookkeeper can verify in thirty seconds.

## 3. What the market already sells, and the gap

Replacement apps are crowded and cheap: Stockful from $19.99/month, Monocle from
$47, Prediko from $49, ReplenishRadar at $99, Inventory Planner, Cin7 Core, inFlow.
Every one of them sells the same thing, which is a new system to run from now
onward. Not one of them rebuilds the history that already existed, because that is
labour, not software. Bookkeep is the only vendor that clearly built a Stocky
migration path, and it brings merchants onto Bookkeep.

That leaves the actual gap: a one-time, fixed-scope job that turns a dead export
into a usable cost and supplier record. It is a service, and apps structurally
cannot sell it.

## 4. Price anchors

Charging $250 for the audit looked low until it was benchmarked.

- Shopify consulting: diagnostic audits $1,000 to $10,000, hourly $100 to $500 (shopexperts.com, 2026)
- Independent supply chain specialists: $150 to $400 per hour (Onflair, 2026)
- Shopify freelancers: $50 to $150 per hour (markcmo.com, 2026)

At $250 for a scoped deliverables list, the audit reads as a cheap first step
rather than a gamble. It also means there is real headroom later. Do not raise it
before there are two clients willing to be quoted.

## 5. Who was contacted, and why each one

Seven recipients. Each has a public address published on their own site, a live MX
record on the domain, and a specific reason that only applies to them.

| # | Firm | Address | Why this one |
| --- | --- | --- | --- |
| 1 | ConnectBooks (Spring Valley, NY) | info@connectbooks.com | Their three-way match glossary has a section called "the ecommerce gap: invoices with no purchase order". They already teach the exact problem the service solves. |
| 2 | Social Commerce Accountants (Sawbridgeworth, UK) | contact@socialcommerceaccountants.com | Sam Hoye's 2026 hiring guide asks whether an ecommerce accountant understands how inventory apps like Stocky talk to finance apps. Since 31 August the answer is that they don't. |
| 3 | Think Accounting (Brampton, ON) | info@thinkaccounting.ca | Their ecommerce page promises inventory that ties to CIN7-class systems with COGS, units and landed cost. Landed cost needs purchase order lines that no longer exist. |
| 4 | Bookkeeper Superhero (UK) | hello@bookkeepersuperhero.co.uk | Fixed-price packages, Xero, A2X and Dext, explicitly no hourly billing and no calls. A Stocky cleanup is the one job that cannot fit a fixed package, so it gets quoted and subcontracted or it gets dropped. |
| 5 | Fox Clever Bookkeeping (Falmouth, UK) | hello@foxcleverbookkeeping.com | Shopify, Amazon, Etsy, eBay and TikTok under one roof, which means margin per SKU only holds up if unit cost is right. |
| 6 | Rocket Bookkeeper (New York, NY) | contact@rocketbookkeeper.com | Ecommerce bookkeeping with inventory tracking plus AP/AR support in the same package. Accounts payable is where the missing POs surface. |
| 7 | EcomBalance (Denver, CO) | support@ecombalance.com | Targets Shopify stores above $250K with accrual COGS. Accrual costing needs receipts and PO lines, and they stopped being in Shopify. |

Considered and rejected:

- Sunrise Integration (NJ): case studies name DHL, Disney, Live Nation. Enterprise, wrong size, and the audit is below their floor.
- Diff Agency: WPP-owned, contact form only, no published address.
- Management One: runs its own Stocky migration programme. Would read the offer as a competitor pitch.
- PandaCodeGen: publishes a Stocky checklist, but is a website migration shop with no inventory clients.
- Finaloop, Bookkeep, Salorworks, Endlesscommerce: they sell the replacement product or the content that ranks for it. Not buyers.
- Growthy, Seller Bookkeeping: no usable public address (form-only, or no MX record).

## 6. What was sent

Subject lines, all lowercase and specific, no colon-and-promise construction:

1. `the three-way match post, and the invoices with no PO`
2. `the Stocky question in your 2026 hiring guide`
3. `landed cost, with no PO left to land it against`
4. `what happens when a client's Stocky cleanup arrives`
5. `five channels, one cost per unit that's gone`
6. `AP support, when the PO history went with Stocky`
7. `COGS accuracy above $250K, after the export window`

Every email carries the same four blocks in a different order and wording: the
specific thing about them, the repair work described concretely, the 29 November
deadline with its source, and one bounded free offer (one vendor set, three days,
no client name needed).

Each has its own tracking link, `?src=partner-<firm>`, so referral traffic is
attributable in Vercel Analytics rather than guessed at.

## 7. What the numbers honestly predict

The account has sent 30 cold emails before, on 17 October, and received zero human
replies. One bounce, from a full mailbox. That is the only real base rate
available, and it is 0 for 30 on a different audience.

Well-targeted cold email to small firms usually lands between 3 and 10 percent
reply. Seven sends at that rate is 0.2 to 0.7 replies. Expect nothing from this
batch on its own.

Which means the batch is a test of three things, not a revenue event:

1. Does the white-label framing get replies at all
2. Does any reply turn into a paid job
3. Which of the seven hooks is worth copying into the next hundred

The path to $1,500 is arithmetic, not luck. Two $750 engagements, or three at $450.
At a 5 percent reply rate and a 20 percent close rate on replies, that is roughly
200 to 300 sends to land two. Seven is the probe. The next step is volume, and it
needs a wider pool than seven firms.

## 8. Follow-up

- Day 3: reply in the same thread, one new piece of information (the MOQ units
  versus minimum order value trap), no repeat of the pitch.
- Day 7: deadline only. The window's earliest close, one line, no ask.
- Then stop. No fourth email.

If anyone says yes, the order is fixed: confirm scope, price and date in writing
first, then ask for the files. Never promise a delivery date before seeing the
export, because the whole cost of the job is set by how clean that export is.

## 9. Risks worth naming

- **Sender reputation.** These go from a personal Gmail with no display name set.
  Before the next batch, set the display name to "Galeka, Small Signal Studio" in
  Gmail settings. It cannot be done through the API.
- **Rate limits.** The 17 October run hit Gmail's sending cap around 09:00 PDT
  after four consecutive failures. Keep batches under ten and space them out.
- **Offshore framing.** The emails state UTC+7 openly. That is deliberate: for a
  white-label partner, the timezone is the product, since work lands overnight.
  If a reply reads it as a discount signal instead, correct it in one line rather
  than arguing.
- **Nobody has reviewed the output yet.** The offer is a free vendor set. That is
  affordable now and will not be once three people take it up. Cap it at three.
