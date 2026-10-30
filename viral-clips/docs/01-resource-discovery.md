# Phase 1 — GitHub Intelligence & Resource Discovery

Audit date: 2026-10-30 · Account: `maskchanel14-source` · Tooling: GitHub API via `gh`, local skill router
(`python3 tools/skill_router.py plan "…"`), filesystem inspection of this checkout.

This report is the input to every later phase. It records **what exists**, **what was reused**, **what was
evaluated and rejected**, and **why**. Nothing here claims an integration that is not in the code.

---

## 1.1 Repositories in the account (15 public)

| Repository | Lang | What it actually contains | Verdict for this project |
|---|---|---|---|
| `agents` (this repo) | Python | Multi-harness agent marketplace: 95 plugins, 202 agents, 187 skills, 107 commands, `skills-lock.json`, `tools/skill_router.py`, quality gates (`make validate/garden/test/smoke-test`) | **Primary reuse.** Skills and workflow conventions used throughout (see §1.3) |
| `ui-ux` | JS | `.agents/skills/awesome-design-md` — per-brand DESIGN.md specs (linear/vercel/raycast/stripe/supabase/notion/…) | **Reused as design input**: dark-interface tokens, spacing/typography discipline for the dashboard |
| `po-pilot-mcp` | TS | Production-shaped MCP server (Shopify replenishment, Open-to-Buy, 3-way invoice match) | **Pattern reuse**: typed config + transport-agnostic service layer; no code copied |
| `obra` | Shell | Agentic skills framework / development methodology | Read for workflow conventions (inspect → plan → verify) |
| `affan` | JS | Agent-harness optimisation system (skills, instincts, memory, security) | Read for verification habits; not imported |
| `banana`, `GenClaw`, `RealGen`, `Rational`, `gradient`, `image-to-prompt`, `image-gen` | Python | Image-generation skills, diffusion-RL research, AI-image-detection research | **Not applicable** to long→short video clipping; no dependency taken |
| `small-signal-site`, `-https-maskchanel14-source.github.io`, `foto` | HTML | Static site/photo scratch repos | Not applicable |

**Finding:** the account contains no video-processing, FFmpeg, Whisper, face-tracking, subtitle or
job-queue implementation. Those had to be built (or sourced externally), which is why the engine in
`apps/api/app/services/media` and `…/moments` exists as first-party code rather than a wrapped library.

## 1.2 External open-source candidates (evaluated, not star-ranked)

Live GitHub search (`gh api search/repositories`, 2026-10-30). "Used" means code/config in this repo.

| Project | Stars | License | Last push | Role | Decision |
|---|---:|---|---|---|---|
| `SYSTRAN/faster-whisper` | 26.3k | MIT | 2026-10-25 | Local CTranslate2 Whisper, word timestamps | **Used (optional provider)** — `app/services/asr/base.py::FasterWhisperASR`. Not installed by default: model download needs network + ≥1 GB RAM |
| `m-bain/whisperX` | 24.9k | BSD-2 | 2026-10-22 | Word-level timestamps + diarization (pyannote) | **Rejected as a dependency** — torch + pyannote weights are too heavy for a 2 vCPU/3 GB worker; documented as the upgrade path for speaker labels |
| `yt-dlp/yt-dlp` | 204k | Unlicense | 2026-10-29 | Optional URL ingest | **Used behind an operator flag** (`ENABLE_YOUTUBE_INGEST`), off by default; uploads are the primary route |
| `google-ai-edge/mediapipe` | 37.5k | Apache-2.0 | 2026-10-30 | Face/pose detection | **Rejected here** — wheel imports fail without `libGL` in this sandbox; replaced by OpenCV Haar |
| `opencv/opencv` | — | Apache-2.0 | — | Frame decode, face detection | **Used**: `opencv-python-headless` + vendored `haarcascade_frontalface_default.xml` (930 KB, Apache-2.0, attributed in `apps/api/vendor/models/`) |
| `NaufalRizqullah/opensource-clipping` | 202 | MIT | 2026-09-26 | Opus-Clip-style pipeline | **Reviewed only** — young codebase, no tests, tightly coupled to one UI; ideas (score-then-cut) re-implemented cleanly |
| `kleZ799/clipmint` | 25 | MIT | 2026-10-05 | Open-source clipper | Reviewed; smaller surface than needed, no job durability |
| `Corzed/AutoMediaV2` | 32 | Apache-2.0 | 2024-08-01 | Clip + auto-upload | Reviewed; stale dependencies (2024), upload-to-platform automation out of scope |
| `Anil-matcha/ai-clipping-comfyui` | 33 | MIT | 2026-07-21 | ComfyUI nodes | Rejected — node-graph runtime, wrong shape for an API product |
| `bottk123-ctrl/TikTok-Movie-Cutter` | 1 | MIT | 2026-10-30 | Vertical clips + TTS | Too small/unmaintained to audit-test |
| `abishek-singh/auto-editor`-class silence tools | — | MIT | — | Silence detection | Rejected as dependency: FFmpeg `silencedetect` + in-process RMS analysis is enough and avoids another binary |

Selection criteria actually applied: license compatibility (no AGPL/GPL in our import graph), test surface,
maintenance recency, dependency weight vs the 2 vCPU/3 GB worker, and whether the capability could be
implemented in <200 audited lines. Stars were only a tie-breaker.

## 1.3 Skills used (from this repo, per `tools/skill_router.py`)

The router was run first; it returned capability-level guidance plus domain matches
(`e2e-testing-patterns`, `python-testing-patterns`, `temporal-python-testing`). Manual `search` for
`video`/`ffmpeg` returned only `file-conversion` — confirming a domain gap for media work, which is why
the FFmpeg layer is bespoke and heavily tested.

| Skill (`plugins/*/skills/*/SKILL.md`) | Applied to |
|---|---|
| `frontend-mobile-development/nextjs-app-router-patterns` | App Router layout, Server Components for data, streaming/loading boundaries, route conventions |
| `api-scaffolding/fastapi-templates` | `app/api/routes`, `app/core`, `app/services` layering, dependency injection |
| `database-design/postgresql-table-design` | Types (`timestamptz`, `numeric` for money), FK indexes, CHECK constraints, JSONB only for optional payloads |
| `python-development/python-background-jobs` | API returns a job id; workers own the long work; idempotent re-runs |
| `python-development/python-resilience` / `python-error-handling` | Retries with jittered backoff, per-clip failure isolation |
| `developer-essentials/auth-implementation-patterns` | scrypt hashing, short-lived JWT + HttpOnly cookie, explicit ownership checks |
| `developer-essentials/e2e-testing-patterns` | Playwright serial flow spec |
| `python-development/python-testing-patterns` | pytest fixtures: session-scoped sample video, isolation tests |
| `security-scanning/stride-analysis-patterns`, `threat-mitigation-mapping` | `docs/05-security-audit.md` structure |
| `ui-design/visual-design-foundations`, `design-system-patterns` | Dark token set, 4/8 spacing, type scale, focus states |
| `file-conversion/file-conversion` | Verified local-only conversion discipline: no uploads to conversion services, inspect real format (magic bytes), preserve originals |
| `payment-processing/stripe-integration`, `pci-compliance` | Billing integration points and the decision **not** to store card data |
| `llm-application-dev/prompt-engineering-patterns` | Strict-JSON rubric prompt with calibration anchors |

Not used on purpose: `rag-implementation`, `vector-index-tuning`, `embedding-strategies` (no retrieval
problem), `langchain-architecture` (provider abstraction is thinner and more auditable).

## 1.4 MCP servers & plugins — what is actually available here

Verified state in this environment (not aspirational):

| Integration | State | How it was used |
|---|---|---|
| GitHub via `gh` CLI (token authenticated as `maskchanel14-source`) | **Available** | Repo audit, code search, fetching the Haar cascade, this report |
| Supabase connector | **Enabled** (`list_connector_tools` → 40 tools incl. `execute_query`, `create_migration`, `list_projects`) | **Not used to create cloud resources** — that is paid/shared infrastructure and needs your approval. `supabase/migrations/0001_init.sql` is ready to apply |
| Vercel / Notion / Linear / Gmail / Google Drive / Dropbox connectors | Enabled per session | Not required by this build |
| Filesystem / shell | Available | All builds, tests, renders |
| Playwright | Installed as a dev dependency (`@playwright/test`) | Spec written; browsers are not pre-installed in this sandbox (`npx playwright install` required) |
| Context7 / docs-retrieval MCP | **Not available** | Vendor docs read directly (`openai`-compatible API shape, FFmpeg filter docs) |
| Redis | **Not installed** in this sandbox | Queue interface ships both drivers; `inline` is the default, `rq` is production |

## 1.5 Integration risks found

1. **FFmpeg build licensing.** `imageio-ffmpeg` ships a *GPL* static build (johnvansickle) including
   `libx264`. Fine for internal/SaaS use, but if you ship the binary to customers you inherit GPL
   obligations. Mitigation documented in `04-dependencies.md` (use an LGPL build + `libopenh264`).
2. **No `drawtext`/freetype** in that build — on-screen text must go through libass (our subtitle engine
   does exactly that, so this costs nothing).
3. **No local ASR model available offline** (HuggingFace/OpenAI model hosts are blocked in this sandbox).
   The pipeline therefore degrades honestly: acoustic+visual analysis with `provider="none"`, and a
   clearly labelled `fixture` provider for demos/tests.
4. **mediapipe unusable** (libGL) → Haar cascade chosen; swap-in point is one function.
5. **Long videos on small boxes** — a 60-min 1080p file needs ~2 GB RSS during scene/sample passes;
   production must run workers on ≥4 GB.
