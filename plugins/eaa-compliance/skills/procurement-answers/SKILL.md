---
name: procurement-answers
description: Use when a buyer sends an accessibility questionnaire, RFP, security review, or vendor assessment, when the same accessibility questions must be answered consistently across deals, when reconciling procurement answers against an issued ACR, or when building a reusable answer bank so the vendor stops re-writing the same thirty responses.
---

# Procurement Answer Bank

Buyers ask the same thirty accessibility questions in every RFP, security questionnaire, and vendor assessment. Vendors re-write the answers each time, under deadline, usually inconsistently — and inconsistency between two documents is what causes a deal to stall.

The answer bank exists so responses are written **once**, reconciled against the issued ACR, and reused. The value is not speed; it is that every answer agrees with every other answer and with the conformance report the buyer already holds.

## When to Use

- A buyer sends an accessibility questionnaire, RFP, or vendor assessment
- The same questions must be answered consistently across multiple deals
- Reconciling draft answers against the current issued ACR
- A question asks for a warranty, indemnity, or liability position
- Building a reusable answer bank so responses stop being re-written under deadline

## The rule that governs everything

**Every answer must be traceable to the ACR.** If an answer states something the ACR does not support, one of two things happens: the evaluator finds the contradiction and discounts both documents, or the answer becomes a representation the vendor cannot stand behind. Neither is survivable.

Before answering anything, load the current issued ACR and the accessibility statement. Reconcile product version, assessment date, conformance levels, and named limitations. Where no ACR exists, say so and answer with the remediation plan and dates instead of inventing conformance — a buyer will almost always accept "not yet assessed, assessment scheduled for {{DATE}}" over an unsupported claim.

## Answer style

Short, specific, evidence-backed, and consistent. The evaluator is reading forty vendors' responses and scoring them; prose that requires interpretation scores worse than prose that does not.

Every answer follows the shape: **direct answer first · the evidence · the exception, if any · the cross-reference.**

- **Rejected:** "Our product is committed to accessibility and follows industry best practices across all supported platforms."
- **Accepted:** "Partially conforms to WCAG 2.1 Level AA. Assessed 12 April 2026 against version 4.2.0; 41 of 50 criteria fully conformant, 7 partially, 2 not evaluated with closing tests scheduled 14 May 2026. Full detail in our ACR, section WCAG Level AA. Known limitation: the hosted payment frame is operated by {{PROVIDER}} and is outside our control; their conformance report is available on request."

Never use: "strives to be", "best-effort", "industry standard" without naming the standard, "no known issues" without a test behind it, "fully compliant" as a bare assertion, or any sentence that could be pasted unchanged into a different vendor's response.

## The questions buyers actually ask

Thirty questions, in six groups. Each is answered in `references/details.md` with a model answer, the follow-up it invites, and the response that disqualifies a vendor.

| Group | What the evaluator is really establishing | Questions |
|---|---|---|
| **Documentation** | Does an ACR exist, is it current, and was it self- or independently evaluated? | 1–5 |
| **Conformance substance** | What actually conforms, what fails, and what was never tested? | 6–10 |
| **Process** | Does accessibility survive the departure of one enthusiastic engineer? | 11–15 |
| **Third parties** | Does the vendor know where its control ends? | 16–19 |
| **Accountability** | Remediation, response commitment, and contractual exposure | 20–24 |
| **Standards** | EN 301 549, Section 508, the EAA, the ADA, machine-readable formats | 25–30 |

Four deserve special handling and are the ones vendors most often lose:

- **Q8 — "which criteria have not been evaluated?"** A trap for anyone who overstates. An honest list with dated closing tests scores *better* than a claim of full coverage, because it shows the vendor understands what its own evidence supports.
- **Q11 — CI gating.** State the limit unprompted: automated scanning detects roughly a quarter to a third of WCAG issues, so a green build is a regression guard and **not** a conformance claim.
- **Q19 — overlay widgets.** A hard filter. Overlays do not deliver conformance and the EU has not endorsed them. If one is in use, describe the narrow purpose and disclaim conformance through it explicitly.
- **Q22–24 — warranties, indemnities, liability.** These are **legal**. Mark the row `PENDING LEGAL REVIEW` with a date. Saying that is a *strong* answer: it tells the evaluator the vendor takes the commitment seriously enough not to improvise it.
- **Q27 — "are you EAA compliant?"** Separate what is verifiable — conformance against a named standard, version, and date — from a legal conclusion about a directive's applicability to the buyer's use, which is not the vendor's to declare.

## Consistency checks before sending

- [ ] product name and **version** identical to the ACR
- [ ] assessment date identical to the ACR
- [ ] conformance status wording identical to the statement and the ACR
- [ ] criterion counts consistent — 30 Level A + 20 Level AA = 50 for WCAG 2.1
- [ ] named limitations identical in wording and owner across all documents
- [ ] response commitment in business days matches the published statement
- [ ] every legal question flagged for counsel rather than answered
- [ ] no placeholder, no template artefact, no invented authority name
- [ ] the ACR attached is the **current issued** version, not a draft

Two documents that disagree get both discarded. Run this list every time, even when reusing an answer verbatim — the version and date are the fields that go stale.

See `references/details.md` for the full thirty-question bank with model answers, the follow-up each question invites, the traps and the disqualifying responses, how to handle a questionnaire when no ACR exists yet, how to answer the legal questions without committing the organisation, and the reuse workflow that keeps the bank current.
