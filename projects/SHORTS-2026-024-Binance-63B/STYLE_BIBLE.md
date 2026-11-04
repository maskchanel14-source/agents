# STYLE BIBLE — viral animated shorts

Source: the style numbers supplied with the brief (measured from 20 shorts at
30 fps) plus everything this repo had to change to make those numbers actually
render. Every value below is the one the code uses, not an aspiration.

> **PHASE 0 could not be run as written.** Extracting 60 frames from each of the
> 20 latest shorts on the reference channel needs YouTube access, and this
> sandbox can only reach npm, PyPI and GitHub. `references/frames/` therefore
> ships a README with the exact commands to populate it on a machine that has
> network access, and the 7 QA agents below are driven by numbers measured
> straight off our own renders (`scripts/analyze_frame.py`) instead of by
> side-by-side comparison against channel frames. Everything else in the
> workflow ran end to end.

---

## 1. Script formula

| Rule | Target | This short |
| --- | --- | --- |
| Total length | 130–150 words / 55–70 s | **138 words, 67.00 s** |
| Hook | line 1, one sentence, 8–12 words | *"In twenty minutes, $6.3 billion walked out of Binance."* — **9 words** |
| Beat 1 (0–15 s) | setup who/where | 29 Oct 2026 · 20:05 UTC |
| Beat 2 (15–40 s) | escalation, 2 facts | ten blockchains; 18,270 BTC unfreezable; $3B frozen |
| Beat 3 (40–60 s) | twist | the door was a fake job interview, not a broken vault |
| Payoff (60–67 s) | answers hook, loopable | Binance paid it back; FBI → TraderTraitor |

Loop: the last shot is a pull-back to the same framing as shot 1, with the coins
marching back *into* the vault, so the replay reads as continuous.

## 2. Visual formula

### Palette — 6 colours, enforced in `src/theme.ts`

| Hex | Name | Used for |
| --- | --- | --- |
| `#FFD23F` | sun | the money, the vault, the lit window, key light |
| `#FF6B6B` | pop | character pop, danger, the Bitcoin lane |
| `#4ECDC4` | sky | sky, ice (frozen funds), bridge rails |
| `#1A535C` | town | painted town masses, ground |
| `#F7FFF7` | paper | plaza, clock face, bridge decks, captions |
| `#2A2E6B` | shadow | **shadows and ink — pure `#000000` is banned** |

### Characters
- 2D planes (billboards) living in the 3D world — `src/characters.tsx`.
- One procedural canvas atlas: 9 poses × 3 characters, 256×512 per tile.
- Eye diameter = 12 % of head diameter (`eyeR = headR * 0.12`).
- Limbs are simple rounded rects; every shape is stroked then filled so each
  carries its own ink line.

### Ink — boiling outline
- Spec: `float jitter = sin(uTime*10.0 + position.x*5.0) * 0.008;`
- Implemented in the fragment shader, then **rescaled from UV into screen
  pixels** so the wobble is a real 0.3–0.8 px instead of ~2.4 px.
- Outline weight dilates from 2.5 px (far) to 4.0 px (near) by sampling the
  alpha neighbourhood, with the distance→px conversion derived from the plane's
  on-screen height.

### Camera — no hard cuts
- One `CatmullRomCurve3` threaded through all 9 shot waypoints (`src/camera.ts`);
  the camera never cuts in 2010 frames.
- Each leg is smoothstep-eased so the glide settles on a beat and then
  accelerates into the next one.
- `lerp 0.08` on the look-at, `orbit 2 °/s` on a 1.15-unit radius, `parallax 5 %`
  between the character planes and the town.
- Dolly rate is reported by `dollyUnitsPerSecond` and checked in `motion.md`.

### Lens blur
- Custom depth-of-field pass, `src/lens.tsx`: render → depth target → 16-tap
  golden-angle disc blur weighted by circle-of-confusion.
- `focusDistance 2.5` → focal plane 2.5 world units in front of the subject.
- `aperture 0.05` → 10 px background blur, 4 px foreground blur.

### Textures, lighting, grade
- Hand-painted canvas textures: 150 brush strokes + dry-brush grain per tile,
  `roughness 0.8`, `metalness 0.0`, AO baked at intensity 0.6.
- Warm key 1.05 (`#FFE3A8`) + cool fill 0.4 (`#8FD6FF`), ambient bounce, and a
  `#2A2E6B`-tinted ambient floor so shadows land on the palette shadow colour
  instead of crushing to black.
- Grade as a DOM layer: contrast +10, saturate 1.06, sepia 0.055 (warm +5),
  vignette 0.15 in `#2A2E6B`.

## 3. Audio formula

| Stem | Target | Delivered |
| --- | --- | --- |
| Music | march, 100 BPM, drums + brass, −18 dB | synthesised, RMS −18 dBFS |
| Voice | −14 LUFS, centred | **−14.8 LUFS** after `loudnorm` |
| SFX | 3–5 per short, −12 dB peak | **5** (riser, vault slam, coin pour, freeze, glitch, boom) |
| Ducking | music −6 dB under voice, 50 ms attack / 250 ms release | one-pole envelope, see `scripts/shorts024_audio.py` |

---

## 4. Deviations — and why

These are the places where the brief's literal instruction does not survive
contact with a real renderer. Each one is a fix, not a shortcut.

1. **`aoMap` silently deletes meshes.** Assigning an `aoMap` to a JSX geometry
   primitive (`<boxGeometry/>`) fails: three needs a second UV set (`uv1`) that
   the primitive never creates, and the mesh simply stops drawing — no error.
   The occlusion is baked into the albedo instead (which is what a painted
   texture looks like anyway) at the same 0.6 intensity.

2. **`@react-three/postprocessing`'s `<EffectComposer/>` renders nothing under
   a software GL stack.** Reproduced on a 3-box scene: with the composer
   mounted the frame is pure clear colour; without it the boxes draw. Since
   headless renders (and this sandbox) run on SwiftShader, the lens blur is a
   self-contained three.js pass (`src/lens.tsx`) that behaves identically on a
   real GPU. The dependency is still installed and the style bible still names
   the same numbers.

3. **`bokehScale` is in the DOF buffer's pixel space.** Passing the desired
   *output* blur (10 px) to a 480 px-tall bokeh buffer produced a 40 px blur at
   1920 px and dissolved the frame. `lensPxForAperture()` now divides the
   4× upscale back out.

4. **Linear vs sRGB.** The DOF pass renders into a linear target, so it owns the
   sRGB encode on the way out. Skipping it made every frame ~40 % too dark.

5. **`toneMapping` in R3F's `gl` prop is ignored** (it goes to the
   `WebGLRenderer` constructor). It is set on the renderer instance instead.

6. **GLSL integer literals.** `4 - 2.5` in a template-interpolated shader is
   `int - float` and fails to compile. All interpolated constants use
   `.toFixed(1)`.
