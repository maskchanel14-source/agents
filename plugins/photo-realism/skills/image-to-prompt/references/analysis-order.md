# Analysis order in detail

Adapted from the `image-to-prompt` skill by
[jiemianduan](https://github.com/jiemianduan/image-to-prompt) (MIT).

The order is a priority queue, not a checklist. Earlier stages constrain later ones, so an error
in stage 1 costs more than an error in stage 8. Work top-down and stop refining a stage when
adding more detail would not change the generated image.

## Stage detail

### 1. Subject and action

Identity category, count, pose, expression, interaction, clothing, props. Record counts
explicitly — `three people` not `a group` — because count is the most common thing to lose.

### 2. Composition

Orientation, crop, subject placement, symmetry, foreground / midground / background, negative
space, viewpoint. Use spatially explicit language: `subject in the lower-right third`,
`horizon on the upper third line`.

Placement worth stating numerically in prose even when the reference is not rule-of-thirds:
subjects in amateur photos are frequently off-center by accident, and reproducing that accident
is often the point.

### 3. Environment

Location, background elements, weather, time-of-day cues, atmosphere. Note deliberately empty
backgrounds as well as busy ones.

### 4. Lighting

Direction, softness, contrast, key/fill/rim behavior, practical lights, shadow character.
`Soft backlight from frame left` is more reproducible than `nice lighting`.

Estimate the source: window, overhead ambient, on-camera flash, practical lamp. Source implies
shadow shape, and shadow shape is what makes lighting believable.

### 5. Color

Dominant palette, accent colors, saturation, temperature, tonal range. Name actual colors where
possible, including the unglamorous ones — a yellow-green white-balance cast is a strong
authenticity signal for phone captures.

### 6. Surface and detail

Materials, texture, depth of field, grain, bloom, motion, reflections. Distinguish **noise**
(digital, luminance) from **grain** (film, clumped) — they are not interchangeable in a prompt.

### 7. Visual language

Photographic, cinematic, editorial, commercial, painterly, vector, cel-shaded, clay, CGI,
collage. Name the medium before naming a genre, and name the medium before naming an artist.

### 8. Capture and render cues

Plausible shot scale, perspective, focal-length range, rendering method, post-processing. For a
phone capture, deep depth of field and soft details are more likely than a shallow, sharp image.

**Mark every value here as an estimate.** These are the fields most likely to be fabricated, and
a confident wrong focal length is worse than an acknowledged guess.

### 9. Text and layout

Transcribe only legible text. For unreadable text write `[unreadable text]` or describe its
placement and typographic character. Do not invent wording.

## Genre special cases

| Genre | What to prioritize |
|---|---|
| Product | Product geometry, material, camera angle, grounding shadow, reflections, backdrop, commercial lighting |
| Portrait | Pose, gaze, crop, expression, hair, wardrobe, background separation, skin-light interaction — **without inferring identity** |
| UI screenshot | Information architecture, layout, component styling, density, color tokens, interaction states. Not a photographic scene |
| Poster or graphic | Separate the visual prompt from exact copy. Preserve hierarchy, grid, spacing, typography category, text placement |
| Highly stylized | Line quality, shape language, shading method, texture, palette, composition — **before** genre labels |
| Poor quality or obstructed | State the limiting issue and give a best-effort prompt. Do not invent hidden detail |

## Worked example: reading a phone-realistic interior

Analysing an image of a cat asleep on a sofa shot to look like a phone snapshot:

| Stage | Observation | Estimate flag |
|---|---|---|
| 1 Subject | One adult tabby cat, asleep, one paw over the cushion edge | — |
| 2 Composition | 4:3 horizontal, sofa in right two thirds, subject right of the vertical midline, tilted slightly | — |
| 3 Environment | Small apartment, table on the left with papers and a mug, plain wall behind | — |
| 4 Lighting | Flat overhead ambient, no directional source, open shadow, no dramatic falloff | source = estimate |
| 5 Color | Warm grey, oatmeal, muted; white balance shifted yellow-green; low saturation throughout | — |
| 6 Surface | Plain woven fabric with soft creases; fur shows individual strands; slight luminance noise | — |
| 7 Visual language | Photographic, unposed, amateur | — |
| 8 Capture cues | Deep depth of field, soft details, phone wide angle | **all estimates** |
| 9 Text | None visible | — |

The resulting prompt should carry stage 1–6 as fact, stage 7 as the medium, and stage 8 as
explicit suggestions. Anything the analysis could not see — lens, seed, model, exact settings —
must not appear at all.

## What not to do

- Do not name an artist, brand, or model that is not visibly documented.
- Do not identify a real person from appearance.
- Do not present a recovered parameter as fact. `Likely a 24–28mm equivalent phone lens` is
  honest; `shot at 26mm f/1.8` is invented.
- Do not blend traits from multiple references without saying which came from which.
- Do not keep a prompt term that fights the observed image just because it is fashionable.
