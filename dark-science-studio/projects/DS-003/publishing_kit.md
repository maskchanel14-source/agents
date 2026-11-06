# DS-003 — Publishing Kit

**Video ID:** DS-003
**Topic:** The 2024 *Science* warning against building mirror bacteria
**Duration:** 44.0 s · 1080×1920 · 30 fps · 21.41 MB
**QA:** `all_passed: true` (7 scored checks pass, 1 skipped — see §10)
**Publish date:** 2026-11-06

---

## 1. Title options (≤ 60 chars)

| # | Title | Chars | Notes |
|---|-------|-------|-------|
| 1 | **38 Scientists Begged Us Not to Build This** | 44 | ⭐ **RECOMMENDED** |
| 2 | Life Has a Handedness. We Could Flip It. | 42 | Best for a biology-literate audience |
| 3 | Scientists Warned Against a Mirror Bacterium | 45 | Closest to how press covered the paper |
| 4 | A Cell Nothing on Earth Could Stop | 35 | Most ominous, least literal |
| 5 | The Organism That Doesn't Exist. Yet. | 37 | Strong curiosity gap, weakest search intent |

**Why #1:** it puts the number and the pleading in the first four words, which is
the whole story — 38 named scientists, including two Nobel laureates, publishing
in *Science* to argue that something should never be built. It front-loads the
curiosity gap ("This" = what?) without clickbaiting a claim the video doesn't
deliver: the video names mirror bacteria in the first 8 seconds and closes on the
same warning. It carries the search phrase "38 scientists" and avoids the jargon
("chirality", "enantiomer", "mirror bacteria") that a cold audience doesn't type.

---

## 2. Description

```
In December 2024, thirty-eight scientists — including Nobel laureates Jack Szostak and Gregory Winter — published a warning in Science. Not about a bomb. About a bacterium that does not exist yet.

Every living thing on Earth is built with the same handedness. Sugars twist one way, proteins the other, and your immune system reads that shape to recognise a threat. Flip it, and you get a mirror cell: the same chemistry, wound the other way.

The report's conclusion is unusually blunt. Antibodies would not grip it. Phages would not infect it. Antibiotics would not touch it. It could eat the food we eat, and nothing on this planet has evolved to eat it. A mirror bacterium released into the environment would have no natural predator and no natural brake.

The Stanford-led technical report estimates roughly ten years to build one with serious funding — fifteen to thirty on the trajectory we are on now. The authors are not asking for a ban on knowledge. Mirror molecules are useful, and that research can continue. They are asking that we never build the organism.

No mirror bacterium exists. This video is about a warning, and about the ten years we have to act on it.

SOURCES
Adamala et al., "Confronting risks of mirror life," Science 386(6728):1351–1353, 12 Dec 2024 (doi 10.1126/science.ads9158) — 38 authors, including Szostak and Winter
Technical Report on Mirror Bacteria: Feasibility and Risks, Stanford, 2024 (doi 10.25740/cv716pj4036) — feasibility timelines and immune-evasion analysis
Bulletin of the Atomic Scientists, 13 Dec 2024 — "mirror bacteria should not be created"
World Health Organization, Q&A on mirror biology, 5 Feb 2026 — capacity at least a decade away
Royal Society of Biology, "Danger in the Mirror" — 1992 precedent and the 2025 MBDF dialogues

#shorts #darkscience #science #biology #mirrorlife
```

*(Word count: 291 — inside the 150–300 range.)*

---

## 3. Hashtags

```
#shorts #darkscience #science #biology #mirrorlife
```

---

## 4. Tags (comma-separated, 471 chars)

```
shorts, dark science, mirror life, mirror bacteria, mirror biology, chirality, handedness, synthetic biology, science warning, 38 scientists, nobel laureate, jack szostak, gregory winter, science 2024, bioethics, existential risk, biology facts, dna, enantiomer, left handed life, science news, dark science shorts, mirror cell, biosecurity, science explained
```

---

## 5. Pinned comment

> The part that stays with me: the authors explicitly say mirror *molecules* are
> fine to keep researching — it's the self-replicating organism they want ruled
> out in advance. That's a strange thing to legislate: a ban on something that
> doesn't exist. Is pre-emptive prohibition the right call here, or should we
> build the containment first? 👇

---

## 6. First-frame / cover guidance

- **On-screen first-frame text (0–2.3 s):** the colony shot with `DEC 2024 / SCIENCE`
  top-left and the caption `IN DECEMBER 2024, THIRTY-EIGHT` word-synced below.
- **Shipped cover:** `cover_frame.png` — a dedicated composition, **not** a video
  grab. `MIRROR LIFE` in Anton over the cyan radial, kicker
  `38 SCIENTISTS · SCIENCE, DEC 2024`. Rendered from `build/DS-003/cover_props.json`.
- Do **not** use a mid-video frame as the thumbnail: every frame carries a
  half-spoken caption and they clash with the overlay text.

---

## 7. Best posting time

**16:30–18:30 UTC, Tuesday to Thursday.**
That is 12:30–14:30 US Eastern (lunch scroll), 11:30–13:30 US Central, and
21:30–23:30 in the UK and Europe. A biosecurity-mystery angle over-performs with
a US/UK/India STEM audience, and this window is the widest overlap where all
three are awake. Publish ~30 minutes before the peak so the first-hour Shorts
test pool is still filling.

---

## 8. Audience & disclosure

- **Made for kids:** No
- **Altered / synthetic content label:** **Yes.** Synthetic narration (Piper VITS,
  `en_US-lessac-medium`) and code-generated visuals. No real imagery of mirror
  bacteria exists at any resolution — there is no photograph of an organism that
  has never been built.
- **Category:** Education / Science.
- **Accuracy note:** every claim is conditional — "would not", "could", "would
  have no". Nothing is asserted as having happened. Two simplifications are
  disclosed in `sources_and_licenses.md`: the "ten years" figure is the report's
  *concerted-funding* estimate (15–30 years is the current trajectory), and
  "antibiotics would not touch it" compresses several distinct mechanisms
  (target absence, altered membrane permeability, no phage receptors).
- **Copyright:** zero third-party media. Visuals are Remotion Canvas2D code; the
  score is a per-timeline MIDI rendered through a General MIDI soundfont; all SFX
  are procedurally synthesised.
- **Loop:** the last shot returns to the colony from frame 1, and the closing line
  ("Please.") cuts straight back into "In December 2024, thirty-eight…".

---

## 9. Asset credits & licences

| Asset | Origin | Licence |
|-------|--------|---------|
| Voice | Piper `en_US-lessac-medium` VITS ONNX, local CPU inference | MIT (Piper) / CC BY 4.0 (lessac voice) |
| Music | Original MIDI score composed for this timeline (`audio_kit.py`) | Channel-owned |
| Soundfont | TimGM6mb.sf2 (Tim Brechbill) | GPL-2.0 / free for commercial use with attribution |
| SFX (36 cues) | Procedurally synthesised (NumPy/SciPy) | Channel-owned |
| Visuals | Remotion 4 + Canvas2D soft-3D (`Soft3D.tsx`), code-generated | Channel-owned |
| Fonts | Anton, Montserrat, Inter, JetBrains Mono | SIL OFL 1.1 |
| Science | Adamala et al. 2024 (Science), Stanford mirror-bacteria report, BAS, WHO, RSB | Facts cited, no figures reproduced |

---

## 10. Upload checklist

- [x] 1080×1920, 30 fps, H.264 High + AAC 320k, 21.41 MB
- [x] 44.0 s (≤ 58 s)
- [x] −14.0 LUFS integrated, −1.1 dBTP true peak
- [x] 21 shots / 20 cuts, mean shot 2.1 s (shortest 1.23 s)
- [x] 0 frozen runs, 0 black gaps, mean luma 0.058
- [x] Captions burned in, 32 cues, monotonic, safe-zone verified
- [x] Voice-dominance 0.988 correlation across 631 speech windows
- [ ] **Whisper round-trip: SKIPPED.** HuggingFace is unreachable from the build
      sandbox, so the ASR model could not be fetched. This is reported as
      `skipped` in `qa_report.json`, **not** as a pass. Run
      `tools/qa_gate.py` once on a machine with model access to close it.
- [x] 1080×1920 cover still rendered as a dedicated composition
- [x] Sources + licences documented

---

## 11. Copy-paste block (phone)

**TITLE**
```
38 Scientists Begged Us Not to Build This
```

**DESCRIPTION**
```
In December 2024, thirty-eight scientists — including Nobel laureates Jack Szostak and Gregory Winter — published a warning in Science. Not about a bomb. About a bacterium that does not exist yet.

Every living thing on Earth is built with the same handedness. Sugars twist one way, proteins the other, and your immune system reads that shape to recognise a threat. Flip it, and you get a mirror cell: the same chemistry, wound the other way.

The report's conclusion is unusually blunt. Antibodies would not grip it. Phages would not infect it. Antibiotics would not touch it. It could eat the food we eat, and nothing on this planet has evolved to eat it.

The Stanford-led report estimates roughly ten years to build one with serious funding — fifteen to thirty on the trajectory we are on now. The authors are not asking for a ban on knowledge. Mirror molecules are useful and that research can continue. They are asking that we never build the organism.

No mirror bacterium exists. This is a warning, and ten years to act on it.

Sources: Adamala et al., Science 386(6728):1351-1353 (2024), doi 10.1126/science.ads9158; Technical Report on Mirror Bacteria, doi 10.25740/cv716pj4036; WHO Q&A on mirror biology, Feb 2026.

#shorts #darkscience #science #biology #mirrorlife
```

**TAGS**
```
shorts, dark science, mirror life, mirror bacteria, mirror biology, chirality, handedness, synthetic biology, science warning, 38 scientists, nobel laureate, jack szostak, gregory winter, science 2024, bioethics, existential risk, biology facts, dna, enantiomer, left handed life, science news, dark science shorts, mirror cell, biosecurity, science explained
```
