# DS-005 — Sources & Licences

**Video:** There Is Another Star Inside Betelgeuse
**Delivered:** 2026-11-07 · 48.47 s · 1080×1920 · 30 fps

Every factual claim in the narration and on-screen text is listed below with its
source. Where the visual had to simplify, the simplification is disclosed.

---

## 1. Claim table

| # | Claim as delivered | Status | Source |
|---|---|---|---|
| 1 | "There is another star inside Betelgeuse. Not next to it. Inside its atmosphere." | Supported (as the leading interpretation) | Radio imaging of Betelgeuse with the VLA and ALMA over 2021–2026 epochs shows the disc becoming elliptical in a way that repeats with orbital phase. The best-supported explanation is a low-mass companion on an orbit of about 2 stellar radii — i.e. inside the extended atmosphere. Lead author Lynn D. Matthews (MIT Haystack Observatory). |
| 2 | "Betelgeuse is a red supergiant, roughly seven hundred times wider than the Sun." | Supported | Betelgeuse radius ≈ 640–800 R☉ depending on method; ~700 is the standard order-of-magnitude figure. |
| 3 | "Put it where the Sun is and it would swallow Mars." | Supported | Mars orbits at 1.52 AU = 327 R☉. A ~700 R☉ star reaches ~3.3 AU, past the asteroid belt, short of Jupiter (5.2 AU). |
| 4 | "Its outer layers are so thin they barely count as a surface." | Supported | Red-supergiant photospheric density is ~10⁻⁹–10⁻¹⁰ g/cm³ — far below any terrestrial vacuum standard. The "surface" is an optical-depth definition, not a solid boundary. |
| 5 | "Something is orbiting through them." | Supported | Same as #1: the companion's orbital distance (~2 R★) is inside the extended atmosphere, not outside it. |
| 6 | "Radio telescopes caught it, reading the giant at twenty two to four hundred eighty five gigahertz." | Supported | Observations spanning 22–485 GHz across seven VLA/ALMA bands. |
| 7 | "Over six years, its disc went out of round, then round again." | Supported | 2021–2026 epochs; the ellipticity peaks near maximum separation and returns toward circular. |
| 8 | "A companion about two stellar radii out, ploughing through the gas it orbits in." | Supported | The 2 R★ figure is the reported best-fit separation. |
| 9 | "Too faint to photograph. Ten to a hundred times below what those maps can pick out." | Supported | A ~1 M☉ companion at that separation and distance falls 10–100× below the radio maps' sensitivity — hence an indirect detection. |
| 10 | "We know it is there only because Betelgeuse breathes unevenly." | Supported, hedged | The evidence is the periodic shape change of the disc, not a direct image. The video uses "only because," which is the honest state of the evidence. |
| 11 | "A heartbeat every two thousand one hundred days, if the model holds." | **Proposed, explicitly hedged** | A ~2,100-day periodicity in Betelgeuse's brightness/radial-velocity behaviour was proposed in 2024 and is the natural orbital period for a 2 R★ orbit. It is a *model*, not a confirmed ephemeris. The narration says "if the model holds"; the on-screen counter (`2,100 D`) cannot carry that hedge, so this file and the pinned comment do. |
| 12 | "The star that will one day explode has a passenger it cannot shake." | Supported | Betelgeuse is a core-collapse (Type II) supernova progenitor; the timescale is ~100,000 years or less, so "one day" is correct and no date is implied. |

### Deliberate omissions
- **No distance figure on screen or in narration.** Published distances range ~500–650 ly; the video avoids the number rather than pick a side.
- **No mass for the companion.** Estimates are model-dependent; saying "a companion" is safe, saying "one solar mass" would not be.
- **No claim that the companion caused the 2019–20 Great Dimming.** That event is attributed to dust, and the video never links the two.

---

## 2. Visual simplifications (disclosed on screen and here)

| Visual | What is real | What is simplified |
|---|---|---|
| `star_wake` companion | Its existence, its ~2 R★ orbit, the "inside the atmosphere" geometry, the disc deformation | The dot is drawn far larger than a ~1 M☉ companion would be at 1080 px, and the orbit is shown inclined for legibility. |
| `star_wake` disc deformation | Ellipticity that peaks near maximum separation | The deformation is exaggerated ~2× so it reads at phone size. |
| `star_wake` "wake" arcs | Disturbed gas trailing the companion | Illustrative — no published image of the wake exists. |
| `counter_slam` 22 → 485 | The real frequency range | The counter animates *through* intermediate frequencies for motion; only the two endpoints are measurements. |
| All HUD readouts | Labels name real instruments (VLA, ALMA) and real numbers | The panel layout is a design device. |

---

## 3. Assets and licences

| Asset | Source | Licence |
|---|---|---|
| Every scene, caption, cover and transition | Generated in code for this episode (`tools/studio/src/scenes/SceneLibrary.tsx`, `tools/cover_kit.py`) | Original work, owned by the channel |
| Narration | Piper TTS `en_US-lessac-medium`, offline | Model: MIT (rhasspy/piper); output is original |
| Music bed and SFX | Synthesised by `tools/audio_kit.py` from the General MIDI soundfont `TimGM6mb.sf2` | TimGM6mb is a free GM soundfont (GPL-compatible, redistribution permitted); the *rendered audio* is original |
| Typefaces | Anton (SIL OFL 1.1), Montserrat (OFL 1.1), JetBrains Mono (OFL 1.1) | OFL — embedding and commercial use permitted |
| Third-party footage or stills | **None** | — |
| Real telescope imagery | **Not used.** VLA/ALMA maps of Betelgeuse are not public-domain and would have needed a licence | — |

---

## 4. Disclosure summary

- Synthetic narration: **yes** (Piper, offline, no key).
- Synthetic visuals: **all** (procedural Remotion/Canvas2D).
- Real footage: **none** — the video is honest about this by never showing a frame labelled "real footage".
- AI-generated photorealistic imagery of real people or events: **none**.
