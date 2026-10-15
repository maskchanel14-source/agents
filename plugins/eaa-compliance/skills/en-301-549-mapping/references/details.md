# EN 301 549 Mapping — Reference Detail

Loaded on demand from `../SKILL.md`. Full WCAG 2.1 SC-to-clause mapping, version differences, clause-4 functional performance, clause-10 documents, and the verification procedure.

## Version discipline

EN 301 549 has been revised several times and the referenced WCAG version changed between revisions. Commonly cited: **v2.1.2 (2018)** referencing WCAG 2.0; **v3.1.1 (2019)** and **v3.2.1 (2021)** referencing WCAG 2.1. Later revisions moving the reference to WCAG 2.2 have been in progress — **confirm which version the buyer's tender specifies before mapping**, and record the version in the report header.

Report the version you mapped against. Producing a v3.2.1 mapping when the tender specifies v3.1.1 is a rejection, and the two differ in referenced WCAG level and clause detail.

Where a buyer says only "EN 301 549", use v3.2.1 as the current widely-cited edition, state that you did, and note that the tender documents should be checked.

## Clause structure

The VPAT 2.5Rev **EU edition** mirrors the EN 301 549 clause numbering directly, which is what makes the mapping mechanical:

| Chapter | Clause | Subject |
|---|---|---|
| Functional Performance Statements | **4** | What the product must enable across vision, hearing, cognition, manual dexterity |
| Generic Requirements | **5** | Multiple modalities, no photosensitive-seizure triggers |
| ICT with Two-Way Voice Communication | **6** | Covered communications products only |
| ICT with Video Capabilities | **7** | Captions, audio description, sign language |
| Hardware | **8** | Covered products only; not web |
| **Web** | **9** | Incorporates WCAG 2.1 A / AA / AAA at 9.1 / 9.2 / 9.3 |
| Non-Web Documents | **10** | PDFs, emails, statements, invoices |
| Software | **11** | Non-web software, and WCAG for software with a user interface |
| Documentation and Support Services | **12** | Accessible documentation and accessible support |

## Mapping rule

Prefix by level, then append the WCAG success-criterion number **verbatim**:

- Level A → `9.1.<SC>`
- Level AA → `9.2.<SC>`
- Level AAA → `9.3.<SC>`

The only error that matters is mis-assigning the level. Cite an AA criterion under `9.1.` and the clause does not exist in the standard.

## WCAG 2.1 Level A — 30 success criteria

| WCAG 2.1 SC | Name | EN 301 549 clause |
|---|---|---|
| 1.1.1 | Non-text Content | 9.1.1.1 |
| 1.2.1 | Audio-only and Video-only (Prerecorded) | 9.1.2.1 |
| 1.2.2 | Captions (Prerecorded) | 9.1.2.2 |
| 1.2.3 | Audio Description or Media Alternative (Prerecorded) | 9.1.2.3 |
| 1.3.1 | Info and Relationships | 9.1.3.1 |
| 1.3.2 | Meaningful Sequence | 9.1.3.2 |
| 1.3.3 | Sensory Characteristics | 9.1.3.3 |
| 1.4.1 | Use of Color | 9.1.4.1 |
| 1.4.2 | Audio Control | 9.1.4.2 |
| 2.1.1 | Keyboard | 9.1.2.1.1 |
| 2.1.2 | No Keyboard Trap | 9.1.2.1.2 |
| 2.1.4 | Character Key Shortcuts | 9.1.2.1.4 |
| 2.2.1 | Timing Adjustable | 9.1.2.2.1 |
| 2.2.2 | Pause, Stop, Hide | 9.1.2.2.2 |
| 2.3.1 | Three Flashes or Below Threshold | 9.1.2.3.1 |
| 2.4.1 | Bypass Blocks | 9.1.2.4.1 |
| 2.4.2 | Page Titled | 9.1.2.4.2 |
| 2.4.3 | Focus Order | 9.1.2.4.3 |
| 2.4.4 | Link Purpose (In Context) | 9.1.2.4.4 |
| 2.5.1 | Pointer Gestures | 9.1.2.5.1 |
| 2.5.2 | Pointer Cancellation | 9.1.2.5.2 |
| 2.5.3 | Label in Name | 9.1.2.5.3 |
| 2.5.4 | Motion Actuation | 9.1.2.5.4 |
| 3.1.1 | Language of Page | 9.1.3.1.1 |
| 3.2.1 | On Focus | 9.1.3.2.1 |
| 3.2.2 | On Input | 9.1.3.2.2 |
| 3.3.1 | Error Identification | 9.1.3.3.1 |
| 3.3.2 | Labels or Instructions | 9.1.3.3.2 |
| 4.1.1 | Parsing | 9.1.4.1.1 |
| 4.1.2 | Name, Role, Value | 9.1.4.1.2 |

Criteria added by WCAG 2.1 at Level A: **2.1.4, 2.5.1, 2.5.2, 2.5.3, 2.5.4**. If a prior audit was run against WCAG 2.0 it will have missed all five — check for this before reusing old findings, because a 2.0-era report claiming WCAG 2.1 coverage is wrong on its face.

## WCAG 2.1 Level AA — 20 success criteria

| WCAG 2.1 SC | Name | EN 301 549 clause |
|---|---|---|
| 1.2.4 | Captions (Live) | 9.2.1.2.4 |
| 1.2.5 | Audio Description (Prerecorded) | 9.2.1.2.5 |
| 1.3.4 | Orientation | 9.2.1.3.4 |
| 1.3.5 | Identify Input Purpose | 9.2.1.3.5 |
| 1.4.3 | Contrast (Minimum) | 9.2.1.4.3 |
| 1.4.4 | Resize Text | 9.2.1.4.4 |
| 1.4.5 | Images of Text | 9.2.1.4.5 |
| 1.4.10 | Reflow | 9.2.1.4.10 |
| 1.4.11 | Non-text Contrast | 9.2.1.4.11 |
| 1.4.12 | Text Spacing | 9.2.1.4.12 |
| 1.4.13 | Content on Hover or Focus | 9.2.1.4.13 |
| 2.4.5 | Multiple Ways | 9.2.2.4.5 |
| 2.4.6 | Headings and Labels | 9.2.2.4.6 |
| 2.4.7 | Focus Visible | 9.2.2.4.7 |
| 3.1.2 | Language of Parts | 9.2.3.1.2 |
| 3.2.3 | Consistent Navigation | 9.2.3.2.3 |
| 3.2.4 | Consistent Identification | 9.2.3.2.4 |
| 3.3.3 | Error Suggestion | 9.2.3.3.3 |
| 3.3.4 | Error Prevention (Legal, Financial, Data) | 9.2.3.3.4 |
| 4.1.3 | Status Messages | 9.2.4.1.3 |

Criteria added by WCAG 2.1 at Level AA: **1.3.4, 1.3.5, 1.4.10, 1.4.11, 1.4.12, 1.4.13, 4.1.3**.

**30 Level A + 20 Level AA = 50 criteria.** An ACR against WCAG 2.1 A and AA reports all 50. A report with 38 rows was built from a WCAG 2.0 list and is incomplete — this is the most common structural defect in reused reports and the fastest way for an evaluator to spot a recycled document.

## Clause 4 — functional performance statements

Clause 4 is answered differently from clause 9. It is not a list of criteria but a set of statements about what the product enables. Address each:

- **4.2.1** Usage without vision
- **4.2.2** Usage with limited vision
- **4.2.3** Usage without perception of colour
- **4.2.4** Usage without hearing
- **4.2.5** Usage with limited hearing
- **4.2.6** Usage with no or limited vocal capability
- **4.2.7** Usage without manipulation or with limited manipulation
- **4.2.8** Usage with limited reach and strength
- **4.2.9** Minimize photosensitive seizure triggers
- **4.2.10** Usage with limited cognition, language, or learning
- **4.2.11** Privacy

Answer each with what the product actually provides, cross-referenced to the clause-9 criteria that deliver it. Where the product does not provide the capability, say so and cross-reference the remediation commitment. Empty or boilerplate clause-4 answers are a common rejection reason in EU public procurement, because the evaluator uses clause 4 as the summary and reads clause 9 as the detail.

## Clause 10 — non-web documents

Every PDF, invoice, order confirmation, contract, statement, and marketing email is in scope. This is where businesses that pass a website audit fail immediately, because their documents were never authored accessibly.

Remediation checklist for a PDF:

- tagged, with a logical reading order and a correct heading structure
- document language set
- a real title in document properties, not the filename
- all images with alternative text; decorative images marked as such
- tables with header rows identified and repeated across page breaks
- sufficient contrast; no information conveyed by colour alone
- no images of text where real text would work
- form fields labelled, with tooltips where instructions are needed
- security settings that do not block assistive technology from reading or extracting content
- links with descriptive text

**The accessibility statement is itself a clause 10 document.** Publishing it as an untagged PDF is a self-inflicted conformance failure and an obvious target for a complaint. Publish HTML first; supply a conforming PDF alongside it only if a buyer requires one.

## Clause 11 — software

Where the product includes native mobile or desktop software, the requirements arrive through clause 11, not clause 9. A web-only audit does **not** cover the iOS or Android application, and the report must say so explicitly rather than letting the reader assume coverage.

For software with a user interface, clause 11 applies the WCAG-equivalent requirements. For non-interactive components, the platform accessibility services and authoring-tool requirements apply. Establish which parts of the product are in scope before assigning any level.

## Clause 12 — documentation and support services

Two requirements almost never assessed, and almost always failing:

- **documentation** must be available in accessible formats on request, and must describe the product's accessibility features and how to use them
- **support services** must be able to help users with disabilities — an accessible product reached through an inaccessible support channel is a documented gap

Support teams are outside the engineering organisation, are never in the audit scope by default, and routinely cannot handle an accessibility enquiry. Raise this early. It is cheap to fix — a documented escalation route and brief training — and expensive to discover during procurement.

## Verification procedure

Before any clause number enters a client document:

1. Confirm the **EN 301 549 version** required, from the tender or the buyer's request.
2. Confirm the **WCAG version and level** that version references.
3. For each criterion, confirm the **level** (A or AA) from the WCAG specification, then apply the prefix rule.
4. Spot-check a sample of at least five clause numbers against the standard's own table of contents — including one from each of clauses 9.1 and 9.2.
5. Confirm the row count: 30 Level A, 20 Level AA, 50 total for WCAG 2.1 A and AA.
6. Record the version, the WCAG level, and the mapping date in the report header.

Never emit a clause number from memory. A mis-cited clause is survivable in a draft and fatal in a submitted report, because it is the first thing a knowledgeable evaluator checks.
