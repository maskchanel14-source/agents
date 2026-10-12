---
name: image-to-prompt
description: Reconstruct a reusable, editable image-generation prompt from a reference image. Use PROACTIVELY when the user supplies a photo or render and wants a prompt for it, when they ask to reverse-engineer or imitate an image's look, when analysing why an image reads as real or as AI-generated, when working from several references at once, or for converting an existing image into an editable template. Also triggers when a user pastes an image and asks how to regenerate it.
---

# Image to Prompt

Reconstruct a prompt from visible evidence. Describe what can be reproduced, separate observation
from inference, and never claim to know the original prompt, seed, model, lens, or settings.

## When to use this skill

| Request | Use it |
|---|---|
| "Write me a prompt for this image" | Yes |
| "Why does this look AI-generated?" | Yes — analyse, then name the stage that reads wrong |
| "Make my output look like this photo" | Yes — reconstruct, then pass to `skills/smartphone-realism` |
| "What model/settings made this?" | **No** — that cannot be recovered. Say so |
| "Describe this image" | No — description is not reconstruction |

## What this is for

Turn a reference into something reusable — a template the user can edit, not a description of
the picture. A faithful description nobody can edit is a worse deliverable than a loose
template that can.

## The analysis order

High-impact facts first. Later stages change less about the result than earlier ones.

1. **Subject and action** — identity category, count, pose, expression, clothing, props
2. **Composition** — orientation, crop, placement, symmetry, foreground/midground/background, viewpoint
3. **Environment** — location, background elements, weather, time-of-day cues
4. **Lighting** — direction, softness, contrast, key/fill/rim behavior, shadow character
5. **Color** — palette, accents, saturation, temperature, tonal range
6. **Surface and detail** — materials, texture, depth of field, grain, reflections, motion
7. **Visual language** — photographic, cinematic, editorial, painterly, vector, clay, CGI, collage
8. **Capture/render cues** — shot scale, perspective, focal-length range, post-processing
9. **Text and layout** — transcribe only legible text; describe unreadable text as layout blocks

Use spatially explicit phrases: `subject in the lower-right third`, `soft backlight from frame
left`. Concrete visual properties beat vague quality words.


## Fidelity rules

- Preserve subject count, spatial relationships, camera angle, crop, lighting direction, palette, and major background geometry.
- Do not add narrative, symbolism, props, logos, text, or scenery that is not visible.
- Do not identify a real person from appearance. Describe observable physical and styling traits.
- Do not assert an artist, brand, camera, lens, model, seed, or parameter unless the user supplied it or it is visibly documented.
- Treat focal length, aperture, film stock, and generation parameters as **reproduction suggestions, not recovered facts**. Mark them as estimates.
- For unreadable text write `[unreadable text]`, or describe its placement and typographic character.
- With multiple references, say which traits come from which image, and flag contradictions instead of blending them silently.
- Remove prompt terms that fight the observed image, even fashionable ones.

Full per-genre guidance in `references/analysis-order.md`.

## Prompt construction order

```
subject -> action/pose -> environment -> composition/viewpoint -> lighting
-> color -> materials/detail -> medium/style -> finish
```

Write natural, information-dense phrases. Avoid keyword spam, duplicated adjectives,
unsupported `8K` / `masterpiece` language, and excessive camera jargon — a lens matters only
when its optical behavior matters.

## Output format

Deliver all of these unless the user asks for less:

1. **Breakdown** — a compact factual summary: subject, composition, lighting, color, medium, key textures. Mark estimates as estimates.
2. **Prompt** — one polished, copy-ready reconstruction prompt, written independently rather than translated word-for-word from the breakdown.
3. **Negative prompt** — only defects and unwanted deviations relevant to this image. Omit when the target generator has no negative slot.
4. **Suggested parameters** — aspect ratio first, then a few model-appropriate starting points, labelled as recommendations.
5. **Editable prompt** — one complete, copy-ready prompt with replaceable spans marked, each holding a usable default so the template works before editing.

### Marking editable spans

Wrap each replaceable value in `【】` with a working current value inside. Do not use empty
brackets, abstract variable labels, or a detached list of variable names.

```
一位【穿深红色长外套的年轻女性】站在【雨夜的城市街道】上，柔和的【蓝紫色霓虹侧光】
从画面左侧照入，保持人物居中的中景构图与潮湿路面反光。
```

Expose high-impact elements — subject, clothing, action, environment, lighting, palette,
material, style, aspect ratio. Leave structural details fixed when changing them would destroy
the composition that defines the reference.

## Examples

Reading a phone-realistic interior, stage by stage:

```text
1 Subject      one adult tabby cat, asleep, one paw over the cushion edge
2 Composition  4:3 horizontal; sofa in the right two thirds; subject right of the
               vertical midline; frame tilted slightly
3 Environment  small apartment; table on the left with papers and a mug; plain wall
4 Lighting     flat overhead ambient, no directional source, open shadow   [source=estimate]
5 Color        warm grey, oatmeal, muted; white balance shifted yellow-green
6 Surface      plain woven fabric with soft creases; fur shows individual strands
7 Language     photographic, unposed, amateur
8 Capture      deep depth of field, soft details, phone wide angle          [all estimates]
9 Text         none visible
```

The resulting brief-and-prompt pair, condensed:

```json
{
  "goal": "Reconstruct the look of a casual phone interior capture.",
  "locks": ["4:3 horizontal", "flat overhead ambient light, no directional source"],
  "direction": {
    "signature": "white balance shifted toward yellow-green with low saturation",
    "avoid": "window light, rule-of-thirds composition, tidiness"
  }
}
```

What to say when the user asks for the original parameters:

```text
Focal length, aperture, model, seed, and settings cannot be recovered from an image.
I can give you a reproduction suggestion, labelled as an estimate, or a model-neutral
prompt that works across generators. Which do you want?
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Prompt reads as a list of adjectives | jumped to writing before analysing | walk the nine stages first |
| Generating from it loses the composition | structural anchors omitted | state crop, placement, and viewpoint explicitly |
| Output is a generic version of the reference | only medium and style captured | add stages 2, 4, and 6 — composition, lighting, surface |
| Invented details appear in the prompt | filled gaps rather than marking them | mark estimates, or omit |
| User thinks the original settings were recovered | framing not made explicit | state that parameters are suggestions, not facts |
| Text in the reference is garbled in the prompt | transcribed unreadable text | write `[unreadable text]` or describe placement only |

## Companion skills

- `skills/smartphone-realism` — turn a reconstruction into a realism-specified prompt
- `skills/visual-brief` — store the reconstruction as a brief when it will be iterated

## See also

- `references/analysis-order.md` — the nine stages in detail, per-genre special cases, a worked example
