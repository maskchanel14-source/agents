# PO Pilot promo — HyperFrames composition

A 24-second, 1920×1080 promo built with [`hyperframes`](https://github.com/heygen-com/hyperframes)
(HTML + GSAP → MP4). Four scenes:

| Scene | Time | Content |
|---|---|---|
| `s1` | 0–6s | “Stocky is gone. Your supplier rules don't have to be.” |
| `s2` | 6–12s | The three gaps: no supplier export, POs as filing cabinet, no invoice audit |
| `s3` | 12–18s | Terminal: `npx -y po-pilot-mcp@1.0.0` → draft PO CSV + 3-way match |
| `s4` | 18–24s | PO Pilot · $49 one-time · po-pilot-henna.vercel.app |

## Status: authored and validated, not rendered

`hyperframes lint` passes with **0 errors, 0 warnings** on all five files. Rendering is the one step that
cannot run in this workspace:

- HyperFrames renders by driving headless Chrome with Puppeteer.
- Chrome is not installed here and its download host is not reachable from the sandbox.
- A Chromium binary extracted from npm (199 MB) starts but needs `libnspr4`, `libnss3`, `libnssutil3`,
  which are not on the image and cannot be installed (no root, no apt).
- FFmpeg is fine and works (installed from npm), so encoding is not the blocker.

## Render it (on a machine with Chrome — your laptop)

Prerequisites: Node 18+ and a normal Chrome/Chromium install.

```bash
cd po-pilot-launch/video

npm run lint          # static check, no browser needed
npm run render:draft  # fast pass, low quality — use this to check timing
npm run render        # final, CRF 16

# output lands in renders/ as po-pilot-promo_<date>_<time>.mp4
```

If Chrome lives somewhere unusual:

```bash
export HYPERFRAMES_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS
export HYPERFRAMES_BROWSER_PATH="/usr/bin/google-chrome"                                        # Linux
```

Preview while editing: `npm run dev` (opens the HyperFrames studio).

## Editing

- Copy lives in `compositions/s1.html … s4.html` — plain HTML, one scene per file.
- Scene timing is set twice on purpose: `data-start` / `data-duration` on the host divs in `index.html`,
  and the GSAP timeline offsets inside each scene file.
- Colours are inline per scene (the palette matches the landing page: `#0a0c10` ground, `#4ade80` accent,
  `#22d3ee` links, `#f87171` warnings).
- Fonts resolve from the system: `Sans` (Inter / SF Pro / Segoe UI) and `Mono` (SF Mono / Menlo / Consolas)
  are declared with `src: local(...)`, so no font files are shipped. Rendered on a Linux box without any of
  those, text falls back to DejaVu — install Inter + a mono face, or add `@font-face` with `.woff2` files,
  if the typography matters.
- Keep `fromTo` (not `from`) in scene timelines: the host re-seeks each scene on every show.

## Using the output

- Landing page: drop the MP4 on Vercel (Static) and embed with `<video>` — or just upload to YouTube and
  embed. Keep the file under ~10 MB by rendering at `--quality looks` and trimming to 20s.
- Social: same file works for X/LinkedIn (16:9). For Shorts/Reels you'd want 1080×1920 — change
  `data-width`/`data-height` on `#root` and all four hosts, and re-check the layouts.
