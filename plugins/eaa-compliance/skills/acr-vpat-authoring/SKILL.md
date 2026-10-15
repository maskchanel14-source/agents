---
name: acr-vpat-authoring
description: Use when authoring an Accessibility Conformance Report on the ITI VPAT 2.5Rev structure, when a buyer or procurement process requests a VPAT, when selecting between the WCAG, EN 301 549, Section 508, or INT edition, when exporting an ACR to OpenACR YAML, or when assigning conformance levels and writing remarks that survive procurement scrutiny.
---

# ACR / VPAT Authoring

The VPAT is the template; the completed, published document is the **Accessibility Conformance Report (ACR)**. Buyers say "VPAT" and mean the ACR. Use "ACR" in the document title and reflect the buyer's term in correspondence.

The template is free. What consultancies charge $350 to $25,000 for is the audit behind it, the accuracy of the remarks, and whether the document can be defended under scrutiny. Your output has to earn that standard, which means being precise about what was tested and what was not.

## When to Use

- A buyer, procurement process, or RFP requests a **VPAT** or ACR
- Selecting between the WCAG, EN 301 549, Section 508, or INT edition
- Assigning conformance levels and writing remarks from audit evidence
- Exporting the report to OpenACR YAML
- Deciding whether an issued report must be re-issued
- Answering a questionnaire where no ACR exists yet

## The governing rule

**Never overstate conformance.** A single unsupported "Supports" is worse than an honest "Partially Supports". Overstatement is what turns a routine procurement question into a misrepresentation problem, and it is what gets a document thrown out when a dispute begins.

| Level | Assign only when |
|---|---|
| **Supports** | Verified, and no failure found. Source inspection alone is **not** verification for criteria requiring assistive-technology testing. |
| **Partially Supports** | Some functionality meets the criterion and some does not, or it is met with a documented limitation. **Name the part that fails.** |
| **Does Not Support** | The majority fails, or the failure blocks the task. |
| **Not Applicable** | The criterion cannot apply to this product. **State why** — unexplained "not applicable" reads as evasion. |
| **Not Evaluated** | No test has been performed. Record the reason, the test required to close it, and a date. |

"Not Evaluated" is a strength, not a weakness. An ACR that honestly marks twelve criteria unevaluated with a dated plan to close them is a stronger document than one that guesses — and it is the document a procurement evaluator believes.

## The remark pattern

Every remark, without exception:

> **What was tested · how it was tested · what was found · what the limitation is · when it will be addressed.**

One or two specific sentences. Banned everywhere in the output: "strives to be accessible", "is committed to accessibility", "meets industry standards", "no known issues" without a test behind it, and any remark that could be pasted into a different product's report unchanged.

Compare:

- **Rejected:** "Partially Supports. Some accessibility features are being improved."
- **Accepted:** "Partially Supports. Tested 12 April 2026 with NVDA 2025.1 and Firefox 136 on Windows 11 across the checkout, cart, and account journeys. All 34 form controls in checkout have programmatic labels. Two of eight filter controls on the category listing expose no accessible name. Remediation scheduled for the 14 May 2026 release; tracked as finding CA-07."

## Editions

| Edition | Use when | Scope |
|---|---|---|
| **WCAG** | Commercial web product; buyer asked for "a VPAT" and named no standard | WCAG 2.1 or 2.2, Level A and AA — **50 criteria** |
| **EN 301 549** | EU public procurement, or any context tied to EAA obligations | Clauses 4–12, with clause 9 carrying the WCAG mapping |
| **Section 508** | US federal procurement | Revised 508 Standards chapters; add the GSA Issue Detail Supplement on request |
| **INT** | Sold across the EU, the US, and elsewhere | All three reconciled into one report |

Confirm the edition before drafting — producing the wrong one is a full rework, and buyers are specific once they have been asked before. Where a buyer says only "VPAT", ask which standard their evaluator will use.

The **INT** edition is the most work and the highest-value deliverable, because it is three documents reconciled into one internally consistent report. If a client sells internationally and has been asked for a VPAT more than once, recommend INT rather than producing the cheapest edition three times.

## Report every criterion in scope

For WCAG 2.1 Level A and AA that is **all 50**: 30 at Level A and 20 at Level AA.

Do not omit the criteria that pass, and do not collapse them into a summary sentence. Evaluators read the remark for the criterion they care about, and a document with gaps reads as a document with something to hide.

A report with **38 rows** was built from a WCAG 2.0 list and is incomplete — WCAG 2.1 added five Level A criteria (2.1.4, 2.5.1, 2.5.2, 2.5.3, 2.5.4) and seven Level AA criteria (1.3.4, 1.3.5, 1.4.10, 1.4.11, 1.4.12, 1.4.13, 4.1.3). Checking the row count is the fastest way to catch a recycled report.

## Always include

- product name and the **exact version** assessed
- assessment date, evaluator, and method
- platforms, browsers, and assistive technologies tested, **with versions**
- scope and exclusions, each with a reason
- a dated remediation commitment for every non-conformance
- the standing note that the report describes a specific version and **must be re-issued after material change**

The version note is what makes the document honest over time. An ACR is a snapshot; treating it as a permanent certificate is how vendors end up with a two-year-old report describing a product that no longer exists.

## OpenACR export

Emit OpenACR YAML alongside the human-readable report. OpenACR is the machine-readable format public-sector ACR libraries use — shipping it lets a buyer ingest the report into their own tooling and signals that the vendor works to the current standard rather than filling in a Word template. It is a genuine differentiator and almost nobody supplies it.

Populate the YAML **from the same source data** as the human-readable version, then diff the two before presenting: criterion counts, conformance levels, product version, and dates must match exactly. Two documents that disagree are worse than one.

Load the schema skeleton from `assets/openacr-skeleton.yaml` and the human-readable structure from `assets/acr-template.md`. Validate against the current OpenACR schema before delivery, and record the schema version used — the schema evolves, and a stale schema reference is a rejection.

## Verification gates

Reject and rework if any of these hold:

- a criterion marked `MANUAL REQUIRED` upstream carries a level other than **Not Evaluated**
- any "Supports" has no recorded test behind it
- any remark is generic, marketing-toned, empty, or reusable unchanged in another product's report
- any criterion in scope is missing from the tables
- the product version, assessment date, or evaluator is absent or still a placeholder
- exclusions exist without a stated reason
- a non-conformance lacks a dated remediation commitment
- the edition's table structure does not match VPAT 2.5Rev for that edition
- the row count does not match the declared standard and level
- the OpenACR YAML disagrees with the human-readable report on any field

See `references/details.md` for the per-edition table structures, the EN 301 549 clause mapping, the Section 508 chapter structure, remark patterns by level and by finding type, how to reconcile the INT edition without contradictions, the re-issue policy, and the evaluation errors that most often cause rejection.
