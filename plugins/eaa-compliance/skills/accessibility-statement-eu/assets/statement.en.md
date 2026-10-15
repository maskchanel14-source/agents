# Accessibility Statement (EN)

> **Template.** Replace every `{{PLACEHOLDER}}`. Delete this note before publishing. Do not invent the feedback contact, the response commitment, or the enforcement authority — mark any missing value `CLIENT MUST SUPPLY` and resolve it before publication.

---

# Accessibility statement for {{PRODUCT_NAME}}

{{ORGANISATION_LEGAL_NAME}} is committed to making {{PRODUCT_NAME}} accessible to the widest possible audience, including people with disabilities. This statement describes the accessibility status of {{PRODUCT_NAME}}, the known limitations, how to report a problem, and how to escalate a complaint.

**Applies to:** {{SCOPE — website, application, service, and version}}
**Statement date:** {{DATE_PUBLISHED}}
**Last reviewed:** {{DATE_REVIEWED}}
**Last assessed:** {{DATE_ASSESSED}}

## Standard and conformance status

This {{WEBSITE | APPLICATION | SERVICE}} is assessed against the **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA**{{, and EN 301 549 where applicable}}.

**Conformance status: {{FULLY CONFORMANT | PARTIALLY CONFORMANT | NOT CONFORMANT}}.**

{{IF PARTIALLY CONFORMANT — state it plainly and list what fails:}}
The following areas do not yet fully meet the standard. Each has an owner and a target date:

| Area | Limitation | Owner | Target date |
|---|---|---|---|
| {{AREA}} | {{LIMITATION}} | {{CLIENT / THIRD PARTY / PLATFORM}} | {{DATE}} |

{{IF CRITERIA WERE NOT EVALUATED — say so:}}
The following criteria were not evaluated during the last assessment and are recorded as **Not Evaluated** rather than assumed conformant: {{LIST}}. Testing to close these is scheduled for {{DATE}}.

## Known limitations

{{LIMITATIONS — be specific and name the responsible party. Never imply control over a surface you do not control.}}

- **{{THIRD_PARTY_COMPONENT}}** is provided by {{VENDOR}} and rendered outside our control. {{DESCRIBE THE BARRIER}}. We have requested remediation in writing on {{DATE}} and are {{EVALUATING ALTERNATIVES | AWAITING A RESPONSE}}.
- **{{PLATFORM_SURFACE}}** — for example a hosted checkout or payment frame — is not modifiable by us. {{DESCRIBE THE LIMITATION}}.

## What we do to maintain accessibility

- {{TESTING CADENCE}} — for example: automated WCAG 2.1 A and AA scanning in continuous integration on every release, with a fail-on-regression gate.
- **Manual testing** of the following customer journeys each release, using keyboard only and {{SCREEN READER AND VERSION}}: {{JOURNEYS — typically checkout, payment, sign-in}}.
- {{REMEDIATION PROCESS}} — how findings are triaged, prioritised, and closed.
- {{TRAINING}} — accessibility requirements for the design and engineering teams.

## Compatibility

{{PRODUCT_NAME}} is tested with the following combinations:

| Browser | Operating system | Assistive technology |
|---|---|---|
| {{BROWSER + VERSION}} | {{OS + VERSION}} | {{AT + VERSION, or "none"}} |

{{NOTE ANY KNOWN DEGRADATION IN AN UNTESTED COMBINATION, OR STATE THAT OTHER COMBINATIONS WERE NOT ASSESSED.}}

## Reporting a problem

If you encounter an accessibility barrier, or if you need information in a different format, contact us:

- **Email:** {{MONITORED_EMAIL}}
- **Form:** {{FORM_URL}}
- **Post:** {{POSTAL_ADDRESS}}

Please tell us the page or screen, what you were trying to do, and the browser and assistive technology you were using. **We aim to respond within {{N}} business days** and to propose a remedy within {{N}} business days of that response.

You may request any part of this content in an accessible alternative format at no cost.

## Escalation and complaints

If you are not satisfied with our response, you may complain to the competent authority:

{{NATIONAL AUTHORITY — take from references/details.md or mark VERIFY. Never invent an authority name.}}

- **Authority:** {{AUTHORITY_NAME}} `{{VERIFY — confirm against the current national instrument}}`
- **Contact:** {{AUTHORITY_CONTACT}}
- **Basis:** {{NATIONAL_INSTRUMENT_CITATION}} transposing Directive (EU) 2019/882

{{WHERE APPLICABLE, note alternative dispute resolution or the consumer complaint route available in this member state.}}

## About this assessment

- **Method:** {{METHOD — automated scanning, static source analysis, manual keyboard testing, screen-reader testing, and by whom}}
- **Assessed by:** {{ASSESSOR — internal team, named vendor, or "self-evaluation"}}
- **Scope:** {{ROUTES, TEMPLATES, AND VERSIONS ASSESSED}}
- **Excluded:** {{WHAT WAS NOT ASSESSED, AND WHY}}

This statement is documentation produced from technical assessment. It is not a certification of conformance and it is not legal advice. Only an independent evaluator can certify conformance, and any legal question about the applicability of Directive (EU) 2019/882 should be confirmed by a qualified lawyer in the relevant member state.

---

**{{ORGANISATION_LEGAL_NAME}}** · {{CONTACT_PAGE_URL}} · This statement was published on {{DATE_PUBLISHED}}.
