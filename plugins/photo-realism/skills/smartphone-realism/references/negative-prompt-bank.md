# Negative prompt bank

**Read this first.** Many generators, including the built-in image tool in some agent platforms,
have **no separate negative-prompt parameter**. In that case every item below must be rewritten
as an affirmative clause inside the main prompt — the surface you actually want rather than the
thing you want avoided. See "Affirmative rewriting" below.

Use these lists literally only when the generator exposes a dedicated negative slot (Flux,
SDXL, ComfyUI, and similar).

## Base bank

Adapted from the JSON prompt collection in
`GitHub30/Reproducible-Photorealistic-Nano-Banana-Pro-JSON-Prompts`.

```
Blurry, low-res, over-smoothed skin, heavy makeup, glam retouching, unrealistic doll face,
warped hands, extra fingers, missing fingers, deformed gestures, crossed eyes, bad anatomy,
distorted background, duplicated objects, text, watermark, logo, posterized lighting.
```

## Extended bank for realism targets

Add these when the goal is specifically "reads as a real capture" rather than "looks nice":

```
perfect composition, professional lighting, studio backdrop, HDR, heavy bokeh, cinematic
grading, magazine cover, retouched skin, symmetric framing, ultra sharp, 8k, render, CGI,
illustration, painting, 3d, plastic texture, glossy fur, glowing eyes, wallpaper, oversaturated,
high contrast, dramatic shadows, rule of thirds, centered subject, posed, editorial
```

## Negative bank for specific failure modes

| Failure | Add to negative |
|---|---|
| Pixel-art appearance | `pixel art, 8-bit, posterized, low-bit-depth dithering, mosaic` |
| Oil-painting surface | `oil painting, canvas texture, brush strokes, impasto` |
| Render appearance | `3d render, octane, unreal engine, CGI, subsurface scattering look` |
| Mould or grime overshoot | `mold, mildew, stains, peeling paint, water damage, filth, grime, heavy weathering` |
| Ratio impossible for a phone | `ultrawide, 21:9, cinematic bars, panorama` |
| Over-smoothing | `airbrushed, beauty filter, skin smoothing, denoise, noise reduction` |

## Affirmative rewriting

When there is no negative slot, invert each intent into a description of the object you want.
This is not a stylistic preference — negation loses to model priors (see
`references/failure-modes.md`), so an affirmative statement is strictly more reliable.

| Negative intent | Affirmative clause |
|---|---|
| `no retouching` | `natural skin showing pores and blemishes`, `fur showing real texture with a slightly dusty sheen rather than gloss` |
| `no professional lighting` | `flat overhead ambient light, no interesting shadows` |
| `no HDR` | `open shadow with low contrast and natural falloff` |
| `no oversaturation` | `not a single color is vivid, everything under a flat grey-yellow cast` |
| `not AI-generated` | `just a very ordinary boring photo taken by an ordinary person by accident` |
| `not centered` | `the exact center of the frame falls on empty surface beside the subject` |
| `not stained` | `freshly painted, uniform, no marks anywhere` — **and make the object genuinely new** |

## The counter-intuitive rule

Do **not** stack negations to fight a strong prior. Adding `not damaged, not stained, not
peeling` after describing something as `worn` and `lived-in` did not work in testing — twice.
Replace the object instead. Negations in Part 3 of the prompt are for **sealing the AI feel**
(authorial claim), not for **correcting object appearance** (physical description). Those are
different jobs and only the first one responds to negation.
