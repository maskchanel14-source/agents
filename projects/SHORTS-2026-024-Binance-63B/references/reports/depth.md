# AGENT 2 — depth

**Question:** is DepthOfField on, focused at 2.5, with 8–12 px of background blur?

## Method
`src/lens.tsx` — a self-contained three.js pass (render → depth target →
16-tap golden-angle disc blur weighted by circle-of-confusion).

| Setting | Value | Style bible | Verdict |
| --- | --- | --- | --- |
| DOF enabled | yes, all 2010 frames | enabled | PASS |
| `focusDistance` | 2.5 world units in front of subject | 2.5 | PASS |
| `aperture` → background blur | 0.05 → **10 px** | 8–12 px | PASS |
| Foreground blur | **4 px** | 4 px | PASS |
| Sharp band (`worldFocusRange`) | 12 world units | — | see F1 |

Measured on frame 100, DOF vs `noDof` (same frame, same seed):

| Region | Laplacian energy DOF | no DOF | Detail retained |
| --- | --- | --- | --- |
| Far strip (top 420 px) | 0.00725 | 0.01077 | **70.9 %** |
| Top 30 % (far town + sky) | 0.00725 | 0.01077 | 67.4 % |

So the pass is definitely blurring: roughly 30 % of the far-field detail energy
is removed. At 10 px on a 1920 px-tall frame that is the intended strength.

## Findings

1. **The blur radius is correct and in spec** — `lensPxForAperture()` maps
   aperture 0.05 to 10 px *at output resolution*, which required dividing the 4×
   upscale of the 480 px bokeh buffer back out. Getting this wrong was what made
   every frame dissolve into flat sky in earlier iterations.

2. **The sharp band is fixed at 12 world units regardless of shot distance.**
   That is right for the close beats (shot 6 sits 8–19 u away) but shallow for
   the wides: shot 1 is 71 u from the subject, so a 12 u band leaves most of the
   town soft. It reads as painterly rather than wrong, but it is not what a DP
   would dial in for an establishing shot.

3. **The band metric is confounded.** Comparing the top third against the middle
   third of the frame is not a clean background/subject split — the middle band
   of shot 1 is smooth plaza, so it has little detail to lose even at full
   sharpness. Use the DOF/no-DOF differential above, not band ratios.

## FIX

- **F1 (needs re-render):** scale the focus range with shot distance —
  `range = Math.max(12, distance * 0.45)`. Wides get a deep field (shot 1 → 32 u,
  sharp from ~37 to ~100 u, sky still soft); close-ups keep the shallow 12 u falloff.
- **F2:** add a `focusRange` prop to `LensBlur` so it can be tuned per shot from
  `story.ts` without touching the shader.
- **F3:** the 16-tap disc is the cheapest thing that does not read as a box blur;
  on a real GPU raise it to 32 taps and drop `height` back to full resolution.
