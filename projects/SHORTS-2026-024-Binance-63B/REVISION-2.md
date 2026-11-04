# REVISION 2 — semi-realist 3D rebuild

Same 67 s story, same script, same audio bed. The **art direction is rebuilt**.

Requested 2026-11-04: *"bisa dibikin 3d ga? dan lebih realistis lagi"*.
Direction chosen: **semi-realism**, **no ink outlines**, **natural (freed)
colour**, **full 3D humanoid characters**, rendered straight to the full 67 s.

## What changed

| | Rev 1 | Rev 2 |
| --- | --- | --- |
| Characters | 2D sprite planes, billboarded, boiling ink outline | jointed 3D figures — hips → thigh → shin → foot, spine → chest → head, shoulder → upper arm → forearm → hand |
| Proportions | chibi | real: ~7.5 heads, hip at 53 % of height, knee at 28.5 %, shoulder width 23 % |
| Animation | 9 baked sprite poses, 2-frame flip | continuous joint curves (breathing, walk cycle at ~110 steps/min, march at 100 BPM), cross-faded over 14 frames at every shot change |
| Outlines | 2.5–4 px boiling ink everywhere | none — form is carried by light and shadow |
| Palette | locked to 6 flat colours | natural dusk: concrete, plaster, brick, slate, asphalt, brass, steel, glass |
| Materials | one roughness (0.8) for everything | per-surface PBR with albedo + bump + roughness + emissive maps, metalness 0 → 0.9 |
| Ambient | ambient + hemisphere lights | procedural dusk equirect → PMREM environment map, so metal and glass actually reflect the sky |
| Sky | 2-colour gradient dome | 1024×512 equirect canvas: zenith → warm horizon → sun disc placed at the key-light direction; used as both `scene.background` and the IBL source |
| Tone mapping | renderer-level, silently ignored | ACES filmic, applied in the LensBlur resolve pass at exposure 1.9 |
| Shadows | shadow map only | PCFSoft 2048² + per-character contact-shadow decals |
| Atmosphere | linear fog 120→340 | exponential fog, density 0.0038 |
| Lens | fov 42 | fov 38 (longer lens is both more filmic and magnifies the cast) |
| Cast | 3 actors + 4 duplicated townsfolk | 3 actors + 4 townsfolk across two extra wardrobe variants, each with its own animation phase |

## Two bugs found and fixed along the way

1. **Tone mapping was never applied.** `WebGLRenderer` skips tone mapping
   whenever the draw target is a render target
   (`WebGLRenderer.js`: `if ( _currentRenderTarget === null || isXRRenderTarget )`).
   The LensBlur DOF pass renders the scene into a render target, so both
   `renderer.toneMapping` and `renderer.toneMappingExposure` were silently
   ignored — every frame came out flat and clipped. ACES now lives in the
   resolve shader in `src/lens.tsx`.

2. **The DOF pass was rendering nothing at all.** The first port of that shader
   named its helper `RRTAndODTFit`, which collides with the name three injects
   via `tonemapping_pars_fragment` into every non-raw `ShaderMaterial`. The
   program failed to compile (`'RRTAndODTFit' : function already has a body`)
   and the frame showed only the background colour plus the DOM text — which
   is why the first "exposure sweep" looked like it had no effect. Helpers are
   now prefixed `lens*`.

Both are recorded in the source comments so they are not reintroduced.

The DOF target also moved from 8-bit to **half-float**: the scene render is
untonemapped linear, so sunlit surfaces and the sky go well past 1.0 and were
being clipped before the ACES curve ever saw them.

## Render cost

Software GL in this sandbox has no GPU, so the PBR + IBL + bump-map fragment
cost is real: **~4.6 s/frame**, about **2 h 35 min** for all 2010 frames.
The scene itself is 3.9 s/frame; the LensBlur resolve is ~0.7 s/frame.
On a machine with a GPU the same composition is a few minutes.

## Files

- `media-production/src/theme.ts` — new palette, per-surface PBR table, dusk
  light rig, atmosphere, grade
- `media-production/src/materials.ts` — procedural albedo/bump/roughness/
  emissive maps, shared material library, per-building facade tiling
- `media-production/src/env.tsx` — equirect sky + PMREM environment
- `media-production/src/characters.tsx` — the humanoid rig
- `media-production/src/world.ts` — layout only (surfacing moved to materials.ts)
- `media-production/src/lens.tsx` — DOF + ACES + sRGB resolve
- `media-production/src/compositions/Binance63B.tsx` — scene, light rig, overlays
- `media-production/scripts/ascii_frame.py` — inspect a frame without a viewer

The audio bed, `facts.json`, `script.txt` and every spoken number are unchanged
from revision 1.
