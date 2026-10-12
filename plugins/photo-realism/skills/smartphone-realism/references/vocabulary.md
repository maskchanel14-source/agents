# Structured vocabulary for photographic prompts

Extracted from `artokun/ComfyUI-Photoreal-Prompt-Builder` (`nodes.py`, MIT). That project ships
the vocabulary inside a ComfyUI node graph; the options and their prose expansions are separable
from the node and usable in any prompt, with or without ComfyUI installed.

Source: https://github.com/artokun/ComfyUI-Photoreal-Prompt-Builder

## How to use this

Two options carry the highest value for defeating an AI look: **`phone candid`** and **`phone
camera angle`**. Not `photorealistic`, not `cinematic`, not `editorial`. Reach for the phone
options first and escalate to the produced options only when the user actually wants polish.

## Lighting, with prose expansions

The prose expansion is what makes a preset work. The label alone is weaker than the label plus
its expansion, and the expansion is where the specificity lives.

| Preset | Prose expansion |
|---|---|
| `ring light` | even ring light illumination with circular catchlights in the eyes and minimal shadows |
| `softbox beauty` | professional softbox beauty lighting with soft wrap-around illumination and flattering skin tones |
| `natural window light` | soft natural light streaming through a window, creating gentle gradients from light to shadow |
| `golden hour` | warm golden hour sunlight with long shadows and rich amber tones |
| `blue hour` | cool blue hour twilight with deep indigo sky and soft diffused ambient light |
| `neon/artificial` | vibrant neon and artificial light casting colorful reflections and electric atmosphere |
| `direct flash` | direct on-camera flash with harsh shadows and high contrast pop |
| `overcast soft` | soft overcast daylight creating even, shadowless illumination with gentle tonal gradations |
| `backlit sun flare` | backlit sun flare with the subject haloed in warm luminous light and lens flare |
| `LED strip ambient` | colorful LED strip ambient light casting soft gradients of color across the scene |
| `screen/monitor glow` | cool screen glow illuminating the face with soft bluish-white light in a dim room |
| `harsh midday sun` | harsh midday sun with strong overhead shadows and high contrast |
| `studio rim light` | dramatic studio rim light separating the subject from the background with a luminous edge |
| `dramatic side light` | strong directional side light carving deep shadows and bright highlights |
| `candlelight` | warm flickering candlelight casting intimate orange glow and dancing soft shadows |
| `custom` |  |

## IG quick effects, with prose expansions

| Effect | Prose expansion |
|---|---|
| `none` |  |
| `add rain` | Add gentle rain falling throughout the scene with wet reflective surfaces |
| `add snow` | Add softly falling snow with a cold winter atmosphere |
| `add lens flare` | Add warm lens flare from the light source |
| `add bokeh background` | Add beautiful circular bokeh lights in the background |
| `add golden dust particles` | Add golden dust particles floating in the light |
| `add neon glow` | Add colorful neon glow and reflections across the scene |
| `add fog/haze` | Add atmospheric fog and haze softening the background |
| `add confetti` | Add colorful confetti falling through the air |
| `add sparkles` | Add glittering sparkles catching the light |
| `change to nighttime` | Change the time to nighttime with dark sky and artificial lighting |
| `change to golden hour` | Change the lighting to warm golden hour with long amber shadows |
| `change to overcast` | Change the sky to soft overcast with even diffused lighting |
| `add wet/reflective surfaces` | Add wet reflective surfaces with puddles catching the light |
| `add motion blur` | Add subtle motion blur suggesting movement and energy |

## Photo styles

`phone candid` and `documentary candid` are the realism-first options. `cinematic`, `editorial`, and `fashion` push toward a produced look, which is a different and usually unintended claim.

`phone candid` · `mirror selfie` · `editorial` · `lifestyle`

`fashion` · `cinematic` · `film grain` · `flash photography`

`golden hour aesthetic` · `neon night` · `studio clean` · `vintage retro`

`street style` · `paparazzi` · `documentary candid`


## Lenses

The two `iPhone` entries imply a real phone capture. Prime lenses imply a dedicated camera, which also implies deliberate framing and therefore weakens the casual premise.

`24mm wide` · `35mm` · `50mm` · `85mm portrait`

`105mm` · `135mm` · `iPhone front camera` · `iPhone rear camera`


## Depth of field

Phone cameras have deep depth of field by default. Selecting a shallow option while claiming a phone capture is internally inconsistent and reads as staged.

`razor thin f/1.4` · `shallow f/2.0` · `shallow f/2.8` · `moderate f/4`

`standard f/5.6` · `sharp f/8`


## Camera angles

`phone camera angle` and `mirror selfie angle` carry the capture logic. `low-angle hero shot` and `3/4 angle` imply a director.

`eye level` · `slightly low angle` · `slightly high angle` · `3/4 angle`

`profile angle` · `mirror selfie angle` · `phone camera angle` · `dutch angle`

`low-angle hero shot` · `overhead selfie angle` · `from below` · `rear 3/4 angle`


## Shot types

`candid mid-shot`, `selfie arm-length`, and `from-behind candid` are the phone-native framings. `environmental portrait` keeps room context in frame, which is usually what sells the capture.

`extreme close-up` · `close-up face` · `headshot` · `upper body portrait`

`chest-up portrait` · `waist-up portrait` · `three-quarter portrait` · `cowboy shot`

`full body` · `wide full-body` · `selfie arm-length` · `environmental portrait`

`candid mid-shot` · `from-behind candid` · `silhouette framing`


## Color gradings

For phone realism use `natural` or `muted desaturated`. `vintage kodak` and `faded film` move the image into film territory, which is a different authenticity claim with a different vocabulary.

`natural` · `warm golden` · `cool blue` · `cinematic teal-orange`

`muted desaturated` · `vibrant` · `film noir` · `vintage kodak`

`fuji velvia` · `faded film` · `high contrast` · `pastel soft`

## Scene types

`bedroom` · `bathroom` · `living room` · `kitchen` · `hotel room`

`urban street` · `cafe` · `bar/club` · `rooftop` · `beach`

`pool` · `park` · `gym` · `studio` · `balcony`

`car` · `stairwell` · `hallway/corridor`

## Poses (53)

`standing` · `standing hand on hip` · `standing both hands on hips` · `standing arms crossed` · `standing hands in pockets` · `standing contrapposto`

`standing one leg bent` · `walking` · `walking mid-step turn` · `sitting` · `sitting cross-legged` · `sitting one knee up`

`sitting on edge` · `sitting couch lounge` · `sitting on floor` · `sitting on stairs` · `leaning against wall` · `leaning on railing`

`leaning in doorway` · `leaning on table` · `crouching` · `squatting` · `kneeling` · `reclining on sofa`

`lying on side` · `lying on back` · `lying on stomach elbows up` · `over the shoulder look` · `back to camera` · `three-quarter turn`

`profile` · `head tilt` · `looking away` · `hair flip` · `touching hair` · `tucking hair behind ear`

`hand on chest` · `chin on hand` · `fingers near lips` · `adjusting collar` · `adjusting jacket` · `mirror selfie pose`

`holding phone` · `texting` · `holding coffee` · `peace sign` · `laughing candid` · `serious editorial`

`twirl` · `dance step` · `small jump` · `stretch overhead` · `yoga warrior pose`

## Hairstyles (35)

`beach waves` · `blunt bob` · `box braids` · `braided crown` · `braided ponytail` · `bun`

`buzz cut` · `cornrows` · `curtain bangs` · `double buns` · `dutch braids` · `fishtail braid`

`french braid` · `half up half down` · `high ponytail` · `hollywood waves` · `layered` · `long straight`

`loose curls` · `low bun` · `low ponytail` · `messy bun` · `messy waves` · `middle part straight`

`pixie cut` · `shag` · `side part` · `side swept` · `slicked back` · `space buns`

`textured bob` · `tight curls` · `top knot` · `wet look` · `wolf cut`

## Hair colors (29)

`ash blonde` · `auburn` · `black` · `bleach blonde` · `blue` · `brunette`

`caramel` · `chestnut` · `copper` · `dark brown` · `dirty blonde` · `ginger`

`golden blonde` · `gray` · `green` · `honey blonde` · `jet black` · `lavender`

`light brown` · `medium brown` · `ombre` · `pastel pink` · `pink` · `platinum blonde`

`red` · `silver` · `strawberry blonde` · `two-tone` · `white`

## Clothing colors (66)

`black` · `white` · `cream` · `ivory` · `beige` · `tan`

`camel` · `brown` · `chocolate` · `cognac` · `burgundy` · `maroon`

`wine` · `red` · `cherry` · `coral` · `salmon` · `pink`

`hot pink` · `blush` · `mauve` · `lavender` · `lilac` · `purple`

`plum` · `violet` · `navy` · `royal blue` · `cobalt` · `baby blue`

`sky blue` · `teal` · `turquoise` · `aqua` · `mint` · `sage`

`olive` · `forest green` · `emerald` · `hunter green` · `khaki` · `army green`

`orange` · `rust` · `burnt orange` · `peach` · `mustard` · `gold`

`yellow` · `lemon` · `charcoal` · `gray` · `light gray` · `silver`

`metallic gold` · `metallic silver` · `rose gold` · `denim blue` · `pastel` · `neon`

`tie-dye` · `camo` · `leopard print` · `plaid` · `striped` · `floral`

## Accessories (37)

`Belt` · `Chain belt` · `Sunglasses` · `Eyeglasses` · `Beanie` · `Baseball cap`

`Handbag` · `Backpack` · `Headphones` · `Watch` · `Choker` · `Leather choker`

`Spiked choker` · `Body harness` · `Leather harness` · `Necklace` · `Pendant necklace` · `Layered necklace`

`Chain necklace` · `Earrings` · `Hoop earrings` · `Stud earrings` · `Bangles` · `Rings`

`Stacked rings` · `Nose ring` · `Septum ring` · `Body chain` · `Waist chain` · `Scarf`

`Silk scarf` · `Necktie` · `Bow tie` · `Bracelets` · `Anklet` · `Clutch bag`

`Tote bag`

## Tops (37)

`T-shirt` · `Tank top` · `Crop top` · `Hoodie` · `Sweater` · `Blouse`

`Bodysuit` · `Bustier` · `Corset` · `Corset top` · `Lace camisole` · `Satin camisole`

`Sheer blouse` · `Chiffon blouse` · `Mesh top` · `Fishnet top` · `Off-shoulder top` · `One-shoulder top`

`Halter top` · `Tube top` · `Plunge neckline top` · `Deep V-neck top` · `Wrap top` · `Peplum top`

`Ribbed knit top` · `Turtleneck` · `Mock neck top` · `Sleeveless turtleneck` · `Cardigan` · `Cropped cardigan`

`Bolero shrug` · `Band t-shirt` · `Graphic tee` · `Long sleeve top` · `Cropped hoodie` · `Gothic lace top`

`Harness top`

## Bottoms (38)

`Jeans` · `Shorts` · `Skirt` · `Leggings` · `Joggers` · `Cargo pants`

`Mini skirt` · `Maxi skirt` · `Slacks` · `Denim skirt` · `Micro skirt` · `Pleated skirt`

`Tennis skirt` · `Pencil skirt` · `Wrap skirt` · `Asymmetrical skirt` · `High-slit skirt` · `Leather skirt`

`Latex skirt` · `Plaid skirt` · `Denim shorts` · `Micro shorts` · `High-waisted shorts` · `Biker shorts`

`Hot pants` · `Leather pants` · `Ripped jeans` · `Skinny jeans` · `High-waisted jeans` · `Bell bottoms`

`Flare pants` · `Wide-leg pants` · `Palazzo pants` · `Track pants` · `Sweatpants` · `Yoga pants`

`Fishnet leggings` · `Suspender skirt`

## Outerwear (27)

`Trench coat` · `Wool coat` · `Long coat` · `Peacoat` · `Puffer jacket` · `Parka`

`Bomber jacket` · `Denim jacket` · `Leather jacket` · `Moto jacket` · `Blazer` · `Oversized blazer`

`Cardigan` · `Long cardigan` · `Cropped jacket` · `Zip hoodie` · `Windbreaker` · `Faux fur coat`

`Cape` · `Poncho` · `Kimono` · `Shawl` · `Wrap coat` · `Duster coat`

`Belted coat` · `Suit jacket` · `Satin robe`

## Shoes (27)

`Sneakers` · `Boots` · `Heels` · `Platform shoes` · `Sandals` · `Flats`

`Strappy heels` · `Stilettos` · `Pumps` · `Wedges` · `Ankle boots` · `Knee-high boots`

`Thigh-high boots` · `Combat boots` · `Platform heels` · `Heeled boots` · `Strappy sandals` · `Gladiator sandals`

`Mules` · `Slides` · `Ballet flats` · `Cowboy boots` · `Pointed-toe heels` · `Clear heels`

`Lace-up heels` · `Thigh-high heeled boots` · `Barefoot`

## Edit types (10)

`add element` · `remove element` · `replace element` · `change style` · `change environment` · `change outfit`

`change hair` · `change makeup` · `add effect` · `custom`

## AI-tells checklist (inspection)

Run this over the returned pixels before accepting a generation. Each tell names where its fix
lives. Grouped by what the eye catches first.

| Tell | What it means | Fix lives in |
|---|---|---|
| Waxy, airbrushed skin with no pores | beauty prior smoothing | `failure-modes.md` §7 |
| Round orange blush patches, over-saturated pink-orange glow | beauty prior coloring | §7 positive texture + flush language |
| Glassy doll-like eyes, oversized catchlights | render-default eyes | §7 (`small natural catchlights`) |
| Mirror-symmetric facial features | model default symmetry | §7 asymmetry lever; `identity-lock` |
| Dreamy bloom haze, over-bright rim light | aesthetic pull toward glamour | §7 light row; cut `cinematic` |
| Every plane separately lit | studio lighting invented for a candid scene | shooting logic: available light only |
| Creamy large-aperture bokeh on a phone premise | device logic ignored | `SKILL.md` device-plus-shooting-logic |
| Floating objects, missing contact shadows | physics evidence absent | state contact: `pressing the cloth slightly, casting soft contact shadows` |
| Hair or fabric ends curling up against gravity | stylized rendering of draped elements | gravity language: `hangs straight down obeying gravity, one continuous flow` |
| Perfect timing, centered subject, level horizon | composed-by-default frame | shooting logic; `visual-brief` locks |
| No residual white-balance difference under mixed light | auto-white-balance erased too much | `residual color-temperature difference` between sources |
| Whole frame slightly brighter/cleaner after an edit | repair creep | `failure-modes.md` §8 |
| Same type, different individual across a series | text-only identity anchor | `skills/identity-lock` |

The checklist is a prompt audit in reverse: every tell corresponds to a missing or discounted
field, so a tell tells you which field to fix — one per iteration.

Vocabulary sources for the skin and face rows: practitioner skin-texture guides (2026) and
`beatra-ai/ai-image-realism-skill` (MIT-0).

## See also

- `references/era-grading.md` — era table and the five realism presets
- `references/failure-modes.md` — what these settings look like when they go wrong
