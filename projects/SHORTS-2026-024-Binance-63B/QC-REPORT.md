# QC REPORT — SHORTS-2026-024B "The Twenty-Minute Heist" — REVISION 3

Rendered 2026-11-05 · branch `arena/ce22919c-agents` · PR #22
Composition `SHORTS-2026-024-Binance63B` · 2145 frames @ 30 fps
Re-rendered 2026-11-05 with the redrawn host (`src/host.tsx`) and a re-cut VO

## 1. Master

| Item | Measured |
| --- | --- |
| Duration | 71.50 s (2145 frames) |
| Resolution | 1080 × 1920, SAR 1:1, 30 fps |
| Video | H.264 High, yuvj420p, 3401 kb/s, CRF 18 |
| Audio | AAC-LC, 44.1 kHz, mono, 203 kb/s |
| Container size | 32.3 MB |
| Silent picture master | `out/video-silent-rev3.mp4`, 30.4 MB |

## 2. Audio

| Item | Measured | Target |
| --- | --- | --- |
| Integrated loudness | **−14.7 LUFS** | −14 LUFS (±1) |
| True peak | −1.8 dBFS | ≤ −1.5 dBFS |
| Loudness range | 2.1 LU | — |
| VO pace | atempo 1.06 | teacher pace |
| Music ducking | −6 dB under voice, 50 ms attack / 250 ms release | −6 dB |
| SFX | 5 (riser, coin pour, freeze, glitch, sub boom) at −12 dBFS peak | — |

VO ends at 70.14 s; the bed runs 1.36 s past it for the end card.
Measured on the delivered master, not only on the mix WAV (see §2).

## 3. Exposure per beat

Measured on the delivered stills with `scripts/ascii_frame.py` (mean luma,
95th percentile, and the share of pixels below 0.06 luma).

| Beat | Frame | mean | p95 | crushed <0.06 | clipped >0.985 |
| --- | --- | --- | --- | --- | --- |
| 01 hook — host + open vault | 90 | 0.178 | 0.703 | 2.2 % | 0.43 % |
| 02 the exchange | 250 | 0.185 | 0.685 | 3.6 % | 0.00 % |
| 03 hot wallet — host explains | 420 | 0.259 | 0.925 | 0.9 % | 1.37 % |
| 04 29 Oct, 20:05, ten chains | 560 | 0.168 | 0.714 | 7.0 % | 1.08 % |
| 05 18,270 BTC | 780 | 0.179 | 0.839 | 7.3 % | 0.30 % |
| 06 $3B frozen / $2.4B gone | 940 | 0.240 | 0.815 | 0.4 % | 0.28 % |
| 07 "how did they get in?" — sealed vault | 1090 | 0.140 | 0.342 | 5.5 % | 0.00 % |
| 08 the fake interview | 1250 | 0.213 | 0.929 | 2.4 % | 1.80 % |
| 09 one laptop — host | 1440 | 0.164 | 0.531 | 4.9 % | 0.02 % |
| 10 every dollar repaid | 1620 | 0.258 | 0.957 | 0.3 % | 2.88 % |
| 11 attribution — dossier | 1790 | 0.192 | 0.805 | 9.5 % | 0.00 % |
| 12 the record (bar chart) | 1910 | 0.137 | 0.429 | 4.3 % | 0.00 % |
| 13 close — host | 2070 | 0.153 | 0.571 | 3.4 % | 0.00 % |

Nothing crushes to black and nothing blows out. The film sits at a mean of
0.14–0.26 on purpose: the backdrop is a designed deep navy (floor #131E33), and
the brightness is carried by the type, the numbers and the host.
An earlier pass used a near-black backdrop and 36–51 % of every frame fell below
0.06 luma; the floor was lifted and the vignette softened before the final
render.

## 4. Host verification

The host was redrawn on 2026-11-05 after the first vector was rejected
("jelek banget"). `src/host.tsx` was rewritten from the skull out. What the new
drawing fixes, verified by rendering the character alone against a flat card and
reading the pixels back:

| Was wrong | Now |
| --- | --- |
| A band of background showed between chin and collar — the head floated | shoulders raised to y 382, neck fill runs to y 442 under the collar: the silhouette is continuous head → neck → torso |
| Jacket gaped open below the lapels, showing a cream triangle of knit | jacket front closes under the lapels; the sweater is confined to the V |
| The gesturing arm was the same navy as the torso and disappeared | its own lighter sleeve gradient + 3 px ink outline + a cast shadow on the chest |
| Hair was a helmet | swept fringe, side parting, hairline strands, sideburns, highlight |
| Eyes were almonds with a dot | sclera + iris + pupil + catchlight |
| Mouth was a dark hole when open | lips + opening + teeth + tongue, opens to 22 px |
| Hands were mittens | four fingers + thumb, three poses |

- On screen in 5 windows: 12–172 (hook, full), 316–485 (hot wallet, present),
  1032–1200 (the question, full), 1358–1536 (one laptop, present),
  1985–2145 (close, full).
- Mouth is driven by `audio/mouth.json`, a per-frame RMS curve of the actual VO
  (2145 values, 0–100), so he moves with the words rather than on a loop.
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

1. **Three beats are hand-drawn vector scenes, not generated illustrations** —
   the sealed vault (frame 1034), the attribution dossier (frame 1732) and the
   record bar chart (frame 1850). The sealed vault is vector on purpose: it is
   the same object as the hook, shut instead of gaping, and drawing it keeps
   that echo exact. The other two were vector because image generation hit its
   per-turn limit at 10. All three are animated, so they read as designed
   rather than as a missing asset.
2. **The host is energy-driven, not phoneme-driven.** He opens and closes on the
   real voice envelope, which reads correctly at short-form scale but is not
   true viseme lip sync.
3. **The illustrations are AI-generated** from a fixed style prompt. They are
   consistent in palette, but a viewer may spot the usual generative artefacts
   on close inspection. They can be swapped one-for-one in
   `media-production/public/shorts024/scenes/` without touching the code.
4. **Revision 2 is still renderable** as `SHORTS-2026-024-Binance63B-3D-rev2`
   if the semi-realist 3D look is ever wanted again.
