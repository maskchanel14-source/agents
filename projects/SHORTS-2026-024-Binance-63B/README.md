# SHORTS-2026-024 — "The Twenty-Minute Heist" (Binance, 29 Oct 2026)

A 67.000 s / 2010 frame / 1080×1920 / 30 fps vertical short: 2D characters in a
painted low-poly 3D town, ink outlines that boil, one continuous gliding camera
with no cuts, depth-of-field, and a 100 BPM march score under the narration.

Built with **Remotion + three.js** (no AI video generator anywhere in the
pipeline).

---

## What the short says

| Beat | Frames | Line |
| --- | --- | --- |
| Hook | 0–200 | "In twenty minutes, $6.3 billion walked out of Binance." |
| Setup | 200–455 | 29 Oct 2026, 20:05 UTC — the largest exchange started draining |
| Escalation | 455–705 | money left hot wallets on ten blockchains at once |
| Escalation | 705–910 | 18,270 BTC went too, and nobody can freeze Bitcoin |
| Escalation | 910–1060 | Tether + Circle froze $3B; the bleeding slowed |
| Twist | 1060–1400 | the door wasn't a broken vault — it was a fake job interview |
| Twist | 1400–1530 | from that one laptop, the attacker took the whole system |
| Payoff | 1530–1685 | Binance paid every dollar back |
| Payoff | 1685–2010 | FBI → TraderTraitor; largest crypto theft in history |

## Files

```
projects/SHORTS-2026-024-Binance-63B/
├── facts.json              every claim + the exact source sentence + URL
├── script.txt              the locked 138-word English VO
├── script_id.txt           Bahasa Indonesia alternate (not used for the VO)
├── STYLE_BIBLE.md          the measured style spec + documented deviations
├── audio/                  voice clips, music.wav, sfx.wav, vo.wav, mix.wav,
│                           final.wav, timing.json
├── stills/                 one still per shot
├── references/
│   ├── frames/README.md    how to capture the reference channel frames
│   └── reports/            the 7 QA agent reports
└── out/
    ├── video-silent.mp4    Remotion render, no audio
    └── final.mp4           final delivery: video + mixed audio
```

Source lives in the studio:

```
media-production/
├── src/theme.ts                    palette + every style-bible constant
├── src/story.ts                    9 shots → VO clip / camera / action / overlay
├── src/camera.ts                   Catmull-Rom glide, no cuts
├── src/world.ts                    painted town, vault, 10 bridges, coins
├── src/characters.tsx              2D plane characters, ink-boiling shader
├── src/lens.tsx                    custom depth-of-field pass
├── src/compositions/Binance63B.tsx the composition
├── scripts/shorts024_audio.py      timeline + 100 BPM score + SFX + ducking
├── scripts/analyze_frame.py        objective frame QA
├── scripts/still.mjs               `node scripts/still.mjs --out … --shot 3`
└── scripts/render-shorts024.sh     sandbox render entry point
```

## Render

### On your own PC (the intended path, full quality)

```bash
cd media-production
npm install
npm run studio                     # preview at http://localhost:3000
npx remotion render src/index.ts SHORTS-2026-024-Binance63B \
    ../projects/SHORTS-2026-024-Binance-63B/out/video-silent.mp4 \
    --codec=h264 --crf=18
```

`public/` is ~1.3 GB in the reference workflow, so point Remotion's temp dir at
a big drive:

```powershell
$env:REMOTION_TMP = "D:\bigdrive\temp"
```

```bash
export REMOTION_TMP=/mnt/bigdrive/temp
```

### In this sandbox (no Chrome, no ffmpeg, npm+PyPI+GitHub only)

`scripts/render-shorts024.sh` unpacks the npm-shipped Chromium
(`@sparticuz/chromium`) and uses the npm-shipped ffmpeg, then renders with
`--gl=swangle`. Expect ~1.2 s/frame → about an hour for 2010 frames.

## Audio

```bash
cd media-production
python3 scripts/shorts024_audio.py
```

It measures the 10 VO clips, time-stretches them by `atempo 1.07`, lays them out
against a 67 s timeline, synthesises the 100 BPM march and the 5 SFX, ducks the
music −6 dB under the voice (50 ms attack / 250 ms release) and loudnorms the
result to −14 LUFS. Output: `audio/final.wav`.

## Fact-checking

`facts.json` holds 14 facts. Each carries the verbatim sentence it came from and
the URL. On-screen numbers are listed separately under `numbers_used_on_screen`
with the fact they trace back to. Sources: TRM Labs, Chainalysis, AP, Reuters via
NBC News, Al Jazeera, CNN, CNET/CNET-cited, NYT, Mashable, Incrypted.
