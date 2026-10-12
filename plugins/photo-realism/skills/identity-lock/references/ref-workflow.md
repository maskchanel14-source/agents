# Reference workflow for identity preservation

Synthesized from `asreynolds1000/ai-image-generation-guide` (CC-BY-4.0), trimmed to the rules
that transfer across generators, with this repository's additions noted where they appear.

## Collecting references

Gather 8–15 real photos when the subject is a consenting real person. Prioritize:

- **Must have:** front-facing (clear, well-lit), three-quarter both sides, profile, full length for full-length work
- **Good to have:** different lighting, different expressions, closeups of distinguishing marks
- **Avoid:** group shots with a small face, heavy filters, faces turned away, low resolution or heavy compression

**Separate eras.** If the subject's look changed over time (age, hair, glasses), keep one ref
set per era. Mixed-era sets get averaged into a person who never existed.

**Compression for API calls.** Identity refs (face-critical): resize to ~1500px, JPEG quality
~50. Non-identity refs (mannequins, scenes, clothing): ~1200px, quality ~35. For high-res
originals, crop head-and-shoulders first so the face fills half the frame or more.

## Who is the authority

**Real photos are the identity authority.** Generated headshots with consistent lighting and
neutral backgrounds make useful *supporting* refs — they resist style contamination better
than messy real photos — but the primary anchor and any face-swap source must be a real
photo. Identity built only from generated assets is a copy of a copy and drifts.

Let a text model describe the subject's face from the real photos; it names geometry better
than manual prose. Then correct its beautification bias (it reports teeth as straight and
white regardless) and verify the skin tone against the photos.

## Ordering and labeling

Earlier image slots are weighted more heavily. A working five-slot call:

| Slot | Content | Label shape |
|---|---|---|
| 1 | real photo, angle-matched, face-dominant | `REAL PHOTO of X — the face must match this` |
| 2 | headshot or second real photo, pose-matched | same |
| 3 | expression-matched ref | same |
| 4 | nose closeup | `NOSE CLOSE-UP. Match exactly.` |
| 5 | teeth closeup, or hairstyle mannequin | `TEETH CLOSE-UP. Match exactly.` / `HAIRSTYLE mannequin. No face. Hair structure only.` |

Rules that fail loudly when broken:

- **Three face refs maximum.** More causes face averaging, not better accuracy.
- **A frontal anchor in every set**, including profile and 3/4 outputs. Sets without one were
  the only sets that drifted in the source testing.
- **Style refs last**, and every non-identity ref carries `IGNORE the face`. Unlabeled refs
  donate their faces to the subject.
- **Match refs to the output angle and expression.** This is the single biggest factor in ref
  selection quality.

## Two-pass generation

For dramatic hairstyle or outfit changes, or any single-pass identity drift:

1. **Pass 1 — identity only.** All slots on identity; subject wears natural hair plus the
   target outfit. This pass must produce a recognizable face before anything else is tried.
2. **Pass 2 — one targeted edit.** Pass-1 output in **slot 1** as base (`This IS X. BASE
   IMAGE. Only change the hair.`), identity refs next, one mannequin last. Frame it as an
   edit, not a regeneration; keep temperature low. Putting identity refs before the base, or
   high temperature, are the two documented ways to fail this pass.

Keep pass-1 outputs: they are reusable bases for future swaps.

Identity scores fall as hair stops framing the face (natural hair down scores highest;
slicked-back and pixie lowest). The model uses hair as part of the identity anchor — expect
it and budget an extra iteration for uncovered-face looks.

## Mannequins: style without face contamination

Generate hairstyles and outfits on a **featureless white mannequin** (no face, no hair for
clothing; bald smooth head for hair) and combine with identity refs at generation time. This
removes the biggest multi-reference problem: style refs that carry a face.

- Specify the part side in frame-relative language in every mannequin prompt.
- Add `no earrings, no jewelry, no accessories, bare ears` — accessories bleed from real refs
  onto mannequins otherwise.
- Include 2–3 real photos of the subject wearing the style when generating their mannequin;
  text-only mannequins default to center parts and generic construction.
- Demand volume explicitly (`natural volume and body, not flat, not sleek`); mannequin hair
  trends sleek.

## Stubborn cases

- **Same angle twice despite prompts:** mirror a successful 3/4 output horizontally and send
  it last as a pose-only reference, labeled `pose reference only; the face must come from
  images 1–4`.
- **Identity keeps failing with a style ref present:** drop the style ref and describe the
  scene fully in text. No ref, no contamination.
- **Right scene, wrong face:** send the bad image as a scene reference after the identity
  set: `recreate this exact image but replace the face with X's face from images 1–5`.

## Provider notes (as tested by the source guide, 2026)

| Provider | Identity behavior |
|---|---|
| Gemini Flash-class image | default for identity work; strong multi-constraint adherence, high rate limits |
| Gemini Pro-class image | 4K and editorial; no identity advantage over Flash |
| gpt-image | 16 refs and native transparency; smooths and airbrushes faces — add texture language |
| Grok Imagine | single-photo edits, cheap; no multi-ref |

## The last layer

When prompting and references still cannot cross the likeness ceiling — short hair, profiles,
occluded faces — generate the composition and swap the real face on with an open-source
face-swap tool, using a clean straight-on real photo as source. This transfers real pixels;
prompting cannot.
