---
name: eaa-legal-scope
description: Use when determining whether Directive (EU) 2019/882 — the European Accessibility Act — applies to a business, product, or service, when applying the Article 4(5) microenterprise exemption, when identifying the applicable member-state transposition and enforcement authority, or when assessing penalty and market-exclusion exposure for selling into the EU.
---

# EAA Legal Scope

Establishes whether an accessibility obligation actually exists, under whose national law, and what ignoring it costs. Run this before any technical audit — auditing a site that is exempt wastes the client's budget, and skipping scope on a site that is covered leaves them exposed.

## When to Use

- A business asks "does the European Accessibility Act apply to us?"
- Before scoping or quoting any remediation work — auditing an exempt site wastes the budget
- A client claims the microenterprise exemption, or believes they have until 2030
- A buyer's questionnaire asks whether the vendor is "EAA compliant"
- Assessing the risk of selling a product or service into the EU from outside it
- An enforcement letter, formal notice, or complaint has arrived

## The instrument

Directive (EU) 2019/882 on the accessibility requirements for products and services. It is a **directive**, so it operates through national transposition: the law that binds a given business is the law of the member state where it is established or where it places products and services on the market. General application date: **28 June 2025**.

The harmonised European standard is **EN 301 549**. In practice the web baseline everyone audits and reports against is **WCAG 2.1 Level AA**, which EN 301 549 incorporates for web and non-web software.

## Decision sequence

Work in this order. Each step can end the analysis.

### 1. Is there an EU consumer on the other end?

| Situation | Conclusion |
|---|---|
| Sells to EU consumers, established in the EU | In scope |
| Sells to EU consumers, established outside the EU | **In scope** — the law follows the market, not the headquarters |
| Genuine B2B with verified business-only accounts | Generally out of scope — no consumer contract |
| Nominally B2B but anyone can register and pay | **Likely in scope** — a private buyer can conclude a consumer contract |
| Sells only outside the EU | Out of scope for the EAA |

"Establishment outside the EU" is not a defence. Fulfilment to EU addresses, acceptance of payment from EU customers, or marketing directed at EU consumers establishes market presence. Record the specific facts, because this is what counsel interrogates first.

### 2. Is it a covered product or service?

**Products:** general-purpose computers and operating systems; self-service terminals (ATMs, ticketing, check-in); smartphones and other two-way terminal devices; TV equipment related to digital television services.

**Services:** electronic communications; elements of passenger transport (air, bus, rail, waterborne, urban/suburban/regional); consumer banking and financial services; software and services for access to audio-visual media; **e-commerce** — services providing access to goods and services via websites or mobile applications, concluded at a distance, on a consumer contract.

The e-commerce test is not "are you a shop". It is **can a consumer conclude a contract with you at a distance through your website or app.** A booking form leading to a paid service counts. A brochure site with no transactional path usually does not.

### 3. Does the Article 4(5) microenterprise exemption apply?

Exempts **microenterprises that provide services**:

- **fewer than 10 persons** — strict, must be met
- **annual turnover ≤ €2 million OR balance sheet total ≤ €2 million** — either figure suffices

Three misreadings to correct explicitly:

1. The exemption attaches to **service providers**. Manufacturers, importers, and authorised representatives placing **products** on the market are not covered by it — a microenterprise making a covered product is still in scope.
2. Headcount follows the EU enterprise-size recommendation, counting annual work units and including categories of staff a small business often omits. Ask how the number was counted before accepting anything under 10.
3. Where a business relies on disproportionate burden, the justification must be **documented formally** and can be challenged. Keep the analysis on file even when exempt.

When the exemption does apply, say so plainly. Telling a client they do not need to spend is what earns the next engagement.

### 4. Which member state, which authority, what exposure?

Per relevant state, establish: the national transposing instrument and citation, the enforcement or market-surveillance authority, the penalty ceiling and how it scales, any pre-enforcement cure window, and whether consumers or disability organisations can act directly.

**Penalty figures, authority names, and deadlines must come from `references/details.md` or be marked `VERIFY`.** Never state one from memory. Directive-level penalties are set by each member state and they differ by an order of magnitude between countries, so a remembered number is very likely wrong.

### 5. Correct the 2030 misconception

Whenever a client believes they have until 2030, identify which clause they are misreading:

- Article 32 lets **service providers** keep using products they already used before 28 June 2025 — payment terminals, typically — until **28 June 2030**
- Service contracts agreed before 28 June 2025 may run to expiry, for **no more than five years**

**Neither clause pauses the requirements for a website or mobile application.** For a web property the deadline has passed and the gap is an active liability, not a future one.

## The non-financial exposure

Usually larger than the fine, and routinely omitted from risk assessments:

- **Remedial orders** — penalties come with corrective action; a court can order fixes on a deadline with daily penalties for delay
- **Market exclusion** — the authority can restrict or withdraw a non-compliant product or service from the EU market
- **Private and representative actions** — every member state must let consumers take a case to a court or regulator, and disability organisations may join or bring them
- **Procurement disqualification** — conformance documentation is now a standard RFP requirement, so non-compliance silently removes a business from deals it never learns it lost
- **Reputational publication** — some regimes allow or require public naming

## The precedent that ends the argument

In July 2025 a French disability association sent formal notices to four grocery chains. On **4 June 2026** the court in Caen ordered Carrefour to make its website and application accessible within six months, with daily penalties for delay. Carrefour argued it already met **71%** of the French accessibility criteria. The court held the store had to be **fully** accessible.

Partial compliance is not a safe harbour. Use this whenever a client believes a mostly-accessible site is defensible.

## Output

Write `eaa-scope-assessment.md`: determination (`IN SCOPE` / `OUT OF SCOPE` / `EXEMPT (microenterprise services)` / `INDETERMINATE`) with rationale · facts relied on · applicable law per state with `VERIFY` markers · exposure · exemption analysis element by element · assumptions and gaps phrased as questions · one recommended next step · dated sources.

Close with the standing limitation: a working technical and regulatory assessment produced by software tooling, **not legal advice**; a qualified lawyer in each relevant member state should confirm it before reliance in a filing, a procurement response, or a dispute.

See `references/details.md` for the member-state jurisdiction table, national instrument citations, penalty ranges with sourcing discipline, the disproportionate-burden documentation pattern, sector-specific edge cases, and the questions to ask a client who cannot answer the headcount and financial tests.
