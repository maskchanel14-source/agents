# Operating cost model (Phase 10)

All numbers are **estimates in USD, October 2026 list prices**, and the token figures come from this
codebase's own prompt sizes (candidate batches of 4–6 windows, ~1.2k characters of transcript each).
Re-price before you publish a plan.

## 1. Per-video unit cost

Assumption: one 60-minute podcast, 5 output clips (30–60 s), 1080×1920 H.264.

| Component | Calculation | Cost |
|---|---|---|
| Transcription (OpenAI `whisper-1`) | 60 min × $0.006/min | **$0.360** |
| Transcription (Groq `whisper-large-v3-turbo`) | 60 min × $0.00067/min | **$0.040** |
| Transcription (own `faster-whisper`, CPU) | amortised worker time only | **≈$0.006** |
| Moment scoring — fast model (`gpt-4o-mini`) | ~35k in / 5k out × ($0.15 / $0.60 per 1M) | **$0.008** |
| Moment scoring — deep model (`gpt-4o`) on the shortlist | ~12k in / 2k out × ($2.50 / $10 per 1M) | **$0.050** |
| Encoding | 5 clips ≈ 4 CPU-minutes on a 2-vCPU worker ($0.03/h) | **$0.002** |
| Storage (R2) | ~40 MB per video, $0.015/GB-month | **$0.0006/mo** |
| Egress | R2 → $0 (zero-egress) | **$0.000** |

**Typical all-in:** `$0.42` with OpenAI ASR + deep scoring, `$0.10` with Groq ASR + fast scoring,
`$0.07` fully self-hosted ASR.

## 2. Fixed monthly infrastructure (reference deployment)

| Item | Spec | Est. |
|---|---|---|
| Web (Next.js) | Vercel Pro or Cloudflare Pages | $20 |
| API | 1× shared vCPU container | $7–12 |
| Worker(s) | 2× 2 vCPU / 4 GB (CPU encode) | $24–40 |
| Postgres | Supabase Pro (or Free while small) | $0–25 |
| Redis | Upstash/serverless small | $0–10 |
| Object storage (R2) | 100 GB + operations | ~$2 |
| Monitoring/logs | optional | $0–15 |
| **Total** | | **≈$55–125 / month** |

(One 60-min video occupies a worker for ~4–6 minutes including decode/analysis; a 2-vCPU worker handles
~10–12 such videos per hour.)

## 3. Plan economics (proposed)

| Plan | Price | Minutes/mo | Max clips/video | Estimated COGS at full usage | Gross margin |
|---|---:|---:|---:|---:|---:|
| Free | $0 | 30 | 3 | ~$0.25 | acquisition cost |
| Pro | $19 | 300 | 10 | $0.53 (Groq) – $2.10 (OpenAI)* | 89–97% |
| Business | $59 | 1 500 | 20 | $2.60 – $18.00† | 70–96% |

\* 300 min = 5 h ⇒ 5 × $0.42 = $2.10 worst case.
† 1 500 min = 25 h ⇒ 25 × $0.42 = $10.50 (OpenAI ASR) up to $18 with deep scoring on every clip.

Encode and storage stay under 5% of COGS; **transcription dominates**, so the ASR provider choice is the
single biggest lever (Groq/self-hosted is ~9–50× cheaper than OpenAI Whisper).

## 4. Controls to stop runaway spend

* Plan quotas enforced server-side (`minutes_per_month`, `max_clips_per_video`, `projects`, upload MB).
* `use_deep_model` is a per-request choice; batch scoring uses the fast model by default.
* Vision analysis is **off** by default (`VISION_ENABLED=false`) — sending frames to a multimodal model is
  the most expensive optional step.
* Every call is written to `ai_usage` with USD; `/api/usage` and Settings expose live spend per user.
* Retries are capped at 3 with jitter; failures fall back to the deterministic heuristic scorer instead of
  retrying a paid call.
* Suggested production guardrails: a per-user daily USD ceiling (reject with 402), and an alert when
  `ai_usage` cost exceeds 20% of MRR.

## 5. Cost of a failed run

Analysis is the expensive part; a render failure costs only CPU (≈$0.0004/clip). Because candidate
generation and scoring happen once per analysis, re-rendering with a different preset/crop is nearly free
for the customer — a deliberate product decision that also keeps retry loops cheap.
