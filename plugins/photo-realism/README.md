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
| **`smartphone-realism`** | The core method. Device-plus-shooting-logic prompting, the golden three-part structure, and six documented failure modes with substitutions |
| **`visual-brief`** | Freeze a versioned brief before generating, so a miss has an address instead of prompting another guess |
| **`image-to-prompt`** | Reconstruct a reusable, editable prompt from a reference image |

## Agent and command

- **`photo-realism-director`** — runs the full loop: brief, prompt, generate, **inspect pixels**,
  diagnose, fix one field. Refuses to report success on the strength of a tool response.
- **`/photoreal-shoot <description>`** — one-shot path through the same method

## What is in the references

| File | Contents |
|---|---|
| `smartphone-realism/references/failure-modes.md` | Six failure classes. Word substitutions with evidence, the damage prior, aspect-ratio and camera-logic traps |
| `smartphone-realism/references/vocabulary.md` | 298 structured options: lenses, angles, shot types, gradings, styles, lighting prose expansions |
| `smartphone-realism/references/era-grading.md` | Era table, the modern-phone trap, five presets, a fill-in template |
| `smartphone-realism/references/negative-prompt-bank.md` | Negative banks, plus how to rewrite them affirmatively for generators with no negative slot |
| `smartphone-realism/references/case-study.md` | Three iterations of one prompt: two failures and the fix that worked |
| `visual-brief/references/schema.md` | Field reference, writing locks that enforce, revision and change-log pattern, canonical hashing, artifact sidecar |
| `image-to-prompt/references/analysis-order.md` | Nine-stage analysis, per-genre special cases, a worked example |

## The two findings worth reading first

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

## Attribution

The method synthesizes four MIT-licensed sources, each credited in the file that draws on it:

- [`JacobYixi/hyperrealistic-image`](https://github.com/JacobYixi/hyperrealistic-image) — golden three-part structure, device-versus-shooting-logic, failure substitutions, era grading
- [`AgriciDaniel/banana-claude`](https://github.com/AgriciDaniel/banana-claude) — the `visual-brief.v1` contract and revision discipline
- [`jiemianduan/image-to-prompt`](https://github.com/jiemianduan/image-to-prompt) — the nine-stage analysis order
- [`artokun/ComfyUI-Photoreal-Prompt-Builder`](https://github.com/artokun/ComfyUI-Photoreal-Prompt-Builder) — the structured vocabulary and lighting prose expansions
- [`GitHub30/Reproducible-Photorealistic-Nano-Banana-Pro-JSON-Prompts`](https://github.com/GitHub30/Reproducible-Photorealistic-Nano-Banana-Pro-JSON-Prompts) — negative-prompt bank

The damage-prior finding and the case study come from testing in this repository.

## License

MIT
