# Harvey audit of the 20 sends

Repo: `ethanplusai/harvey` v0.3.0, MIT, commit `4237f07`, read 29 October 2026.
Vendored, unmodified, at `vendor/harvey/`. Wrapper: `pre_send_gate.py`.
Written 30 October 2026.

## What the audit is

Harvey is a cold-email engine with a deterministic gate in `harvey/gate.py`:
banned phrases, do-not-contact matching, link discovery. On top of it sits a set
of writing rules in `prompts/writer.md` and `skills/email_frameworks.md` that the
gate never checks. `pre_send_gate.py` runs both layers, so a draft has to clear
Harvey's hard checks *and* the rules Harvey only writes down. 12 self-tests, 12
passing.

I ran it against what actually went out on 28 October.

## The finding that matters

**All 20 emails broke Harvey's word target by roughly 2.7x.**

| | v1, as sent | Harvey rule |
|---|---|---|
| Body length | 180 and 206 words (ConnectBooks, James Scott) | under 75 for email 1 |
| Questions | 2 | exactly 1 |
| Links | 1, with a tracking parameter | 0 is better; tracking costs 8 to 12% of inbox placement |
| CTA | "Worth a look?", "Interested?" | must be answerable in four words |
| Postal address | **none** | `compliance.postal_address` is required before the first campaign |

The two bodies above are the ones I pulled back from the mailbox. The other 18
were built from the same skeleton with the opening and the `?src=` value swapped,
so the length, the question count and the link are structural, not accidental.

Two of those four failures are cosmetic. One is not:

**Every one of the 20 went out with no physical mailing address in the footer.**
That is the CAN-SPAM requirement Harvey's README calls out before a first
campaign, and I shipped without it. Stockholm-syndrome exception: an opt-out line
was present, and Harvey treats opt-out as permanent, so the harm is a compliance
gap rather than a spam complaint. It still has to be fixed before the next send,
which is why nothing new goes out until it is.

## The second finding: my own gate was wrong twice

Writing the drafts exposed two bugs in `pre_send_gate.py`, both now fixed and
covered by tests:

1. The markdown `---` between drafts was being read as part of the body, so the
   last draft in every file failed the em dash check on a horizontal rule.
2. Harvey's own default opt-out line (*Not interested? Reply "no thanks"…*) is
   itself a question, so literal question counting failed every compliant email.
   The opt-out is now excluded from the CTA count, and a missing opt-out is
   reported instead. Follow-ups in an existing thread are exempt from the footer,
   which matches what Harvey does when it sends.

Point 2 is worth recording because it is the kind of thing that gets a good draft
rewritten to satisfy a bad rule. The fix belongs in the gate, not in the copy.

## What changed in the copy

`DRAFTS-v2.md`, 10 drafts, all passing, 53 to 70 words:

- **One question, and it is about them.** "Who is rebuilding that history for your
  Shopify clients?" replaces "Worth a look?".
- **No links at all in a first email.** This costs attribution: with no `?src=`
  there is no query string telling me which draft produced a reply. That trade is
  deliberate, and the answer is that replies get asked about instead of tracked.
- **The studio name appears once, in the signature.** Harvey's rules keep the
  product out of email 1.
- **A specific hook per recipient** off their own site copy: Unloop's "only
  accounting firm serving inventory businesses", ShipCalm's onboarding, SHIPHYPE's
  48 hour receiving SLA, Encore's UPC scan against expected inbounds.
- **One number doing the work in all of them:** suppliers never had an export, and
  the purchase order history stopped on 31 August. Nothing else in the email needs
  to be believed for the question to land.

## Does this explain zero replies?

Partly, and it is the most useful thing the gate told me. 20 sends with no reply
on day 2 is inside normal range for cold outreach (5% reply would be one reply), so
zero is not evidence of anything by itself. But a 200-word email with two questions
and a vague CTA has two ways to die: too long to finish, and no single thing to
answer. The rewrite removes both, so the 31 October and 4 November follow-ups, and
batch 3, test the copy rather than the list.

## Decision

The 20 sent emails are **not** re-sent. Harvey's rules allow at most 3 emails per
recipient per 30 days, and a resend of the same pitch in the same week reads as a
burst. The fix ships forward instead:

1. Follow-ups on 31 October and 4 November use the v2 follow-up drafts, 38 and 21
   words, one question, no footer on the threaded reply.
2. Batch 3's seven targets get v2 first emails, not the v1 template.
3. No further cold email goes out until the postal address line is real.

## Files

- `vendor/harvey/` — the parts of the repo this depends on: `skills/`, `prompts/`,
  `harvey/gate.py`, licence and README.
- `pre_send_gate.py` — the wrapper. `python3 pre_send_gate.py FILE.md`, `--text`,
  `--selftest`, `--postal`.
- `DRAFTS-v2.md` — 10 drafts, 10 clean.
