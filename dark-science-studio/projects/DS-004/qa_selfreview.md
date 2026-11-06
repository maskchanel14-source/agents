# DS-004 — QA Self-Review

**Delivered:** 2026-11-06 · `renders/DS-004/final.mp4`
**Gate result:** `all_passed: true` · `degraded: true` · `skipped_checks: ["whisper"]`
**Self-score: 8.7 / 10**

---

## 1. Measured results (from `projects/DS-004/qa_report.json`)

| Check | Result | Threshold | Verdict |
|---|---|---|---|
| Specs | 49.60 s · 1080×1920 · 30 fps · h264 + aac · 19.64 MB | 9:16, ≥ 30 fps, < 60 s | PASS |
| Freeze / black | 0 frozen runs, 0 black frames | 0 | PASS |
| Scene changes | 68 detected cuts (31 authored) | ≥ 16 in 49.6 s | PASS |
| Loudness | −14.0 LUFS · −1.0 dBTP | ±1 LUFS of −14, TP ≤ −1 | PASS |
| Whisper ASR | **SKIP** — model unreachable (TLS/Hub blocked) | ≥ 0.96 word match | **not verified** |
| Voice dominance | correlation 0.985 across 699 speech windows | ≥ 0.80 | PASS |
| Captions | 36 cues, monotonic, max gap 0.208 s, last end 48.51 s | monotonic, no gap > 0.4 s | PASS |
| Luminance | mean 0.0641 (0.0453–0.1516) | 0.03–0.20 | PASS |
| Timeline | 32 shots, mean 1.55 s, min 0.83 s | mean ≤ 4.0 s | PASS |

---

## 2. What changed from DS-003

DS-003 shipped at 35 detected cuts and a 2.1 s mean shot. DS-004 cuts much
harder: **32 shots, 1.55 s mean, 0.83 s minimum**, 68 detected changes. The
faster rhythm suits a body-horror beat better than the cosmic-dread pacing of
DS-003, but it is the single biggest risk in this cut — see §4.

Two engine changes landed here:

1. **Per-video accent colour.** `theme` is now a runtime value set from
   `props.meta.accent` (`setAccent()` in `brand/theme.ts`). DS-004 uses iris
   violet `#B36BFF`; the HUD panels, rules, glows and the `Soft3D` default all
   follow it. Previously the cyan was hardcoded in six places.
2. **Four new scenes** built for this story: `misfold_chain` (beta-stack fibre
   that converts residue by residue), `thalamus_grid` (two nuclei + four
   polysomnography lanes), `pedigree` (three generations with descent buses and
   a 50/50 split bar), `mortality` (locked 100 % dial).

---

## 3. Ten fixes made during this build

1. `CounterSlam` first landed on **"6 → 1 CM"** for the walnut — an invented
   statistic. Replaced with a `WALNUT` shout over the true sub-fact
   (`ABOUT SIXTY GRAMS`).
2. Script originally said "one family in **Bologna**." The literature says an
   Italian gentleman (1765) and a Venetian kindred (1986), not Bologna, and the
   link between them is not documented. Rewritten to "one **Italian** family,"
   kicker changed to `1765 · ITALY`, and the caveat disclosed in
   `sources_and_licenses.md` and the pinned comment.
3. `GlitchReveal` used to shift the shout block up **54 px** whenever a `sub`
   line existed. That put the sub *inside* the type and read as a ghosted
   double image (visible in DS-003 too). Now the whole caption band is reserved
   via `paddingBottom`, and multi-line blocks drop to 118 px so they fit.
4. First `misfold_chain` pass drew two thin wavy ribbons that read as scribbles.
   Rebuilt as a pack fibre: 15 residues, 16-point loops, four side chains each,
   a brighter backbone, and a tightening radius once converted.
5. HUD labels overflowed their 380 px panel (`CONFORMATION` + `MISFOLDED
   (PrP-Sc)` collided with `SEEDING`). Labels shortened and the native-state
   rows were given honest values (they previously read `DISINFECTION:
   INEFFECTIVE` even for a healthy protein).
6. `pedigree` first drew naive sibling-to-child lines that crossed into a
   genetically **wrong** X. Rebuilt with proper descent buses (carrier →
   midpoint bus → fan of children) and fixed carrier indices per generation.
7. `thalamus_grid` first placed the lobe mesh on top of the four trace lanes.
   Added a `yOffset` to `project()`/`drawSegs()` so the anatomy lifts 205 px
   into the clear zone instead of being clipped or fought over.
8. `freeze_black` initially **FAILED** with 4 frozen runs at 2.0 s, 35.4 s,
   36.1 s and 39.2 s — the pedigree holds sat perfectly still between
   generation reveals. Fixed by giving every node a breathe transform, the
   rails a pulse, and the tree a travelling scan band.
9. `mortality` showed **87 %** mid-climb at the moment the caption says "zero
   survivors" — a fatality dial that is still counting up reads as a data
   error. The dial is now locked at 100 % from frame one, with only a slow
   breathing pulse.
10. `handed_helix` with `split:false` drew **both** enantiomers at separation 0,
    producing unreadable spaghetti. Single-molecule shots now draw one helix;
    the L/D labels and the Δ-pitch panel only appear in split mode.

---

## 4. Known limitations (be honest)

- **Whisper is not verified.** The gate skipped it because the model cannot be
  fetched in this sandbox. Captions are derived from Piper's own word timings,
  which is usually accurate, but nothing in this report proves the delivered
  transcript matches the delivered audio. Treat "36 cues, monotonic" as a
  *timing* result, not a *transcript* result.
- **1.55 s mean shot is aggressive.** If retention drops in the first 3 s,
  stretch the two `glitch_reveal` shots at 12.5 s and 17.6 s before touching
  the misfold scenes — those carry the argument.
- **No WebGL.** All 3D is Canvas2D perspective projection (`Soft3D`). The fibre
  is convincing at Short scale but has no real lighting or occlusion.
- **The prion structure is a schematic.** No experimental PrP^Sc structure
  exists. The film labels the fibre as a schematic; do not let a thumbnail cut
  imply it is a model.
- **The 1765 → 1986 link is traditional, not documented.** Disclosed in two
  places; keep it that way if the script is ever re-cut.
- **Piper, not Kokoro.** DS-001/DS-002 used Kokoro; DS-003 and DS-004 use Piper
  `lessac`. The voice has changed mid-channel — audibly. Either accept the
  drift or re-voice DS-004 to match, but do not pretend it is the same narrator.
- **`degraded: true`** is correct and should stay until Whisper runs for real.

---

## 5. Scores

| Dimension | Score | Note |
|---|---|---|
| Factual discipline | 9.5 | Every number sourced; two claims rewritten for accuracy; two caveats disclosed. |
| Publishing readiness | 9.5 | Kit, cover, captions, disclosure, checklist all present. |
| Visual design | 7.8 | New scenes are the best in the channel, but Canvas2D caps the ceiling and two shots (17.6 s, 32.9 s) are still just type on a gradient. |
| Audio | 9.0 | −14.0 LUFS / −1.0 dBTP, voice dominance 0.985, score ducks under narration. |
| **Overall** | **8.7** | Best-researched episode so far; held back from 9.0 by unverified transcript and thin visual coverage on two beats. |
