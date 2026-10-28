# Cycle 001 — ScopeReply pre-build decision

Recorded: 2026-10-28, before product implementation.

## Four required answers

1. **WHO exactly will pay?** Solo web designers and two-person web studios serving direct clients on fixed-fee projects, with at least two active projects and an existing paid engagement. They already quote extra work but write the approval message from scratch. Not consumers, hourly-only contractors, enterprise procurement teams, or people looking for a lawyer.
2. **WHERE are they complaining right now?** Public Reddit discussions in r/web_design and adjacent r/webdev communities. Recent examples include a client changing half an approved project (April 2026), a redesign after approval (March 2026), and a freelance client withholding payment while expanding scope (May 2026). These are historical complaints indexed today, not live conversations we have joined. Sources: `PAINS.md`.
3. **HOW will we reach them in 24h without spam?** ONE channel: Reddit, specifically r/web_design. Offer a useful, fictional change-order example in a permitted feedback thread or one moderator-approved feedback post. Disclose that we make it. Ask whether the buyer would pay $19, with a link to an explicit launch-interest form. No automated comments, unsolicited DMs, vote manipulation, fake accounts, or repeated posts. **Execution is currently blocked: no Reddit publishing connector/account is available, and the subreddit rules page returned HTTP 403. Zero people have been contacted. The 24-hour acquisition test is not complete.**
4. **WHY will they pay $9–$29 today?** Proposed offer: **$19 USD, one-time personal license**, unlimited locally generated change orders. Turn an extra request into a clear email plus a printable cost/schedule/approval record; offer pay, swap, or phase-two choices. No subscription, account, client-data upload, or AI credits. The value is finishing an uncomfortable admin task now, not a promise to recover money. A free sample is marketing, not a free-forever full product.

## Validation contract

- Research complaints are **signals**, not commitments.
- A qualified commitment is a distinct prospective buyer explicitly agreeing to the $19 offer, with a way to notify them when checkout opens. A like, email signup without price agreement, or our own message does not count.
- Gate A: three qualified commitments before 2026-10-30 21:05 UTC, the conservative hard stop 48 hours after experiment creation. Record the actual first-post time separately; never extend the deadline silently.
- Gate B: before calling the product validated, the first three customers must actually pay. Payment-provider receipts, not form submissions, establish revenue.
- If three commitments cannot be obtained within 48 hours, stop product work and record the reason. Distinguish an untested offer from an offer the market rejected.
- No full product implementation before Gate A. A sales-validation page and studio operations code are allowed; they are not the MVP.
- No invented checkout, payment confirmation, testimonials, customer counts, or revenue.

## Before-you-build pre-mortem

**Risk verdict: HIGH.** The pain is well evidenced; willingness to pay for another lightweight tool is not.

**Main assumption:** Designers who already know they should use change orders will pay $19 for a faster, private workflow rather than use a free template, a chatbot, or their existing project-management tool.

**Evidence to find first:** Three explicit $19 commitments from the stated buyer segment, followed by three real payments.

**Do next:** Publish one permitted, disclosed Reddit feedback offer; collect price-specific consent; keep the product unbuilt until the gate passes.

**Delay:** The generator, accounts, AI integrations, team permissions, client portal, e-signatures, invoice collection, and additional acquisition channels.

## Competition and positioning

- ScopeShift advertises $9/month, AI change orders, approvals, and payment collection: [2](https://www.scopeshift.cc/).
- Kivo is an open-source, local-first scope/change-order project: [1](https://github.com/Txxjasss/Kivo).
- ScopeGuard advertises inexpensive spreadsheets and email scripts: [3](https://scopeguardstudio.github.io/).
- Free templates and a manually written email remain the strongest substitutes.

Positioning hypothesis: **the private, one-task change-order desk for a designer who does not want another subscription or client portal.** This is differentiation to test, not a claim of uniqueness. Do not advertise AI-generated scope judgments or legally enforceable contracts.

## Smallest eventual MVP (not built)

One local workspace: original deliverable, new request, hours/rate or fixed fee, schedule impact, and approval deadline. Produce a client email, a print-ready change record, and a plain-text file. User explicitly reviews all wording and prices. Browser storage only, with an export/erase control. No backend storage of client requests. Price and payment activation remain separate gates.

## Commercial readiness audit

- Vercel and Supabase are connected.
- No Stripe connector or payment credential was found in the inspected product environments.
- The connected Gmail contains Gumroad reminders dated October 16 and 19 requesting more information to process payouts. This proves a payout-information blocker, **not** that new checkout is disabled; checkout capability has not been verified.
- A $0 product download is not a sale and is excluded from revenue.
- Do not request identity documents, bank details, or credentials in chat.
- Checkout stays unavailable until a real provider product and payment path are verified. The validation page must say so.

## Skills used for this decision

GitHub source: `maskchanel14-source/agents`, branch `arena/1318282f-agents`.

- `tools/skill_router.py plan` and `search`: routed the task; broad automatic matches were not treated as domain expertise.
- `plugins/before-you-build/skills/before-you-build/SKILL.md`: risk checklist, smallest validation, delayed scope.
- `plugins/startup-business-analyst/skills/competitive-landscape/SKILL.md`: substitutes and positioning.
- `plugins/payment-processing/skills/stripe-integration/SKILL.md`: hosted checkout, server-side prices, verified payment events; no payment integration activated without credentials.
- `gh auth status`, `gh repo view`, `gh issue list`: verified GitHub access and repository permissions; issues are disabled, so Linear is the work tracker.

Restoration caveat: the required `npx skills experimental_install` command was attempted and timed out after partially restoring 14 of 256 locked skills. The command was not duplicated. Relevant repository-local skills were available and read directly. No claim is made that all locked skills were restored.
