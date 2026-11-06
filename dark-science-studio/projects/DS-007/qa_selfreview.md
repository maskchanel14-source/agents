# DS-007 — QA Self-Review

**Delivered:** 2026-11-07 · `renders/DS-007/final.mp4`
**Gate result:** `all_passed: True` · `degraded: True` · `skipped_checks: ['whisper']`
**Self-score: 8.7 / 10**

---

## 1. Measured results (`qa_report.json`)

| Check | Result | Threshold | Verdict |
|---|---|---|---|
| Specs | 46.72 s · 1080×1920 · 30 fps · h264 + aac · 20.34 MB | 9:16, ≤ 58 s | PASS |
| Freeze / black | 0 frozen runs · 0 black frames | 0 / 0 | PASS |
| Cut density | 47 detected cuts (authored 27) · mean shot 1.67 s | ≥ 1 cut / 3 s | PASS |
| Loudness | -14.0 LUFS · -1.5 dBTP | −14 ±1 / ≤ −1 dBTP | PASS |
| Captions | 34 cues · monotonic True · max gap 0.208 s · last end 46.093 s | monotonic, gap ≤ 0.4 s | PASS |
| Luminance | mean 0.0537 (0.0361–0.1187) | 0.03–0.20 | PASS |
| Whisper ASR | **SKIPPED** — faster-whisper weights unreachable (huggingface.co blocked) | ≥ 0.97 word match | not verified |

---

## 2. What I judged by eye (contact sheet at 12 fps)

- Frame 1 is the amoeba already on the olfactory nerve, halfway to the brain, before a single word is spoken.
- The `nerve_invasion` scene animates the actual route — nasal cavity, cribriform plate, nerve bundle, bulb — so the anatomy is the story, not decoration.
- Counters land 167 → 4 and 0 → 97 %, which is the whole episode in two beats.
- Loop: "it begins as a headache" cuts back to the organism entering the nose.

## 3. What is not perfect

- Every number follows CDC wording, which means the episode under-claims on purpose: "above ninety seven percent" rather than a clean 99 %, and "one hundred sixty seven cases" rather than "about 200".
- The 2016 survivor is named only by age and state in the narration; the pinned comment names him, because the case is public and widely reported.
- The organisms are drawn as comma-shaped trophozoites at a scale that would be enormous next to a real 10–25 µm cell. Illustrative, not to scale — no on-screen claim says otherwise.
- Whisper transcription check skipped (weights unreachable).

## 4. Score breakdown

| Axis | Score | Why |
|---|---|---|
| Hook | 9 | Highest-stakes first line in the series so far, and the image supports it immediately. |
| Accuracy | 9 | CDC + NCBI Bookshelf only; the temptation to say 99 % or 'flesh-eating' was refused. |
| Visual craft | 8 | The nerve scene carries the episode; the two `mirror_colony` beats are less specific to this topic than the rest. |
| Sound | 8 | On target, functional score. |
| Retention design | 9 | Survivor reveal at 36 s gives the video a second act instead of a single doom beat. |
| Packaging | 9 | Cover: "IT EATS YOUR BRAIN IN 5 DAYS" + 4/167 badge. Aggressive without inventing a single fact. |

**Total 8.7 / 10.** Publishable as-is; the gaps above are disclosed in the publishing kit and the pinned comment rather than hidden.
