# DS-006 — QA Self-Review

**Delivered:** 2026-11-07 · `renders/DS-006/final.mp4`
**Gate result:** `all_passed: True` · `degraded: True` · `skipped_checks: ['whisper']`
**Self-score: 8.9 / 10**

---

## 1. Measured results (`qa_report.json`)

| Check | Result | Threshold | Verdict |
|---|---|---|---|
| Specs | 49.6 s · 1080×1920 · 30 fps · h264 + aac · 26.21 MB | 9:16, ≤ 58 s | PASS |
| Freeze / black | 0 frozen runs · 0 black frames | 0 / 0 | PASS |
| Cut density | 49 detected cuts (authored 28) · mean shot 1.71 s | ≥ 1 cut / 3 s | PASS |
| Loudness | -14.0 LUFS · -1.4 dBTP | −14 ±1 / ≤ −1 dBTP | PASS |
| Captions | 34 cues · monotonic True · max gap 0.208 s · last end 49.261 s | monotonic, gap ≤ 0.4 s | PASS |
| Luminance | mean 0.0642 (0.0444–0.1515) | 0.03–0.20 | PASS |
| Whisper ASR | **SKIPPED** — faster-whisper weights unreachable (huggingface.co blocked) | ≥ 0.97 word match | not verified |

---

## 2. What I judged by eye (contact sheet at 12 fps)

- Frame 1 is the muon track already slicing through a detector it is too small to see — motion, scale and mystery in one image.
- The Cherenkov cone expands *after* the interaction point, so the moment of detection is a visible event rather than a static diagram.
- 220 PeV and 30× arrive as separate number slams, so the two facts that make the story land each get their own beat.
- The loop closes on "a crack in physics" cutting straight back to the particle crossing the sea.

## 3. What is not perfect

- The detector is drawn as 8 strings of 9 modules; the real ARCA grid is 230 m × 700 m with 100 m string spacing and ~200,000 PMTs. The geometry is illustrative, the labels are real.
- The 3σ tension with IceCube is stated as a disagreement, not as proof of new physics. The narration offers "either lucky, or missing physics" — that is the honest framing.
- The energy counter starts at 7 PeV (the old record) which is a narrative device, not a measured intermediate value.
- Whisper transcription check skipped (weights unreachable).

## 4. Score breakdown

| Axis | Score | Why |
|---|---|---|
| Hook | 9 | First frame is the impossible image; first line is the impossible sentence. |
| Accuracy | 9 | Nature DOI, 90 % credible interval and the tension citation are all in the sources file; no invented physics. |
| Visual craft | 9 | New scene geometry built for this episode; additive glow, depth-sorted tubes, no borrowed clip art. |
| Sound | 8 | Clean and on target, but the score is a synthesised bed rather than a composed cue. |
| Retention design | 9 | 33 s of the run is numbers, claims and reversals; nothing sits still longer than 2.4 s. |
| Packaging | 9 | Cover: "1 PARTICLE / 220 PeV / SHOULD NOT EXIST" with a 30× badge — three hooks stacked, still readable at 320 px. |

**Total 8.9 / 10.** Publishable as-is; the gaps above are disclosed in the publishing kit and the pinned comment rather than hidden.
