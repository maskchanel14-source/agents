# Verification log — what was actually run

Environment: 2 vCPU / 3 GB RAM Linux sandbox, Python 3.11.2, Node 22.22.3,
FFmpeg 7.0.2 static (`imageio-ffmpeg`), OpenCV 4.10.0 headless, no GPU, **no LLM/ASR API keys**.

## Automated tests — 69 passing

```bash
cd apps/api && ../../.venv/bin/python -m pytest tests/ -q
# 69 passed
```

| File | Covers |
|---|---|
| `test_auth.py` | scrypt salting/verification, duplicate email, generic 401, HttpOnly cookie, forged-token rejection, short-password rejection |
| `test_isolation.py` | other tenants get 404 on project/clip/render/delete/media; unauthenticated media is 401 |
| `test_upload_validation.py` | wrong extension → 415, fake container → 415, rights attestation required, YouTube ingest disabled by default, non-HTTP scheme rejected |
| `test_pipeline.py` | **full cycle**: upload → analyze → scored clips (bounds, breakdown, explanation, no-overlap) → single-clip render → 1080×1920 H.264/AAC verified by probing the downloaded file → HTTP Range 206 (first + suffix) → ZIP export with `manifest.json` → clip edits + validation + preset gating |
| `test_moments.py` | candidates cover the full timeline (a 60-min timeline's last window starts > 10 min), no-transcript mode, length variants, deterministic scoring, 0–100 bounds, selection cap/order/no-overlap, "no virality guarantee" wording |
| `test_ass_subtitles.py` | cue grouping + pause splitting, non-overlap clamping, ASS structure, keyword accent colour, uppercase preset, brace escaping, all six presets, bilingual stopword filtering, timestamp rebasing |
| `test_media_utils.py` | crop-window maths for 16:9 / 9:16 / tall sources, clamping, face vs motion vs centre planning, storage traversal guard, size cap, ASR/LLM selection with missing credentials, cost maths |
| `test_face_tracking.py` | vendored cascade loads, **a real portrait is detected**, the resulting crop window keeps the face inside a 9:16 frame |
| `test_fixture_asr_captions.py` | `ASR_PROVIDER=fixture` → transcript with words → caption cues → ASS contains spoken words → render → **pixel check**: >400 near-white pixels in the lower band of a 1080×1920 frame |

## Manual / live verification

| Check | Result |
|---|---|
| API boot, `GET /api/health` | `{"status":"ok","database":"sqlite","ffmpeg":true}` |
| Register → cookie → dashboard through the Next proxy | 200, session survives page loads |
| 4-minute 1280×720 sample: full analysis | 3 clips, ~12 s wall clock, warnings `[]`, visuals available |
| Render 3 clips (30–40 s each) | ~38 s total, files 1.4–1.9 MB, 1080×1920 |
| Burned-in captions | decoded a frame from a rendered clip: uppercase bold viral captions with the active word highlighted in yellow (see below) |
| Media streaming through the proxy | `Range: bytes=0-1023` → 206 + `Content-Range`, `video/mp4` |
| Zip export | downloads, contains MP4s + `manifest.json`, `testzip()` clean |
| Face detector on real imagery | 1 face at x≈0.47–0.48 on `/home/user/agents/IMG-20260615-WA0002(8).jpg`, stable across 3 cascade settings |
| UI pages | `/login`, `/dashboard`, `/projects/new`, `/projects/{id}/analysis`, `/projects/{id}/clips`, `/clips/{id}/editor`, `/clips/{id}/subtitles`, `/export`, `/history`, `/settings` all render 200 with real data |
| Production build | `npm run build` (see the build log in the repo history) |

## Honest gaps — not verified here

1. **Live LLM scoring.** No `LLM_API_KEY` in this sandbox, so the LLM branch of `score_candidates` was
   exercised only through its error path (falls back to heuristics, warning recorded). The prompt, JSON
   parsing and blending are unit-testable but the *quality* of LLM ranking is unverified.
2. **Live ASR.** Same reason: OpenAI/Groq Whisper endpoints were not called. Provider plumbing, chunking
   maths and normalisation are covered by code + fixture tests, not by a real API response.
3. **Real podcast material.** All renders came from a generated 1280×720 sample. Face-cropping is verified
   on a still portrait, not on a moving two-speaker video (no such source was available offline).
4. **Long-tail formats.** 4K sources, VFR phone footage, MKV with multiple audio tracks and rotation
   metadata are handled in code but not load-tested.
5. **Playwright suite.** Written (`apps/web/e2e/flow.spec.ts`) but not executed: Chromium is not installed
   in this sandbox (`npx playwright install chromium` then `make e2e`).
6. **Postgres path.** Everything ran on SQLite. The SQLAlchemy models are portable and
   `supabase/migrations/0001_init.sql` mirrors them, but the Postgres/asyncpg path needs a smoke test on
   real infrastructure.
7. **Billing.** Integration points only. No Stripe keys, no live charges — by design.
