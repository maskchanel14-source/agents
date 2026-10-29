---
status: 待执行
date: 2026-10-29
author_model: Arena Agent
acceptance: hard
workspace_mode: same-workspace
branch: arena/35ab5ba1-agents
---

# Handoff: outreach pipeline for the purchasing audit service

**交接目的**: let a fresh session continue the outreach pipeline without re-deriving
the research, the sending limits, or the decisions already made, and without
repeating a send that has already gone out.

> **接手方须知**: you are picking up a live outbound pipeline. Read this document
> top to bottom. The truth about what has been sent is `outreach/ledger.json`, not
> any narrative, including this one. If the two disagree, the ledger wins and you
> should fix the narrative.

---

## 最小验收锚点

The handoff succeeded if every line below is true when checked against the repo,
not against memory:

1. `python3 po-pilot-launch/outreach/send-budget.py status` exits 0 and reports
   `total sends` equal to the number of entries in `ledger.json`.
2. No address appears twice in `ledger.json`, and no domain appears twice within
   any rolling 7 day window.
3. Every send after 2026-10-28 carries a `message_id` that exists in Gmail Sent.
4. No email body links to `smallsignalstudio.com`. That domain belongs to an
   unrelated developer; see `SENDING-POLICY.md` section 8.
5. Follow-ups were sent no earlier than day 3 (2026-10-31) and day 7 (2026-11-04),
   and no follow-up went to an address that had already replied.
6. The sender display name on every send is `Small Signal Studio`, not a personal
   name.

## 背景与现状

The money goal is 1,500 USD inside 30 days, and the route chosen is the fixed-fee
purchasing audit sold as a subcontract to ecommerce accountants and fractional
CFOs, not to design agencies. Design agencies hand a store back at launch and never
touch a purchase order again, which is why the first instinct was wrong.

Twenty emails have gone out to twenty distinct domains, between 19:43 and 20:46 UTC
on 28 October 2026. Zero bounces, zero replies. Reply counts at this volume are
expected to be 0 or 1; the informative events are the day 3 and day 7 follow-ups.

The market gap being sold: replacement apps are crowded and cheap (Stockful 19.99,
Monocle 47, Prediko 49, ReplenishRadar 99, Cin7 349 per month) and every one of them
sells a new system to run from now on. None rebuilds the history that already
existed, because that is labour rather than software.

## 关键决定（别改动）

- **Buyer is the accountant, not the agency.** Already settled in
  `PARTNER-RESEARCH.md`. Do not re-open.
- **The offer is a white-label subcontract at a fixed fee**, where the firm keeps
  the client and bills the output as its own work. Not a hire-me pitch.
- **Sender identity stays Small Signal Studio from
  `smallsignalstudiolife@gmail.com`. Domain purchase is deferred.** Owner decision,
  29 October, recorded in `SENDING-POLICY.md` section 8. Do not re-litigate it, and
  never treat `smallsignalstudio.com` as ours.
- **Sending ceiling: 20 per day, 3 minute gap, 15 per hour, 40 absolute.** Owner
  asked for 20 in 24 hours and the phase-1 budget was raised to match. The gap and
  the stop rules were not loosened.
- **No claim that anything has been sold.** The only Polar transaction is the
  owner's own test at 0.00.

## 范围铁律

- Never send to a domain already in the ledger within the same week.
- Never send a fourth email to anyone. Three is the cap per person per 30 days.
- One spam complaint means a 7 day stop and a review of the sourcing criteria, not
  a reduced rate.
- Do not invent an address. If a firm publishes only a form, it is skipped. This is
  why Intrepid Advisory, Brankit and ShipHype's contact-form-only peers were dropped.
- Do not touch the Vercel site or the Supabase tables as part of outreach work.

## 相关文档索引

| File | What it holds |
| --- | --- |
| `po-pilot-launch/outreach/ledger.json` | The only authoritative send record |
| `po-pilot-launch/outreach/SENDING-POLICY.md` | Limits, stop rules, sender identity, domain audit |
| `po-pilot-launch/outreach/PARTNER-RESEARCH.md` | Sourcing, price anchors, who was rejected and why |
| `po-pilot-launch/outreach/TARGETS-BATCH-3.md` | Seven verified targets, not yet sent |
| `po-pilot-launch/outreach/SENT-2026-10-29.md` | Day 3 and day 7 follow-up copy |
| `po-pilot-launch/outreach/OUTREACH-DOSSIER.md` | Owner-facing summary, regenerated from the ledger |

## 受影响文件/落点

Writes go to `po-pilot-launch/outreach/`. The ledger is append-only in normal use;
correcting a bad record in place is allowed when the record itself is wrong (a
malformed subject line was corrected this way on 28 October), and the correction
must not change timestamps or recipients.

## 验证步骤

```bash
cd po-pilot-launch/outreach
python3 send-budget.py status          # budget and phase for today
python3 send-budget.py check --to x@y.com   # exit 1 means do not send
```

Check Gmail after any batch:

```
in:sent newer_than:1d
from:mailer-daemon OR subject:"Delivery Status Notification" newer_than:1d
```

Zero results on the second query is the expected state, not a reason to relax the
bounce rule.

## 下一步，按顺序

1. **31 October**: day 3 follow-up to all 20, one new piece of information only
   (MOQ units versus minimum order value). Text in `SENT-2026-10-29.md`.
2. **4 November**: day 7 follow-up, deadline only, to everyone who ignored day 3.
3. **Before either**: check for replies. Any reply cancels the sequence for that
   address permanently and takes priority over sending.
4. **Pool, not ceiling, is the constraint.** Batch 3 holds seven firms. The whole
   English-speaking pool of qualifying firms is roughly 60 to 90, which is four
   days at 20 per day. Widening geography, adding a segment, or raising price per
   engagement are the three real options once it is exhausted; adding volume without
   improving targeting is not one of them.

## 交接地址

Workspace: `/home/user/agents`, branch `arena/35ab5ba1-agents`, same workspace, no
worktree to create. Read `po-pilot-launch/outreach/ledger.json` first.
