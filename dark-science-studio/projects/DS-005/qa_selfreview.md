# DS-005 — QA Self-Review

**Delivered:** 2026-11-07 · `renders/DS-005/final.mp4`
**Gate result:** `all_passed: True` · `degraded: True` · `skipped_checks: ['whisper']`
**Self-score: 8.8 / 10**

---

## 1. Measured results (`qa_report.json`)

| Check | Result | Threshold | Verdict |
|---|---|---|---|
| Specs | 48.47 s · 1080×1920 · 30 fps · h264 + aac · 38.57 MB | 9:16, ≤ 58 s | PASS |
| Freeze / black | 0 frozen runs · 0 black frames | 0 / 0 | PASS |
| Cut density | 52 detected cuts (authored 28) · mean shot 1.67 s | ≥ 1 cut / 3 s | PASS |
| Loudness | -14.0 LUFS · -1.4 dBTP | −14 ±1 / ≤ −1 dBTP | PASS |
| Captions | 38 cues · monotonic True · max gap 0.0 s · last end 48.125 s | monotonic, gap ≤ 0.4 s | PASS |
| Luminance | mean 0.0613 (0.0384–0.1324) | 0.03–0.20 | PASS |
| Whisper ASR | **SKIPPED** — faster-whisper weights unreachable (huggingface.co blocked) | ≥ 0.97 word match | not verified |

---

## 2. What I judged by eye (contact sheet at 12 fps)

- Frame 1 opens on the star with its companion already mid-orbit — the most striking moving image in the episode, no title card first.
- The `star_wake` disc visibly deforms as the companion crosses maximum separation, which is exactly what the VLA/ALMA ellipticity measurement shows. The visual argument matches the narration.
- The counter slams from 12 → 700 R☉ and 300 → 2,100 D with real numeral roll, so the biggest numbers are the only thing moving in those beats.
- Contact sheet reads as one film: orange photosphere, cyan HUD, identical type stack, no shot that looks like a different channel.

## 3. What is not perfect

- The companion is drawn oversized relative to a true 2 R☉ / ~1 R★ mass-ratio pair so it survives a 1080-wide frame. Disclosed on screen as `SEPARATION ≈ 2 R☉`, which is the real figure, but the dot itself is illustrative.
- The 2,100-day cycle is a 2024 *proposed* period. The narration says "if the model holds"; the counter slider cannot carry that nuance, so the pinned comment repeats it.
- No real telescope imagery in the episode: the VLA/ALMA radio maps are not public-domain, and a real map would have been the honest anchor. Everything is animation, disclosed in the kit.
- Whisper transcription check was skipped (weights unreachable), so caption accuracy is authored-timing only, not ASR-verified.

## 4. Score breakdown

| Axis | Score | Why |
|---|---|---|
| Hook | 9 | Opens inside the story (a star with a passenger), not on a title or a logo. |
| Accuracy | 9 | Every number is traceable; the two soft claims (2,100-day period, companion size in frame) are hedged in narration and disclosed here. |
| Visual craft | 9 | Continuous 3D motion, a new image every 1.67 s on average, zero still frames. |
| Sound | 8 | −14.0 LUFS / −1.49 dBTP, voice dominates, but the score is synthesized from a GM soundfont and is functional rather than memorable. |
| Retention design | 9 | Number slams at 7.9, 21.6, 31.0 and 39.0 s; the loop returns to the opening frame. |
| Packaging | 9 | Cover is a four-line shout with a ringed companion and a 2,100 badge; titles are curiosity-gap, not spoilers. |

**Total 8.8 / 10.** Publishable as-is; the gaps above are disclosed in the publishing kit and the pinned comment rather than hidden.
