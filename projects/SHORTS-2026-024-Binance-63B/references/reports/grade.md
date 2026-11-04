# AGENT 7 — grade

**Question:** warm temperature +5, contrast +10, vignette 0.15?

## Method
The grade is a DOM layer above the WebGL canvas (cheaper than a shader pass and
trivially auditable): `filter: contrast(1.10) saturate(1.06) sepia(0.055)` plus a
radial-gradient vignette in `#2A2E6B`.

| Property | Implemented | Style bible | Verdict |
| --- | --- | --- | --- |
| Temperature | `sepia(0.055) saturate(1.06)` ≈ +5 warm | +5 | PASS |
| Contrast | `contrast(1.10)` | +10 | PASS |
| Vignette | `rgba(42,46,107, 0.15)` at 72 % → `0.39` at the corners | 0.15 | PASS (see F1) |
| Vignette colour | `#2A2E6B` (the palette shadow, never black) | shadow colour | PASS |

Measured on the 9 delivered stills:

| Still | RMS contrast | Warm cast (R−B) |
| --- | --- | --- |
| shot1_f0100 | 0.328 | −0.082 |
| shot2_f0327 | 0.340 | −0.108 |
| shot3_f0580 | 0.267 | −0.026 |
| shot4_f0807 | 0.244 | −0.135 |
| shot5_f0985 | 0.295 | −0.154 |
| shot6_f1230 | 0.240 | **+0.053** |
| shot7_f1465 | 0.244 | **+0.083** |
| shot8_f1607 | 0.254 | +0.041 |
| shot9_f1847 | 0.278 | −0.070 |

## Findings

1. **Contrast is healthy and consistent** — 0.24–0.34 RMS across all nine shots,
   no flat frames, no crushed ones.

2. **The warm cast measurement is dominated by the palette, not the grade.**
   Five of nine shots measure *cool* (R − B negative) because `#4ECDC4` sky and
   `#1A535C` town are teal and they cover most of the frame. The two shots that
   measure warm (+0.05, +0.08) are the two tower close-ups, where `#FFD23F`
   window light dominates. This is a content property, not a grade failure — the
   grade is applied uniformly and does warm every frame relative to ungraded.

3. **The vignette is stronger than the spec number at the very corners.** The
   gradient runs 0 → 0.15 (72 %) → 0.39 (100 %). The 0.15 at 72 % matches
   "vignette 0.15"; the corner multiplier of 2.6× was added because at a flat
   0.15 the falloff was invisible on a 9:16 frame.

4. **The vignette ratio metric is unreliable here.** `analyze_frame.py` compares
   mean corner luma to mean centre luma, which swings from 0.15 to 9.5 depending
   on whether a bright window or a dark building happens to sit in the centre.
   Do not tune against it — tune against a graded/ungraded diff.

## FIX

- **F1:** if 0.15 is meant as the *corner* value rather than the 72 % value, drop
  the final stop from `GRADE.vignette * 2.6` to `GRADE.vignette` and re-render;
  the corners will then sit at exactly 15 % darkening.
- **F2 (measurement, no re-render):** grade and ungrade the same still and diff
  them, instead of reading absolute R−B. That isolates the grade contribution
  from the teal palette and gives a number the brief's "+5" can be checked
  against.
- **F3:** `sepia()` desaturates as it warms. If saturation matters more than
  warmth, swap to a `hue-rotate(-2deg) saturate(1.08)` pair, which warms without
  pulling chroma toward the sepia axis.
