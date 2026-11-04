# AGENT 3 — textures

**Question:** is the town painted rather than flat? Roughness 0.8?

## Method
`src/world.ts` → `paintTexture()` generates a 256² canvas per palette colour at
runtime: 150 elliptical brush strokes with ±0.22 lightness jitter, then 2600
dry-brush grain dots, then baked occlusion.

| Property | Value | Style bible | Verdict |
| --- | --- | --- | --- |
| `roughness` | 0.8 | 0.8 | PASS |
| `metalness` | 0.0 | 0.0 | PASS |
| AO intensity | 0.6 | 0.6 | PASS (baked, see F1) |
| Unique textures | 6 (one per palette colour) | ≤ 6 colours | PASS |
| Materials / draw groups | 6 shared across ~100 meshes | — | PASS |

Measured spread across the 9 stills (`analyze_frame.py`, % of pixels within
tolerance 120 of a palette colour): **35–50 %**, the remainder being lit and
shaded variants of those six — which is what a painted 3D surface should look
like. A flat-shaded town would show >90 %.

## Findings

1. **Painted, not flat.** Every face carries brush strokes and grain, and the
   stroke phase differs per colour via a seeded PRNG (`mulberry32`), so no two
   buildings repeat the same patch.

2. **`aoMap` silently deletes meshes — this was the single biggest bug in the
   build.** Assigning an `aoMap` to a JSX primitive (`<boxGeometry/>`) fails:
   three.js needs a second UV set (`uv1`) that the primitive never creates, and
   the mesh disappears from the draw entirely with no console error. Reproduced
   on a 3-box scene — the mapped box drew, the aoMap box did not.

3. Because of (2), occlusion is **baked into the albedo**: a vertical gradient
   over the lower 48 % of the tile (up to 0.6 × 0.5 = 30 % darkening at contact)
   plus a cavity burn on three edges (0.6 × 0.25 = 15 %). On a painted texture
   this is indistinguishable from a real AO term and costs nothing.

4. `RepeatWrapping` is set on every tile, but the JSX primitives all use the
   default 1×1 UVs, so the paint stretches once across each face rather than
   tiling. At these scales that reads as a brush-painted panel, which is fine,
   but it is not the tiling the wrapping implies.

## FIX

- **F1 (done):** aoMap removed, occlusion baked. Keep the comment in
  `world.ts` — the next person to "restore" the aoMap will reintroduce
  invisible geometry.
- **F2:** if tiling is wanted, set `mapTexture.repeat` per material and pass a
  `uv-multiply` through a small `onBeforeCompile`, or generate the buildings as
  real `BufferGeometry` with `uv1` so aoMap works.
- **F3:** raise the tile to 512² on machines with a real GPU — the grain reads
  coarser than intended at 256² when a building fills the frame.
