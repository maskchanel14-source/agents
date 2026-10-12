# Era grading and realism presets

Two independent axes: the **era** (how degraded the capture is) and the **preset** (what kind of
capture it is). Choose both, then write the shooting logic. Era keywords come from the
`hyperrealistic-image` skill.

## Era table

An older photo is not just a filter — yellowing, fading, grain, and resolution move together.
Using modern-quality language with an old era produces a contradiction the model resolves
unpredictably.

| Era | Yellowing | Fading | Quality | Saturation | Typical devices |
|---|---|---|---|---|---|
| 1970s | severe | severe, near black-and-white with faint color | poor, blurry, unclear detail | very low | film cameras, Seagull, Shanghai brand |
| 1990s | moderate | noticeable, muted colors | average, heavy grain | low | Kodak Gold, Fuji film, point-and-shoot |
| 2000s | yellowish-gray | noticeable, dull and muted | average, digital feel, low resolution | low | early digicams, camera phones |
| 2010s | minimal | almost none | good, clear but not modern | medium | early smartphones, compact cameras |
| Present | none | none | full, but see the phone trap below | natural | modern smartphones |

**1970s keywords:** severe yellowing, severe fading, extremely low saturation, drab, poor
quality, blurry, film grain, mottled walls, plain clothes, no vivid colors.

**1990s keywords:** yellowing, fading, low contrast, hazy, heavy grain, Kodak Gold film, old
furniture, studio backdrops.

**2000s keywords:** yellowish-gray, dull muted colors, noticeable fading, low saturation,
digital noise, low resolution, soft details.

## The modern-phone trap

Present-day phones are not a "high quality" era by default in the AI sense. A modern phone
capture still has: white balance that is off toward yellow-green indoors, flat overhead ambient
light with no interesting shadows, mild digital noise, low-contrast dull colors, and slightly
soft details. **Good resolution is not the same as good photography**, and prompting only for
resolution produces the polished look this skill exists to avoid.

## Five presets

| Preset | Core device or medium | Opening template | Use for |
|---|---|---|---|
| Phone snapshot | smartphone, one-handed | `Casual 4:3 horizontal photo taken with a smartphone, held one-handed and pressed without composing anything, frame slightly tilted, random composition, average quality, not high resolution, soft details, slight digital noise, white balance off toward yellow-green, dull low-contrast colors, low saturation, everything under a flat grey-yellow cast` | daily life, campus, casual interiors |
| Film feel | Kodak Gold, Fuji C200 | `Shot on Kodak Gold film, heavy grain, warm yellowish tones, low contrast, slightly faded, slight vignette` | mood, portraits, artistic |
| Documentary street | Leica, Ricoh GR, point-and-shoot | `Documentary street photo, held up and pressed the shutter, tilted composition, authentic messy feel, high contrast, hard light, film grain, slight motion blur` | street, human interest |
| Life record, indoor | phone, indoors | `Shot indoors with a phone, warm yellow lighting, yellowish white balance, average quality with noise, white balance off, things on the table, casual home snapshot feel` | home, food, daily |
| Vintage photo | film plus scan | `1990s old photo, shot on film, severely faded and yellowish-dark, low contrast hazy, average quality heavy grain, dust and scratches, scanned from old album` | nostalgia, family archive |

Note that the film presets describe **grain**, while phone presets describe **noise**. They are
not interchangeable — see `references/failure-modes.md` for why `grain` breaks a digital
capture.

## Template: phone snapshot

```
Casual 4:3 horizontal photo taken with a smartphone, held one-handed and pressed without
composing anything, frame slightly tilted, random composition, average quality, not high
resolution, soft details, slight digital noise, white balance off toward yellow-green, dull
low-contrast colors, low saturation, everything under a flat grey-yellow cast.

[ORDINARY SUBJECT], [IMPERFECT DETAIL]. Environment: [ORDINARY ROOM], mildly cluttered with
[EVERYDAY CLUTTER]. Flat ambient light, no interesting shadows, nothing dramatic happening.

Not a retouched photo, not professional photography, not a high-res image, not AI-generated,
just a very ordinary boring photo taken by an ordinary person by accident.
```

## Adapting the template

- **Swap `smartphone` for another device only together with its shooting logic.** See the device
  table in `SKILL.md`.
- **Keep 4:3** unless the user asks for a video still. See `references/failure-modes.md`.
- **Put the ratio in the opening sentence.** Mid-prompt ratio instructions were ignored in
  testing.
- **Count the clutter.** `only two or three small crumbs and a single loose hair` beats
  `a few crumbs`.
