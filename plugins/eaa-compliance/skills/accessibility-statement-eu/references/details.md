# EU Accessibility Statement — Reference Detail

Loaded on demand from `../SKILL.md`. Per-element drafting guidance, wording that survives scrutiny versus wording that creates liability, the national authority and escalation table, publication checklist, third-party limitation wording, and the review-cadence model.

## Per-element drafting guidance

### 1. Commitment and scope

Name the legal entity, not the trading name alone, and state precisely what the declaration covers — the domain, the application and its version, or the named service. A scope that says "our digital presence" is unauditable and invites a complaint about something you never assessed.

Where multiple products exist, issue one statement per product or clearly enumerate the covered products with their versions. Do not let one statement silently cover an application that was never tested.

### 2. Technical standard

Cite **WCAG 2.1 Level AA** as the assessment baseline. Add **EN 301 549** where the context is EU public procurement or where the buyer specified it. Cite the version you actually assessed against — a WCAG 2.0 assessment presented as 2.1 coverage is wrong on its face and misses five Level A criteria (2.1.4, 2.5.1, 2.5.2, 2.5.3, 2.5.4) and seven Level AA criteria (1.3.4, 1.3.5, 1.4.10, 1.4.11, 1.4.12, 1.4.13, 4.1.3).

### 3. Conformance status

Three states only: fully conformant, partially conformant, not conformant. There is no "mostly" and no "substantially".

**Fully conformant** requires that every criterion in scope was evaluated and none failed — which requires assistive-technology testing, not a scan. Claiming it on the strength of an automated result is the single most common overstatement in published statements and it is trivially falsifiable by any evaluator with a keyboard.

**Partially conformant** is the honest state for nearly every real website, and stating it with a dated remediation plan is more credible and more defensible than an inflated claim. Buyers and regulators read a partial-conformance statement with a real plan as competence; they read a full-conformance claim next to obvious defects as either ignorance or dishonesty, and neither is survivable.

**Not conformant** is the correct status when core tasks are blocked. Saying so, with a plan and dates, is materially better than being found out.

### 4. Known limitations

Name each limitation, its owner, and a date. Where a third party or platform owns the barrier, say so explicitly — and never imply control you do not have, because a conformance claim that silently includes a surface you cannot modify is the specific misrepresentation that causes a statement to be withdrawn.

Effective pattern:

> The payment step is served by {{PROVIDER}} within a hosted frame that we cannot modify. Keyboard operation within that frame is the provider's responsibility. We hold their current conformance report, dated {{DATE}}, and have recorded the following limitations from it: {{LIST}}. We review their report at each renewal.

Ineffective pattern — vague, unauditable, and reads as evasion:

> Some third-party content may not be accessible.

### 5. Measures taken

Be specific and falsifiable. "Regular testing" is not a measure. "Automated WCAG 2.1 A and AA scanning in CI on every release, with a fail-on-regression gate, plus a manual keyboard and NVDA pass on checkout and sign-in each release" is a measure, and it can be checked.

Include the remediation process and training. Procurement evaluators read this section as evidence of an ongoing programme rather than a one-off project, which is what the EAA's maintenance expectation is actually about.

### 6. Feedback mechanism

A monitored route, and a stated response commitment in business days. This is an obligation the statement creates, so the commitment must be one the organisation can actually meet — an unmet published commitment is a documented breach that a complainant can hand to an authority.

Ask the client who reads the inbox. If the answer is nobody, the commitment must not be published until the process exists. **A statement with a dead contact route is worse than no statement.**

Also state that alternative formats are available on request at no cost. This is a specific expectation under clause 12 of EN 301 549 and it is missing from most statements.

### 7. Escalation route

Name the competent national authority with a contact route, and cite the national instrument transposing Directive (EU) 2019/882. Where the member state offers a mediation or alternative-dispute route, or a consumer complaint body, include it.

**Never invent an authority name.** Take it from the table below or mark it `VERIFY` and name where to confirm. A wrong escalation route in a published statement actively misdirects a disabled user who is trying to exercise a right — it is the most harmful error available in this document.

### 8. Dates and method

Statement date, last review, last assessment, and the assessment method with the assessor. Distinguish self-evaluation from independent evaluation explicitly — a self-evaluation presented as an audit misleads the reader about its weight.

State the scope and the exclusions. An exclusion with a reason is professional; an unstated exclusion discovered later is a credibility failure.

### 9. Compatibility

List the browser, OS, and assistive-technology combinations actually tested, with versions. Then say what was not tested rather than implying general coverage.

## National authority and escalation

**Verify before publishing.** National transposition differs by member state, the responsible bodies differ, and several were still being designated or amended through 2025–2026. Take the authority from the current national instrument or from an official government page, record the source and date, and mark `VERIFY` where unconfirmed.

| State | Typical escalation body | Basis | Status |
|---|---|---|---|
| **Germany** | Competent market-surveillance authority under the BFSG; separately, the public-sector conciliation body (`Schlichtungsstelle`) | BFSG, transposing Directive (EU) 2019/882 | Market-surveillance route for private-sector services; confirm the competent Land authority `VERIFY` |
| **France** | DGCCRF for enforcement; the Défenseur des droits for individual discrimination complaints | Code de la consommation as amended; RGAA governs the public sector | Confirm the current competent service before citing `VERIFY` |
| **Ireland** | National Disability Authority and designated officers | S.I. No. 636 of 2023 | Confirm the complaint route published by the NDA `VERIFY` |
| **Italy** | AGID — Agenzia per l'Italia Digitale | Legislative decree transposing the directive | AGID handles reports and may allow a cure period before fines `VERIFY` |
| **Spain** | The competent authority, which varies by autonomous community | National transposition (Real Decreto) | Regional variation — establish the community before naming a body `VERIFY` |
| **Netherlands** | The Dutch market-surveillance authority for the EAA; separately, the equal-treatment body for discrimination complaints | Dutch transposing act | Confirm which body is competent for a private-sector service `VERIFY` |
| **Other** | — | — | Mark `VERIFY`; do not estimate |

Always cite the **national instrument** alongside the authority. A statement that names a body without a legal basis reads as informal; a statement that cites the instrument reads as prepared.

## Publication and discoverability checklist

- [ ] Published as **HTML** at a stable URL — not PDF-only
- [ ] Linked from the **footer of every page**, with descriptive link text ("Accessibility statement", not "Accessibility")
- [ ] Reachable without an account, and not behind a cookie-consent wall
- [ ] `lang` attribute matches the document's actual language
- [ ] One `h1`; headings in logical order with no skipped levels
- [ ] Sufficient contrast; no colour-only signalling
- [ ] Descriptive link text throughout; no "click here"
- [ ] Real `<title>` identifying the page
- [ ] Landmarks present and labelled
- [ ] Keyboard-operable throughout, with a visible focus indicator
- [ ] No autoplaying media; no time limit on reading
- [ ] Tables, if any, with proper header cells
- [ ] Any PDF supplied alongside is tagged, language-set, and conforming
- [ ] Every `{{PLACEHOLDER}}` resolved — no template artefacts in production
- [ ] Every `CLIENT MUST SUPPLY` gap closed before publication

The last two are the most common failures in shipped statements. A published template placeholder is indefensible and it is visible to anyone who looks.

Under EN 301 549 the statement is a **clause 10 non-web document** — publishing it as an untagged PDF is a documented conformance failure, about conformance.

## Review cadence

The statement is a living document. Review and re-date it on:

- every material release that changes the customer journeys
- every change of third-party provider touching a covered journey
- any change to the assessed version of the product
- at minimum annually, even where nothing changed — and record that the review happened
- immediately after any remediation that changes a limitation listed in the statement

An out-of-date statement that lists limitations which have been fixed understates the organisation's position; one that claims conformance which has since regressed overstates it. Both are worse than a current statement saying something unfavourable.

## Cross-document consistency

Where an ACR, remediation plan, or procurement answer bank exists, reconcile before publishing:

- product name and **version** identical across all documents
- assessment and statement dates consistent and non-contradictory
- conformance levels in the ACR consistent with the status claimed in the statement
- named limitations identical in wording and owner
- criterion counts consistent — 30 Level A plus 20 Level AA equals 50 for WCAG 2.1 A and AA

A statement claiming full conformance beside an ACR full of "Partially Supports" gets **both** documents discarded. Record that you reconciled them and list what changed.
