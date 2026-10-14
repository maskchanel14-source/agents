# External anti-AI-look additions

Complements `failure-modes.md` with checks synthesized from two external MIT-licensed skills
found while pressure-testing the plugin against "masih terlihat AI" reports. Repo-local
substitutions and the damage prior still govern; this file adds tells and strip-lists the
external sources documented beyond our four original sources.

Sources:

- [`Sugamdeol/UltraReal-Prompt-Architect`](https://github.com/Sugamdeol/UltraReal-Prompt-Architect) (MIT) — visual-tell → prompt-correction table, strip-word list, prompt slot architecture
- [`nanbada/muse-creative-skills`](https://github.com/nanbada/muse-creative-skills) (license in repo) — phone-shot realness checks

## Visual tells → prompt corrections (additions to failure-modes §substitutions)

| Tell | Correction |
|---|---|
| Plastic / waxy / poreless skin | lived texture + one directional light; delete `flawless`, `perfect`, `beauty` |
| Bilaterally identical face halves | `slight asymmetry`, uneven hair, natural smile |
| Doll eyes / decorative star catchlights | catchlight shaped like the actual key light; moisture, no sparkle |
| Veneer-tile teeth | closed mouth, or `ordinary slightly uneven teeth` |
| Helmet hair | flyaways, wind, parting, weather in the hair |
| Age mismatch (young neck, old face) | `neck and hands match the age of the face` |
| Fake HDR / glowing edges | `natural dynamic range, unretouched colour`; delete `HDR`, `hyper`, `ultra sharp` |
| Teal-orange or neon grade | neutral observed colour, or name one film stock |
| Two suns / shadow chaos | one key, one shadow direction, named fill |
| Rim light from nowhere | give the rim a source or remove it |
| Floating subject / product | contact shadow, weight, ground texture |
| Clone crowds | fewer background people, or `varied faces and clothes` |
| Unreadable fake text | remove text, or quote exact short copy on a text-capable model |
| Ring-light influencer default | specify window, overcast, or sun instead |

## Words that cause the AI look (strip them)

`flawless`, `perfect`, `gorgeous`, `stunning`, `beautiful lighting`, `cinematic lighting`
(alone), `ultra detailed`, `insanely detailed`, `8K`, `4K`, `UHD`, `masterpiece`,
`best quality`, `award winning`, `hyper realistic`, `ultra realistic`, `octane`,
`Unreal Engine`, `trending`, `artstation`, `glass skin`, `airbrushed`, `HDR`,
`dramatic volumetric god rays` (as decoration).

Overlap with this plugin: `realistic`, `photoreal`, `8K`, `masterpiece` were already
stripped by `smartphone-realism`; the list above extends it. Note the tension with
identity work: a brief may legitimately demand a `stunning` person (user-specified
attribute) — in that case describe the *grooming* (neat ponytail, soft-glam matte makeup,
flight-attendant posture) instead of the adjective, because the adjective pulls the
beauty prior (failure-modes §beauty-prior).

## Words that usually help (use few)

`photograph`, `candid`, `unretouched`, `available light`, `documentary still`,
`ordinary`, `slightly uneven`, `visible pores`, `fine film grain`, `contact shadow`,
one honest lens name.

## Prompt slot order (UltraReal, compatible with the golden three-part structure)

Medium → Subject → Action/pose → Environment → Lighting (source, direction, softness,
colour, shadows, bounce) → Materials → Composition → Camera (only if optics matter) →
Colour/atmosphere → Imperfections (1–4 honest details) → Constraints.
Length: 60–110 words portrait, 80–150 environmental; ceiling ~180 unless Flux JSON.
The golden three-part order of `smartphone-realism` (device+logic+color+quality first,
negations last) still wins for phone-capture premises; use slots *inside* Part 2.

## Less-AI refinement recipe (post-generation, one field at a time)

1. Delete filler tokens. 2. One motivated light. 3. 2–4 imperfections. 4. Ordinary
posture. 5. Photographic aspect in the opening sentence. 6. If the grade is too clean:
mute saturation once, add digital noise (not `grain`), double JPEG — measure against a
real-photo reference band, never by eye alone (see `identity-lock/references/measuring.md`).
