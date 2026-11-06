# DS-003 — Thumbnail / cover pack (clickbait pass)

**Replaces:** `cover_frame.png` (a clean frame pulled from the video, now kept only as the
"no-clickbait" control).

Why the old one underperformed: it was typographically beautiful and emotionally empty.
Centred "MIRROR LIFE", a thin tech rule, a lot of empty black — nothing for the eye to
land on, no promise, no tension, and it gave away nothing to be curious about. It looked
like a title slide, not a thumbnail.

This pack is built for a **cold feed at 270 px wide**. Every rule below exists because of
that size.

## The rules this pack follows

| Rule | Why |
|---|---|
| One idea, three words max on the loud line | At 270 px you get ~3 saccades. Anything longer is unreadable. |
| Text in the top 55% | The bottom strip collides with the duration badge + title overlay on Shorts. |
| A face, if used, on the right third, looking *into* the frame | The human eye locks onto eyes; gaze direction pulls the viewer across the type. |
| Red is used for ONE thing only | If everything shouts, nothing shouts. |
| Sticker + arrow at most once | Two annotations read as a diagram; one reads as a reaction. |
| 8–12 px black outline on all type | Guarantees contrast over any part of the art. |
| Nothing important in the outer 60 px | Safe area on mobile crops. |
| Claim must be delivered by the video | Every line on these covers is literally in DS-003. No invented stakes. |

## The three variants

### A — `cover-A-kaget.png` · the shock-face version
`THEY WARNED US / NOT TO BUILD / **THIS**` + rim-lit face + `IT DOESN'T EXIST. YET.` + `38 SCIENTISTS`

The most clickable of the three and the riskiest: face + red + rhetorical bait is the
classic formula. It works because the shout is *true* — 38 scientists did publish a
warning asking that this not be built — and because the sticker answers the question the
headline raises, so the viewer isn't left feeling tricked.

### B — `cover-B-angka.png` · the number version
`38 SCIENTISTS BEGGED US / DON'T BUILD / **THIS**`, with a ghosted 38 filling the frame.

The number is the art, so the cover reads at a glance even with the sound off and the
type blurred. Safest of the three with YouTube's "misleading metadata" reviewer, because
"38 scientists" is a checkable fact and it's the first thing you see.

### C — `cover-C-hitam.png` · the ominous one
`NOTHING ON **EARTH CAN STOP IT**`

Highest tension, lowest information. Best for a re-upload or a re-test once the first
cover has already taught the algorithm who the audience is. Worst cold-open click-through,
because nothing anchors it to a topic.

**Recommendation:** ship **A** first. If CTR is under ~4 % after 48 h, swap to **B** —
same video, new cover, and YouTube re-tests distribution on the new asset.

## What is and isn't real on these covers

- The microscopic art (`cover-art-bg.png`) and the face (`reaction-face.png`) are
  **AI-generated illustrations**, and both covers say `AI ILLUSTRATION` in the bottom
  rule. The face is a model, not a person from the story — never present it as one.
- The bacterium is a *proposed* organism. Nothing in this cover implies one exists;
  `IT DOESN'T EXIST. YET.` is the truth and it is on the cover on purpose.
- No fake arrows to nothing, no circled empty space, no "GONE WRONG", no invented
  authority, no death/imminent-disaster framing. Those are the things that get a channel
  struck rather than promoted, and they'd also be lies about a paper that is a *warning*,
  not an incident.

## Rebuilding / re-wording

```bash
python3 cover_build.py --art cover-art-bg.png --out .
```

`cover_build.py` draws every element from primitives, so headline, sticker text, colours
and positions are one-line edits. The `-small.png` files are 270×480 readability checks —
look at those, not the 1080×1920, before you ship a change.

Fonts are Anton (shout), JetBrains Mono (telemetry), both SIL OFL 1.1.
