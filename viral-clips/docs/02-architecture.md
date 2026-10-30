# Phase 2 — Architecture

## 2.1 Shape of the system

```
                 ┌──────────────────────────────────────────┐
  Browser  ────► │ Next.js 15 (App Router, RSC)   :3000     │
  (same origin)  │  • dashboard, project, editor, export UI │
                 │  • /api/*  and /media/*  rewritten to API│
                 └───────────────┬──────────────────────────┘
                                 │ internal HTTP (cookie forwarded)
                 ┌───────────────▼──────────────────────────┐
                 │ FastAPI                         :8000     │
                 │  auth · projects · clips · jobs · media  │
                 │  ├── JobQueue  inline | RQ(Redis)        │
                 │  ├── Storage   local | Cloudflare R2     │
                 │  ├── LLM       openai|groq|anthropic|…   │
                 │  └── ASR       openai|groq|faster-whisper│
                 └───────────────┬──────────────────────────┘
                                 │
        ┌────────────────────────┼───────────────────────────┐
        ▼                        ▼                           ▼
  Worker (same code,     SQLite dev /              Local disk dev /
  separate process)      Supabase Postgres        Cloudflare R2 prod
        │
        ├── FFmpeg 7 (decode, crop, scale, libass, loudnorm, encode)
        ├── OpenCV  (frame sampling, Haar face boxes, motion)
        └── numpy   (RMS energy, speech regions)
```

Four deployables: **web**, **api**, **worker**, **(redis)**, plus **postgres** and **object storage**.
Why split? Rendering is CPU-bound and long (minutes); putting it in the API process would starve request
handling. `QUEUE_BACKEND=inline` keeps a single-process demo possible without lying about the production
shape.

## 2.2 Analysis pipeline (Phase 3–4)

Every stage writes progress (0–100) to `jobs`/`projects` so the UI can stream state.

1. **Probe** (`media/probe.py`) — no `ffprobe` dependency: parse the `ffmpeg -i` banner for duration,
   codecs, dimensions, fps, rotation.
2. **Audio extraction** → 16 kHz mono PCM WAV.
3. **Acoustics** (`media/audio.py`) — RMS per 250 ms hop → adaptive-threshold speech regions, dynamic
   range (a proxy for vocal energy).
4. **Transcription** (`asr/`) — provider chosen by config; long audio is chunked at 10 min with timestamp
   offsets. Word-level timestamps when the provider supports them; otherwise sentence timings are
   distributed proportionally (flagged in the transcript's `provider`).
5. **Scene cuts** (`media/scenes.py`) — FFmpeg `select='gt(scene,0.32)'` + `showinfo`, single low-res pass.
6. **Visual intelligence** (`media/faces.py`) — frames sampled at 0.5 fps (capped 900), per-frame Haar
   face boxes, motion (frame-difference), brightness. **No thousands of redundant frames**, and no frames
   sent to a paid API by default (`VISION_ENABLED=false`).
7. **Candidate windows** (`moments/candidates.py`) — transcript mode: three length variants snapped to
   sentence boundaries; energy mode: sliding windows inside merged conversation blocks. Both cover the
   **whole timeline**, never just the opening minutes.
8. **Scoring** (`moments/scoring.py`) — nine dimensions (hook, curiosity, emotion, story completeness,
   shareability, engagement, information value, context independence, visual engagement).
   - deterministic heuristic model from measured features (always runs)
   - optional LLM rubric (`SYSTEM_PROMPT` with calibration anchors, strict JSON), blended 65/35
   - per-clip explanation + `keeps_meaning` penalty; no virality promises anywhere
9. **Selection** — score-ranked, overlap-capped and density-limited; `allow_overlap` is opt-in.
10. **Persistence + thumbnails** — clips, score breakdown, caption cues (relative to clip start), computed
    crop centre, storage keys.

## 2.3 Render pipeline (Phase 5–6)

For each clip: compute the 9:16 window from the crop plan → build ASS from words in range → one FFmpeg
process:

```
-ss <start> -t <dur> -i source
filter_complex:
  [0:v]crop=W:H:X:Y,scale=1080:1920:flags=lanczos,setsar=1,fps=30,ass=clip.ass[vout]
  [0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a1]  (+ optional bgm amix)
-c:v libx264 -crf 20 -profile:v high -pix_fmt yuv420p -c:a aac 160k -movflags +faststart
```

`fit_mode=blur` swaps the crop chain for `split → blurred background + contained foreground → overlay`.
Caption rendering is pure Python (`media/ass.py`): chunking, karaoke highlight per word, keyword accent,
six presets, timing clamped so cues never overlap. One bad clip cannot fail the batch (per-clip try/except
with `render_error`).

## 2.4 Data model

`users → projects → {transcripts, clips, jobs}`, plus `ai_usage` for cost accounting. JSON columns are
used only for genuinely optional/semi-structured payloads (analysis report, score breakdown, cues, words).
Canonical DDL: `supabase/migrations/0001_init.sql` (RLS + triggers + indexes). The ORM uses portable text
UUIDs so the same code runs on SQLite (dev) and Postgres (prod).

## 2.5 Provider abstraction (Phase 9)

* `LLMProvider` (`services/ai`): `openai-compatible` covers OpenAI/Groq/Together/Ollama/Gemini-OAI;
  `anthropic` has its own adapter. Retries (3, jittered), timeouts, `ai_usage` rows with token and USD cost.
* `ASREngine` (`services/asr`): `openai`-compatible chunked Whisper, `faster_whisper` (local),
  `fixture` (labelled demo/test only), `none` (graceful degradation).
* Registry returns `None` when unconfigured — the pipeline falls back to the heuristic scorer instead of
  raising, and the UI shows *why*.

**Cost control:** `llm_model_fast` for batch scoring, `llm_model_deep` for the final pass (configurable);
per-plan clip caps, per-plan upload/minute caps, per-route rate limits, and `ai_usage` visible in Settings.

## 2.6 Frontend architecture

* Server Components fetch through `lib/api.ts` (token from cookie → Bearer to the internal API); browser
  code calls relative `/api/*`, rewritten by Next. Same origin ⇒ no CORS, cookie stays HttpOnly.
* Client islands only where interaction lives: upload form (XHR progress), job poller, clip editor,
  subtitle editor, render buttons.
* Design system in `components/ui.tsx` + Tailwind tokens (ink/mist palette, gradient accent, score ring,
  progress, badges) with `prefers-reduced-motion`-safe CSS animations.

## 2.7 Decisions & trade-offs

| Decision | Alternative | Why |
|---|---|---|
| Own FFmpeg wrapper | `moviepy` / `ffmpeg-python` | Explicit argv, no shell, timeouts, progress parsing, auditable escaping |
| RMS-based speech regions | webrtcvad / Silero | Zero extra model download, deterministic, good enough for boundaries |
| Haar cascade faces | mediapipe / YOLO | Works offline, 930 KB, headless-safe; swap point is `_cascade()` |
| HAAR + motion fallback | face-only | Screen recordings, animation and slides still need a sane crop |
| Sentence-snapped windows | fixed-grid cuts | Preserves the speaker's meaning (hard product requirement) |
| SQLite dev / Postgres prod | Postgres-only | One-command local run **and** a real Supabase schema |
| Inline queue default | Redis-only | Demo runs with zero infra; RQ path is one env var |
| `.ass` subtitles | drawtext | The shipped FFmpeg has no freetype; libass gives styling + karaoke |

## 2.8 Out of scope (deliberately)

Auto-posting to TikTok/IG (platform ToS + review), guaranteed-virality prediction, multi-track music
licensing, GPU diarization, and billing activation (integration points only).
