# DS-003 — QA Self-Review

**Verdict:** shippable. 8.7 / 10. Two real weaknesses, both documented below.

## Measured

| Metric | Result | Target | |
|---|---|---|---|
| Resolution / codec | 1080×1920, H.264 High, 30 fps | same | ✅ |
| Duration | 58.773 s | ≤ 60 s | ✅ |
| Size | 21.84 MB | ≤ 60 MB | ✅ |
| Integrated loudness | −14.1 LUFS | −14 ±1 | ✅ |
| True peak | −1.5 dBTP | ≤ −1.0 | ✅ |
| Voice intelligibility (mix) | 98.37 % | ≥ 96 % | ✅ |
| MP4 Whisper round-trip | 98.37 % | ≥ 96 % | ✅ |
| Frozen runs (>0.4 s identical) | 0 | 0 | ✅ |
| Black frames | 0 | 0 | ✅ |
| Mean luma | 0.094 | > 0.04 | ✅ |
| Shots / cuts | 11 / 10 | ≥ 8 shots | ✅ |
| Shortest shot | 3.18 s | ≥ 1.0 s | ✅ |
| Caption groups | 43, monotonic, max gap < 2.5 s | — | ✅ |
| QA gate | `all_passed: true` (6/6 checks) | — | ✅ |

## Scored

| Dimension | Score | Note |
|---|---|---|
| Hook (first 3 s) | 8.5 | "38 scientists published a warning" + "not about a bomb" is a clean two-beat turn, but it front-loads authority rather than danger. A first line closer to *what it does* would test better. |
| Script craft | 9.0 | 154 words / 58.8 s. Concrete throughout (handedness, flipped shape, protein printer). Only one abstraction survives: "anything that lives". |
| Factual discipline | 9.5 | Every claim is traceable to the Science paper or its 300-page report; the three compressions are disclosed in `sources_and_licenses.md`. Language stays in the conditional ("would", "could") throughout — nothing is asserted as having happened. |
| Visual design | 8.0 | Consistent, on-brand, safe-zone compliant. **Penalty:** this sandbox cannot initialise a WebGL context, so all 3D is a software Canvas2D projection at ~1,500 line segments/frame. It reads as deliberate schematic instrumentation rather than as photoreal 3D. Storytelling is intact; richness is not what it would have been with a GPU. |
| Pacing / retention | 8.0 | **The real weakness.** 10 cuts in 58.8 s (5.9 s/shot) versus 25 cuts at 57.3 s for DS-002. Three reveals carry the back half, but S04 (colony drift, 8.5 s) and S09 (ribosome, 5.8 s) hold single compositions too long for Shorts. |
| Audio mix | 9.0 | Sidechain-ducked score, −19 dB bed, 11 cue types. Voice is never masked; no cue collides with the twist. |
| Captions | 9.0 | Word-synced, 43 groups, emphasis weight on the seven load-bearing words. Font size and horizontal padding tuned after a review pass showed words colliding. |
| Publishing readiness | 9.5 | 5 titles, 1,562-char description with sources, 486-char tag string, pinned comment pre-empting the "this is fake" reflex, upload settings and a dedicated cover frame (not a mid-caption grab). |

**Weighted: 8.7 / 10.** Above the DS-001 bar (9.0) only if visual richness mattered less
than factual care; the pacing regression is the honest reason this lands lower.

## What was fixed during QA (kept for the record)

1. **Words collided in captions.** Flex `gap` was silently ignored by this Chromium
   build, so `scientists published a` rendered as `scientistspublisheda`. Switched to
   explicit per-word padding.
2. **Callout badge overlapped the artwork.** Added a dark gradient plate and a left rule;
   dropped the badge from y=404 to y=372.
3. **Two shots were static cards.** The `A BACTERIUM` reveal held one identical frame
   for ~4 s (right at the retention cliff) and the mirror-scan shot was frozen. The
   reveal now punches in and RGB-splits per frame; the scan helices rotate with progress.
4. **Colony shot read as a dust cloud.** Rebuilt as hollow membrane rings with bright
   nucleoids that split on division.
5. **Perfect wreath of antibodies** looked synthetic; replaced the constant-radius ring
   with a three-lobe jittered halo.
6. **`mirror_scan` showed two identical helices.** The D-handed strand is now genuinely
   mirrored in x rather than phase-shifted.
7. **Cover frame** taken from the video showed a half-finished caption. Rendered a
   dedicated cover composition instead.

## Known limitations (accepted)

- Software 3D only. No volumetric lighting, no true depth of field, no post-processing
  bloom. The `Soft3D` painter sorts by depth and draws flat strokes.
- Music is a 4-bar minor drone with a sparse upper motif — deliberately understated, and
  it will read as similar to DS-001/002 in a playlist. Acceptable for a series;
  a texture change is worth doing around DS-006.
- The phage and antibody schematic is illustrative, not to scale, and not modelled on any
  specific micrograph.
- Voice is `am_onyx` at 1.08 — identical to DS-001/002. Brand-consistent on purpose.

## Recommendation

**Publish Mon–Thu 16:30–18:30 UTC** with the primary title. Watch the 3-second view
retention in the first 2 hours; if it lands under ~65 %, the hook line is the cause and
DS-004's opener should lead with consequence rather than authority.

Before DS-004: fix the pacing rule. Target ≤ 4.0 s mean shot length and ≥ 18 cuts for a
58-second cut, and re-time the timeline *after* the voice pass so shot changes land on
sentence boundaries (three of DS-003's shots straddle a comma).
