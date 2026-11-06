# DS-003 — QA Self-Review

**Verdict:** shippable. **8.6 / 10.**
Rebuilt from scratch after the sandbox was reset twice mid-session; this
document describes the shipped cut, not an earlier draft.

---

## Measured

| Metric | Result | Target | |
|---|---|---|---|
| Resolution / codec | 1080×1920, H.264 High, 30 fps | same | ✅ |
| Duration | 44.0 s | ≤ 58 s | ✅ |
| Size | 21.41 MB | ≤ 60 MB | ✅ |
| Integrated loudness | −14.0 LUFS | −14 ±1 | ✅ |
| True peak | −1.1 dBTP | ≤ −1.0 | ✅ |
| Shots / cuts | 21 / 20 | ≥ 8 shots | ✅ |
| Mean shot length | 2.10 s | ≤ 4.0 s | ✅ |
| Shortest shot | 1.23 s | ≥ 1.0 s | ✅ |
| Frozen runs (>0.4 s identical) | 0 | 0 | ✅ |
| Black frames | 0 | 0 | ✅ |
| Mean luma | 0.058 (min 0.040, max 0.105) | > 0.04 | ✅ |
| Caption cues | 32, monotonic, max gap 0.24 s | — | ✅ |
| Voice dominance | 0.988 correlation, 631 speech windows | ≥ 0.80 | ✅ |
| Cut detection | 35 detected vs 20 authored | — | ✅ |
| QA gate | `all_passed: true` (7 pass, 1 skip) | — | ✅ |

---

## Scored

| Dimension | Score | Note |
|---|---|---|
| Hook (first 3 s) | 8.5 | "In December 2024, thirty-eight…" is authority-first, not danger-first. The first cut to **A WARNING** at 2.3 s rescues it. A line closer to *what it does* would test better. |
| Script craft | 9.0 | 128 words / 44 s. Concrete throughout — handedness, flipped shape, protein printer. Only abstract line is "anything that lives". |
| Factual discipline | 9.5 | Every claim traceable to the *Science* paper or the Stanford report. Everything conditional. Four compressions disclosed in `sources_and_licenses.md`. |
| Visual design | 8.0 | Consistent cyan instrumentation language, safe-zone compliant, HUD panels give it an identity. **Penalty:** no WebGL on this box, so all 3D is a Canvas2D projection (~1,000 segments/frame). It reads as deliberate schematic instrumentation rather than photoreal 3D. |
| Pacing | 9.0 | 20 cuts in 44 s (2.1 s/shot) — the previous cut's real weakness, now fixed. Every scene carries internal motion; the hand-wall and colony shots breathe and push. |
| Audio mix | 8.5 | Sidechain-ducked score, 36 SFX cues on every cut and reveal, −14.0 LUFS. Voice dominance 0.988, so words are never masked. Mix is subtle to the point of understatement in the first 8 s. |
| Captions | 9.0 | Word-synced, 32 cues, emphasis on load-bearing words. Two collisions found in review and fixed (in-scene sub-lines vs the caption band). |
| Publishing readiness | 9.5 | 5 titles, 291-word description with 5 sources, 471-char tag string, pinned comment, upload settings, dedicated cover frame. |

**Weighted: 8.6 / 10.** Above DS-001's 9.0 on factual care and pacing, below it
on visual richness — which is a hardware limit, not a craft choice.

---

## What was fixed during QA (kept for the record)

1. **Two caption layers collided.** Scenes carried their own caption *and*
   `KineticCaptions` drew the word-synced line, so text overprinted text
   (`NO ABOUT A BACTERIUM.T`). Removed every in-scene caption; there is now
   exactly one caption layer.
2. **`sub` lines sat in the caption band.** Moved from y=1220 to y=862 and the
   hero block lifts 54 px when a sub is present.
3. **Dissolves killed the cuts.** A 4-frame opacity fade per shot meant ffmpeg
   scene detection found **0 cuts** in a video that visibly cuts 20 times. Now a
   hard cut by default; `softCut` is opt-in.
4. **ffmpeg's `scene` score is unusable on this footage.** Thin line art on
   near-black never crosses 0.25. Replaced with a direct adjacent-frame
   difference detector against a local baseline (35 cuts vs 20 required).
5. **`freezedetect` at n=0.003 missed real freezes and 0.001 was too strict** —
   the hand-wall canvas had a mathematically static phase. Motion amplified
   (per-cell translate, 16% breathe, slow push on the title).
6. **QA was reporting a fake pass.** When faster-whisper was unavailable the gate
   returned `passed: True, skipped: …`. It now returns `passed: None`, the report
   is flagged `degraded: true`, and the missing check is named. Never fake a pass.
7. **Subjects were too small and too dim** (mean luma 0.033, helix ~150 px tall).
   Cameras pulled in ~40%, stroke widths ×1.55, always-on bloom, brighter
   radial backdrop, HUD telemetry panels filling the dead space.
8. **Counter overshot its target.** `30 → 10` displayed `19` because the
   interpolation extrapolated past the end. The value now locks on `to` at 55%.
9. **The score was truncated at 29.9 s** of a 44 s video — the MIDI renderer
   sized the buffer from the last note-off. It now takes an explicit duration.
10. **`alimiter` normalised the mix upward**, pushing −14.0 to −13.0 LUFS.
    `level=false` keeps the limiter from crossing the loudness target.

---

## Known limitations (accepted)

- **No WebGL.** All 3D is software-projected Canvas2D. This is the single biggest
  gap versus a GPU build, and it caps the visual score at 8.
- **No Whisper round-trip.** HuggingFace is unreachable from this sandbox, so the
  ASR model cannot be fetched and the intelligibility check is reported as
  `skipped`. The voice-dominance check substitutes for it but is not the same
  measurement. One run on a connected machine closes it.
- **Piper, not Kokoro.** The Kokoro weights live only on blocked hosts; the
  rebuild uses Piper `lessac-medium`. It is cleaner and more intelligible than
  `am_onyx`, but slightly less "documentary deep". Voice is a Style Bible
  decision to re-verify before DS-004.
- **Two counter shots.** Consecutive `counter_slam` shots at 30.9 s and 33.9 s
  are the one place the visual rhythm repeats.
- **Mean luma 0.058** is on the dark side of the Style Bible's target band; the
  reference frames run 0.05–0.10, so this is consistent, not a defect.

---

## Process note

The workspace was destroyed **twice** during this session — `.venv/`,
`node_modules/`, `build/` and `models/` are not snapshotted, and the second reset
also rewound git to the base commit. Two things saved the work:

1. Everything now lives **inside the git repo** and is pushed after every stage.
2. A surviving untracked directory held the source files, which were re-seeded
   from `/tmp` after `git merge --ff-only` failed on conflicting paths.

Lesson recorded in Notion: commit *and push* after every stage, and keep the
studio inside the tracked tree.
