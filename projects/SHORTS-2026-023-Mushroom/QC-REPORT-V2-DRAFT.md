# QC report — V2 hyper-documentary review export

**Status:** review export only. This is a creative rebuild after the user rejected the prior footage cut. It is **not** approved, packaged, uploaded, or publish-ready.

## Creative changes tested

- **Pacing:** 22 footage shots cut on a 120-BPM half-bar/bar grid, plus on-beat data/typography hits.
- **Footage movement / enhancement:** every shot has an eased push, drift, micro-motion and hard-cut/whip accent. Supplied 1080p source proxies were given a restrained temporal-denoise, unsharp and tonal-contrast pass before the editorial grade. This is a clarity enhancement, not a claim that proprietary Remini AI was used.
- **Captions:** the narration was rebuilt into ten known sentence clips. MIT `remotion-captions-kit` paginates them in short punctuation-aware chunks; the active word receives a lime underline. This avoids static all-caps scene-paragraph subtitles.
- **Visual hierarchy:** Space Grotesk display type, IBM Plex Mono metadata, one lime evidence accent, distinct cyan/amber/red factual states, and a grain/vignette finish.
- **Sound design:** original 120-BPM dark-pulse bed, whooshes ahead of cuts, bass/sub hits on factual turns, and ticks on data beats. Music ducks under narration.

## Render result

- **Candidate file:** `renders/v2-hyper-documentary/shorts023-v2-hyper-documentary.mp4`
- **Runtime:** 41.002 seconds / 1230 frames.
- **Video:** H.264, 1080×1920, 30 fps, 7.19 Mb/s.
- **Audio:** AAC-LC stereo, 48 kHz, 294 kb/s.
- **Size:** 38.4 MB.

## Mechanical verification

- Full decode with FFmpeg `-v error -xerror`: **PASS**; `decode-final.log` is empty.
- `blackdetect` with `d=0.10`, `pic_th=0.97`, `pix_th=0.10`: **PASS**; no black event found.
- Integrated loudness: **−14.7 LUFS** (social delivery range target −16 to −12 LUFS): **PASS**.
- True peak: **−1.5 dBFS**: **PASS**.
- The final frame remains picture, not a black tail; see `qc/frames/last.jpg`.
- `qc/audio-spectrum.png` confirms continuous low-frequency score content plus transient/high-frequency SFX content. This is waveform/spectral evidence, not a claim of human audio listening.

## Frame-review evidence

`qc/contact-sheet.jpg` and the named frame extracts show:

1. **Hook:** real macro mushroom footage and the “TINY PEOPLE?” story hit occur inside the first half-second.
2. **DNA:** China → Philippines is expressed as an evidence line over generic context footage; the footage is not identified as *L. asiatica*.
3. **Genome / unknown:** the edit separates “no known pathway” from “active compound unknown,” avoiding a false discovery claim.
4. **Evidence limit and safety:** Papua New Guinea non-verification and the no-testing safety language are legible in the safe zone.
5. **Payoff:** `SPECIES: KNOWN` versus `MOLECULE: UNKNOWN` resolves the story without overstating research.

## Remaining approval gate

Technical QC passes. Creative acceptance remains solely with the user after viewing the full review export—especially the hook, music/SFX intensity, subtitle feel, and ending. Do not replace the prior delivery package or publish this candidate until that feedback is received.
