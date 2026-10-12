---
name: identity-lock
description: Keep a generated person, animal, or character recognizably the same individual across generations and edits. Use PROACTIVELY when a reference photo is supplied, when the user asks for the same face, the same person, or the same pet in a new scene, when building a series, storyboard, or catalog, when an output drifts to a lookalike of the intended subject, or when repairing identity after a failed generation.
---

# Identity Lock

Make generation N+1 read as the **same individual** as generation 1 — same face, same markings
— while scene, outfit, pose, and light change around it.

## When to use this skill

| Request | Use it | Target |
|---|---|---|
| A series, storyboard, or catalog of one subject | Yes | frozen identity block + reference workflow |
| "Put me / this person / this pet in a new scene", photo supplied | Yes | reference anchoring |
| Output came back a cousin, not the subject | Yes | diagnose the drift, then repair |
| One-off image, no reference, no series | No | `smartphone-realism` alone is enough |
| Logo, diagram, flat illustration | No | identity language harms flat work |

## The core principle: two anchors, different strengths

| Anchor | Locks | Does not lock |
|---|---|---|
| **Text identity block** — one frozen description, reused verbatim | the *type*: species, palette, marking pattern, age band | the individual |
| **Visual reference** — an image passed as anchor | the *individual*: this face, these markings | anything it is not told to ignore |

Observed in this repository's tests (`references/case-series.md`): regenerating a cat from a
frozen text block produced **a different cat of the same type** — cooler grey, other pattern
class, notch gone. Passing the previous image as base and framing the change as a single
targeted edit reproduced the same individual. A description denotes a category; pixels denote
a person. Type-level consistency is free; individual-level consistency costs a reference.

**The likeness ceiling.** Prompting *approximates* a face; it never reproduces one exactly
(after `asreynolds1000/ai-image-generation-guide`, CC-BY-4.0). For pixel-exact likeness of a
real person, generate the composition first and swap the real face on with an open-source
face-swap tool. Say so when a user expects exact real likeness from prompting alone.

## Tier 1 — Prompt-level identity (no reference available)

1. **Freeze one identity block**, reused verbatim in every prompt of the series. Enumerate
   distinctive features; `same person as before` is not a description.
2. **Change only the scene block.** Contradictory identity language across prompts gives the
   model permission to reinterpret the face.
3. **Specific beats generic.** `close-set eyes, asymmetric smile, scar above the right brow`
   locks; `handsome man` drifts. For animals: `white chest, notched left ear` locks.
4. **Anchor the angle.** Ask for a camera angle matching one of your references' angles.
5. **Never fight the anchor with text.** If a reference shows the outfit, delete the outfit
   prose — the two weights compete and both lose.
6. **One approved anchor, constant ratio, no chaining.** Reusing an output as the next
   reference compounds drift. Re-anchor to the original every time.

Templates and the freeze-and-hash rule: `references/identity-block.md`.

## Tier 2 — Reference workflow (a reference exists)

1. **Identity refs first, style refs last.** Earlier images are weighted more heavily.
2. **Three face refs maximum.** More causes face averaging. Feature closeups travel in
   separate labeled slots.
3. **A frontal anchor in every ref set**, even for profile outputs.
4. **Label every image by role**; `IGNORE the face` on every non-identity reference.
5. **Two-pass for dramatic changes.** Pass 1 spends every slot on identity; pass 2 puts the
   pass-1 output in slot 1 as base and edits one thing.

Full workflow — collection, ordering, labeling, mannequins, providers:
`references/ref-workflow.md`.

## Tier 3 — Platform parameters

| Platform | Mechanism | Note |
|---|---|---|
| Nano Banana Pro / Gemini image | up to 14 refs (6 high-fidelity) + lock phrasing | refs carry pixels, prompt carries the scene |
| Midjourney V6 | `--cref <url>` + `--cw 0–100` | `--cw 100` also inherits the ref's lighting and outfit; `--cw 0` concentrates on the face |
| Midjourney V7 | `--oref <url>` + `--ow 1–1000` | `--cw` chooses what is copied, `--ow` how strongly |
| gpt-image | up to 16 refs | tends to airbrush faces — compensate with texture language |
| SD / Flux (ComfyUI) | PuLID-Flux, IPAdapter-FaceID, InstantID | conditioning, not prompting |

Real photographs are weak `--cref` sources: models trained on generated symmetry stumble on
real asymmetry. For fictional subjects, generate the base portrait in-model and anchor to it.

## Tier 4 — Measure, do not only eyeball

Detect (YuNet), embed (SFace or ArcFace), compare (cosine). Judge a series from a **grid of
ten outputs**, and scale the pass bar with face size in frame — a far face embeds weaker than
a closeup of the same person. Routing and calibration: `references/measuring.md`.

## The repair path — fix one field without re-rolling identity

A full regeneration re-rolls the scene; field-level fixes belong to an **edit**: base image in
slot 1, framed as `a single targeted edit`, with a preserve-list naming everything that must
not change — including color cast and noise level, because edits quietly beautify (repair
creep, `smartphone-realism` `references/failure-modes.md` §8). Evidence:
`references/case-series.md`.

## Consent boundary

Generate a real person's likeness only with that person's explicit permission, and record it
in the brief. These techniques are for consented portraits, the user's own face, and fictional
characters.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Same type, different individual | text-only anchor | add a visual anchor (Tier 2), or accept type-level and say so |
| Face blends with the outfit ref | non-identity ref unlabeled | `IGNORE the face` per image; style refs last |
| Face reads generic / averaged | more than three face refs | cut to three, add feature closeups |
| 3/4 and profile outputs drift | no frontal anchor in the set | add one straight-on ref per angle's set |
| Wardrobe will not change | character weight too high, or text fights the ref | lower `--cw`/`--ow`; delete clothing text |
| Field fixed but whole scene re-rolled | field fix via regeneration | use the repair path |
| Repair came back brighter and cleaner | repair creep | re-assert cast and noise in the preserve-list |

## Companion skills

- `skills/smartphone-realism` — the capture realism this identity rides on
- `skills/visual-brief` — freeze the identity block in `facts`, markings in `locks`
- `skills/image-to-prompt` — derive the identity block from a reference photo

## Reference material

- `references/identity-block.md` — lock formula, enumeration checklist, template, freeze-and-hash
- `references/ref-workflow.md` — ref collection, ordering, labeling, two-pass, mannequins, providers
- `references/measuring.md` — embedding scores, adaptive thresholds, grid review, calibration
- `references/case-series.md` — three generations of one cat: text-anchor drift, base-image lock, repair creep

Sources are credited in the reference files that draw on them and in the plugin README.
