# The identity block

The identity block is one frozen paragraph of distinctive-feature description, reused
verbatim across every prompt in a series. It is the cheapest consistency mechanism that
exists and the most often skipped.

## The lock formula

State identity as an enumeration of checkable features, not as a claim of sameness:

```text
Maintain the exact same facial features as the reference — identical eye shape, nose bridge
contour, jawline angle, lip proportions, and skin texture.
```

Without a reference, the same shape works as a self-contained block:

```text
A 35-year-old man with short black hair, a trimmed beard, a small scar above his right
eyebrow, an angular jawline, close-set brown eyes, and an asymmetric smile.
```

`Same person as the previous image` carries no pixels and no geometry. The enumeration is
what the model can actually aim at.

## Enumeration checklist

Cover what survives a change of scene, in this order of locking power:

1. **Geometry** — face shape, jawline angle, eye set and depth, nose bridge contour, lip proportions
2. **Marks** — scars, moles, freckle fields, notched ears, asymmetries (asymmetry locks harder than symmetry; symmetric faces are the model's default)
3. **Color** — exact eye color, hair color with undertone, verified skin tone
4. **Hair construction** — style, length, volume, and part side in frame-relative language (`part line on the left of the image`), never body-relative (`part on her left`), which flips with the angle
5. **Age band** — a concrete number or narrow band; drastic age changes between prompts read as different people
6. **One signature trait** — the feature a friend would name first

Skin tone deserves its own verification pass against real photos: descriptions drift toward
`olive` and `warm complexion` by default, and a wrong skin-tone anchor is one of the strongest
producers of "that is not the same person".

## What not to write

| Avoid | Why |
|---|---|
| Negative identity constraints (`NOT narrow jaw`, `NOT angular`) | they cause overcorrection rather than prevention; the reference images carry identity, the prompt carries the scene |
| `CRITICAL`, `NON-NEGOTIABLE` headers | no observed effect on model behavior |
| Detailed nose/teeth prose when closeup refs exist | the refs outperform the description |
| Identity language that changes between prompts | every contradiction is permission to reinterpret |
| `beautiful`, `handsome` as the only face content | a type, not an identity |

## Freeze and hash

Treat the identity block like a `visual-brief` governing field:

- Store it once, in the brief's `facts`, with the marking-level details repeated in `locks`.
- Any edit to the block is a **revision**: bump the counter, log what changed and why, and
  expect the subject to shift — deliberately.
- Scene, outfit, pose, and light live in separate fields so they can change without touching
  the block.
- If two sessions produce different-looking subjects from "the same" prompt, diff the blocks
  before blaming the model; paraphrase is not freeze.

## Worked blocks

A human subject, series-ready:

```text
IDENTITY (frozen): woman, early 30s, oval face, high cheekbones, jawline that angles sharply
below the ear, close-set dark brown eyes with a faint epicanthic fold, straight nose with a
low bridge, full lower lip, a mole above the left corner of the mouth, black hair to the
shoulder with a center part (part line in the middle of the frame), warm-light undertone in
fair skin with pink cheeks. Signature: the mole and the sharp jaw angle.
```

An animal subject, from this repository's test series:

```text
IDENTITY (frozen): ordinary tabby cat, dark grey-brown mackerel stripes, a white chest
patch, a small notch in the left ear tip. Signature: the notch.
```

The cat series (`references/case-series.md`) is also the caution: this block kept the *type*
across independent generations and failed to keep the *individual*. It is a type anchor.
Pair it with a visual anchor for individual-level consistency.

## Attribution

Lock phrasing patterns cross-checked against `ZeroLu/awesome-nanobanana-pro` (MIT) and
practitioner identity-preservation guides (2026); the freeze-and-hash discipline follows this
plugin's `visual-brief` skill.
