---
name: visual-brief
description: Freeze a versioned visual brief before generating, editing, or regenerating an image. Use PROACTIVELY when an image request has more than one moving part, when a generation must be reproduced or iterated, when a specific element must not drift between attempts, when working from a reference or product photo, when reconciling several attempts into one direction, or when a previous attempt missed and the reason is unclear.
---

# Visual Brief

Record what an image must communicate **before** writing the prompt, so a miss has an address.

## When to use this skill

| Situation | Use a brief |
|---|---|
| One-off, simple, no reproduction needed | No — a prompt is enough |
| The image will be iterated or regenerated | Yes |
| Elements must not drift | Yes |
| A previous attempt missed and you cannot say why | Yes |
| Several people or sessions contribute | Yes |
| Working from a product or reference photo | Yes — `locks` per reference |

## Why a brief instead of a prompt

A prompt states a hope. A brief states a specification. When a result misses, a prompt gives you
nothing to reason with — you rewrite from scratch and hope differently. A brief tells you **which
field was wrong**, so the next attempt changes one thing on purpose. The prompt is derived from
the brief, not the reverse.

## The contract

```json
{
  "schema_version": "banana.visual-brief.v1",
  "goal": "What the image must communicate",
  "facts": ["Things that cannot change"],
  "locks": ["Elements that must be preserved exactly"],
  "freedoms": ["What may vary"],
  "direction": {
    "mode": "creative",
    "thesis": "The one-line creative idea",
    "signature": "One distinctive detail that makes this image not generic",
    "avoid": "What would make it generic"
  },
  "composition": ["Framing and layout rules"],
  "rendering": ["Light, material, finish"]
}
```

`mode` is `creative` when the image should communicate an idea, `preserve` when it must reproduce
supplied material. Full field reference, revision pattern, and hashing in
`references/schema.md`.

## The fields that earn their place

**`signature`** is the highest-leverage field and the one most often omitted. One concrete
detail that no generic image would contain — `one narrow stripe of dawn light crosses the front
dial`. Without it you get a competent image indistinguishable from every other competent image.

**`avoid`** names the generic version explicitly: `generic glossy pedestal`, `floating
particles`. Naming the cliché beats naming a quality, because the cliché is what the model
reaches for by default.

**`locks`** must be **checkable by looking at the output**. `Keep the mood consistent` cannot be
verified. `The subject is not in the center of the frame` can.

**`freedoms`** stops over-constraining — naming what may vary keeps the model from locking
everything and producing something stiff.

## If a deviation would not be a violation, it is not a lock

A field that mentions a property without forbidding its opposite is not a constraint. A brief
saying the subject should sit `off-center in the lower-right third` did not prevent a centered
result, because nothing made centering a failure. Two fixes were needed, and the second is the
one people miss:

1. Add an explicit lock — `the subject is NOT in the center of the frame`.
2. **Assign the leftover space a purpose** — `the upper-left third belongs to the room, not the
   subject`. Forbidding a centered subject without saying what fills the rest leaves the model
   nowhere to put its attention, and the subject drifts back.

## The revision rule

> **If any governing field changes, the brief is revised and its hash changes. Do not edit the
> prompt without revising the brief.**

Governing fields: `goal`, `facts`, `locks`, `freedoms`, `direction`, `composition`,
`rendering`. A brief therefore carries a `revision` counter and a `change_log` of what changed,
from what, and why. Without it, the next iteration cannot tell whether a field is deliberate or
accidental.

## Brief problem or prompt problem?

When an attempt misses, decide which you are fixing:

| Miss | Belongs in | Why |
|---|---|---|
| Subject ended up centered when it should not be | brief — `composition`, plus a lock | intent was under-specified |
| Output came back 11:6 when a phone capture was the premise | prompt — the ratio instruction's placement | intent unchanged; the instruction was misplaced |
| A surface rendered as damaged when intact was wanted | brief — replace the described object | the described object was wrong for the intent |
| An element drifted between attempts | brief — add it to `locks` | reproducibility is an intent |

If you are editing the prompt to express something the brief does not contain, the brief is
incomplete. Fix the brief first.

## Examples

A minimal brief for a truthful, unglamorous capture:

```json
{
  "schema_version": "banana.visual-brief.v1",
  "goal": "A phone snapshot of an ordinary apartment, believable rather than attractive.",
  "facts": ["One adult tabby cat, asleep", "The room is genuinely lived in"],
  "locks": ["The cat is NOT in the center of the frame",
            "The light is ambient overhead, not directional or dramatic"],
  "freedoms": ["The exact clutter on the table", "The cat's pose within the right half"],
  "direction": {
    "mode": "creative",
    "thesis": "A boring photo taken by accident",
    "signature": "A charger cable running from a wall outlet to a phone on the cushion",
    "avoid": "Rule-of-thirds composition, soft window light, tidy staging"
  },
  "composition": ["Casual 4:3 horizontal, frame slightly tilted",
                  "The right two thirds hold the sofa; the left third holds the cluttered table"],
  "rendering": ["Flat overhead ambient light, open shadow",
                "White balance off toward yellow-green, dull low-contrast colors",
                "Plain beige cotton slipcover, evenly colored and clean"]
}
```

A revision entry, showing what a useful `reason` looks like:

```json
{
  "field": "locks",
  "was": "(no lock about centering)",
  "now": "The subject is NOT in the center of the frame",
  "reason": "Revision 1 produced a centered subject. The composition field said 'off-center' but no lock made centering a failure, so the deviation was noted without consequence."
}
```

Verifying that a brief file still matches the hash recorded in an artifact sidecar:

```python
import json, hashlib
obj = json.load(open("brief.json"))
canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
print(hashlib.sha256(canonical.encode("utf-8")).hexdigest())
# must equal the brief_sha256 recorded in the artifact sidecar
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Competent but forgettable | `signature` missing or vague | one concrete detail no other image would share |
| Result ignores a constraint | lock is a preference, not a violation | rewrite it so the wrong outcome fails inspection |
| Result is stiff | no `freedoms` listed | name what may vary |
| Regeneration does not match the original | brief was edited without a revision bump | restore the hash, or accept the new revision explicitly |
| Cannot tell why an attempt missed | fields too vague to check | a brief is only diagnostic if its fields are checkable |
| Model drifts back to a cliché | cliché not named in `avoid` | name it explicitly |
| Element oscillates between attempts | not locked | add it to `locks` |

## Companion skills

- `skills/smartphone-realism` — compile the brief into a realism-specified prompt
- `skills/image-to-prompt` — produce a brief from a reference image

## See also

- `references/schema.md` — field reference, locks that enforce, change-log pattern, canonical hashing, artifact sidecar
