# REVISION 4 — the host, rebuilt on a real avatar library

2026-11-05 · branch `arena/ce22919c-agents` · PR #22

## The request

> "perbaiki lagi vektor nya, gunakan skill2 atau plugin di repo GitHub publik…
>  dan standar kualitas harus sama kayak youtuber yang punya 50 juta subscriber"

Two instructions: stop hand-drawing the host and build it out of public,
professionally drawn vector libraries instead — and hold the result to the
standard of a 50-million-subscriber channel, not to "good enough for a short".

## What the host is made of now

| Layer | Library | Licence |
| --- | --- | --- |
| Artwork | **DiceBear — Notionists**, drawn by Zoish | **CC0 1.0** (public domain) |
| Assembler | **@dicebear/core 10.7.0** | MIT |

Why these:

- **CC0, not CC-BY.** Nine DiceBear styles (Adventurer, Big Ears, Big Smile,
  Croodles, Dylan, Micah, Miniavs, Personas, ToonHead) are CC-BY-4.0 and would
  need a visible on-screen credit on every frame. Notionists is CC0 — no credit
  obligation, safe for commercial upload.
- **npm, not the HTTP API.** The parts are baked into the repository
  (`src/host/parts.ts`), so the render is reproducible offline and cannot drift
  because a CDN changed.
- **Half-body, hand-drawn line art.** Notionists draws a *bust*, not a
  head-only circle avatar — exactly the framing a presenter needs — in a
  sketchy editorial line that matches the rest of the film.

## Pipeline

```
scripts/dicebear_lab.mjs   →  public/_lab/*.svg    contact sheets, every variant
                              (authoring aid; nothing shipped)
scripts/lab_cells.py       →  per-variant ink coverage / symmetry / bbox
scripts/dicebear_host.mjs  →  src/host/parts.ts    AUTO-GENERATED, the baked parts
src/host.tsx               →  the rig: depth order, recolour, per-frame motion
```

Re-baking after a change is one command:

```bash
cd media-production && node scripts/dicebear_host.mjs
```

## Picking the parts by measurement, not by eye

The library ships 64 hairstyles, 30 mouths, 25 outfits, 20 noses, 13 brows, 12
beards, 11 glasses, 10 gestures and 5 eye sets. Each candidate was rendered and
measured — ink coverage inside its cell, left/right symmetry, and bounding box —
and the pick is the one that scores best for a presenter:

| Part | Variant | Measured reason |
| --- | --- | --- |
| head | `variant01` | the style ships one head shape |
| hair | `variant12` | even weight, symmetric, reads as a hairline rather than a helmet |
| mouth | `variant11` | widest, most symmetric open mouth *with teeth* — ink/paper ratio 1.46 (lowest of the open set = most open), symmetry 0.94 |
| nose | `variant03` | smallest, least distracting at presenter scale |
| eyes | `variant01` | coverage 0.028, symmetry 0.97 |
| glasses | `variant03` | thin frame, **no lens fill**, so the eyes stay visible |
| eyebrows | `variant02` | carries a brow raise without turning into a cartoon |
| clothes | `variant14` | flat front, few fold lines, coverage 0.311, symmetry 0.99 |
| gestures | `hand` / `point` / `pointLongArm` | idle / explanatory jab / open palm |

## The rig

- **Canvas** 1744 × 1744 (the style's own). The composition uses the measured
  ink extents as the viewport — `HOST_VIEW {x:172, y:234, w:1372, h:1538}` — so
  the figure is framed to its own silhouette with no dead margin, and
  `Binance63B2D.tsx` sizes the host from `HOST_ASPECT` instead of a hard-coded
  ratio.
- **Depth order:** clothes → head → hair → mouth → nose → eyes → glasses → brows
  → gesture. The arm is last, so it crosses in front of the body the way a real
  one does.
- **Recolour.** The style ships as black ink on white paper. Each part is
  re-inked for the film's palette: ink `#140F0B`; skin `#E8B58A`; hair and brows
  `#6B4A30`; suit `#4A6A9C` (chosen so the torso separates from the deep-navy
  backdrop — measured 3.9 × the backdrop luma); teeth `#F6EDE2`; eye whites
  `#FDF7F0`. The hair is drawn by the library as a solid silhouette, so its ink
  is tinted to the hair colour rather than left black.
- **Motion, all driven per frame:** mouth opens 0.09 → 1.00 from the real VO
  envelope (`audio/mouth.json`) and narrows slightly as it opens; eyes blink on a
  deterministic 3.9 s double-blink; the head nods on two sine terms plus a
  speech term; the torso breathes at 0.8 Hz and bobs; the brow lifts 7 px; the
  gesture arm swings about the shoulder. Every transform is applied about the
  part's own centre, taken from the library's component geometry.
- **Public API unchanged:** `<Host frame mouth gesture brow width height />`, so
  the composition did not have to change beyond the aspect constant.

## Verification

The character was rendered alone against a flat card and read back pixel by
pixel (no vision available — measurement only):

- mouth closed vs open → 4,942 pixels change, confined to the mouth box;
- blink frames 2 and 17 → the eye box changes, and nothing else does;
- idle / point / open-palm → verified in the film at frames 90, 420, 1080 and
  1450, with the raised arm inside frame and clear of the caption;
- figure vs backdrop, measured on the delivered frames: torso 0.283 against
  0.073 backdrop, hair 0.201, head 0.423.

`HostTest` (1080 × 1920, registered in `src/Root.tsx`) is kept as the rig
playground for future host tweaks; it is not part of the film.

## Attribution

Host artwork: **Notionists** by Zoish, CC0 1.0 (public domain dedication).
Assembled with **@dicebear/core**, MIT © DiceBear. Both permit commercial use
without credit; the credit is recorded here and in the QC report as a matter of
record.

## Result

| | Revision 3 | Revision 4 |
| --- | --- | --- |
| Host drawing | hand-authored SVG paths | DiceBear Notionists (CC0), mix-and-match |
| Parts available per swap | 1 (redraw) | 196, pickable from contact sheets |
| Host mean luma on the dark backdrop | 0.140–0.164 | 0.169–0.197 |
| Master | 32.3 MB | 34.6 MB |
| Audio | −14.7 LUFS | −14.7 LUFS (unchanged — the VO was not re-cut) |

Nothing else changed: same 2145-frame edit, same 170-word script, same
illustrations, same timing.
