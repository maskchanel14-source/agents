---
name: en-301-549-mapping
description: Use when mapping WCAG 2.1 or 2.2 success criteria to EN 301 549 clauses, when producing the EU edition of an Accessibility Conformance Report, when a European public-sector buyer specifies EN 301 549, or when reconciling an EU accessibility requirement against a WCAG-only audit.
---

# EN 301 549 Mapping

EN 301 549 is the harmonised European accessibility standard for ICT products and services. It is the standard the European Accessibility Act points at, and it is what EU public-sector procurement specifies by name.

The single most useful fact for most engagements: **EN 301 549 incorporates WCAG for web and non-web software.** A WCAG 2.1 Level AA audit is the substantive work; EN 301 549 adds the clause structure, the non-web chapters, and the documentation obligations around it. Do not let a client believe that "EN 301 549" means a second, separate audit of their website.

## When to Use

- An EU buyer or tender names **EN 301 549** rather than WCAG
- Producing the EU edition of an Accessibility Conformance Report
- Mapping an existing WCAG 2.1 audit onto clause numbers
- Reconciling EU obligations against a Section 508 or WCAG-only assessment
- Verifying a clause number **before** it goes into a client document
- A client believes "EN 301 549" means a second, separate audit

## How the standard is organised

EN 301 549 is clause-structured, not criterion-structured, and the numbering differs from WCAG. The chapters that matter in practice:

| Clause | Subject | Relevance |
|---|---|---|
| **4** | Functional performance statements | What the product must enable across vision, hearing, cognition, and manual dexterity |
| **5** | Generic requirements | Includes the accessibility of **documentation** and **support services** — frequently missed, and a real conformance gap |
| **6** | ICT with two-way voice communication | Only for covered communications products |
| **7** | ICT with video capabilities | Captions, audio description, sign language — relevant to media and e-learning |
| **8** | Hardware | Only for covered products; not web |
| **9** | **Web** — incorporates WCAG 2.1 Level A and AA | The chapter that carries almost all web audit work |
| **10** | Non-web documents | PDFs, emails, statements, invoices, and this standard's own documentation |
| **11** | **Software** — non-web software, plus WCAG for any software with a user interface | Where a native app or desktop product lands |
| **12** | Documentation and support services | Accessibility of the documentation you ship and the support you provide |

**Clause 9 is the one that maps to WCAG.** The sub-clause numbering follows the WCAG structure: `9.1.x` carries Level A, `9.2.x` carries Level AA, and `9.3.x` carries Level AAA. Within those, the suffix is **WCAG's own success-criterion number, unchanged** — so:

| WCAG 2.1 SC | Level | EN 301 549 clause |
|---|---|---|
| 1.1.1 Non-text Content | A | **9.1.1.1** |
| 3.3.2 Labels or Instructions | A | **9.1.3.3.2** |
| 2.5.3 Label in Name | A | **9.1.2.5.3** |
| 1.4.3 Contrast (Minimum) | AA | **9.2.1.4.3** |
| 2.4.7 Focus Visible | AA | **9.2.2.4.7** |
| 4.1.3 Status Messages | AA | **9.2.4.1.3** |

The rule is mechanical: prefix `9.1.` for Level A, `9.2.` for Level AA, then append the SC number verbatim. Getting the **level** right is therefore the whole task — cite an AA criterion under `9.1.` and the clause does not exist.

**This numbering is version-dependent and it is the single most common source of error in an EU-edition ACR.** EN 301 549 has been revised (v2.1.2, v3.1.1, v3.2.1), and clause numbering and referenced WCAG version changed between revisions.

Therefore: **state the EN 301 549 version you are mapping against, and verify every clause number against that version's own table before it goes into a client document.** Load `references/details.md` for the version differences, the WCAG-to-clause mapping table, and the verification procedure. Never emit a clause number from memory — a mis-cited clause is the fastest way for a procurement evaluator to lose confidence in the whole report.

## What EN 301 549 adds beyond WCAG

These are the requirements a WCAG-only audit misses, and they are where EU-edition reports most often under-deliver:

- **Clause 5 — generic requirements.** Functionality must be provided in more than one modality where a single modality would exclude users; the product must not trigger photosensitive seizures.
- **Clause 10 — non-web documents.** Every PDF, invoice, order confirmation, statement, and marketing email is in scope. Most businesses that pass a website audit fail here immediately, because their documents were never authored accessibly. **The accessibility statement itself is a clause 10 document** — publishing it as an inaccessible PDF is a self-inflicted conformance failure.
- **Clause 11 — software.** Where the product includes native mobile or desktop software, the WCAG-equivalent requirements apply through clause 11, not clause 9. A web-only audit does not cover the iOS or Android app, and saying so is mandatory.
- **Clause 12 — documentation and support.** The documentation you ship must be available in accessible formats, and **support services must be able to help users with disabilities** — an accessible product with an inaccessible support channel is a documented gap. Support teams are almost never assessed and almost always fail this.

Flag these four explicitly in every EU-edition engagement. They are the difference between a report that survives procurement scrutiny and one that is quietly marked incomplete.

## Reconciling a WCAG audit into an EU-edition ACR

1. Take the WCAG 2.1 Level A and AA findings — all 50 success criteria.
2. Map each to its EN 301 549 clause **in the declared version**, verifying against that version's table.
3. Add the non-WCAG clauses in scope: 4, 5, and whichever of 6, 7, 10, 11, 12 apply to the product. Mark clauses that genuinely cannot apply as **Not Applicable with a reason** — never silently omit them, because an EU evaluator checks that all chapters were considered.
4. Carry the conformance levels across unchanged. **Do not re-grade** a criterion because the clause number changed; the level comes from the evidence, not from the mapping.
5. Record the EN 301 549 version, the WCAG version, and the mapping date in the report header.

Where the buyer asked for "EN 301 549" without specifying a version, state the version you used and why, and note that a different version may be specified in the tender documents. Check the tender — buyers do specify, and specifying v3.1.1 while reporting against v3.2.1 is a rejection.

## When to use which edition

| Buyer | Edition |
|---|---|
| EU public body, university, or tender referencing EN 301 549 | **EN 301 549** |
| Commercial EU buyer referencing the EAA or WCAG | **WCAG** edition, with EN 301 549 clauses noted where asked |
| US federal, or a US university procurement process | **Section 508** |
| Sold across the EU, the US, and elsewhere | **INT** — all three reconciled |

The INT edition is the most work and the highest-value deliverable, because it is three documents reconciled into one consistent report. If a client sells internationally and has been asked for a VPAT more than once, INT is usually the right recommendation and it is worth saying so rather than producing the cheapest edition three times.

See `references/details.md` for the full WCAG 2.1 SC-to-clause mapping table, the version-difference notes between EN 301 549 v2.1.2 / v3.1.1 / v3.2.1, the clause-4 functional performance statements and how to answer them, the clause-10 PDF remediation checklist, and the verification procedure for clause numbers.
