# REVISION 3 — 2D explainer with a host

2026-11-05 · branch `arena/ce22919c-agents` · PR #22

## The request

> "gausah bikin 3d.. 2d aja cukup asal kualitas nya diatas rata rata, aku gamau
> 2d murahan.. aku mau ada kayak person yang jelasin kasus ini dengan bahasa
> yang mudah dipahami, semacam 'guru' gitu.. disertai ilustrasi juga sesuai isi
> narasi.. sama text nya juga diperbaiki.. buat lebih menarik"

Four things: drop the 3D, make the 2D good (not cheap), add a teacher who
explains, illustrate the narration, rewrite the copy.

Decisions locked with the user before any code was written:

| Question | Choice |
| --- | --- |
| VO + on-screen language | English |
| Visual style | editorial illustration (Vox / WSJ register) |
| When the host appears | full frame at the hook, at the turn into the twist, and at the close — out of the way when the picture carries the point |
| What the host looks like | clean vector cartoon (not an AI portrait) |

## Host redraw (2026-11-05)

> "perbaiki lagi vektor gurunya, jelek banget"

The first host drawing was not good enough, so `src/host.tsx` was thrown out and
redrawn from the skull out. What was wrong, and what it is now:

| Problem in the first drawing | Fix |
| --- | --- |
| The head floated — the neck stopped at y 358, the shoulders started at y 416, so a band of empty background showed between chin and collar | shoulders raised to y 382; the neck fill runs to y 442, well under the collar |
| The jacket gaped open below the lapels and showed a big cream triangle of knit | the jacket front closes under the lapels; the knit sweater is confined to the V |
| The gesturing arm was the same navy as the torso, so it vanished into the chest | its own lighter sleeve gradient, a 3 px ink outline, and a soft cast shadow on the chest |
| Hair was a flat helmet | swept fringe with a side parting, two hairline strands, sideburns, a highlight |
| Eyes were white almonds with a dot in them | sclera + iris + pupil + catchlight, with a double blink every 3.8 s |
| The mouth became a dark hole when it opened | lips + opening + teeth + tongue; it opens to 22 px and never reads as a hole |
| Hands were mittens | four fingers and a thumb, in three poses (`hang` / `point` / `open`) |

The palette, the rim light, the blink and breathing cycles and the gesture
vocabulary are unchanged, so the redraw drops straight into the composition that
was already built around it.

## What changed from revision 2

| | Rev 2 (semi-realist 3D) | Rev 3 (2D explainer) |
| --- | --- | --- |
| World | three.js town, PBR materials, IBL, ACES | flat vector illustration, one hand-built card per beat |
| Cast | 7 rigged 3D humanoids | one vector host, drawn as SVG in `src/host.tsx` |
| Camera | one continuous spline glide, no cuts | 12 scenes crossfaded over 18 frames |
| Text | caption bar | display type, word-by-word, colour-coded by role |
| Story | the same 67 s, read as a heist | the same facts, now *explained* to a viewer who has never bought crypto |
| Length | 67.0 s (2010 f) | 71.5 s (2145 f) |
| Render | ~2 h 35 m on software GL | ~21 min, no GPU needed |

The 3D composition is still registered as `SHORTS-2026-024-Binance63B-3D-rev2`
so revision 2 stays renderable.

## New script (`script-rev3.txt`)

170 words in 10 VO lines. The rewrite rules:

- **Analogy before jargon.** "A bank for digital money" lands before the word
  *exchange*; "a small pile online for withdrawals" lands before *hot wallet*.
- **One idea per line**, one breath each, 10-27 words.
- **The close restates the hook in reverse**: the vault was never broken —
  somebody just asked for the keys.
- **One claim was deliberately dropped.** Revision 2 said "the world's largest
  crypto exchange". No sentence in `facts.json` says that, so the line is now
  "Binance is a crypto exchange". Everything else still maps to a fact id.

## New audio (`scripts/shorts024_audio_rev3.py`)

- VO re-recorded with the selected educational/English voice, 10 clips,
  `atempo 1.06` (teacher pace — revision 2 ran at 1.07).
- **Score replaced.** Revision 2 was a 100 BPM military march. Revision 3 is a
  92 BPM documentary bed: warm detuned pad, plucked arpeggio, soft kick, rim
  clicks, hats, sub accents, in five sections that follow the story.
- Film length is now **derived** from the measured VO (71.50 s / 2145 frames),
  not hard-coded.
- Same mix chain: music ducked −6 dB under voice (50 ms attack / 250 ms
  release), SFX peaking at −12 dBFS, loudnorm to −14 LUFS.
- **New export:** `audio/mouth.json` → `src/data/shorts024Mouth.ts`, a
  per-frame voice-energy curve that drives the host's mouth, so he appears to
  speak the actual words.
- **New export:** `src/data/shorts024Timeline.ts`, the caption timing the
  composition reads. The picture cannot drift from the voice.

## New composition (`src/compositions/Binance63B2D.tsx`)

- **Layout** (`src/theme2d.ts`): one card (960 px wide, 660 px tall, 520 when
  the host steps up), display type below it, chrome at the top, chapter rail
  and a key-numbers strip at the bottom that fade out when the host is on.
- **Host** (`src/host.tsx`): one SVG, 520×780, with a driving rig — mouth from
  the voice envelope, deterministic double blink, breathing torso, head bob,
  eyebrow raise on the question beats, and a right arm that takes `idle`,
  `point` or `open` gestures.
- **Scenes** (`src/scenes2d.tsx`): 10 generated illustrations + 2 hand-drawn
  vector scenes (the attribution dossier and the record bar chart), each with a
  slow Ken Burns push and a bottom scrim.
- **Overlays**: the ten chain chips, the 18,270 BTC counter that counts up, the
  frozen/gone split bar, the 50-authorisation tick wall, the 1 Nov date chip —
  all animated on springs.
- **Grade**: warm bloom, vignette and a procedural film grain over everything.

## Known limits

- Image generation is capped at 10 per turn, so the attribution dossier
  (frame 1652) and the record chart (frame 1772) are hand-drawn vector scenes
  rather than generated illustrations. Both are animated, so they read as
  designed rather than as a missing asset.
- The film is dark by design (mean luma ≈ 0.13-0.25 depending on the beat). The
  type, the host and the numbers carry the brightness.
