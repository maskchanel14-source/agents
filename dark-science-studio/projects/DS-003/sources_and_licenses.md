# DS-003 — Sources & Licences

Claim-by-claim verification for *"38 Scientists Begged Us Not to Build This"*.

**Verification date:** 2026-11-06
**Primary source:** Adamala et al., *Confronting risks of mirror life*,
*Science* 386(6728):1351–1353, published online 12 Dec 2024, in print 20 Dec 2024.
doi:10.1126/science.ads9158

---

## 1. Claim verification

| # | Claim as spoken | Verdict | Evidence |
|---|---|---|---|
| 1 | "In December 2024, thirty-eight scientists published a warning." | ✅ Exact | *Science* 386(6728), 12 Dec 2024; 38 named authors (PubMed 39666824). |
| 2 | The signatories include Nobel laureates. | ✅ Exact | Jack Szostak (2009, Physiology/Medicine) and Gregory Winter (2018, Chemistry) are both on the author list. The video does not name them on screen; the description does. |
| 3 | "Not about a bomb." | ✅ Editorial framing | A contrast device, not a factual claim. The paper is about a biological agent, not a weapon. |
| 4 | "Every living thing on Earth is built with the same handedness." | ✅ Standard biology | All known life uses L-amino acids and D-sugars — homochirality. |
| 5 | "Sugars twist right. Proteins twist left." | ⚠️ Simplified | D-sugars are *dextro*rotatory in the naming convention and L-amino acids *levo*; the words "twist right/left" describe the naming convention, not literal optical rotation of every molecule. Disclosed simplification #1. |
| 6 | "Your immune system reads that shape." | ✅ Accurate | Innate recognition depends on pathogen-associated molecular patterns, which are stereospecific. |
| 7 | "Your antibodies would not grip it." | ✅ Report finding | Impaired PAMP/PRR recognition and antibody binding are explicit in the technical report's immune-evasion section. Conditional tense is correct — no such organism exists. |
| 8 | "Phages would not infect it." | ✅ Report finding | Phage adsorption depends on chiral surface structures; the report notes mirror cells would be refractory. |
| 9 | "Antibiotics would not touch it." | ⚠️ Compressed | Three separate mechanisms are folded into one line: absent targets, altered membrane permeability, and no phage-based alternatives. Disclosed simplification #2. |
| 10 | "It could eat the food you eat." | ✅ Report finding | Mirror bacteria could metabolise the same achiral nutrients (glucose, etc.) while their own chiral biomass would be indigestible to existing life. |
| 11 | "Nothing on this planet could eat it." | ✅ Report finding | No known predator, parasite or decomposer has machinery for D-chiral biomass. Conditional ("could") is preserved. |
| 12 | "The report says ten years, with serious funding." | ✅ Report finding | The Stanford technical report gives ~10 years under concerted funding. Disclosed simplification #3 — this is the *optimistic* scenario, not the default. |
| 13 | "Fifteen to thirty on the path we are on now." | ✅ Report finding | The 15–30 year window is the report's current-trajectory estimate. The WHO Q&A (5 Feb 2026) independently says capacity is "at least a decade" away. |
| 14 | "They are not asking for a ban on knowledge." | ✅ Accurate | The paper and the accompanying *Bulletin of the Atomic Scientists* piece (13 Dec 2024) explicitly permit continued work on mirror *molecules*; the ask is that mirror *organisms* not be created. |
| 15 | "They are asking us to never build it." | ✅ Accurate | Recommendation wording: mirror bacteria "should not be created"; funders should decline to support the work. |

**No claim in the video is asserted as having happened.** Every statement about a
mirror organism is in the conditional or the future — because none exists.

---

## 2. Disclosed simplifications

1. **"Sugars twist right, proteins twist left."** — the D/L naming convention
   encodes the configuration of the chiral centre, and only loosely tracks actual
   optical rotation for any given molecule. The line is mnemonic, not a
   stereochemistry lecture, and the animation shows the *backbone* handedness,
   which is what matters for the argument.
2. **"Antibiotics would not touch it."** — one line covering target absence,
   membrane differences and the collapse of phage therapy. A viewer who knows the
   field will find it compressed; the honest long form is the report's §3.
3. **"Ten years."** — the concerted-funding estimate. It is deliberately paired in
   the very next shot with 15–30 years, so the video never presents the fast
   number alone.
4. **"Nothing on this planet could eat it."** — strictly, "no known organism has
   the machinery". Environmental decomposers are the open question the report
   flags as the main uncertainty, and the video keeps "could".

---

## 3. Sources

1. **Adamala, K. P., et al. (2024).** "Confronting risks of mirror life."
   *Science* 386(6728):1351–1353. doi:10.1126/science.ads9158.
   Online 12 Dec 2024. 38 authors. — The primary source for the warning itself
   and the signatory list.
2. **Technical Report on Mirror Bacteria: Feasibility and Risks (2024).**
   Stanford Digital Repository. doi:10.25740/cv716pj4036. — The ~300-page
   technical backing: timelines, immune evasion (PAMP/PRR, complement,
   phagocytosis, T-cell activation), environmental persistence, biocontainment
   ("removable by a moderately skilled actor with access to mirror DNA").
3. **Bulletin of the Atomic Scientists (13 Dec 2024).** "Mirror bacteria should
   not be created." — The recommendation wording and the molecule/organism
   distinction.
4. **World Health Organization Q&A on mirror biology (5 Feb 2026).** — Independent
   confirmation that capacity is "at least a decade" away, and that a window for
   pre-emption still exists.
5. **Royal Society of Biology, "Danger in the Mirror."** — The 1992 *Science*
   precedent warning and the 2025 Mirror Biology Dialogues.

---

## 4. Asset licences

| Asset | File | Origin | Licence | Commercial use |
|---|---|---|---|---|
| Narration | `build/DS-003/voice.wav` | Piper `en_US-lessac-medium` VITS, local CPU inference | Piper: MIT. lessac voice: CC BY 4.0 (Blizzard/Lessac dataset lineage) | ✅ with attribution |
| Score | `build/DS-003/score.mid` → `score.wav` | Original MIDI composed for this timeline in `tools/audio_kit.py` | Channel-owned | ✅ |
| Soundfont | `assets/TimGM6mb.sf2` | Tim Brechbill, TimGM6mb | GPL-2.0; free for commercial music use | ✅ |
| SFX | `build/DS-003/sfx.wav` | Procedurally synthesised, NumPy/SciPy | Channel-owned | ✅ |
| Visuals | `tools/studio/src/**` | Remotion 4 + Canvas2D `Soft3D` projection | Channel-owned | ✅ |
| Fonts | `node_modules/@fontsource/*` | Anton, Montserrat, Inter, JetBrains Mono | SIL OFL 1.1 | ✅ |
| Science figures | — | None reproduced | — | n/a |

**No third-party footage, no stock imagery, no generative-image model output, and
no licensed music library.** Everything on screen is drawn in code; everything in
the mix is synthesised or rendered locally.

---

## 5. Model + tool versions

| Component | Version |
|---|---|
| Remotion | 4.x (`@remotion/cli` 4.x) |
| Node.js | v22.22.3 |
| Python | 3.11.2 |
| Piper (piper-tts) | 1.8.0 |
| Voice | `lessac.onnx` — `en_US-lessac-medium`, 16 kHz |
| SpessaSynth Core | 4.x (`soundBankManager.addSoundBank`) |
| ffmpeg | imageio-ffmpeg static build 9.0.2 |
| Chromium | @sparticuz/chromium 153 (`swiftshader`, no WebGL) |
