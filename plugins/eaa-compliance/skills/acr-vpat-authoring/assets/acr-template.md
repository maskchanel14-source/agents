# ACR Template — VPAT 2.5Rev {{EDITION}} Edition

> **Template.** Replace every `{{PLACEHOLDER}}`. Delete this note before delivery. Do not assign a conformance level without a recorded test behind it — an unevaluated criterion is **Not Evaluated** with a dated closing test, never a guess.

---

# Accessibility Conformance Report

**{{PRODUCT_NAME}} — Version {{PRODUCT_VERSION}}**

Based on VPAT® 2.5Rev {{EDITION}} edition

| | |
|---|---|
| **Product name** | {{PRODUCT_NAME}} |
| **Product version** | {{PRODUCT_VERSION}} |
| **Report date** | {{REPORT_DATE}} |
| **Edition** | {{WCAG \| EN 301 549 \| Section 508 \| INT}} |
| **Standard assessed against** | {{WCAG 2.1 Level A and AA \| EN 301 549 v3.2.1 \| Revised 508 Standards}} |
| **Prepared by** | {{EVALUATOR_NAME_AND_ORGANISATION}} |
| **Evaluation type** | {{SELF-EVALUATION \| INDEPENDENT EVALUATION}} |
| **Contact** | {{EMAIL}} |

## Product description

{{ONE_PARAGRAPH — what the product is, what it does, who uses it, and which surfaces the assessment covers.}}

## Evaluation methods

{{METHODS — be specific and falsifiable.}}

- Automated scanning against WCAG 2.1 Level A and AA tags on {{DATE}} using {{TOOL AND VERSION}}
- Static source analysis of the codebase at commit {{SHA}} on {{DATE}}
- Manual keyboard-only testing of the following journeys on {{DATE}}: {{JOURNEYS}}
- Screen-reader testing on {{DATE}} using {{AT AND VERSION}} with {{BROWSER AND VERSION}} on {{OS AND VERSION}}
- Zoom and reflow testing at 200% text size, 400% zoom, and 320 CSS pixels on {{DATE}}

Automated scanning detects approximately a quarter to a third of WCAG issues. Criteria established by automated or source analysis alone are identified as such in the remarks below.

## Platforms and assistive technologies tested

| Platform | Browser | Assistive technology |
|---|---|---|
| {{OS + VERSION}} | {{BROWSER + VERSION}} | {{AT + VERSION, or "none"}} |

## Scope and exclusions

**In scope:** {{ROUTES, TEMPLATES, APPLICATION VERSIONS, AND DOCUMENT SETS ASSESSED}}

**Excluded, with reasons:**

| Excluded surface | Reason | Owner |
|---|---|---|
| {{SURFACE}} | {{REASON}} | {{CLIENT \| THIRD PARTY \| PLATFORM}} |

Exclusions are stated because a conformance claim that silently covers a surface the vendor does not control is a misrepresentation. Where an excluded surface is operated by a third party, that party's own conformance report is referenced in the relevant remark.

---

{{EDITION_TABLES — select the block matching the edition and delete the others}}

## WCAG 2.1 Level A — 30 criteria

| Criteria | Conformance Level | Remarks and Explanations |
|---|---|---|
| 1.1.1 Non-text Content | {{LEVEL}} | {{REMARK}} |
| 1.2.1 Audio-only and Video-only (Prerecorded) | {{LEVEL}} | {{REMARK}} |
| 1.2.2 Captions (Prerecorded) | {{LEVEL}} | {{REMARK}} |
| 1.2.3 Audio Description or Media Alternative (Prerecorded) | {{LEVEL}} | {{REMARK}} |
| 1.3.1 Info and Relationships | {{LEVEL}} | {{REMARK}} |
| 1.3.2 Meaningful Sequence | {{LEVEL}} | {{REMARK}} |
| 1.3.3 Sensory Characteristics | {{LEVEL}} | {{REMARK}} |
| 1.4.1 Use of Color | {{LEVEL}} | {{REMARK}} |
| 1.4.2 Audio Control | {{LEVEL}} | {{REMARK}} |
| 2.1.1 Keyboard | {{LEVEL}} | {{REMARK}} |
| 2.1.2 No Keyboard Trap | {{LEVEL}} | {{REMARK}} |
| 2.1.4 Character Key Shortcuts | {{LEVEL}} | {{REMARK}} |
| 2.2.1 Timing Adjustable | {{LEVEL}} | {{REMARK}} |
| 2.2.2 Pause, Stop, Hide | {{LEVEL}} | {{REMARK}} |
| 2.3.1 Three Flashes or Below Threshold | {{LEVEL}} | {{REMARK}} |
| 2.4.1 Bypass Blocks | {{LEVEL}} | {{REMARK}} |
| 2.4.2 Page Titled | {{LEVEL}} | {{REMARK}} |
| 2.4.3 Focus Order | {{LEVEL}} | {{REMARK}} |
| 2.4.4 Link Purpose (In Context) | {{LEVEL}} | {{REMARK}} |
| 2.5.1 Pointer Gestures | {{LEVEL}} | {{REMARK}} |
| 2.5.2 Pointer Cancellation | {{LEVEL}} | {{REMARK}} |
| 2.5.3 Label in Name | {{LEVEL}} | {{REMARK}} |
| 2.5.4 Motion Actuation | {{LEVEL}} | {{REMARK}} |
| 3.1.1 Language of Page | {{LEVEL}} | {{REMARK}} |
| 3.2.1 On Focus | {{LEVEL}} | {{REMARK}} |
| 3.2.2 On Input | {{LEVEL}} | {{REMARK}} |
| 3.3.1 Error Identification | {{LEVEL}} | {{REMARK}} |
| 3.3.2 Labels or Instructions | {{LEVEL}} | {{REMARK}} |
| 4.1.1 Parsing | {{LEVEL}} | {{REMARK}} |
| 4.1.2 Name, Role, Value | {{LEVEL}} | {{REMARK}} |

## WCAG 2.1 Level AA — 20 criteria

| Criteria | Conformance Level | Remarks and Explanations |
|---|---|---|
| 1.2.4 Captions (Live) | {{LEVEL}} | {{REMARK}} |
| 1.2.5 Audio Description (Prerecorded) | {{LEVEL}} | {{REMARK}} |
| 1.3.4 Orientation | {{LEVEL}} | {{REMARK}} |
| 1.3.5 Identify Input Purpose | {{LEVEL}} | {{REMARK}} |
| 1.4.3 Contrast (Minimum) | {{LEVEL}} | {{REMARK}} |
| 1.4.4 Resize Text | {{LEVEL}} | {{REMARK}} |
| 1.4.5 Images of Text | {{LEVEL}} | {{REMARK}} |
| 1.4.10 Reflow | {{LEVEL}} | {{REMARK}} |
| 1.4.11 Non-text Contrast | {{LEVEL}} | {{REMARK}} |
| 1.4.12 Text Spacing | {{LEVEL}} | {{REMARK}} |
| 1.4.13 Content on Hover or Focus | {{LEVEL}} | {{REMARK}} |
| 2.4.5 Multiple Ways | {{LEVEL}} | {{REMARK}} |
| 2.4.6 Headings and Labels | {{LEVEL}} | {{REMARK}} |
| 2.4.7 Focus Visible | {{LEVEL}} | {{REMARK}} |
| 3.1.2 Language of Parts | {{LEVEL}} | {{REMARK}} |
| 3.2.3 Consistent Navigation | {{LEVEL}} | {{REMARK}} |
| 3.2.4 Consistent Identification | {{LEVEL}} | {{REMARK}} |
| 3.3.3 Error Suggestion | {{LEVEL}} | {{REMARK}} |
| 3.3.4 Error Prevention (Legal, Financial, Data) | {{LEVEL}} | {{REMARK}} |
| 4.1.3 Status Messages | {{LEVEL}} | {{REMARK}} |

**Row-count check:** 30 Level A + 20 Level AA = **50**. A report with 38 rows was built from a WCAG 2.0 list and is incomplete.

---

## EN 301 549 chapters (EU edition)

Report chapters 4 through 12. Where a chapter cannot apply, mark it **Not Applicable with a reason** — never omit it silently, because an EU evaluator checks that all chapters were considered.

| Clause | Chapter | Conformance Level | Remarks |
|---|---|---|---|
| 4.2.1 – 4.2.11 | Functional Performance Statements | {{LEVEL}} | {{REMARK}} |
| 5 | Generic Requirements | {{LEVEL}} | {{REMARK}} |
| 6 | ICT with Two-Way Voice Communication | {{LEVEL}} | {{REMARK}} |
| 7 | ICT with Video Capabilities | {{LEVEL}} | {{REMARK}} |
| 8 | Hardware | {{LEVEL}} | {{REMARK}} |
| 9.1 | Web — WCAG 2.1 Level A | see WCAG tables | clause = `9.1.<SC>` |
| 9.2 | Web — WCAG 2.1 Level AA | see WCAG tables | clause = `9.2.<SC>` |
| 10 | Non-Web Documents | {{LEVEL}} | {{REMARK — includes the accessibility statement itself}} |
| 11 | Software | {{LEVEL}} | {{REMARK — native mobile and desktop, if any}} |
| 12 | Documentation and Support Services | {{LEVEL}} | {{REMARK — support's ability to help users with disabilities}} |

**EN 301 549 version used:** {{VERSION}}. Confirm against the tender — specifying v3.1.1 while reporting against v3.2.1 is a rejection.

---

## Section 508 chapters (508 edition)

| Chapter | Subject | Conformance Level | Remarks |
|---|---|---|---|
| 3 | Functional Performance Criteria | {{LEVEL}} | {{REMARK}} |
| 4 | Hardware | {{LEVEL}} | {{REMARK}} |
| 5 | Software — incorporates WCAG **2.0** Level A and AA, plus 502 interoperability and 503 authoring tools | {{LEVEL}} | {{REMARK}} |
| 6 | Support Documentation and Services | {{LEVEL}} | {{REMARK}} |

Note the version difference explicitly: Section 508 references **WCAG 2.0** (38 criteria at A and AA), while the EAA and EN 301 549 reference **WCAG 2.1** (50). Conflating the two is a visible, disqualifying error.

Add the **GSA Issue Detail Supplement** as a further section only where the solicitation requests it, keyed to that solicitation's issue numbers. Obtain the supplement rather than reconstructing it from memory.

---

## Remediation commitments

Every non-conformance carries a dated commitment.

| Finding | Criterion | Journey | Owner | Commitment date | Status |
|---|---|---|---|---|---|
| {{ID}} | {{SC}} | {{JOURNEY}} | {{CLIENT \| THIRD PARTY \| PLATFORM}} | {{DATE}} | {{OPEN \| IN PROGRESS \| CLOSED}} |

Items owned by a third party or platform are listed separately from client-owned work, with the vendor named and the date of the written remediation request. Client-owned and third-party-owned items must not be merged into one list — a plan that includes items the team cannot complete stalls in week two.

## Not Evaluated criteria

| Criterion | Reason | Closing test | Scheduled |
|---|---|---|---|
| {{SC}} | {{REASON}} | {{TEST}} | {{DATE}} |

These criteria carry **no conformance claim**. They are listed because an honest gap with a dated plan is a stronger document than a guess, and because a procurement evaluator will ask.

## Re-issue policy

This report describes version **{{PRODUCT_VERSION}}** as assessed on **{{REPORT_DATE}}**. It will be re-issued after any material release changing a covered journey, any change of third-party provider touching a covered journey, remediation closing a recorded non-conformance, a change in the standard or edition required by a buyer, and at minimum annually.

Prior versions remain retrievable. Issued reports are never edited in place — procurement files reference specific versions, and a silently-edited document is a serious credibility problem.

## Legal disclaimer

This Accessibility Conformance Report is a vendor-completed evaluation of the product identified above at the version and date stated. It is **not** an independent certification of conformance, and it is **not** legal advice. Only an independent evaluator can certify conformance. Any question about the applicability of Directive (EU) 2019/882, the Revised 508 Standards, or another accessibility instrument should be confirmed by a qualified lawyer in the relevant jurisdiction.

---

**{{ORGANISATION_LEGAL_NAME}}** · {{CONTACT}} · Report issued {{REPORT_DATE}}
