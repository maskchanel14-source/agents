# EAA Legal Scope — Reference Detail

Loaded on demand from `../SKILL.md`. Contains the member-state table, the disproportionate-burden documentation pattern, sector edge cases, and the client interview.

## Sourcing discipline (read this first)

Directive (EU) 2019/882 sets the floor. **Penalties, authority names, cure windows, and citation numbers are set by each member state's transposing instrument** and they differ by an order of magnitude between countries. National implementations were still being finalised, amended, and litigated through 2025 and 2026.

Therefore, for every jurisdiction-specific figure in a client-facing document:

1. Take the figure from the table below **and** record its source type and date.
2. Where the table says `VERIFY`, mark the line `VERIFY` in the deliverable and name the authority to check with. Do not fill the gap with a plausible number.
3. Where the client's exposure is material — a real enforcement risk, a procurement deadline, a dispute — advise confirmation against the **official national instrument** and, where the sum at risk justifies it, review by a qualified lawyer in that state.

A wrong fine figure in a client document is worse than a marked gap. The gap gets filled in an afternoon; the fabrication is discovered at the worst possible moment and it discredits every other number in the document.

Figures below are drawn from practitioner guidance and national implementation reporting as at mid-2026. Treat them as **indicative and requiring confirmation**, not as a substitute for the instrument.

## Member-state table

| State | Transposing instrument | Enforcement body | Reported maximum penalty | Notes |
|---|---|---|---|---|
| **Germany** | Barrierefreiheitsstärkungsgesetz (BFSG); penalty provision at § 37 | Marktüberwachung / competent state authority | up to **€100,000** for the most serious breaches; up to €10,000 for others | Two-tier structure — cite the tier, not just the ceiling `VERIFY` |
| **France** | Code de la consommation as amended for the EAA (ordonnance and decree transposing the directive); RGAA governs the public sector separately | DGCCRF; court-ordered remediation | reported range **€5,000 – €250,000**, plus potential public disclosure of non-compliance | **Carrefour precedent, court in Caen, 4 June 2026**: six months to make website and app accessible, daily penalties for delay, after the defendant argued 71% conformance `VERIFY` figures against the current code |
| **Ireland** | S.I. No. 636 of 2023 — European Union (Accessibility Requirements for Products and Services) Regulations 2023 | National Disability Authority / designated officers | up to **€60,000** and/or **18 months' imprisonment** on indictment; class A fine and/or 6 months on summary conviction | Criminal exposure on indictment — unusual in this space and worth flagging to a client `VERIFY` |
| **Italy** | Legislative decree transposing the directive (D.Lgs. 82/2022 framework) | **AGID** (Agenzia per l'Italia Digitale) | up to **€50,000** per violation reported; AGID may give **30 days** to remedy a reported issue before inspection and administrative fines | Cure window is the operative feature — a complaint starts a 30-day clock `VERIFY` |
| **Spain** | National transposition (Real Decreto) | reported as varying by regional authority | reported **€5,000 – €300,000** depending on severity | Regional variation means the answer differs by autonomous community `VERIFY` |
| **Netherlands** | Dutch transposing act | Dutch market surveillance authority | reported up to **€4.3 million or 4% of annual revenue** | Highest reported ceiling in the EU for this instrument — the figure is extraordinary and **must** be verified against the official act before it is quoted to a client `VERIFY` |
| **Other member states** | — | — | — | Mark `VERIFY`, name the state's market-surveillance or disability-rights body, and do not estimate |

Cross-cutting: some practitioner sources describe a GDPR-style ceiling of **up to 4% of global annual turnover** for the most serious cases, by analogy with the proportionality principle in the directive. This is **not** uniform across member states. Do not present 4% as a general rule; present the specific state's figure or mark `VERIFY`.

## Beyond fines: the exposure that actually changes behaviour

Clients fixate on the penalty ceiling. In practice the following do more damage:

**Remedial orders.** The directive requires penalties to come with corrective action. A court can order fixes on a deadline with **daily penalties for delay** — the Carrefour outcome. The daily-penalty structure converts a one-off cost into an escalating one, which is what makes a missed deadline expensive rather than merely embarrassing.

**Market exclusion.** The authority can restrict or withdraw a non-compliant product or service from the EU market, and can suspend business operations until compliance. For a business whose EU revenue is meaningful, this is existential and dwarfs any fine.

**Private and representative actions.** Every member state must permit consumers to bring a case to a court or to a regulator. Disability organisations may join or bring those cases — which is exactly how the French grocery-chain notices began. A single organised complainant can start enforcement against a business that was never on any regulator's radar.

**Procurement disqualification.** Conformance documentation is now a standard RFP, security-questionnaire, and vendor-assessment requirement. A vendor without an ACR is not rejected — it is **never shortlisted**, and it does not learn that it lost. This is the most common and least visible cost of non-compliance, and it is the one most likely to be felt by a small software vendor before any regulator notices.

**Reputational publication.** Some regimes allow or require public naming of non-compliance. Practitioners consistently rate this worse than the fine.

**Delisting.** Non-compliant digital products may be removed from app marketplaces, which is a distribution loss with no appeal process comparable to a regulatory one.

## Article 32 transition — what it does and does not cover

The transition is narrower than clients assume. It permits:

- **service providers** to continue using **products** they already used before 28 June 2025 — the canonical example is a payment terminal installed in 2023 — until **28 June 2030**
- **service contracts** agreed before 28 June 2025 to run until expiry, for **no more than five years**

It does **not** pause any requirement applying to a website or a mobile application. There is no grace period for a web property: the deadline has passed and any gap is an active liability.

When a client says "I thought we had until 2030", ask what they are relying on. If it is a website, correct the belief and show them which clause they misread. If it is genuinely a pre-2025 payment terminal, the transition may apply and you should say so.

## Disproportionate burden — the documentation pattern

Where a business relies on disproportionate burden, the justification must be **documented formally** and it can be challenged. It is not a self-certification that ends the question.

Produce `eaa-disproportionate-burden.md` with:

1. **The requirement** — the specific accessibility requirement claimed to be disproportionate, cited to the standard
2. **The organisation** — size, turnover, headcount and how counted, market, and the specific product or service
3. **The burden assessed** — cost, technical feasibility, organisational capacity. Quantified, with the basis of the estimate stated. "It would be expensive" is not an assessment.
4. **Alternatives considered** — cheaper partial measures, phased delivery, a different implementation. A justification that did not consider alternatives is weak and reads as predetermined.
5. **What was done anyway** — the accessible portion delivered. A burden claim alongside zero effort is not credible.
6. **Review date** — when the assessment will be revisited. Circumstances change, and a justification with no review date is a standing liability.
7. **Signature and date** — who in the organisation owns this assertion.

Advise that the document be retained and be producible on demand, and that a burden claim which is later found unsupported is materially worse than never having made one.

Note the interaction with the microenterprise exemption: the exemption is a **status** test under Article 4(5); disproportionate burden is a **per-requirement** assessment. They are different instruments and a business may rely on one, both, or neither. Do not conflate them in a client document.

## Sector and product edge cases

**Booking and reservation flows.** A site that sells nothing but lets a consumer book a paid service at a distance is generally within the e-commerce category. "We don't take payment online" is not automatically a defence where the contract is concluded at a distance.

**B2B with an open registration path.** If any person can register and pay without verified business status, a consumer contract is possible and the offering is likely in scope. The fix is either to genuinely restrict registration to verified businesses or to accept scope.

**Manufacturers and importers.** The microenterprise service exemption does not reach them. A two-person company importing a covered product into the EU is in scope.

**Third-party marketplaces.** A merchant selling through a marketplace is generally not responsible for the marketplace's own conformance, but is responsible for the content and flows it supplies into it. Establish the boundary in writing before either party makes a conformance claim about the other's surface.

**Mobile applications.** Covered alongside websites. A business that audited its website and stopped has assessed half its exposure.

**Internal tools and employee-facing software.** Generally outside the consumer-facing scope of the EAA, but frequently inside other obligations — national public-sector accessibility law, Section 508 for US federal work, or the client's own procurement commitments. Say which regime applies rather than concluding "not covered".

**Non-EU markets.** Out of scope for the EAA, but the US ADA Title III exposure is separate and live: reported US web-accessibility litigation exceeded **4,500 filings in 2024, up roughly 14% year on year**. A business told it is out of EAA scope should still be told what its US exposure looks like.

## Client interview — the questions that decide scope

Ask these before analysing. Clients cannot self-assess reliably, because the questions are not the ones they expect.

1. What exactly do you sell — a product, a service, or both?
2. Can a customer complete a purchase, booking, or paid registration on your website or app, end to end?
3. Which countries do you ship to, bill in, or advertise to?
4. Where is the business legally established, and where are the entities that hold the contracts?
5. How many people work for you — and **how did you count them**? Full-time, part-time, contractors, seasonal, owners?
6. What was last year's turnover, and what is the balance sheet total? Which is lower?
7. Do you manufacture or import any hardware, or only provide services?
8. Do you sell to other businesses, and if so **can an individual register and pay without verification**?
9. Have you received a complaint, a formal notice, a procurement request for conformance documentation, or a lawyer's letter?
10. Do you have a mobile application as well as a website?
11. Which third parties render parts of the customer journey — payment, checkout, chat, reviews, cookie consent, booking?
12. Has anyone previously assessed accessibility, and what did they produce?

Question 5 is the one that most often changes the answer, because headcount is counted inconsistently and the test is strict. Question 8 catches the nominally-B2B business that is actually in scope. Question 11 establishes the ownership boundary that will determine what can be fixed and what must be documented as a limitation.
