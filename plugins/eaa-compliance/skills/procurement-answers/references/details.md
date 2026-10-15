# Procurement Answer Bank — Reference Detail

Loaded on demand from `../SKILL.md`. The full thirty-question bank with model answers, the follow-ups each invites, disqualifying responses, how to answer with no ACR, how to handle the legal questions, and the reuse workflow.

## How to use model answers

The answers below are **patterns**, not text to paste. Every one contains fields that must come from the current issued ACR. Pasting a model answer without substituting real values is how a vendor sends a questionnaire containing another product's numbers — and evaluators do notice.

Substitute, then run the consistency checklist in `../SKILL.md`.

## Bank 1 — documentation existence and currency

**Q1. Do you have a current VPAT or ACR? Which edition and date?**

> Yes. Accessibility Conformance Report for {{PRODUCT}} version {{VERSION}}, on VPAT® 2.5Rev {{EDITION}} edition, dated {{DATE}}. Attached.

*Follow-up invited:* "Is it independent or self-evaluated?" — answer before being asked.
*Disqualifying:* "We can provide one on request." If it exists, attach it. If it does not, say so with a date.

**Q2. Which WCAG version and level?**

> Assessed against WCAG {{2.1}} Level A and AA — {{50}} success criteria. {{WHERE RELEVANT: also mapped to EN 301 549 v{{VERSION}} clause 9.}}

*Trap:* answering "WCAG" without a version. WCAG 2.0 A and AA is 38 criteria; WCAG 2.1 A and AA is 50. The version tells the evaluator whether the report is current, and a vendor who cannot state it has not read its own document.

**Q3. Who performed the evaluation?**

> {{SELF-EVALUATION by our engineering team using {{METHODS}} | INDEPENDENT EVALUATION by {{FIRM}} on {{DATE}}}}.

*Disqualifying:* blurring the two. Evaluators discount self-evaluations but they disqualify vendors who mislabel one as independent. State it plainly — a well-documented self-evaluation with named methods beats an implied audit every time.

**Q4. When will you re-issue?**

> Our re-issue policy: after any material release changing a covered journey, any change of third-party provider touching a covered journey, remediation closing a recorded non-conformance, a change in required standard or edition, and at minimum annually. Current report issued {{DATE}}; next scheduled review {{DATE}}.

**Q5. Is your accessibility statement published?**

> Yes, at {{URL}}, in {{LANGUAGE}}, last updated {{DATE}}. Linked from the footer of every page.

*Check before answering:* the URL must be live, must not require an account, and must not sit behind a cookie-consent wall. Evaluators click it.

## Bank 2 — conformance substance

**Q6. Current conformance status against WCAG 2.1 AA?**

> Partially conforms. {{VERSION}} assessed {{DATE}}: {{N}} of 50 criteria fully conformant, {{N}} partially conformant, {{N}} not conformant, {{N}} not applicable, {{N}} not evaluated with closing tests scheduled {{DATE}}. Detail in the attached ACR.

Give the distribution. It is the first thing an evaluator reads and it makes every later answer credible.

**Q7. Which criteria do not conform, and when will they?**

> {{SC}} {{NAME}} — {{SPECIFIC BARRIER}} on the {{JOURNEY}} journey. Remediation committed {{DATE}}. {{SC}} {{NAME}} — {{BARRIER}}. Committed {{DATE}}.

*Disqualifying:* "A small number of minor issues remain." Name them. An evaluator who has to ask twice marks the vendor down for opacity, and opacity in a compliance questionnaire reads as concealment.

**Q8. Which criteria have not been evaluated?**

> {{SC}} {{NAME}} and {{SC}} {{NAME}} require assistive-technology testing not performed in the {{DATE}} assessment. Closing tests — a keyboard-only and {{SCREEN READER + VERSION}} pass of the {{JOURNEY}} journeys — are scheduled {{DATE}}. No conformance claim is made for these criteria.

*This is the question that separates credible vendors from the rest.* An honest list with dated closing tests scores better than a claim of full coverage, because it demonstrates the vendor understands what its own evidence supports. Vendors who answer "none" and then fail a keyboard walkthrough in the demo are finished in that deal.

**Q9. Assistive technology tested?**

> {{SCREEN READER + VERSION}} with {{BROWSER + VERSION}} on {{OS + VERSION}}; {{SECOND COMBINATION}}. Keyboard-only testing on all combinations above.

Name versions. "NVDA and VoiceOver" without versions tells the evaluator the testing was not documented.

**Q10. Do you test with users with disabilities?**

> {{YES — describe the programme, cadence, and what changed as a result | NOT CURRENTLY. Our testing is conducted by {{WHO}} using {{AT}}. We are {{PLAN AND DATE}}.}}

*Disqualifying:* "Yes" with no detail. If the answer is no, say no with a plan — an unverifiable yes is worse and it invites a follow-up the vendor cannot answer.

## Bank 3 — process and maintenance

**Q11. Is accessibility testing in CI? What does it gate?**

> Yes. Automated WCAG {{2.1}} A and AA scanning runs on every release against a baseline of known legacy findings, failing the build on **new** violations. Component-level assertions cover {{COMPONENTS}}.
>
> The limit, stated plainly: automated scanning detects approximately a quarter to a third of WCAG issues. Our CI gate is a regression guard, not a conformance claim, and we do not present a green build as evidence of compliance.

Saying the limit unprompted is the single highest-value sentence in this bank. It signals the vendor knows the difference between a scan and an audit — which most do not, and which the evaluator has learned the hard way.

**Q12. Testing cadence and re-test triggers?**

> Automated on every release. Manual keyboard and screen-reader testing of {{JOURNEYS}} each release. Full re-assessment {{CADENCE}}. Re-test triggered by: material release, third-party provider change, a customer-reported barrier, or a change in required standard.

**Q13. Who owns accessibility?**

> {{ROLE AND NAME}} owns the programme, reporting to {{WHO}}. Engineering ownership sits with {{TEAM}}. Findings are tracked in {{SYSTEM}} with the same priority as functional defects.

*What the evaluator is establishing:* whether accessibility survives the departure of one enthusiastic engineer. Name a role, not just a person.

**Q14. Training?**

> {{WHAT}}, delivered {{DATE}} to {{WHO}}, covering {{TOPICS}}. Next session {{DATE}}.

**Q15. Regression prevention?**

> Fail-on-regression CI gate plus a baseline that shrinks as remediation lands. Component assertions on every primitive we have fixed. A growing baseline is treated as a process failure and escalated.

## Bank 4 — third parties and boundaries

**Q16. Which parts are operated by third parties?**

> {{SURFACE}} is served by {{PROVIDER}} within {{MECHANISM — hosted frame, injected script, iframe}}. We do not control its markup.

Naming the boundary precisely is what makes the rest of the answer credible.

**Q17. Do you hold their conformance reports?**

> {{YES — {{PROVIDER}} ACR dated {{DATE}}, available on request | NO — requested {{DATE}}, {{STATUS}}}}.

*Disqualifying:* "Our providers are all compliant." If you cannot produce the report, you cannot say that.

**Q18. What happens when a third-party component is not accessible?**

> We raise it with the vendor in writing, record it as a known limitation in our statement and ACR with the vendor named, set a review date, and {{EVALUATE ALTERNATIVES | ESCALATE TO ACCOUNT MANAGEMENT | PLAN MIGRATION}}. We do not claim conformance for a surface we do not control.

That last sentence is the answer. It is what an evaluator is listening for.

**Q19. Do you use an accessibility overlay widget?**

> {{NO | YES — {{PRODUCT}}, used for {{SPECIFIC PURPOSE}}. We do not claim conformance through it.}}

Overlays do not deliver conformance, the EU has not endorsed them, and enforcement authorities favour source-code remediation. A vendor that uses one **and claims conformance through it** has told the evaluator something decisive about its judgement. If one is in use, describe the narrow purpose and disclaim conformance explicitly.

## Bank 5 — remediation and accountability

**Q20. Remediation process for a customer-reported barrier?**

> Reported via {{CHANNEL}}. Triaged within {{N}} business days, reproduced, assigned a severity by user impact — blocking a task ranks above friction — and scheduled by journey risk, with checkout, payment, and sign-in ahead of marketing surfaces. The reporter is updated at each stage.

**Q21. Response commitment?**

> {{N}} business days to acknowledge, {{N}} business days to a substantive response. This matches the commitment published in our accessibility statement at {{URL}}.

*Check before answering:* the number must match the published statement exactly. A mismatch is visible in two clicks and it undermines every other number in the response.

**Q22–Q24. Contract terms, warranties, indemnities, liability, committed remediation dates.**

> **{{FLAG FOR LEGAL REVIEW — DO NOT ANSWER FROM A QUESTIONNAIRE}}**

These are legal commitments. Answer with what the organisation is prepared to commit to commercially, escalate to counsel before anything is signed, and mark the row `PENDING LEGAL REVIEW` with a date rather than answering it.

Never commit a warranty, an indemnity, a liability position, or a contractual remediation date from a questionnaire response. A questionnaire is not the instrument for it, the person filling it in usually has no authority to bind the organisation, and an inconsistency between a questionnaire answer and the negotiated contract is a problem that surfaces at the worst moment.

Saying "this requires legal review, we can respond by {{DATE}}" is a **strong** answer. It tells the evaluator the vendor takes the commitment seriously enough not to improvise it.

## Bank 6 — standards and jurisdiction

**Q25. EN 301 549? Which version?**

> Mapped to EN 301 549 v{{VERSION}}. Chapter 9 carries the WCAG {{2.1}} mapping — clause numbering is `9.1.<SC>` for Level A and `9.2.<SC>` for Level AA. Chapters 4, 5, 10, 11, and 12 are reported in the attached EU-edition ACR. {{CONFIRM AGAINST THE TENDER: if it specifies a different version, say so and offer to re-map.}}

Mentioning chapters 10, 11, and 12 unprompted is a differentiator — most vendors report clause 9 only, and EU evaluators check that the document chapters were considered.

**Q26. Section 508? GSA Issue Detail Supplement?**

> Revised 508 Standards chapters 3 through 6, assessed against WCAG **2.0** Level A and AA as chapter 5 incorporates it. {{SUPPLEMENT: supplied where the solicitation requests it, keyed to its issue numbers — send us the supplement and we will complete it.}}

State the version difference explicitly: Section 508 references WCAG 2.0 (38 criteria), the EAA and EN 301 549 reference WCAG 2.1 (50). Conflating them is a visible, disqualifying error.

**Q27. Are you compliant with the European Accessibility Act?**

> {{PRODUCT}} version {{VERSION}} was assessed on {{DATE}} against WCAG 2.1 Level A and AA and mapped to EN 301 549 v{{VERSION}}. Conformance status is {{PARTIALLY CONFORMANT}}, with {{N}} criteria fully conformant, {{N}} partially, and {{N}} not evaluated with closing tests scheduled {{DATE}}. Our accessibility statement is published at {{URL}}.
>
> Whether the EAA applies to a given deployment is a legal question turning on your use of the product, your establishment, and your market. We supply the conformance evidence; applicability should be confirmed by your counsel.

This is the answer most vendors get wrong, in both directions — either a bare "yes, we are EAA compliant", which is a legal conclusion no vendor can properly declare, or a refusal to engage. The pattern above separates what is verifiable (the product's conformance against a named standard and version) from what is not the vendor's to declare (applicability of a directive to a buyer's use). It answers precisely and it does not overreach.

**Q28. Which member states?**

> Our conformance evidence is standard-based — WCAG 2.1 AA and EN 301 549 — and is not state-specific. National transposition of the directive differs by member state. Our statement names the enforcement authority for {{STATE}}; for others we can supply the technical evidence and your counsel should confirm the national position.

**Q29. ADA / US exposure?**

> {{PRODUCT}} is assessed against WCAG 2.1 AA, which is the benchmark US courts and demand letters reference for ADA Title III web claims. We hold {{SECTION 508 ACR WHERE APPLICABLE}}. ADA exposure is a legal question for your counsel; we supply the conformance evidence.

**Q30. OpenACR or machine-readable format?**

> Yes. We supply the ACR as OpenACR YAML alongside the human-readable report, populated from the same source data so the two cannot disagree. Schema version {{VERSION}}.

Almost nobody answers yes to this. Where the export exists, attach it — it lets a buyer ingest the report into their own tooling and it is the clearest available signal that the vendor works to the current standard rather than filling in a Word template.

## Answering when no ACR exists

Common, and survivable if handled honestly. Do not fabricate one under deadline.

> We do not yet hold an issued ACR for {{PRODUCT}}. A static source audit against WCAG 2.1 Level A and AA was completed {{DATE}}, identifying {{N}} findings across {{JOURNEYS}}; assistive-technology testing to close the remaining criteria is scheduled {{DATE}}. We expect to issue an ACR on {{DATE}}.
>
> In the interim we can supply: the audit findings with criterion mapping and remediation dates, our published accessibility statement, our CI regression-gate configuration, and our remediation process. We will not state a conformance level we have not tested.

The last sentence is what makes this answer work. An evaluator who has been handed an unsupported "fully compliant" by three other vendors reads it as competence.

## Reuse workflow

1. **Load the current issued ACR and the published statement before answering anything.** Never work from a previous response.
2. Substitute real values into the pattern. No field left from another product.
3. Run the consistency checklist — version, dates, status wording, criterion counts, limitation wording, response commitment.
4. Flag every legal question for counsel with a response date rather than answering it.
5. Verify every URL in the response is live and public before sending.
6. Save the completed response into the bank with the deal reference and date, so the next response can be reconciled against it.
7. When the ACR is re-issued, mark every stored response referencing the prior version as **stale**. A reused stale answer is the most common consistency failure in this workflow, and it is entirely avoidable.
