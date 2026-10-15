# EAA Compliance

**European Accessibility Act compliance work, from legal scope to the document the buyer actually asks for.**

The EAA has applied since **28 June 2025**. WCAG 2.1 Level AA is now a legal requirement for anyone selling products or services to EU consumers — regardless of where the business is headquartered. WebAIM found detectable WCAG 2 failures on **95.9%** of the top one million home pages, averaging **56.1 errors per page**. Surveys put EAA readiness at **3.7%**, with **18.5%** of businesses unaware the law exists.

Meanwhile the documentation that proves compliance is priced out of reach for most of them: a manual audit runs **€319 to €25,000**, and an Accessibility Conformance Report costs **$350 to $25,000** depending on who writes it.

This plugin does the work in between.

## What it is not

This is not another axe-core wrapper. Automated scanning detects roughly a **quarter to a third** of WCAG issues, and every serious practitioner says so. This plugin does not pretend otherwise — it is explicit about what static analysis proves and what it cannot, and it never lets an untested criterion become a conformance claim.

It is the **legal deliverable layer**: scope determination, evidence-backed audit, the mandated accessibility statement, the ACR procurement teams require, and the answers to the questionnaire that arrives with every enterprise deal.

## Install

### Claude Code

```text
/plugin marketplace add maskchanel14-source/agents
/plugin install eaa-compliance@claude-code-workflows
```

### Cursor

Cursor reads the plugin's agents and skills directly from the repository. Add the marketplace and install as above, or point Cursor at a local clone.

### Other harnesses

The plugin is authored once in the shared Markdown source format and generated for **Codex CLI, OpenCode, Antigravity CLI, GitHub Copilot, and Pi** by the repository's adapter framework. See the root `README.md` for per-harness installation.

## Commands

| Command | What it does |
|---|---|
| `/eaa-compliance:scope-check` | Does the EAA apply here? Scope, microenterprise exemption, member-state exposure, next step |
| `/eaa-compliance:audit` | Static audit of the codebase against WCAG 2.1 AA and EN 301 549, prioritised by revenue-journey risk |
| `/eaa-compliance:remediate` | Sequenced remediation plan, evidence log, third-party ownership split, CI regression gate |
| `/eaa-compliance:statement` | The EAA-mandated Accessibility Statement, in EN, DE, FR, ES, IT, or NL |
| `/eaa-compliance:acr` | Accessibility Conformance Report on VPAT 2.5Rev — WCAG, EN 301 549, Section 508, or INT edition, with OpenACR YAML export |

## Agents

| Agent | Role |
|---|---|
| `eaa-compliance-advisor` | Legal scope, jurisdiction, penalty and market-exclusion exposure, disproportionate-burden justification |
| `eaa-codebase-auditor` | Framework-aware static audit with findings mapped to file and line, and honest `MANUAL REQUIRED` marking |
| `eaa-documentation-author` | Statements, ACRs, remediation plans, evidence logs, procurement answer banks |

## Skills

| Skill | Covers |
|---|---|
| `eaa-legal-scope` | Directive (EU) 2019/882 scope, Article 4(5) microenterprise exemption, Article 32 transition, member-state table, the Carrefour precedent |
| `en-301-549-mapping` | Full WCAG 2.1 SC-to-clause mapping for all 50 A and AA criteria, version discipline, clauses 4–12 |
| `wcag-codebase-audit` | Framework patterns and fixes for Next.js/React, Vue, Svelte, Angular, Shopify Liquid, WordPress/WooCommerce, Astro; findings JSON schema; CI patterns; manual-test protocol |
| `accessibility-statement-eu` | All nine mandatory elements, defensible conformance wording, national authority table, publication checklist, six language templates |
| `acr-vpat-authoring` | Per-edition table structures, remark patterns, OpenACR export, re-issue policy, the eleven causes of rejection |
| `procurement-answers` | The thirty questions buyers actually ask, with model answers, traps, and the legal-question escalation rule |

## Language templates

Native-register drafts, not translations of the English — escalation conventions and legal phrasing differ by country:

`assets/statement.en.md` · `statement.de.md` · `statement.fr.md` · `statement.es.md` · `statement.it.md` · `statement.nl.md`

Every template is a **drafting scaffold with placeholders**. Each must be reviewed for the specific member state, and where exposure is material, by counsel.

## The discipline this plugin enforces

Three rules run through every agent, command, and skill. They are the reason the output is usable rather than decorative.

**1. Never overstate conformance.** A single unsupported "Supports" is worse than an honest "Partially Supports". Overstatement turns a routine procurement question into a misrepresentation problem. Criteria requiring assistive-technology testing are recorded as **Not Evaluated** with a dated closing test — never guessed.

**2. Never invent a citation, a fine figure, an authority name, or a deadline.** National transposition differs by member state and was still being amended and litigated through 2025–2026. Anything unconfirmed is marked `VERIFY` with the authority to check against. A marked gap gets filled in an afternoon; a confident fabrication is discovered at the worst possible moment and discredits every other number in the document.

**3. Never fabricate a contact route.** A statement with a dead feedback address is worse than no statement, because it creates an obligation the organisation is already failing and hands a complainant a documented breach.

## Why partial conformance is the honest answer

On **4 June 2026** the court in Caen ordered Carrefour to make its website and application accessible within six months, with daily penalties for delay. Carrefour argued it already met **71%** of the French accessibility criteria. The court held the store had to be **fully** accessible.

Partial compliance is not a safe harbour — but neither is claiming full conformance on the strength of a green automated scan. A statement saying "partially conformant" with a dated remediation plan is more credible and more defensible than an inflated claim, and it is what an evaluator who has been burned before will believe.

## Framework coverage

Audit patterns and fixes are specific, not generic: **Next.js and React** (App Router metadata, icon-only buttons, `outline-none`, hydration-aware live regions), **Vue** (`v-html`, i18n `lang`), **Svelte** (`svelte-ignore a11y-` dismissals as high-confidence findings), **Angular** (CDK primitives versus hand-rolled), **Shopify Liquid** (merchant-owned versus the checkout extensibility surface merchants cannot modify), **WordPress and WooCommerce** (page-builder output, gateway iframe boundaries, consent-plugin focus traps), **Astro** (island boundaries).

Every finding carries an `owner` of `client`, `third-party`, or `platform` — because a remediation plan that includes work the team cannot perform stalls in week two, and a conformance claim covering a surface the vendor does not control is a misrepresentation.

## What it produces

| Artefact | File |
|---|---|
| Scope assessment | `eaa-scope-assessment.md` |
| Audit findings | `eaa-audit-findings.md`, `eaa-audit-findings.json` |
| Remediation plan | `eaa-remediation-plan.md` |
| Evidence log | `eaa-evidence-log.md` |
| Accessibility statement | `accessibility-statement.<lang>.html`, `.md` |
| ACR | `acr-<product>-<edition>.md`, `.html`, `.yaml` (OpenACR) |
| Disproportionate-burden justification | `eaa-disproportionate-burden.md` |

## Not legal advice

This plugin produces **technical and documentation work product** from a codebase and a declared standard. It is not legal advice and it is not a certification of conformance — only an independent evaluator can certify conformance.

Jurisdiction-specific figures, authority names, and deadlines are drawn from practitioner guidance and national implementation reporting and are marked as requiring confirmation against the official national instrument. Any legal question about the applicability of Directive (EU) 2019/882, the Revised 508 Standards, or another instrument should be confirmed by a qualified lawyer in the relevant jurisdiction.

## License

MIT.
