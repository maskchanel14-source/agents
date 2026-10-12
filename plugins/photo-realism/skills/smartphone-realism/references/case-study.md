# Case study: three iterations to a believable phone snapshot

One prompt, one subject (a cat asleep on a sofa), three generations. Recorded because the two
failures are more instructive than the success.

## Goal

Move away from the polished look of an earlier brief-driven generation and toward something that
reads as a photo an ordinary person took by accident. Not "a good photo" — a **believable** one.

## Iteration 1 — method works, premise broken

Applied the three-part structure: device plus shooting logic, low-quality words, negations.

**Result:** The aesthetic landed. Drab grey-yellow palette, a sofa with a flattened shiny patch
where people sit, unbrushed fur, real clutter (charger, cables, a stack of papers), flat
overhead light with no drama.

**Two defects:**

1. **Aspect ratio 1408×768 (ratio 1.833).** No phone shoots 11:6. The image was impossible as a
   phone capture before any other quality was judged — which invalidates the entire premise.
2. **Wall surface severely damaged.** The prompt read `the wall slightly mottled with a scuff
   mark and a power outlet visible`. The output showed dark mould-like speckling across the
   whole wall.

## Iteration 2 — ratio fixed, surface still overshooting

Moved the ratio to the opening sentence: `Casual 4:3 horizontal photo taken with a smartphone`.
Added an explicit and repeated correction to the wall: `mostly intact, clean and smooth with
only two or three small faint smudges ... not damaged, not stained, not peeling`.

**Result:**

- **Ratio fixed:** 1200×896 (ratio 1.339 ≈ 4:3). Opening-sentence placement worked.
- **Fur improved:** `individual strands clearly visible` defeated the smooth-mass default.
- **Wall still speckled.** The negation was explicit, repeated, and adjacent to the description.
  It lost.

## The finding

> A model has a strong prior toward dirt and damage once the surrounding vocabulary contains
> `worn`, `faded`, `lived-in`, `imperfect`, `casual`, `cheap`, or `ordinary`. Explicit negation
> does not win against that prior, and repeating it does not help — the mechanism is not
> forgetting, it is being pulled somewhere else.

This mirrors, in the opposite direction, the discount rule documented by the
`hyperrealistic-image` skill: a single positive qualifier gets discounted (`low saturation`
once ≈ mildly desaturated), and a negative qualifier gets overridden by a prior. Both mean the
same thing:

**Describe the object you want, not an adjective applied to a different object.**

## Iteration 3 — change the object, not the adjective

Kept every element that worked. Replaced the two objects that were fighting the prior:

| Field | Iteration 2 | Iteration 3 |
|---|---|---|
| Sofa | `worn fabric sofa ... faded with pilling, a flattened shiny patch` | `a plain light beige cotton slipcover, evenly colored and clean, with soft gentle creases from everyday sitting` |
| Wall | `mottled, clean and smooth, only two or three small faint smudges, not damaged, not stained, not peeling` | `plain flat off-white paint in even tone, freshly painted and uniform across the whole surface, smooth and clean, with no marks, no stains and no discoloration anywhere` |

**Result:** clean, uniform wall; plain slipcover with soft creases. No speckling, no crackle
texture. The ordinary quality survived — it now comes from light and color (flat grey-yellow
cast) and from clutter (charger, papers, mug, remote, folded blanket), not from object decay.

## Transferable rules

1. **Put the aspect ratio in the opening sentence.** Mid-prompt ratio instructions were ignored.
2. **State a checkable framing result.** `far enough that the entire sofa fits inside the
   frame` works; `far from the subject` does not.
3. **Give negative space a job.** Forbidding a centered subject without assigning the empty
   area caused the subject to drift back to center. `the upper-left third belongs to the room`
   fixed it.
4. **Count specifics.** `only two or three small crumbs and a single loose hair` instead of
   `a few crumbs`, which rendered as a scattered field.
5. **Negation seals the AI feel; it does not repair physical description.** Part 3 negations
   are authorial claims (`not a retouched photo`). Do not use them to correct how an object
   looks.
6. **Verify the pixels before believing the tool.** Both failures were described as successes
   by the generation call. Only inspecting the images caught the impossible ratio and the
   mould-like wall.

## What this case does not establish

- Whether the result passes an AI-image detector. No detector was available, and "looks real
  to a human" is not the same claim as "classified as real by a model".
- That the damage prior behaves identically across models. It was observed on one generator;
  the source skill reports it was tuned on a different one. Treat the mechanism as likely
  general and the exact wording as needing per-model tuning.

## A second case series

The same cat returned for three more generations under a frozen identity block, testing
type-versus-individual anchoring and the repair path: text-only regeneration kept the type and
lost the individual; a base-image edit kept both and showed repair creep. Recorded in
`skills/identity-lock/references/case-series.md`, with its failure classes filed under
`failure-modes.md` §8 and §9.
