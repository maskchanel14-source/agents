# AGENT 6 — outlines

**Question:** is the ink 2.5–4 px, and does it boil 0.3–0.8 px every frame?

## Method
`src/characters.tsx`. The sprite is drawn with a 6 px outline in a 512 px-tall
tile; the fragment shader then boils the sample coordinates and dilates the
silhouette by a distance-scaled amount.

| Property | Value | Style bible | Verdict |
| --- | --- | --- | --- |
| Ink weight | 2.5 px far → 4.0 px near | 2.5–4 px | PASS |
| Boil amplitude | 0.3–0.8 px, `sin(uTime*3 + vUv.y*9)` | 0.3–0.8 px | PASS |
| Boil formula | `sin(uTime*10.0 + vUv.x*5.0) * 0.008` | exact | PASS |
| Boil update | every frame (driven by `useCurrentFrame`) | every frame | PASS |
| Silhouette dilation | 4-tap alpha max, up to +1.2 px | — | PASS |

## Findings

1. **The spec formula is implemented verbatim** and then *rescaled into screen
   pixels*. This matters: 0.008 in UV space on a 256-wide tile is ~2 px of
   wobble, roughly 2.4 px on screen — three times the spec. `uPxToUvY` converts
   screen px to UV using the plane's on-screen height, so both the boil and the
   outline dilation are specified in real pixels.

2. **Weight varies with distance** as required: `uInkWidth` interpolates 4.0 px
   at 6 units down to 2.5 px at 46 units, derived from the camera-to-plane
   distance each frame.

3. **One real bug found and fixed during the render.** `${INK.maxPx}` is `4.0`,
   which template-interpolates to the integer literal `4`, producing
   `clamp((uInkWidth - 2.5) / (4 - 2.5), …)` — GLSL `int − float`, shader fails
   to compile, and the browser crashed on frame 0. Every interpolated constant
   now uses `.toFixed(1)`. **Any future numeric constant added to these shaders
   must do the same.**

4. **Not yet verified in isolation.** The boil is a sub-pixel effect on
   characters that occupy 3–5 % of frame height in most shots (see
   `characters.md` F1), so the delivered stills cannot confirm it visually. The
   uniforms and math are verified by construction, not by measurement.

5. Only the characters carry ink. The town, vault and bridges have painted
   textures but no outline, so the frame mixes inked characters with un-inked
   environments.

## FIX

- **F1 (verification, no re-render):** render a 400×400 crop of the guard at
  frame 100 and at frame 101 and diff them. A boiling line changes between
  consecutive frames; a static texture does not. Target: 0.3–0.8 px of edge
  displacement, i.e. a thin fringe of changed pixels along every silhouette.
- **F2 (needs re-render):** add a screen-space ink pass over the whole scene —
  a depth+normal Sobel with the same 2.5–4 px distance ramp and the same boil
  function — so the town is outlined too. That is what makes the reference
  channel read as "2D characters in a 3D world" rather than "3D world with
  stickers in it".
- **F3:** after F1 in `characters.md` (bigger characters), re-measure: at 8–14 %
  of frame height the boil becomes directly measurable.
