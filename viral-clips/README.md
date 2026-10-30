# AI Viral Clip Generator

**Paste a long video → the engine reads all of it → it finds the moments worth posting → it cuts captioned
vertical clips → you download them.**

A working full-stack product, not a mockup: FastAPI + Next.js + FFmpeg/OpenCV pipeline, with a real
end-to-end test that uploads a video, analyzes it, renders a 1080×1920 clip and streams it back.

```
apps/api   FastAPI service, job runner, media engine, moment scoring
apps/web   Next.js 15 dashboard (9 screens, dark premium UI)
docs       resource discovery, architecture, API, dependencies, security, cost, deployment, verification
supabase   production schema (RLS, triggers, indexes)
scripts    sample video generator, transcript fixture, demo seeder
```

---

## Quick start

```bash
cd viral-clips
cp .env.example .env          # offline-friendly defaults
make setup                    # venv + pip + npm install
make sample                   # 75s test video
make api                      # :8000  (docs at /api/docs)
make web                      # :3000  ← open this
make seed                     # optional: demo account + processed project
```

Demo login after `make seed`: **`demo@viralclips.example` / `demo-password-123`**

**Just want to click around?** Set `DEMO_MODE=1` in `apps/web/.env.local` and the login wall disappears.
Preview frames are cross-site, so browsers drop third-party cookies and a redirect-based auto-login loops
forever; instead the server keeps one short-lived demo token (`lib/demo.ts`), Server Components use it
directly and `middleware.ts` attaches it to `/api/*` and `/media/*` requests. Unset it (the default) for
normal cookie auth — production never sees this path.

No API keys are required to run the whole flow. Without them the engine tells you so and falls back to
deterministic acoustic + visual analysis with the local heuristic scorer (no captions, since captions need
a transcript). Add keys in `.env` to switch on the full AI pipeline — no code changes:

```env
LLM_PROVIDER=openai      LLM_API_KEY=sk-...        LLM_MODEL_FAST=gpt-4o-mini   LLM_MODEL_DEEP=gpt-4o
ASR_PROVIDER=groq        ASR_API_KEY=gsk_...       ASR_MODEL=whisper-large-v3-turbo
```

---

## What it actually does

1. **Ingest** — upload MP4/MOV/WEBM/MKV (validated by extension, MIME **and** magic bytes, size-capped by
   plan), or import a direct media URL with an explicit rights attestation. YouTube ingest exists but ships
   **disabled** (`ENABLE_YOUTUBE_INGEST`).
2. **Understand** — whole-timeline analysis: 16 kHz audio → RMS energy → adaptive speech regions; Whisper
   transcription with word timestamps (chunked for long files); FFmpeg scene-cut detection; frames sampled at
   0.5 fps for Haar face boxes + motion + brightness.
3. **Find moments** — sentence-snapped candidate windows in three length variants (never cutting a sentence
   in half), scored 0–100 across nine signals: hook strength, curiosity, emotional impact, story
   completeness, shareability, engagement, information value, context independence, visual engagement.
   Heuristics always run; an LLM rubric (OpenAI/Groq/Anthropic/Gemini/Ollama) re-scores and writes
   titles/hooks, blended 65/35. Every score carries a breakdown and a written explanation — and no
   virality promises anywhere.
4. **Cut** — 1080×1920 H.264/AAC, loudness-normalised (−14 LUFS), `+faststart`, smart 9:16 crop from the
   face/motion plan (with a manual crop slider and a blurred-fit mode for slides/screen recordings).
5. **Caption** — libass/ASS engine with six presets (Modern Podcast, Bold Viral, Minimal Clean, Cinematic,
   Highlighted Keywords, Professional Educational), per-word karaoke highlight, keyword accents, and a full
   editor that writes back to the MP4 on re-render.
6. **Deliver** — per-clip downloads, ZIP bundle with a manifest, HTTP Range streaming for the player.

## Screens

`/login` · `/dashboard` (stats, live jobs, recent projects) · `/projects/new` (drag-drop upload or URL,
analysis settings) · `/projects/{id}/analysis` (stage-by-stage progress, transcript/audio/visual report,
engine warnings) · `/projects/{id}/clips` (ranked clip library with scores and render/download) ·
`/clips/{id}/editor` (9:16 crop preview, framing mode, preset, score breakdown, save & render) ·
`/clips/{id}/subtitles` (cue editor: timings, text, add/delete, burn in) · `/export` (ZIP + individual
files) · `/history` (projects + job log) · `/settings` (plan, usage, AI spend, provider status).

Every control is wired to the API — there are no decorative buttons.

## Architecture in one screen

```
Next.js RSC ──(/api,/media rewritten)──► FastAPI ──► JobQueue (inline | RQ/Redis)
                                            │            └──► Worker: FFmpeg · OpenCV · numpy
                                            ├──► Postgres (dev: SQLite) 
                                            ├──► R2 / local disk
                                            └──► LLM + ASR providers (server-side keys only)
```

Rendering is deliberately **not** serverless: a clip needs tens of seconds of continuous CPU. Full detail
and trade-offs: [`docs/02-architecture.md`](docs/02-architecture.md).

## Documentation

| Doc | Contents |
|---|---|
| [`docs/01-resource-discovery.md`](docs/01-resource-discovery.md) | GitHub audit of the account, external OSS evaluated (stars/licence/maintenance) and what was accepted or rejected, skills used, MCP/integration state, integration risks |
| [`docs/02-architecture.md`](docs/02-architecture.md) | Pipeline stages, render command, data model, provider abstraction, decisions & trade-offs, non-goals |
| [`docs/03-api.md`](docs/03-api.md) | Every endpoint, payloads, examples, rate limits |
| [`docs/04-dependencies.md`](docs/04-dependencies.md) | Dependency + licence inventory, vendored assets, **GPL FFmpeg warning** |
| [`docs/05-security-audit.md`](docs/05-security-audit.md) | Controls implemented, accepted risks, prioritised gaps (SSRF, secrets, scanning) |
| [`docs/06-cost-model.md`](docs/06-cost-model.md) | Per-video unit economics, infra cost, plan margins, spend controls |
| [`docs/07-deployment.md`](docs/07-deployment.md) | Local run, production topology (Supabase + R2 + RQ workers), CI sketch, launch checklist |
| [`docs/08-verification.md`](docs/08-verification.md) | What was actually tested, measured timings, and the honest gaps |

## Testing

```bash
make test    # 69 API tests: auth, tenant isolation, upload validation, full analyze→render→export,
             # caption rendering (pixel-checked), face tracking on a real portrait, crop maths
make e2e     # Playwright flow (needs `npx playwright install chromium` first)
```

The pipeline test is the important one: it uploads a real video, waits for the analysis job, asserts clip
bounds/scores/breakdowns, renders a clip, probes the downloaded MP4 for **1080×1920 / h264 / audio**, checks
Range requests, then unzips the export bundle.

## Security posture (summary)

scrypt password hashing · HS256 JWT in an **HttpOnly** cookie · server-side ownership checks on every
resource (404 for other tenants, tested) · magic-byte upload validation + size caps · path-traversal-guarded
storage keys · argv-only FFmpeg with timeouts · rate limits on auth/upload/analyze · plan quotas enforced
server-side · per-call AI cost accounting · secrets never reach the browser bundle. Open gaps with fixes are
listed in the audit.

## Honest limitations

* **No live AI provider was called in this build's verification** (no keys in the sandbox): LLM scoring and
  real Whisper transcription are wired and unit-covered, but their output quality is unverified. The
  fallback path *is* verified.
* Face tracking is verified on a still portrait; two-speaker dynamic framing is the next quality step
  (MediaPipe/pyannote diarization).
* Postgres/Redis/R2 paths are implemented and documented but were exercised against SQLite/local disk here.
* YouTube ingestion is disabled by default for rights/ToS reasons — uploads are the supported route.
* Billing is **not** activated: plans, quotas and metering exist; payment is left as an integration point.

## Third-party notes

All application dependencies are MIT/BSD/Apache-2.0. The bundled FFmpeg static build is **GPL** (libx264) —
fine to run server-side, but read `docs/04-dependencies.md` before redistributing the binary. The vendored
Haar cascade is Apache-2.0 (OpenCV), attributed in `apps/api/vendor/models/README.md`.
