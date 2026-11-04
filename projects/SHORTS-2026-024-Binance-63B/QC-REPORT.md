# QC REPORT — SHORTS-2026-024B "The Twenty-Minute Heist"

**Revision 2 (semi-realist 3D).** Rendered 2026-11-05. Master: `01_VIDEO.mp4`.
See `REVISION-2.md` for what changed from revision 1.

## Master spec

| Property | Value | Verdict |
| --- | --- | --- |
| Duration | 67.000 s (2010 frames @ 30 fps) | PASS (55–70 s) |
| Resolution | 1080×1920 | PASS |
| Frame rate | 30 fps, constant | PASS |
| Video codec | H.264 High, yuv420p, 5235 kb/s | PASS |
| Audio | AAC-LC 44.1 kHz mono, 192 kb/s | PASS |
| Script length | 138 words | PASS (130–150) |
| Hook | 9 words, one sentence | PASS (8–12) |
| Cuts | 0 — one continuous Catmull-Rom glide | PASS |

## Per-shot exposure (measured on rendered stills)

| Shot | Beat | mean luma | p95 | crushed < 0.06 | clipped |
| --- | --- | --- | --- | --- | --- |
| 1 | $6.3 BILLION | 0.315 | 0.567 | 1.9 % | 0.0 % |
| 2 | 29 OCT 2026 · 20:05 UTC | 0.422 | 0.754 | 4.6 % | 0.0 % |
| 3 | 10 BLOCKCHAINS | 0.336 | 0.664 | 1.4 % | 0.0 % |
| 4 | 18,270 BTC | 0.362 | 0.730 | 4.3 % | 0.0 % |
| 5 | $3B FROZEN | 0.271 | 0.467 | 8.4 % | 0.0 % |
| 6 | FAKE JOB INTERVIEW | 0.364 | 0.909 | 0.3 % | 0.0 % |
| 7 | ONE LAPTOP | 0.433 | 0.929 | 0.0 % | 0.0 % |
| 8 | $6.34B REFUNDED | 0.331 | 0.577 | 2.5 % | 0.0 % |
| 9 | LARGEST CRYPTO THEFT | 0.265 | 0.529 | 0.0 % | 0.0 % |

Shot 5 is deliberately the darkest — it is the freeze beat. Shots 6 and 7 carry
the brightest values because the entire frame is lit by a single window.

## Audio (unchanged from revision 1)

| Stem | Measured | Target |
| --- | --- | --- |
| Music (100 BPM march) | RMS −18.0 dBFS | −18 dB |
| SFX (5 cues) | peak −12.0 dBFS | −12 dB |
| Ducking under VO | −6.00 dB, 88 ms attack | −6 dB, 50 ms |
| Master | −14.8 LUFS / −1.4 dBTP | −14 LUFS |

## Rig verification

Checked with a throwaway full-frame composition and read back as ASCII
(`scripts/ascii_frame.py`): head, cap, torso, both upper arms, both forearms,
both thighs, both shins and both feet all project to the expected screen
positions, symmetric about the centre line, at real human proportions. The walk
and march cycles are continuous and left/right opposed; the salute raises the
character's right arm (screen left, since the figure faces camera).

## Known open items

1. **Characters are small in the wides.** They now occupy roughly 8–14 % of
   frame height in shots 1, 2 and 9 (revision 1 was 3–5 %). Making them bigger
   would mean either closer cameras or abandoning the establishing shots.
2. **The camera only sits on its waypoint at the first frame of each shot** and
   glides for the rest of it. That is the "no hard cuts" design, but it means
   each beat's hero composition exists for only an instant. Holding the framing
   for ~45 % of each shot before gliding would be the fix.
3. **Dolly rate is still above the style bible's 0.8 u/s** — the nine beats span
   a ~110-unit town and the glide is continuous.
4. **PHASE 0 (reference-channel comparison) has not been run.** It needs
   YouTube access this build sandbox does not have. `references/frames/README.md`
   has the commands.
5. **The salute lands the hand beside the head, not on the temple.** With real
   arm proportions the shoulder-to-temple distance is too short for the hand to
   reach with the elbow out; it reads as a raised-arm gesture. Only visible in
   one wide shot.

## Fact check

14 facts in `facts.json`, each carrying the verbatim source sentence and URL.
No claim in the VO is unsourced. On-screen numbers are cross-referenced to their
fact IDs under `numbers_used_on_screen`.
