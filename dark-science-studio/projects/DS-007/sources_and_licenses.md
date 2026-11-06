# DS-007 — Sources & Licences

**Video:** The Amoeba That Eats Brains — 167 Cases, 4 Survivors
**Delivered:** 2026-11-07 · 46.70 s · 1080×1920 · 30 fps

**Rule applied to this episode:** every number follows CDC / NCBI wording, even
where a punchier number existed. This topic kills people who trust a bad
infographic, so the video under-claims on purpose.

---

## 1. Claim table

| # | Claim as delivered | Status | Source |
|---|---|---|---|
| 1 | "An amoeba swam up a boy's nose and started eating his brain." | Supported (as a description of primary amoebic meningoencephalitis) | *Naegleria fowleri* enters via the olfactory neuroepithelium and causes PAM. The video's hook is a plain-English description of the pathology, not a specific case. |
| 2 | "It is Naegleria fowleri. Not a parasite, a free living amoeba." | Supported | CDC: "Naegleria fowleri is a free-living amoeba." It is not an obligate parasite. |
| 3 | "It lives in warm fresh water, above thirty degrees Celsius." | Supported | CDC: grows best at up to 45 °C and tolerates >30 °C; found in warm freshwater, lakes, rivers, hot springs. |
| 4 | "You cannot catch it by drinking. Stomach acid destroys it." | Supported | CDC: "You cannot get infected by drinking contaminated water." Infection requires nasal exposure. |
| 5 | "It has to go up the nose, along the olfactory nerve, through a plate of bone, into the brain." | Supported | CDC/NCBI: organisms traverse the cribriform plate along the olfactory nerve into the olfactory bulb, then the CNS. |
| 6 | "Then it multiplies, and the brain swells." | Supported | Trophozoites proliferate in brain tissue, producing haemorrhagic necrotising meningoencephalitis with cerebral oedema. |
| 7 | "From first symptom to death: five point three days, on average." | Supported | NCBI Bookshelf: mean duration from symptom onset to death ≈ 5.3 days (range 1–12). |
| 8 | On-screen `EXPOSURE TO DEATH 9.9 DAYS` | Supported | NCBI Bookshelf: mean duration from exposure to death ≈ 9.9 days. **This is a different interval from #7 and is labelled separately — earlier drafts mislabelled it "onset".** |
| 9 | "The CDC has recorded one hundred sixty seven American cases since 1962." | Supported | CDC: 167 known US cases, 1962–2024. |
| 10 | "Four people survived." | Supported | CDC: 4 survivors among those 167 cases. |
| 11 | "That is a fatality rate above ninety seven percent." | Supported | 163/167 ≈ 97.6 %. The video says "above ninety seven percent," not "99 %". |
| 12 | "In 2016, a sixteen year old in Florida became one of them." | Supported | Sebastian DeLeon, 16, infected July 2016 in Florida; treated at Florida Hospital for Children and survived. Public and widely reported with family consent. |
| 13 | "Treated within hours" (on screen) | Supported | Survival depended on rapid empirical treatment with the amphotericin B + miltefosine protocol and induced hypothermia; his diagnosis came unusually fast. |
| 14 | "Salt water kills the amoeba. The ocean is safe." | Supported | CDC: *N. fowleri* does not survive in salt water. |
| 15 | "But the lake is not. And it begins as a headache." | Supported | Freshwater exposure is the risk route; early symptoms (headache, fever, nausea) are non-specific and are the reason diagnosis is usually late. |

### Deliberate omissions and refusals
- **Never called "the brain-eating amoeba" in the narration** (it is in the search tags only). The phrase encourages the idea that it eats people generally; it kills by meningoencephalitis after a nasal exposure.
- **No "99 %" and no "you will die in a week" framing.** CDC gives >97 % and 5.3 days mean.
- **No claim you can be infected by swimming in any lake.** Exposure is common; disease is extremely rare. The video does not state a per-swim risk because no defensible number exists.
- **No case count beyond 2024.** New cases exist (a 2026 teen case, a Louisiana death) but the CDC table the video cites ends at 2024, and mixing sources would break the arithmetic.

---

## 2. Visual simplifications

| Visual | What is real | What is simplified |
|---|---|---|
| `nerve_invasion` route | Nasal cavity → cribriform plate → olfactory nerve → olfactory bulb | Anatomy is schematic: the plate is drawn as a regular perforated grid, the nerve as 9 filaments, the bulb as a wireframe sphere. |
| Organism shape | Trophozoites are ~10–25 µm, amoeboid, with lobose pseudopodia | Drawn as comma-shaped bodies with a trailing flagellum-like line. **Not to scale** — at true scale they would be invisible. |
| Animated route speed | Onset is days, not seconds | The traversal is compressed into seconds for the shot. |
| `mirror_colony` culture beats | Amoebae are single-celled and divide | The colony scene is a generic culture visual reused from the channel library. |

---

## 3. Assets and licences

| Asset | Source | Licence |
|---|---|---|
| Every scene, caption, cover, transition | Generated in code for this episode | Original work, owned by the channel |
| Narration | Piper TTS `en_US-lessac-medium`, offline | MIT model; output is original |
| Music bed and SFX | Synthesised by `tools/audio_kit.py` from `TimGM6mb.sf2` | Free GM soundfont; rendered audio is original |
| Typefaces | Anton, Montserrat, JetBrains Mono | SIL OFL 1.1 |
| Third-party footage, micrographs, patient photos | **None** | — |

---

## 4. Primary references

1. CDC, "About Naegleria fowleri" — case counts, transmission route, temperature range, salt-water statement.
2. CDC, "Naegleria fowleri — Primary Amoebic Meningoencephalitis" surveillance summary (1962–2024).
3. NCBI Bookshelf, *Naegleria fowleri* (StatPearls/NCBI chapter) — 5.3-day symptom-to-death and 9.9-day exposure-to-death intervals, treatment protocol, survivor circumstances.
4. Contemporary reporting of the 2016 Florida case (Sebastian DeLeon).

---

## 5. Disclosure summary

- Synthetic narration: **yes** (Piper, offline).
- Synthetic visuals: **all** (procedural).
- Real footage or microscopy: **none**.
- Health disclaimer: this is a science-education video, not medical advice; that line is in the description.
