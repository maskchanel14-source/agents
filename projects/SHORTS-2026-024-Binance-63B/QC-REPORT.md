# QC REPORT — SHORTS-2026-024B "The Twenty-Minute Heist" — REVISION 3

Rendered 2026-11-05 · branch `arena/ce22919c-agents` · PR #22
Composition `SHORTS-2026-024-Binance63B` · 2055 frames @ 30 fps

## 1. Master

| Item | Measured |
| --- | --- |
| Duration | 68.50 s (2055 frames) |
| Resolution | 1080 × 1920, SAR 1:1, 30 fps |
| Video | H.264 High, yuvj420p, 3107 kb/s, CRF 18 |
| Audio | AAC-LC, 44.1 kHz, mono, 192 kb/s |
| Container size | 27.6 MB |
| Silent picture master | `out/video-silent-rev3.mp4`, 26.6 MB |

## 2. Audio

| Item | Measured | Target |
| --- | --- | --- |
| Integrated loudness | **−14.46 LUFS** | −14 LUFS |
| True peak | −1.42 dBFS | ≤ −1.5 dBFS |
| Loudness range | 2.20 LU | — |
| VO pace | atempo 1.06 | teacher pace |
| Music ducking | −6 dB under voice, 50 ms attack / 250 ms release | −6 dB |
| SFX | 5 (riser, coin pour, freeze, glitch, sub boom) at −12 dBFS peak | — |

VO ends at 67.27 s; the bed runs 1.23 s past it for the end card.

## 3. Exposure per beat

Measured on the delivered stills with `scripts/ascii_frame.py` (mean luma,
95th percentile, and the share of pixels below 0.06 luma).

| Beat | Frame | mean | p95 | crushed <0.06 |
| --- | --- | --- | --- | --- |
| 01 hook — host + open vault | 60 | 0.159 | 0.444 | 3.8 % |
| 02 the exchange | 220 | 0.176 | 0.511 | 1.7 % |
| 03 hot wallet — host explains | 380 | 0.275 | 0.861 | 3.1 % |
| 04 29 Oct, 20:05, ten chains | 600 | 0.169 | 0.523 | 3.8 % |
| 05 18,270 BTC | 740 | 0.163 | 0.570 | 3.9 % |
| 06 $3B frozen / $2.4B gone | 890 | 0.215 | 0.723 | 1.0 % |
| 07 "how did they get in?" — host | 1040 | 0.186 | 0.497 | 1.2 % |
| 08 the fake interview | 1220 | 0.162 | 0.469 | 4.6 % |
| 09 one laptop — host | 1400 | 0.152 | 0.393 | 2.0 % |
| 10 every dollar repaid | 1520 | 0.237 | 0.847 | 2.1 % |
| 11 attribution | 1700 | 0.192 | 0.788 | 7.4 % |
| 12 the record (bar chart) | 1890 | 0.133 | 0.318 | 4.1 % |
| 13 close — host | 1990 | 0.149 | 0.407 | 2.9 % |

Nothing crushes to black and nothing blows out. The film sits at a mean of
0.13–0.28 on purpose: the backdrop is a designed deep navy (floor #131E33), and
the brightness is carried by the type, the numbers and the host.
An earlier pass used a near-black backdrop and 36–51 % of every frame fell below
0.06 luma; the floor was lifted and the vignette softened before the final
render.

## 4. Host verification

- On screen in 5 windows: 12–170 (hook, full), 292–468 (hot wallet, present),
  966–1132 (the question, full), 1292–1466 (one laptop, present),
  1912–2055 (close, full).
- Mouth is driven by `audio/mouth.json`, a per-frame RMS curve of the actual VO
  (2055 values, 0–100), so he moves with the words rather than on a loop.
- Eyes blink on a deterministic 3.8 s double-blink cycle; the torso breathes at
  0.8 Hz; the right arm takes `point` on the hot-wallet beat and `open` on the
  question and "one laptop" beats.
- The card shrinks from 660 px to 520 px and the caption lifts whenever the host
  is full-frame, so his head never collides with the type.

## 5. Script and fact check

- 170 words, 10 VO lines, every line 10–27 words. Teacher register: the
  analogy lands before the jargon ("a bank for digital money" before
  *exchange*, "a small pile online" before *hot wallet*).
- Every line maps to a fact id in `facts.json`; the mapping is in
  `script-rev3.txt`.
- **One claim was dropped.** Revisions 1 and 2 said "the world's largest crypto
  exchange". No source sentence in `facts.json` states that, so the line is now
  "Binance is a crypto exchange".
- No number was invented for the visuals: the chain chips name only the four
  chains the sources name (ETH, BTC, TRON, SOL) and label the other six
  generically.

## 6. Known open items

1. **Two beats are hand-drawn vector scenes, not generated illustrations** —
   the attribution dossier (frame 1652) and the record bar chart (frame 1772).
   Image generation hit its per-turn limit at 10. Both are animated, so they
   read as designed rather than as a missing asset.
2. **The host is energy-driven, not phoneme-driven.** He opens and closes on the
   real voice envelope, which reads correctly at short-form scale but is not
   true viseme lip sync.
3. **The illustrations are AI-generated** from a fixed style prompt. They are
   consistent in palette, but a viewer may spot the usual generative artefacts
   on close inspection. They can be swapped one-for-one in
   `media-production/public/shorts024/scenes/` without touching the code.
4. **Revision 2 is still renderable** as `SHORTS-2026-024-Binance63B-3D-rev2`
   if the semi-realist 3D look is ever wanted again.
