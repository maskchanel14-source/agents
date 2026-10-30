# API reference

Base URL: `http://127.0.0.1:8000` · interactive docs: `/api/docs` · OpenAPI: `/api/openapi.json`

Auth: `Authorization: Bearer <jwt>` **or** the `vc_token` HttpOnly cookie (set by login/register, and
forwarded by the Next.js rewrite so browser code never handles the token).

All errors use FastAPI's shape: `{"detail": "human readable message"}`.
Common status codes: `401` not authenticated · `402` plan/quota · `404` not found **or not yours** ·
`409` state conflict · `413` too large · `415` wrong file type · `422` validation · `429` rate limited.

## Auth

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/auth/register` | `{email, password(≥8), display_name?}` | 201 + token + cookie. Rate limit 5/min/IP |
| POST | `/api/auth/login` | `{email, password}` | Generic 401 message (no account enumeration). 10/min/IP |
| POST | `/api/auth/logout` | — | Clears the cookie |
| GET | `/api/auth/me` | — | Current profile |

Supabase tokens are accepted when `SUPABASE_JWT_SECRET` is set: the first call maps `sub`/`email` to a
local profile.

## Projects

| Method | Path | Notes |
|---|---|---|
| POST | `/api/projects/upload` | multipart `file` (+ `title`, `auto_analyze`) → 201 `Project` |
| POST | `/api/projects/from-url` | `{url, attests_rights, title?}` — rights attestation required |
| GET | `/api/projects?limit&offset&status` | newest first |
| GET | `/api/projects/{id}` | `ProjectOut` (includes `source_url_playable`, `clip_count`) |
| DELETE | `/api/projects/{id}` | 204, removes DB rows + stored media |
| POST | `/api/projects/{id}/analyze` | `AnalyzeRequest` → 202 `Job` |
| GET | `/api/projects/{id}/analysis` | media/audio/transcript/visual/scoring report + warnings |
| GET | `/api/projects/{id}/transcript` | 404 when ASR was unavailable |
| GET | `/api/projects/{id}/clips` | ranked `ClipOut[]` incl. `video_url`/`thumb_url` |
| POST | `/api/projects/{id}/render` | `{clip_ids?, preset?, fit_mode?}` → 202 `Job` |
| GET | `/api/projects/{id}/export` | ZIP (rendered MP4s + `manifest.json`) |

`AnalyzeRequest`:

```json
{ "target_clips": 5, "min_seconds": 15, "max_seconds": 60,
  "language": "id", "use_deep_model": true, "allow_overlap": false }
```

`target_clips` is clamped to the plan's `max_clips_per_video`.

## Clips & captions

| Method | Path | Notes |
|---|---|---|
| GET | `/api/clips/{id}` | `ClipOut` |
| PATCH | `/api/clips/{id}` | `{title?, hook?, start_s?, end_s?, crop_x?, fit_mode?, preset?, subtitle_json?}` |
| POST | `/api/clips/{id}/render` | re-render a single clip |
| GET | `/api/clips/{id}/subtitle-preview?preset=` | generated ASS text (debug styling) |
| DELETE | `/api/clips/{id}` | 204 + asset cleanup |

`subtitle_json` accepts `{"cues": [{"start": 0.0, "end": 1.6, "text": "Halo"}]}`; saving marks the clip
`edited: true` and reset to `suggested`, so a re-render burns the edited text.

## Jobs

| Method | Path | Notes |
|---|---|---|
| GET | `/api/jobs/{id}` | `JobOut` — poll this for progress (`stage`, `progress`, `error`) |
| GET | `/api/jobs?project_id=&limit=` | recent jobs |

## Usage, plans and system

| Method | Path | Notes |
|---|---|---|
| GET | `/api/usage` | plan limits, minutes used/remaining, clip + AI cost totals |
| GET | `/api/usage/ai-breakdown` | per provider/model/task calls, tokens, USD |
| GET | `/api/plans` | free / pro / business limits |
| GET | `/api/presets` | the six caption presets + tiers |
| GET | `/api/providers` | which providers are configured + capability warnings |
| GET | `/api/health` | liveness (db flavour, ffmpeg present) |

## Media delivery

`GET /media/{key}` — requires auth and a key inside your own prefix (`<userId>/…`). Supports HTTP `Range`
(206) for seeking, `?download=name.mp4` for an attachment, and redirects to a presigned R2 URL when
`STORAGE_BACKEND=r2`.

## Example session

```bash
API=http://127.0.0.1:8000

curl -s -X POST $API/api/auth/register -H 'content-type: application/json' \
  -d '{"email":"me@studio.example","password":"correct-horse-9"}' | tee /tmp/reg.json

TOKEN=$(python3 -c "import json;print(json.load(open('/tmp/reg.json'))['access_token'])")
H="Authorization: Bearer $TOKEN"

PID=$(curl -s -X POST "$API/api/projects/upload?auto_analyze=false&title=Episode%2042" \
  -H "$H" -F "file=@data/sample.mp4" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

JOB=$(curl -s -X POST $API/api/projects/$PID/analyze -H "$H" -H 'content-type: application/json' \
  -d '{"target_clips":3,"min_seconds":20,"max_seconds":45}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

curl -s $API/api/jobs/$JOB -H "$H"          # poll until status=done
curl -s $API/api/projects/$PID/clips -H "$H" | python3 -m json.tool | head -40

curl -s -X POST $API/api/projects/$PID/render -H "$H" -H 'content-type: application/json' -d '{}'
curl -s -OJ $API/api/projects/$PID/export -H "$H"     # clips.zip
```

## Rate limits (per IP, in-process sliding window)

| Route | Limit |
|---|---|
| `/auth/register` | 5 / min |
| `/auth/login` | 10 / min |
| `/projects/upload` | 20 / hour |
| `/projects/from-url` | 10 / hour |
| `/projects/{id}/analyze` | 30 / hour |

Multi-node deployments must move this counter to Redis (single interface in `services/ratelimit.py`).
