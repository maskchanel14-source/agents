# AGENT 5 — lighting

**Question:** are shadows `#2A2E6B` rather than black? Is there AO?

## Method
`src/compositions/Binance63B.tsx`. Measured on the 9 delivered stills with
`analyze_frame.py`; "near-black" counts pixels whose RGB sum is < 24 (i.e. far
below the `#2A2E6B` floor, which sums to 195).

| Still | Mean luma | Near-black | Clipped high |
| --- | --- | --- | --- |
| shot1_f0100 | 0.395 | 1.44 % | 0.77 % |
| shot2_f0327 | 0.477 | 0.79 % | 1.12 % |
| shot3_f0580 | 0.441 | 0.19 % | 0.68 % |
| shot4_f0807 | 0.474 | 0.04 % | 0.81 % |
| shot5_f0985 | 0.436 | 0.00 % | 0.78 % |
| shot6_f1230 | **0.176** | 0.06 % | 1.41 % |
| shot7_f1465 | 0.276 | 0.00 % | 0.75 % |
| shot8_f1607 | 0.358 | 0.27 % | 0.71 % |
| shot9_f1847 | 0.347 | 0.76 % | 0.92 % |

Rig: warm key `#FFE3A8` at 1.05 with shadows, cool fill `#8FD6FF` at 0.4,
hemisphere 0.6, cool ambient 1.25, plus a **second ambient at 0.42 tinted
`#2A2E6B`** — that last light is the shadow floor.

## Findings

1. **No black.** Eight of nine shots are at or below 0.8 % near-black, and the
   shadowed sides of buildings sample close to `#2A2E6B` rather than `#000`.
   Getting here needed the shadow-tinted ambient floor: before it, 8.8 % of the
   frame was crushed and the first full-bleed wide was unreadable.

2. **Shot 6 is too dark** — mean luma 0.176 against a 0.28–0.48 range
   everywhere else. It is the twist beat (the DevOps tower at night, one lit
   window), so some darkness is intentional, but 0.176 is 40 % below the next
   darkest shot and will read as a dropped frame in a feed.

3. **Highlights are clean** — under 1.5 % clipped on every shot.
   `NeutralToneMapping` at exposure 1.35 is doing that work. Note it has to be
   set on the renderer instance: passing `toneMapping` through R3F's `gl` prop
   silently does nothing, because the object goes to the `WebGLRenderer`
   constructor.

4. **AO is baked, not computed** (see `textures.md` F1). At 0.6 intensity it
   contributes the contact darkening; there is no screen-space or ray-traced
   occlusion term.

5. Shadow map is 1024² over a ±70 unit ortho frustum — about 7 texels per world
   unit. Adequate for the town, a little soft on the character planes.

## FIX

- **F1 (needs re-render, highest value):** brighten shot 6. Add a warm point
  light at `[10.5, 13.6, -6.5]` intensity ~8, and raise the tower's fill by
  swapping its material from `town` to `paper` for the two frames either side of
  the window. Target mean luma 0.28–0.32, keeping the window as the brightest
  thing in frame.
- **F2:** raise the shadow map to 2048² and tighten the ortho frustum to ±40 —
  the town only needs ~50 units of coverage, and the extra texels clean up the
  character contact shadows.
- **F3:** the 1.44 % near-black in shot 1 is the deep shadow under the bridge
  decks. Add a dim upward-facing fill at `[0, -3, 0]` if it still reads as a
  hole after F1.
