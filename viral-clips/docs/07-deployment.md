# Running & deploying

## 1. Local (one command per service)

```bash
cd viral-clips
cp .env.example .env                 # defaults work offline: local disk, inline queue, heuristics
make setup                           # python venv + pip + npm install
make sample                          # 75 s test video (make long-sample → 4 min)
make api                             # http://127.0.0.1:8000  (docs at /api/docs)
make web                             # http://127.0.0.1:3000
make seed                            # demo@viralclips.example / demo-password-123 + a processed project
```

Requirements: Python ≥3.11, Node ≥20, ~1 GB free disk per hour of 1080p source. No Redis, no Postgres,
no API key needed to see the full flow — the engine degrades to acoustic/visual analysis with the
deterministic heuristic scorer and says so in the UI.

Tests: `make test` (69 API tests incl. a real analyze→render→ZIP cycle) · `make e2e` (Playwright; run
`npx playwright install chromium` once).

## 2. Configuration

Everything is env-driven; see `.env.example` for the full list with comments. The knobs that matter:

| Variable | Default | Production guidance |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///../../data/viralclips.db` | `postgresql+asyncpg://…` (Supabase pooler, port 5432) |
| `STORAGE_BACKEND` | `local` | `r2` + the four `R2_*` values |
| `QUEUE_BACKEND` | `inline` | `rq` + `REDIS_URL`, run `make worker` on its own host |
| `JWT_SECRET` | dev placeholder | 64 random chars, rotated on deploy |
| `COOKIE_SECURE` | `false` | `true` behind HTTPS |
| `ASR_PROVIDER` | `auto` | `groq` or `faster_whisper` for cost; `openai` for portability |
| `LLM_PROVIDER` | `auto` | `openai` / `anthropic` / `groq`; `heuristic` to run with zero AI spend |
| `LLM_MODEL_FAST` / `_DEEP` | `gpt-4o-mini` / `gpt-4o` | keep fast for batch scoring, deep for the shortlist |
| `VISION_ENABLED` | `false` | leave off unless you budget for multimodal frames |
| `ENABLE_YOUTUBE_INGEST` | `false` | only turn on where you have confirmed the rights/terms position |
| `MAX_VIDEO_MINUTES` | 90 | lower on small workers |
| `SUPABASE_JWT_SECRET` | — | set to accept Supabase Auth tokens |

## 3. Production topology

```
Cloudflare / Vercel (TLS, CDN)
        │
        ├── Next.js web  ──── INTERNAL_API_URL ────► API (private network)
        │                                              │
        │                                              ├── Supabase Postgres
        │                                              ├── Redis (RQ)
        │                                              └── Cloudflare R2
        │
        └── /media/* proxied (local storage) or presigned R2 URLs (r2 storage)

Worker fleet (N × 2–4 vCPU, 4 GB, CPU encode) ── consumes RQ ── writes MP4s to R2
```

**Why not serverless for rendering:** a 60 s clip takes 10–40 s of continuous CPU and minutes of wall time
for a full analysis. Lambda/Workers would hit execution limits and cold-start FFmpeg every time.

### Steps

1. **Database.** Create a Supabase project, then apply the schema:
   ```bash
   psql "$SUPABASE_DB_URL" -f supabase/migrations/0001_init.sql
   # or: supabase db push  /  the Supabase MCP connector's execute_query
   ```
   Set `DATABASE_URL=postgresql+asyncpg://…:5432/postgres` and `pip install asyncpg`.
2. **Storage.** Create an R2 bucket, an API token with object read/write, and (optionally) a public
   custom domain. Set `STORAGE_BACKEND=r2` + `R2_*`. R2 has zero egress fees, which is why it is preferred
   over S3 for clip delivery.
3. **Redis & worker.**
   ```bash
   # API
   QUEUE_BACKEND=rq uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
   # worker container(s)
   rq worker -u "$REDIS_URL" viral-clips --max-jobs 20
   ```
   Scale workers horizontally; each runs one FFmpeg process at a time by design (`FFMPEG_THREADS`).
4. **Web.** `npm ci && npm run build && npm start` (or Vercel). Set `INTERNAL_API_URL` to the private API
   address. No secrets are exposed to the browser bundle.
5. **Realtime progress.** The UI polls `GET /api/jobs/{id}` every 1.5 s. If you prefer push, Supabase
   Realtime on the `jobs` table is a drop-in replacement (the API already writes stage/progress).
6. **Backups.** Supabase PITR for the DB; R2 versioning (or a weekly `rclone sync`) for media. The DB is
   small (kilobytes per project); media dominates.
7. **Housekeeping.** `data/work` is deleted after each job; add an R2 lifecycle rule expiring `*/<project>/work/*`
   after 24 h as a safety net.
8. **Observability.** `/api/health` for liveness, job rows for throughput/failures, `ai_usage` for spend.
   Recommended: Prometheus scrape on `/api/health`, alert on `jobs.status='failed'` rate and on
   `sum(ai_usage.cost_usd)` per hour.

## 4. CI/CD sketch

```yaml
# .github/workflows/ci.yml (not committed; wire to your policy)
jobs:
  api:   { steps: [pip install -r apps/api/requirements.txt, pytest apps/api/tests -q] }
  web:   { steps: [npm ci --prefix apps/web, npm run build --prefix apps/web, npx tsc --noEmit] }
  e2e:   { steps: [make sample, make api &, make web &, npx playwright test] }
```

## 5. Environment checklist before charging money

- [ ] `JWT_SECRET` is 64 random bytes, not the dev value
- [ ] `COOKIE_SECURE=true` and HTTPS enforced
- [ ] `STORAGE_BACKEND=r2` with private bucket + presigned URLs
- [ ] `QUEUE_BACKEND=rq`; API and workers on separate hosts
- [ ] SSRF deny-list added to URL ingest (gap G1)
- [ ] Per-user daily AI spend ceiling (gap in `05-security-audit.md`)
- [ ] Stripe webhook signature verification + `stripe_customer_id` backfill before enabling billing
- [ ] R2 lifecycle + DB backup policy verified by an actual restore
