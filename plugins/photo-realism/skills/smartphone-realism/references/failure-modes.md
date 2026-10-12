# Failure modes and their fixes

Everything here is either observed in testing or documented by a source skill. Where a claim
comes from testing this repository's own generations, it says so.

## 1. Word substitutions that backfire

| Instead of | Write | Failure it prevents |
|---|---|---|
| `blurry` | `low resolution`, `soft details`, `focus isn't quite locked on` | `blurry` is interpreted as image degradation and produces pixel art |
| `grain` | `noise`, `digital noise`, `scan quality` | `grain` produces an oil-painting surface texture |
| `low saturation` (once) | `extremely extremely low saturation`, `drab and yellowish`, `not a single color is vivid`, `every color is covered in gray and yellow` | a single qualifier gets discounted by the model |
| `high quality`, `8K`, `masterpiece`, `ultra detailed` | omit entirely | unsupported quality language pulls the output toward a CGI look |
| camera brand and model as decoration | the device's shooting logic | the model treats a device name as a prop and keeps default perfect composition |

**The repetition rule.** Each qualifier can be discounted. One statement of `low saturation`
produces a merely desaturated image. The fix is repetition and intensification, not a
different word: `extremely extremely low saturation`, `drab and yellowish`, `not a single
color is vivid`. This is documented by the `hyperrealistic-image` skill, which developed the
rule over 40+ rounds across 6 scenes.

## 2. The damage prior — prior beats negation

**Observed directly in this repository's test generations, not just reported by a source.**

Two prompts asked for an ordinary, lived-in room with a modestly imperfect wall:

```
the wall is slightly mottled with a scuff mark and a power outlet visible
```

```
the wall behind is plain painted plaster, mostly intact, clean and smooth with only two or
three small faint smudges and one light scuff near the power outlet — an ordinary clean
apartment wall that has been lived against, not damaged, not stained, not peeling
```

Both produced a wall covered in dark mould-like speckling. The second prompt's negation was
explicit, repeated, and positioned immediately after the description. It lost.

**Mechanism.** The prior is not a failure to parse the negation. The model is pulled toward
the damaged reading by the surrounding vocabulary (`worn`, `faded`, `lived-in`, `imperfect`,
`casual`, `cheap`, `ordinary`) and the negation only competes with that pull — it does not
cancel it. Adding more negations adds more competing tokens without removing the pull.

**Fix — change the object, not the adjective.**

| Approach | Prompt shape | Result |
|---|---|---|
| Fight the prior | `worn sofa` + `wall: clean, smooth, not stained, not damaged` | damaged surface |
| Change the object | `a plain beige slipcover, evenly colored and clean` + `freshly painted, uniform, no marks, no stains, no discoloration anywhere` | clean surface |

Same prompt, same model, one generation apart. The fix is to stop describing a damaged object
and asking it not to look damaged. Describe an object that is genuinely intact, and move the
ordinary-ness into **light, color, and clutter** — a flat grey-yellow cast, table clutter, a
plugged-in charger cable, a tilted frame.

This mirrors the repetition rule: **describe the object you want, not an adjective applied to
a different object.**

## 3. Aspect-ratio traps

Every device implies a plausible ratio. An impossible ratio invalidates the premise before any
other quality is judged.

| Device | Plausible | Implausible |
|---|---|---|
| Smartphone, default | 4:3 | 11:6, 21:9 |
| Smartphone, video frame | 16:9 | — |
| Point-and-shoot, 2000s | 4:3 | tall portrait crops |
| 35mm film | 3:2 | — |

**Observed:** `smartphone, 4:3` as a mid-prompt instruction produced 1408×768 (11:6, ratio
1.833). Moving `Casual 4:3 horizontal photo taken with a smartphone` to the **opening
sentence** produced 1200×896 (ratio 1.339). The model resolves framing from the opening, so
the ratio belongs there, not in a later clause.

## 4. Camera-logic traps

| Trap | Consequence | Fix |
|---|---|---|
| Device named without shooting logic | model ignores the era and composes perfectly | always pair the device with how a person holds and fires it |
| `"far from the subject"` stated abstractly | model stands right in front of the subject anyway | state a checkable result: `far enough that the entire sofa fits inside the frame` |
| Prompting a tight close-up for a phone-realism scene | removes the room context that sells the capture | keep some surrounding environment in frame |
| Negative space left unspecified while forbidding a centered subject | subject drifts back to center | give the empty area a job: `the upper-left third belongs to the room, not the subject` |

## 5. Detail traps

| Trap | Consequence | Fix |
|---|---|---|
| `mottled, irregular, weathered` on a wall | intended to defeat a 3D-render look; in practice overshoots into visible damage | use a much smaller dose than reads natural, or skip it and defeat the render look through light and color |
| `just a few crumbs` | reads as a scattered field | state the count: `only two or three small crumbs and a single loose hair` |
| Ordinary people described plainly | model substitutes a template face | `everyone looks different with their own features`, `skin has pores, blemishes` |
| Multi-person scenes without orientation | model scrambles body directions | `everyone faces the same direction, no one facing the camera` |
| Fur or hair described generically | reads as a smooth mass | `individual strands clearly visible`, `uneven and unbrushed` |

## 6. Verification failure

A successful tool response is not a successful image. Inspect the returned pixels against what
the prompt asked for, and check specifically for the failure modes above. Accepting a
generation because the tool reported success is how a damaged wall and an impossible
aspect ratio both ship.
