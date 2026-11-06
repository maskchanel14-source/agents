# DS-006 — Sources & Licences

**Video:** The 220 PeV Ghost Particle That Should Not Exist
**Delivered:** 2026-11-07 · 49.60 s · 1080×1920 · 30 fps

---

## 1. Claim table

| # | Claim as delivered | Status | Source |
|---|---|---|---|
| 1 | "Something crossed the Mediterranean and struck a detector three and a half kilometres down." | Supported | KM3-230213A was recorded on 2023-02-13 by the ARCA detector of KM3NeT, moored at ~3,450 m depth off Portopalo di Capo Passero, Sicily. |
| 2 | "One particle. It lit more than a third of the sensors in a cubic kilometre of water." | Supported | A single through-going muon triggered more than 30 % of the optical modules active at the time (the video's counter reads 30 %). |
| 3 | "We call them ghost particles, because they pass through planets without slowing." | Supported (popular usage) | Neutrinos interact only weakly; a neutrino of this energy has a mean free path vastly larger than Earth. The on-screen phrasing is the standard lay description. |
| 4 | "On the thirteenth of February, 2023, KM3NeT caught one muon." | Supported | Event date and detector, per the KM3NeT/Nature publication. |
| 5 | "Its angle and brightness imply a neutrino of two hundred and twenty peta electronvolts." | Supported | Best-fit neutrino energy ~220 PeV (reconstructed muon energy ~120 PeV). |
| 6 | On-screen `72 – 2,600 PeV / 90% CL` | Supported | The published 90 % credible interval for the neutrino energy. |
| 7 | "About thirty times the previous record." | Supported | Highest previously detected neutrino energies (~10 PeV) — roughly 30× lower. |
| 8 | "And the detector was barely ten percent finished." | Supported | At the time of the event only a small fraction of the planned detector was deployed (~1/10 of final configuration). |
| 9 | "When complete, it will hang two hundred thousand light sensors on towers a hundred metres apart." | Supported | Final KM3NeT/ARCA design: ~1 km³, ~200,000 PMTs, detection units ~100 m apart; ARCA footprint ~230 m × 700 m (the on-screen card uses `200,000 SENSORS`). |
| 10 | "IceCube, at the South Pole, has seen nothing like it." | Supported | No comparable-energy event in IceCube's catalogues; the non-observation underpins the tension. |
| 11 | "Two detectors, one sky, a three sigma disagreement." | Supported, with caveat | The KM3NeT–IceCube tension is quoted at roughly 3–3.6σ depending on the analysis (Li et al., *Phys. Lett. B*, 2026). Three sigma is a **tension**, not a discovery; the video says "disagreement," not "proof." |
| 12 | "Either we got extremely lucky, or the Standard Model is missing something. Sterile neutrinos. New interactions." | Supported as hypotheses | Both are live, unconfirmed explanations in the literature (e.g. sterile-neutrino / BSM readings of the event). The video frames them as possibilities, never as findings. |
| 13 | "One flash, and a crack in physics." | Editorial | Explicitly a metaphor in the closing line, not a claim of a confirmed anomaly. |

### Deliberate omissions
- **No claim of discovery.** The episode never says new physics has been found.
- **No source direction.** The reconstruction gives a direction with large uncertainty; the video does not claim an origin object.
- **No date for the tension's resolution.** It is an open question and is presented as one.

---

## 2. Visual simplifications

| Visual | What is real | What is simplified |
|---|---|---|
| `neutrino_shower` detector | Vertical strings of optical modules in ~3.5 km of water | Drawn as 8 strings × 9 modules around the track. The real ARCA grid is 230 m × 700 m with ~100 m string spacing and ~200,000 PMTs; at frame scale it would be a grey smear. |
| Cherenkov cone | Directional light cone along the muon track | Emission is instantaneous in reality; the animation grows the cone over ~0.35 of a shot so the eye can follow it. |
| Module "lighting up" | PMTs record photons along the entire track | The animation lights modules in a moving band to make the reading visible. |
| Track length | The muon crosses the whole detector | Drawn nearly horizontal and fully within frame. |
| Counters (30×, 220 PeV) | Both figures are real | The animation passes through intermediate values for motion; only the endpoints are measurements. |

---

## 3. Assets and licences

| Asset | Source | Licence |
|---|---|---|
| Every scene, caption, cover, transition | Generated in code for this episode | Original work, owned by the channel |
| Narration | Piper TTS `en_US-lessac-medium`, offline | MIT model; output is original |
| Music bed and SFX | Synthesised by `tools/audio_kit.py` from `TimGM6mb.sf2` | Free GM soundfont; rendered audio is original |
| Typefaces | Anton, Montserrat, JetBrains Mono | SIL OFL 1.1 |
| Third-party footage or stills | **None** | — |
| KM3NeT photography | **Not used** — press images are not licensed for reuse in a monetised video | — |

---

## 4. Primary references

1. KM3NeT Collaboration, "Observation of an ultra-high-energy cosmic neutrino with KM3NeT," *Nature* **638**, 376–382 (2025). doi:10.1038/s41586-024-08543-1
2. KM3NeT press release, 2025 (event date, detector configuration, 220 PeV fit).
3. Max-Planck-Institut für Radioastronomie press note, 2025 (independent summary of the event).
4. Li et al., *Physics Letters B* (2026) — KM3NeT/IceCube compatibility analysis, 3–3.6σ tension.
5. Brdar & Chattopadhyay, *Physical Review Letters* (2026) — BSM/sterile-neutrino interpretation.

---

## 5. Disclosure summary

- Synthetic narration: **yes** (Piper, offline).
- Synthetic visuals: **all** (procedural).
- Real footage: **none**.
- No image of a real person, and none generated.
