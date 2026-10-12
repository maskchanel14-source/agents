# Photo Realism

Make generated images read as photographs someone actually took, instead of images a model
produced.

The premise: **photorealism is a specification problem, not an adjective problem.** Writing
`realistic`, `photoreal`, `8K`, or `masterpiece` triggers the AI look it is meant to avoid.
Realism comes from a specific device, the shooting logic of someone holding it, perceivable
quality flaws, ordinary subjects, and a few closing negations.

## Skills

| Skill | Purpose |
|---|---|
| **`smartphone-realism`** | The core method. Device-plus-shooting-logic prompting, the golden three-part structure, and nine documented failure modes with substitutions |
| **`identity-lock`** | Keep the same individual across generations and edits: frozen identity blocks, the reference workflow, platform parameters, and measured identity scoring |
| **`visual-brief`** | Freeze a versioned brief before generating, so a miss has an address instead of prompting another guess |
| **`image-to-prompt`** | Reconstruct a reusable, editable prompt from a reference image |

## Agent and command

- **`photo-realism-director`** — runs the full loop: brief, prompt, generate, **inspect pixels**,
  diagnose, fix one field. Refuses to report success on the strength of a tool response.
- **`/photoreal-shoot <description>`** — one-shot path through the same method

## What is in the references

| File | Contents |
|---|---|
| `smartphone-realism/references/failure-modes.md` | Nine failure classes. Word substitutions with evidence, the damage prior, the beauty prior, repair creep, identity drift, aspect-ratio and camera-logic traps |
| `smartphone-realism/references/vocabulary.md` | 298 structured options: lenses, angles, shot types, gradings, styles, lighting prose expansions |
| `smartphone-realism/references/era-grading.md` | Era table, the modern-phone trap, five presets, a fill-in template |
| `smartphone-realism/references/negative-prompt-bank.md` | Negative banks, plus how to rewrite them affirmatively for generators with no negative slot |
| `smartphone-realism/references/case-study.md` | Three iterations of one prompt: two failures and the fix that worked |
| `identity-lock/references/identity-block.md` | The lock formula, enumeration checklist, fill-in template, freeze-and-hash rule |
| `identity-lock/references/ref-workflow.md` | Reference collection, ordering, labeling, two-pass, mannequins, provider notes |
| `identity-lock/references/measuring.md` | Embedding scores, adaptive thresholds by face size, grid review, calibration |
| `identity-lock/references/case-series.md` | Three generations of one cat: text-anchor drift, base-image lock, repair creep |
| `visual-brief/references/schema.md` | Field reference, writing locks that enforce, revision and change-log pattern, canonical hashing, artifact sidecar |
| `image-to-prompt/references/analysis-order.md` | Nine-stage analysis, per-genre special cases, a worked example |

## The three findings worth reading first

**1. Word substitutions change more than any rewording.**

| Instead of | Write |
|---|---|
| `blurry` | `low resolution`, `soft details`, `focus isn't quite locked on` |
| `grain` | `noise`, `digital noise` |
| `low saturation` once | extreme repetition — the model discounts a single qualifier |

`blurry` produces pixel art. `grain` produces an oil-painting surface.

**2. Prior beats negation.**

A model has a strong prior toward dirt and damage once it sees `worn`, `faded`, `lived-in`, or
`imperfect`. Explicit, repeated negation does not win against it. The fix is to **change the
object, not the adjective** — describe a surface that is genuinely intact, and place the
ordinary-ness in light, color, and clutter instead. Observed directly in this plugin's test
generations: `not damaged, not stained, not peeling` produced a mould-speckled wall twice.

**3. Text anchors lock the type; pixel anchors lock the individual.**

A frozen identity block (`dark grey-brown stripes, a white chest patch, a small notch in the
left ear tip`) regenerated without a reference produced a different individual of the same
type — cooler coat, other pattern class, notch gone. Passing the previous image as base and
framing the change as a single targeted edit kept the exact same animal. A description denotes
a category; pixels denote a person. Individual-level consistency costs a reference, and
field-level fixes belong to edits, not regenerations. Evidence, and the repair-creep caveat
(edits quietly brighten and clean what they touch), in
`identity-lock/references/case-series.md`.

## Attribution

The method synthesizes four MIT-licensed sources, each credited in the file that draws on it:

- [`JacobYixi/hyperrealistic-image`](https://github.com/JacobYixi/hyperrealistic-image) — golden three-part structure, device-versus-shooting-logic, failure substitutions, era grading
- [`AgriciDaniel/banana-claude`](https://github.com/AgriciDaniel/banana-claude) — the `visual-brief.v1` contract and revision discipline
- [`jiemianduan/image-to-prompt`](https://github.com/jiemianduan/image-to-prompt) — the nine-stage analysis order
- [`artokun/ComfyUI-Photoreal-Prompt-Builder`](https://github.com/artokun/ComfyUI-Photoreal-Prompt-Builder) — the structured vocabulary and lighting prose expansions
- [`GitHub30/Reproducible-Photorealistic-Nano-Banana-Pro-JSON-Prompts`](https://github.com/GitHub30/Reproducible-Photorealistic-Nano-Banana-Pro-JSON-Prompts) — negative-prompt bank

Identity locking adds sources credited in the skill files that draw on them:

- [`asreynolds1000/ai-image-generation-guide`](https://github.com/asreynolds1000/ai-image-generation-guide) (CC-BY-4.0) — the reference workflow: three-refs-max, ordering, frontal anchors, two-pass, mannequins, the likeness ceiling
- [`ZeroLu/awesome-nanobanana-pro`](https://github.com/ZeroLu/awesome-nanobanana-pro) (MIT) and [`PicoTrex/Awesome-Nano-Banana-images`](https://github.com/PicoTrex/Awesome-Nano-Banana-images) (Apache-2.0) — identity-lock phrasing patterns and the consistency-dataset context
- [`artfat-creator/ComfyUI-Artfat-FaceConsistency`](https://github.com/artfat-creator/ComfyUI-Artfat-FaceConsistency) (MIT) and [`SiddharthFulia/face-consistency-toolkit`](https://github.com/SiddharthFulia/face-consistency-toolkit) (MIT) — identity scoring, adaptive thresholds by face size
- [`beatra-ai/ai-image-realism-skill`](https://github.com/beatra-ai/ai-image-realism-skill) (MIT-0) — the repair-prompt shape and the AI-tells inspection vocabulary
- Prior art, unlicensed — ideas referenced, no text copied: [`aidenli/krea2-photography-prompt-skills`](https://github.com/aidenli/krea2-photography-prompt-skills) — causal imperfection (one reasoned, localized flaw per capture)

The damage-prior finding, the first case study, and the identity case series come from testing
in this repository.

## License

MIT
