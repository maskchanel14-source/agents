# Measuring identity instead of eyeballing it

A generation that "looks like them" to a tired author is not evidence. Face-identity scoring
is small, CPU-only, and turns the director loop's inspect step into a number with a threshold.

## The stack

1. **Detect** faces: YuNet (ONNX, tiny, CPU) is the default; a YOLO face model helps on
   full-body shots with small faces.
2. **Embed** the crop: SFace (light) or ArcFace (`insightface` `buffalo_l`, 512-d L2-normalized)
   for stronger discrimination.
3. **Compare**: cosine similarity between the output's face and the reference profile
   (average embedding of the anchor set).

Two open implementations worth reading: `artfat-creator/ComfyUI-Artfat-FaceConsistency` (MIT,
ComfyUI nodes with an inline pass/fail gate) and `SiddharthFulia/face-consistency-toolkit`
(MIT, Python library plus CLI that ranks a folder of outputs and writes a per-frame manifest).

## One flat threshold is unfair

A face embeds from its pixels, so **a small far face in a full-body shot legitimately scores
lower than a closeup of the same person**. A single pass bar either rejects good full-body
frames or lets weak closeups through. Scale the bar with face size:

| Face fraction of frame | Pass bar (cosine, SFace defaults) |
|---|---|
| ≥ 0.15 (closeup) | 0.60 |
| ≤ 0.03 (full-body, far) | 0.50 |
| between | linear interpolation |

These are the published defaults of the Artfat node, not universal constants. **Calibrate
from your own subject:** log `face_frac`, applied threshold, and score per frame for one
pack, then read where that subject's good frames actually land per size and set the bars from
the distribution.

## Borderline is a verdict, not a shrug

Route results three ways:

- **pass** — at or above the bar
- **borderline** — within a small margin *below* the bar (one-sided band; above already
  passed) — send to manual review instead of silently failing
- **fail** — below the band, or no face detected at all

A series review should look at the routing table, not at favorites.

## Grid of ten, not one hero image

Judge consistency from a grid of about ten outputs of the same identity. Single-image
judgment rewards the lucky frame; the grid shows the drift envelope — which features move,
how far, and whether the subject is still recognizable at a glance across all ten. Perceptual
consistency (a viewer instantly says "same person") is the achievable target; pixel-exact
consistency is not a property of sampling-based generators.

## Wiring into the director loop

In `photo-realism-director`'s inspect step, when the job carries a face reference:

1. Score the output against the anchor profile.
2. Report the number and the routing verdict alongside the visual diagnosis.
3. On fail: fix **one** identity-relevant field per iteration (ref set composition, frontal
   anchor, labeling, weight) — the same one-field discipline as visual failures.
4. On borderline: look at the crop before deciding; note which feature moved.
5. Append scores to a per-run manifest so iterations can be diffed, not remembered.

## Limits

- Embeddings measure face geometry, not styling: a correct face with wrong hair can score
  well while reading as "different person" to humans. Pair the number with the visual check,
  never replace it.
- Occlusion, extreme angles, and closed eyes degrade embeddings; treat those frames as
  unmeasurable rather than failed.
- Thresholds are model-pair specific (detector + embedder + generator). Re-calibrate when any
  of the three changes.

## Attribution

Adaptive-threshold design and default values from `artfat-creator/ComfyUI-Artfat-FaceConsistency`
(MIT); embedding/ranking architecture from `SiddharthFulia/face-consistency-toolkit` (MIT).
