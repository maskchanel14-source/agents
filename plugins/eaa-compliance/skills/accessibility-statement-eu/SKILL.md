---
name: accessibility-statement-eu
description: Use when producing the Accessibility Statement that the European Accessibility Act requires, when a client needs the statement in German, French, Spanish, Italian, or Dutch rather than translated English, when deciding what conformance status wording is defensible, or when the statement must name a national enforcement authority and a monitored feedback route.
---

# EU Accessibility Statement

The EAA requires more than a gesture toward accessibility. The statement is a mandatory deliverable with prescribed content, it commits the organisation to a response time, it names an enforcement authority, and **it must itself meet the standard it describes**.

It is the deliverable most businesses get wrong, precisely because it looks easy.

## When to Use

- Producing the Accessibility Statement the EAA requires
- A client needs the statement in German, French, Spanish, Italian, or Dutch
- Deciding what conformance-status wording is defensible
- Naming a national enforcement authority and escalation route
- Checking that the statement itself meets the standard it describes
- Reconciling a statement against an issued ACR or remediation plan

## Mandatory content

All nine, every time:

1. **Commitment**, and the name of the product, service, website, or application covered
2. **Technical standard** relied on — WCAG 2.1 Level AA, plus EN 301 549 where relevant
3. **Conformance status** — stated unambiguously as fully conformant, partially conformant, or not conformant
4. **Known limitations**, naming the responsible party where a third party or platform owns the barrier
5. **Measures taken** to ensure accessibility — testing cadence, remediation process, staff training
6. **Feedback mechanism** — a real, monitored contact route, plus a stated response commitment in business days
7. **Complaint and escalation route**, including the competent national authority, so an unsatisfied user knows where to go
8. **Dates** — statement date, last review, last assessment, and the assessment method described
9. **Compatibility** — the browsers and assistive technologies actually tested

## Conformance status wording

Three permitted states. Never round up, and never soften into ambiguity.

| Status | Use when |
|---|---|
| **Fully conformant** | Every criterion in scope was evaluated and none failed. Rare, and requires assistive-technology testing — not a scan. |
| **Partially conformant** | Some criteria fail or were not evaluated. **The normal, honest case** for almost every real website. List the failures and the unevaluated criteria. |
| **Not conformant** | The majority of relevant criteria fail, or the failures block core tasks. |

"Partially conformant" is not a weakness to be hidden. It is the accurate description of nearly every website in existence, and a statement that says so with a dated remediation plan is more credible — and more defensible — than one claiming full conformance on the strength of a green automated scan.

Banned from every statement: "strives to be", "as accessible as possible", "committed to continuous improvement" without a named cadence, and any status claim not traceable to an assessment.

## The statement must conform

A statement about accessibility that is not itself accessible is the most common self-inflicted wound in this space and an obvious target for a complaint. Verify the statement's own markup before publishing:

- `lang` attribute present and matching the document's actual language
- one `h1`; headings in logical order with no skipped levels
- sufficient contrast, no colour-only signalling
- descriptive link text — no "click here" or bare "more"
- a real `<title>` identifying the page
- landmarks present and labelled
- every interactive element keyboard-operable with a visible focus indicator
- no autoplaying media; no time limit on reading the statement
- tables, if any, with proper headers

Under EN 301 549 the statement is also a **clause 10 non-web document**. Publish HTML first at a stable, discoverable URL, linked from the footer of every page. Supply a PDF only if a buyer requires one, and it must be tagged and conforming — an untagged PDF statement is a documented conformance failure about conformance.

## Language

Load the matching template from `assets/` — `statement.en.md`, `statement.de.md`, `statement.fr.md`, `statement.es.md`, `statement.it.md`, or `statement.nl.md`.

Write in the register and legal phrasing of the market. Escalation conventions differ by country, and a machine-translated statement reads as one. The templates are **drafting scaffolds with placeholders**, not finished legal text: every one of them must be reviewed for the specific member state and, where the exposure is material, by counsel.

For a language with no template, say so explicitly and produce the English statement plus a marked translation brief. Do not guess at legal phrasing in a language you cannot verify — a wrong escalation route in a published statement is worse than an English-only statement with a clear note.

## Placeholders that must never be invented

Mark these `CLIENT MUST SUPPLY` and explain the consequence of shipping without them:

- the feedback contact — a monitored email address or form URL
- the response commitment in business days
- the national enforcement authority for the relevant member state
- the assessment date, assessor, and method
- the tested browsers and assistive technologies, with versions
- the organisation's legal name and the product version

**A statement with a dead contact route is worse than no statement**, because it creates an obligation the organisation is already failing and hands a complainant a documented breach. Say this to the client directly.

For the national authority, apply the same discipline as the scope assessment: take it from `references/details.md` or mark it `VERIFY` and name where to confirm. Never emit an authority name from memory.

## Consistency

If an ACR, remediation plan, or procurement answer bank exists, reconcile before presenting: version numbers, dates, criterion counts, conformance levels, and named limitations must agree across all of them.

A statement claiming full conformance next to an ACR full of "Partially Supports" is the failure mode that gets **both** documents discarded. Note in your response that you reconciled them and list what you changed.

See `references/details.md` for per-element drafting guidance, wording patterns that survive scrutiny versus phrases that create unintended liability, the national authority and escalation table with `VERIFY` discipline, the publication and discoverability checklist, third-party limitation wording, and the review-cadence model.
