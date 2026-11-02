# QC report — render checked 3 November 2026 (Asia/Jakarta)

## Render result
- **Status:** Remotion render exited successfully (exit code 0).
- **File:** `video.mp4`
- **Runtime:** 41.00 s / 1230 frames.
- **Video:** H.264 High / yuv420p, 1080×1920, 30 fps, 2049 kb/s video stream.
- **Audio:** AAC-LC, stereo, 48 kHz, 317 kb/s audio stream.
- **File size:** approximately 12.2 MB at verification.

## Mechanical verification
- Full decode ran with FFmpeg `-v error -xerror`: **PASS** (no decode errors).
- `blackdetect` found no black intervals of ≥0.1 seconds using `pic_th=0.97`, `pix_th=0.10`.
- Representative decoded output frames were reviewed at ~0.5, 4.2, 10.3, 18.7, 28.3, 33.0, 37.0 and 40.2 seconds. They show the hook, animated mini-figure scene, DNA scene, molecular reveal, still evidence card, safety card and final mystery line without a visible error screen or cropped caption.
- Cover inspected at its native 1080×1920 and 270×480 small-screen preview: headline remains legible and the AI-illustration label is visible.

## Audio technical check
- Integrated loudness: **−19.6 LUFS**.
- Measured true peak: **−4.2 dBFS**; no clipping indicated by this measurement.
- The voice track is present to 40.36 s inside a 41.0 s render; ambient bed carries the tail.
- Background audio is coded at a lower Remotion gain (0.18) than narration (1.0); riser, shimmer and low impacts are intentionally non-percussive.
- **Listening limitation:** this environment exposes technical audio analysis but no reliable audio playback/listening tool to the agent. I verified track presence, durations, codec and loudness/peak measurements; I do not claim a human listening review.

## Editorial truth check
- 3D scenes visibly use Three.js / React Three Fiber and are labelled `3D SCIENTIFIC VISUALIZATION`.
- The real species still is labelled `SPECIES PHOTO • NOT FOOTAGE`.
- **Open requirement gap:** the final export does not contain a separately sourced moving real-footage clip. The sandbox allowed research to identify legal CC video candidates, but its outbound-host restriction prevented downloading a video binary. This is documented rather than disguised; do not call this export footage-complete.
