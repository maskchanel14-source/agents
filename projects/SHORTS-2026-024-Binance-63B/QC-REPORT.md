# QC REPORT — SHORTS-2026-024B "The Twenty-Minute Heist"

Rendered 2026-11-04. Master: `01_VIDEO.mp4`.

## Master spec

| Property | Value | Verdict |
| --- | --- | --- |
| Duration | 67.000 s (2010 frames @ 30 fps) | PASS (55–70 s) |
| Resolution | 1080×1920 | PASS |
| Frame rate | 30 fps, constant | PASS |
| Video codec | H.264 High, yuv420p, 4.7 Mb/s | PASS |
| Audio | AAC-LC 44.1 kHz mono, 192 kb/s | PASS |
| Integrated loudness | −14.8 LUFS | PASS (target −14) |
| True peak | −1.4 dBFS | PASS |
| Script length | 138 words | PASS (130–150) |
| Hook | 9 words, one sentence | PASS (8–12) |

The full 7-agent breakdown is in `05_QA-REPORTS.zip`
(`motion.md`, `depth.md`, `textures.md`, `characters.md`, `lighting.md`,
`outlines.md`, `grade.md`). Each was measured with
`media-production/scripts/analyze_frame.py`, not eyeballed.

## Measured, per shot

| Shot | Mean luma | RMS contrast | Clipped high | Near-black |
| --- | --- | --- | --- | --- |
| 1 wide / hook | 0.395 | 0.328 | 0.77 % | 1.44 % |
| 2 clock tower | 0.477 | 0.340 | 1.12 % | 0.79 % |
| 3 ten chains | 0.441 | 0.267 | 0.68 % | 0.19 % |
| 4 bitcoin | 0.474 | 0.244 | 0.81 % | 0.04 % |
| 5 frozen | 0.436 | 0.295 | 0.78 % | 0.00 % |
| 6 window | **0.176** | 0.240 | 1.41 % | 0.06 % |
| 7 laptop | 0.276 | 0.244 | 0.75 % | 0.00 % |
| 8 refill | 0.358 | 0.254 | 0.71 % | 0.27 % |
| 9 final wide | 0.347 | 0.278 | 0.92 % | 0.76 % |

## Audio

| Stem | Measured | Target |
| --- | --- | --- |
| Music (100 BPM march) | RMS −18.0 dBFS | −18 dB |
| SFX (5 cues) | peak −12.0 dBFS | −12 dB |
| Ducking under VO | −6.00 dB, 88 ms attack | −6 dB, 50 ms |
| Master | −14.8 LUFS / −1.4 dBTP | −14 LUFS |

## Open items (carried into the next pass)

1. **Shot 6 is dark** — mean luma 0.176, ~40 % below every other beat. It is the
   twist (DevOps tower at night, one lit window), so it is partly intentional.
   `lighting.md` F1 has the fix.
2. **Dolly rate 2.69 u/s** vs the style bible's 0.8. The 9 beats span a ~110-unit
   town; `motion.md` F1 gives the waypoint compression that lands it at ~1.0 u/s.
3. **Characters are small** — 3–5 % of frame height in most shots, and the pop
   colour `#FF6B6B` registers at ~0 % in the wides. `characters.md` F1–F3.
4. **PHASE 0 not run.** The reference-channel frame extraction needs YouTube
   access the build sandbox does not have. `references/frames/README.md` has the
   commands; re-run the 7 agents against real channel frames when you have them.

## Fact check

14 facts in `facts.json`, each carrying the verbatim source sentence and URL.
No claim in the VO is unsourced. On-screen numbers are cross-referenced to their
fact IDs under `numbers_used_on_screen`.
