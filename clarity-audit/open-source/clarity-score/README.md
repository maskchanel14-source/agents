# clarity-score (open core)

Score a landing page's HTML against a transparent **25-check / 100-point clarity rubric** — the same engine behind the free hosted [Clarity Audit](https://clarity-audit-five.vercel.app). Pure function, zero dependencies, MIT licensed.

> Would a stranger understand the offer in 5 seconds? This library checks the structural signals: headline outcome + audience, CTA placement and wording, proof, price transparency, FAQ, form friction, and mobile basics. Every finding cites evidence found in the HTML and ships a concrete fix.

## Install

Copy `index.mjs` into your project (single file, no build step), or vendor this folder. Canonical source (until the standalone repo is published): https://github.com/maskchanel14-source/agents/tree/main/clarity-audit/open-source/clarity-score

> Owner note: standalone-repo creation was blocked by integration permissions on 2026-10-18. To publish: `gh repo create clarity-score --public` from a clone of this folder (2 min), then update this link.

## Usage

```js
import { analyzeHtml } from "./index.mjs";

const html = await (await fetch("https://example.com/landing")).text();
const { score, checks, pageFacts } = analyzeHtml(html, { url: "https://example.com/landing" });

console.log(score); // 0–100
for (const c of checks.filter((c) => c.status !== "pass")) {
  console.log(`${c.label}: ${c.evidence} → ${c.fix}`);
}
```

Ideas: CI check for marketing pages, pre-launch gate in a page builder, agency client audits, template-marketplace quality bar.

## The rubric (weights)

| Category | Points | Checks |
|---|---|---|
| Message clarity | 25 | H1 present · glance-length · outcome language · audience named · title↔H1 match |
| CTA & next step | 20 | CTA present · early · specific · repeated |
| Trust & proof | 15 | social proof · contact · privacy · human presence |
| Offer transparency | 15 | price visible · deliverables · FAQ · risk reversal |
| Form friction | 10 | form exists · short form · email capture |
| Mobile & basics | 15 | viewport · HTML weight · alt text · HTTPS · response time |

Full methodology with evidence rules and stated limits: see the hosted site's `/methodology` page.

## Honest limits

Automated checks read HTML structure, not rendered design or real conversion data. Client-side-rendered content may be under-credited. A high score means "a cold visitor can understand this fast" — it guarantees nothing about demand or revenue.

## Hosted version

The hosted **Instant Website Clarity Audit** adds: an SSRF-hardened fetcher, shareable result pages with Open Graph images, score badges/widgets, and paid reports with headline/CTA rewrites and a 7-day fix plan. Free score, no email required. [clarity-audit-five.vercel.app](https://clarity-audit-five.vercel.app)

## License

MIT — see `LICENSE`. Use it anywhere; don't use it to fake scores or mislead buyers (that's on your conscience and, in many places, the law).
