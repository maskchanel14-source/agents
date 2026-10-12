---
name: smartphone-realism
description: Make a generated image read as a photograph someone actually took instead of an AI render. Use PROACTIVELY when the user asks for a realistic photo, when a generation comes back glossy, airbrushed, or over-polished, when reproducing a candid or snapshot look, when creating a phone-camera, film-era, or documentary aesthetic, when working from a reference image, or for fixing a prompt that keeps producing render-like output.
---

# Smartphone Realism

Make an image read as a photograph someone actually took, not an image a model made.

## When to use this skill

| Request | Use it | Target |
|---|---|---|
| A believable phone snapshot | Yes | casual framing, 4:3 |
| A film-era or vintage photo | Yes | era table in `references/era-grading.md` |
| Documentary or street photography | Yes | rangefinder logic, tilt, motion |
| **A clean, polished, professional photo** | **No** | makes believable captures, not good photography |
| A logo, diagram, or illustration | No | camera vocabulary harms flat work |

If the request is for polish, say so and skip the realism vocabulary. Applying it to a
commercial brief produces an image that looks like a bad photo on purpose.

## The core principle

Writing `realistic`, `photoreal`, `8K`, or `masterpiece` does **not** produce realism — those
words trigger an AI style. Realism comes from specific, perceivable imperfections that only
exist in a real capture:

```
Realism = Specific Device + Shooting Logic + Quality Flaws
        + Imperfect Details + Ordinary Subjects + Anti-AI Negation
```

Photorealism is a **specification problem, not an adjective problem**. If a field cannot be
checked by looking at the output, it does not belong in the prompt.

## The device-name trap

A device name is not a realism lever on its own. A model treats `Sony Cyber-shot` or `iPhone` as
a **prop** and keeps using overhead angles, centered subjects, and refined lighting. Pair the
name with **how a person holding that device shoots**:

| Device | Real shooting logic | Default model mistake |
|---|---|---|
| Phone, casual | one-handed, pressed without composing, tilted, foreground intrusion | overhead, centered, clean frame |
| Point-and-shoot | eye-level quick snap, no waiting for the moment, tilted | overhead, centered, perfect timing |
| Studio, older era | posed subjects, frontal flash, cloth backdrop | gradient background, soft light |
| Film camera | heavy grain, color shift, slight misfocus | sharp, accurate color, clean depth of field |

`Smartphone` alone is decoration. `held one-handed and pressed without composing anything, frame
slightly tilted, slightly cropped` is the lever.

## Golden three-part structure

Order matters — the opening carries the most weight.

**Part 1 — Device + shooting logic + color + quality.** Determines most of the result.
**Part 2 — Subject + imperfect details.** Ordinary subjects: uneven fur, an ear bent back, a paw
hanging awkwardly, worn fabric.
**Part 3 — Negation, to seal the AI feel.** Two or three: `not a retouched photo`, `not
professional photography`, `not a high-res image`, `not AI-generated`.

Use **4:3** for phone realism, in the **opening sentence** — mid-prompt ratio instructions get
ignored. An ultrawide ratio makes a phone capture impossible, defeating the premise before
anything else is judged.

## Words that backfire

| Instead of | Write | Because |
|---|---|---|
| `blurry` | `low resolution`, `soft details`, `focus isn't quite locked on` | `blurry` produces pixel art |
| `grain` | `noise`, `digital noise` | `grain` produces an oil-painting surface |
| `low saturation` once | extreme repetition, `not a single color is vivid` | a single qualifier gets discounted |
| `worn`, `faded`, `lived-in` + a surface | a surface that is simply intact | the damage prior overrides negation |

Evidence in `references/failure-modes.md`.

## Prior beats negation

A model has a **strong prior toward dirt and damage** once it sees `worn`, `faded`, `lived-in`,
`mottled`, or `imperfect`. Explicit negation **does not win** against it, and repeating the
negation does not help — the mechanism is not forgetting, it is being pulled somewhere else.

Observed in testing: a wall described as `mostly intact, clean and smooth, only two or three
small faint smudges, not damaged, not stained, not peeling` came back covered in mould-like
speckling — twice.

**Fix: change the object, not the adjective.** Declare the thing as genuinely not damaged — `a
plain beige slipcover, evenly colored and clean`, `freshly painted, uniform, no marks, no
discoloration anywhere` — and put the ordinary-ness elsewhere: table clutter, a plugged-in
charger, a tilted frame. Let drab quality come from **light and color**, not **object decay**.

## Examples

A working phone-snapshot prompt, three parts marked:

```text
PART 1 — Casual 4:3 horizontal photo taken with a smartphone, held one-handed and pressed
without composing anything, frame slightly tilted, random composition, average quality, not
high resolution, soft details, slight digital noise, white balance off toward yellow-green,
dull low-contrast colors, everything under a flat grey-yellow cast.
PART 2 — An ordinary tabby cat asleep on a sofa, fur uneven and unbrushed with individual
strands clearly visible, one ear bent back, one paw hanging awkwardly off the cushion edge.
The sofa has a plain light beige cotton slipcover, evenly colored and clean. Mildly cluttered
room: a phone charger on the cushion, a folded blanket, a mug and papers on the table. Flat
overhead ambient light, no interesting shadows, nothing dramatic happening.
PART 3 — Not a retouched photo, not professional photography, not a high-res image, not
AI-generated, just a very ordinary boring photo taken by an ordinary person by accident.
```

The one change that fixed the wall, as a diff:

```diff
- slightly mottled with a scuff mark
+ plain flat off-white paint in even tone, freshly painted and uniform across the whole
+ surface, smooth and clean, with no marks, no stains and no discoloration anywhere
```

For a reproducible job, freeze the same intent as a brief first — see the `visual-brief` skill.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Looks like pixel art | used `blurry` | `low resolution`, `soft details` |
| Surface looks like oil paint | used `grain` on a digital capture | `noise`, `digital noise` |
| Still glossy and produced | quality adjectives present | remove `realistic`, `8K`, `masterpiece` |
| Surfaces render damaged or dirty | damage-prior pull | replace the object; more negations will not help |
| Aspect ratio impossible for a phone | ratio mid-prompt or absent | move `Casual 4:3` to the opening sentence |
| Subject drifted back to center | negative space unassigned | give the empty area a job |
| Framing too close for the story | distance stated abstractly | state a checkable result: `far enough that the entire sofa fits in frame` |

Deeper causes in `references/failure-modes.md`.

## Reference material

- `references/failure-modes.md` — word substitutions with evidence, the damage prior, ratio and camera-logic traps
- `references/vocabulary.md` — 298 structured options: lenses, angles, shots, gradings, lighting expansions
- `references/era-grading.md` — era table, the modern-phone trap, five presets, a fill-in template
- `references/negative-prompt-bank.md` — negative prompts, plus affirmative rewriting when there is no negative slot
- `references/case-study.md` — three iterations of one prompt, the two failures and the fix

## Companion skills

- `skills/visual-brief` — freeze locks, freedoms, and a signature element before generating
- `skills/image-to-prompt` — reconstruct a prompt when working from a reference image instead of prose
