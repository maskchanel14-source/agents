# ACR / VPAT — Reference Detail

Loaded on demand from `../SKILL.md`. Per-edition table structures, the Section 508 chapters, remark patterns by finding type, INT reconciliation, the re-issue policy, and the rejection causes.

## VPAT 2.5Rev structure

The ITI VPAT 2.5Rev document opens with: product name and version, product description, date of the report, evaluator and method, the platforms and assistive technologies tested, scope and exclusions, and a notes section. Then the edition-specific tables. Then a legal disclaimer noting that the VPAT is a vendor-completed self-evaluation, not an independent certification, and that it describes a specific version.

Every edition's tables use four columns: **Criteria · Conformance Level · Remarks and Explanations**, plus the criterion's own text or a reference to it. Keep the columns stable — evaluators parse these tables mechanically and a reordered column set breaks their process.

## WCAG edition

Two tables: **Level A** (30 criteria) and **Level AA** (20 criteria). Row order follows the WCAG numbering, 1.1.1 through 4.1.3. Do not reorder by severity or by result — the evaluator cross-references row positions across vendors.

For each row record the conformance level and the remark. Where a criterion was tested on multiple journeys and results differ, the remark must say which journey failed. "Partially Supports — fails on the category listing filters only" is usable; "Partially Supports" alone is not, because the evaluator cannot scope the risk.

Where the product contains no prerecorded audio or video, criteria 1.2.1 through 1.2.5 are **Not Applicable** — and the remark must say "The product contains no prerecorded or live audio-only or video media", not merely "N/A".

## EN 301 549 (EU) edition

Chapters follow the EN 301 549 clause numbering directly:

| Chapter | Clause | Content |
|---|---|---|
| Functional Performance Statements | **4** | 4.2.1 – 4.2.11 |
| Generic Requirements | **5** | Multiple modalities; no photosensitive-seizure triggers |
| ICT with Two-Way Voice Communication | **6** | Only where applicable — otherwise mark the chapter not applicable with a reason |
| ICT with Video Capabilities | **7** | Captions, audio description, sign language |
| Hardware | **8** | Only for covered products |
| Web | **9** | 9.1 Level A, 9.2 Level AA, 9.3 Level AAA |
| Non-Web Documents | **10** | PDFs, emails, statements, invoices |
| Software | **11** | Non-web software, and WCAG for software with a user interface |
| Documentation and Support Services | **12** | Accessible documentation and accessible support |

Clause mapping: prefix by level, then append the WCAG success-criterion number verbatim — Level A becomes `9.1.<SC>`, Level AA becomes `9.2.<SC>`, Level AAA becomes `9.3.<SC>`.

| WCAG SC | Level | Clause |
|---|---|---|
| 1.1.1 Non-text Content | A | 9.1.1.1 |
| 3.3.2 Labels or Instructions | A | 9.1.3.3.2 |
| 2.5.3 Label in Name | A | 9.1.2.5.3 |
| 1.4.3 Contrast (Minimum) | AA | 9.2.1.4.3 |
| 2.4.7 Focus Visible | AA | 9.2.2.4.7 |
| 4.1.3 Status Messages | AA | 9.2.4.1.3 |

The only error that matters is mis-assigning the level: cite an AA criterion under `9.1.` and the clause does not exist in the standard.

**Report the EN 301 549 version used.** v2.1.2 references WCAG 2.0; v3.1.1 and v3.2.1 reference WCAG 2.1; later revisions moving to WCAG 2.2 have been in progress. Where the buyer says only "EN 301 549", use v3.2.1, state that you did, and note that the tender documents should be checked — specifying v3.1.1 while reporting against v3.2.1 is a rejection.

Chapter 4 is answered differently from chapter 9: it is a set of statements about what the product enables across vision, hearing, cognition, and manual dexterity, cross-referenced to the clause-9 criteria that deliver each capability. Boilerplate clause-4 answers are a common rejection reason in EU public procurement, because the evaluator reads clause 4 as the summary and clause 9 as the detail.

Chapters 10, 11, and 12 are where WCAG-only vendors under-deliver. Clause 10 covers every PDF, invoice, and statement — including the accessibility statement itself. Clause 11 covers native mobile and desktop software, which a web-only audit does not reach. Clause 12 covers documentation formats **and the ability of support services to help users with disabilities** — almost never assessed and almost always failing.

## Section 508 edition

Chapters follow the Revised 508 Standards:

| Chapter | Subject |
|---|---|
| **3** | Functional Performance Criteria |
| **4** | Hardware |
| **5** | Software |
| **6** | Support Documentation and Services |

Chapter 5 incorporates WCAG 2.0 Level A and AA by reference for electronic content, plus the additional 502 and 503 requirements — interoperability with assistive technology, and authoring-tool accessibility. Where the buyer requests the **GSA Issue Detail Supplement**, produce it as an additional section keyed to the specific solicitation issues; it is a US federal procurement artefact and its structure is dictated by the solicitation, so obtain it rather than reconstructing it from memory.

Note the version difference explicitly: Section 508 references **WCAG 2.0**, while the EAA and EN 301 549 reference **WCAG 2.1**. A report covering both must state which criteria set each chapter was assessed against, and the row counts will differ — 38 for WCAG 2.0 A and AA, 50 for WCAG 2.1 A and AA. Conflating them is a visible, disqualifying error.

## INT edition reconciliation

The INT edition contains all three sets. Produce it as one report with three table groups, reconciled so no criterion contradicts itself across groups.

Reconciliation procedure:

1. Assess against **WCAG 2.1 Level A and AA** as the substantive baseline — it is the superset of the WCAG 2.0 requirements that Section 508 references.
2. Build the WCAG edition tables from that baseline.
3. Map to EN 301 549 clauses and build the chapter 9 tables, then add chapters 4, 5, 6, 7, 10, 11, and 12 as applicable.
4. Build the Section 508 chapters, deriving WCAG 2.0 rows from the 2.1 assessment and marking the five Level A and seven Level AA criteria that exist only in 2.1 as out of scope for the 508 chapter rather than silently dropping them.
5. Add 502 and 503 requirements to the 508 software chapter.
6. **Cross-check every criterion that appears in more than one group.** Conformance levels must agree, or the difference must be explained by the differing standard version.
7. State in the header which WCAG version each group was assessed against.

The value of INT is consistency. A contradiction between groups is worse than three separate reports, because it demonstrates the vendor did not reconcile them.

## Remark patterns by finding type

**Failure found, fix scheduled:**
> Does Not Support. Tested 12 April 2026 with keyboard only and NVDA 2025.1 on Firefox 136 / Windows 11. The cart quantity input has no programmatic label and is announced as "edit blank". Fix implemented in branch `a11y/cart-labels`, scheduled for the 14 May 2026 release; tracked as finding CT-03.

**Partial, scoped to a journey:**
> Partially Supports. All 34 form controls in checkout carry programmatic labels, verified 12 April 2026. Two of eight filter controls on the category listing expose no accessible name. Remediation scheduled 14 May 2026; finding CA-07.

**Third-party owned:**
> Partially Supports. The payment step is served by {{PROVIDER}} in a hosted frame outside our control. {{PROVIDER}}'s own conformance report, dated {{DATE}}, records the following limitations: {{LIST}}. We review their report at each renewal and have raised these items with them in writing on {{DATE}}.

**Platform boundary:**
> Not Applicable to the extent of the platform surface. Checkout markup on this platform is not modifiable by the merchant beyond sanctioned extension points. Where a barrier exists on that surface it is the platform operator's responsibility; the operator's current conformance position is {{STATUS}}, confirmed {{DATE}}.

**Not evaluated — the honest case:**
> Not Evaluated. This criterion requires assistive-technology testing that was not performed in the assessment dated {{DATE}}. The closing test is a keyboard-only and screen-reader pass of the {{JOURNEY}} journey, scheduled for {{DATE}}. No conformance claim is made.

**Not applicable:**
> Not Applicable. The product contains no prerecorded or live audio-only or video media. Where such media is added, this row will be re-assessed before the next release.

## Re-issue policy

An ACR is a snapshot of a specific version. Re-issue after:

- any material release that changes a covered journey
- any change of third-party provider touching a covered journey
- remediation that closes a finding recorded as a non-conformance
- a change in the standard or edition the buyer requires
- at minimum annually, with the date advanced even where nothing changed

State the re-issue policy in the report and in the answer bank. A buyer who receives a stale report will ask when it was last updated; a vendor who can answer with a dated policy is in a materially stronger position than one who cannot.

Never edit an issued ACR in place. Issue a new version with a new date, and keep the prior version retrievable — procurement files reference specific versions, and a silently-edited document is a serious credibility problem.

## Causes of rejection

The errors that most often cause an ACR to be rejected or quietly marked incomplete:

1. **Unsupported "Supports"** — a level with no test behind it. The most common and the most damaging.
2. **Missing criteria** — 38 rows instead of 50, from a WCAG 2.0 list presented as 2.1 coverage.
3. **Generic remarks** — text that could be pasted into any product's report unchanged.
4. **No version or no date** — the report cannot be tied to a product, so it cannot be relied on.
5. **Unstated exclusions** — a mobile app, a hosted checkout, or a document set silently omitted and discovered later.
6. **Non-conformances without dates** — reads as an admission with no plan.
7. **Wrong edition** — WCAG when the tender specified EN 301 549, or the wrong EN 301 549 version.
8. **Empty clause 4 or chapter 3** — the functional-performance section left as boilerplate, which EU and US evaluators read first.
9. **Clause 12 ignored** — support services not assessed. Cheap to fix, commonly missed, and a stated requirement.
10. **Contradiction with the accessibility statement** — two documents that disagree get both discarded.
11. **Placeholder text left in a delivered document** — indefensible and visible to anyone who reads it.

Check all eleven before delivery. Every one of them is caught by re-reading the document once with the buyer's perspective in mind.
