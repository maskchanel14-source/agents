# Repo Patterns — how this owner's projects are built

## Observed patterns
1. **Single-purpose micro-sites.** One offer per site, one page doing the heavy lifting (Small Signal audit, Nudgely waitlist). Clarity Audit follows: one free tool, one job.
2. **Static-first, zero-backend.** GitHub Pages hosting, no build step, hand-rolled CSS design tokens (`--bg`, `--ink`, `--line`…), system+Google font pairing, dark-ink-on-paper aesthetic, generous whitespace.
3. **SEO-conscious from day one.** Canonicals, OG tags, JSON-LD, sitemap.xml, robots.txt, favicon discipline.
4. **Audit/checklist as the product wedge.** Free scored self-assessment → trust → paid depth. The Clarity Audit is the direct evolution of the 12-Point AI Ops Audit pattern (0–3 anchors there, 25-check rubric here).
5. **Honest, anti-hype copy voice.** "No course, no call, no 7-email drip you didn't ask for." The site copy style guide inherits this: plain claims, published methodology, no fake proof.
6. **Python tooling conventions in `agents`** (uv, ruff, ty, Makefile quality gates: `validate`, `garden`, `test`, `smoke-test`) → mirrored here in JS terms: `npm run test` / `typecheck` / `lint` / `build` as the pre-push gate, documented in README.

## Anti-patterns to avoid for this owner
- Heavy multi-service architectures they'd have to babysit.
- Anything requiring manual server ops. Managed hosting only (Vercel/Cloudflare + Supabase).
- Framework churn. Boring, documented choices.
