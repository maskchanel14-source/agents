# Security audit

Scope: this repository's application code, its default configuration, and the documented deployment
topology. Method: STRIDE-style review of each trust boundary + automated tests for the claims that can be
tested (`apps/api/tests`). Findings are separated into **implemented controls**, **accepted risks**, and
**gaps with a concrete fix**.

## 1. Trust boundaries

```
anonymous ──► Next.js (public) ──► FastAPI ──► worker ──► FFmpeg/OpenCV ──► object storage
                                        └──► LLM/ASR providers (server-side keys)
                                        └──► untrusted URL ingest (SSRF surface)
```

## 2. Implemented controls

### Authentication & session
* Passwords: **scrypt** (`n=2^14, r=8, p=1`, 16-byte random salt), constant-time compare, minimum length
  enforced at both schema and hash layer. `passwords are never logged`.
* Tokens: HS256 JWT, `sub`/`iat`/`exp`/`aud="authenticated"`, 7-day TTL, signed with `JWT_SECRET`.
  Verification pins `audience` and requires `exp`+`sub`.
* Delivery: **HttpOnly, SameSite=Lax cookie** (+ `Secure` in production). The browser never reads the
  token; no `localStorage` usage anywhere.
* Supabase mode: separately verified HS256 token (`SUPABASE_JWT_SECRET`) mapped to a local profile —
  never blindly trusted.
* Login failures return one generic message (no account enumeration) and are rate limited.

### Authorization & data isolation
* Every project/clip/job read goes through `owned(user, obj)` → **404 for other tenants** (not 403, so
  existence isn't leaked).
* List endpoints filter `user_id` at the query level; media keys must start with `<userId>/`.
* Six dedicated tests cover cross-tenant project/clip/render/delete/media access.

### Uploads & media
* Extension allowlist (`.mp4 .mov .m4v .webm .mkv`), MIME allowlist, **magic-byte sniffing**
  (`ftyp` / EBML) — a text file renamed to `.mp4` is rejected (tested).
* Size cap from the plan *and* a global cap; the stream is aborted and the partial file deleted on
  overflow (tested).
* Storage keys are validated against the storage root — path traversal raises (tested).
* FFmpeg runs with an argv list (never a shell), a timeout, and `-nostdin`; the filtergraph path is escaped.
* `Render` failures are per-clip and do not break the batch.

### API surface
* Rate limits: register 5/min, login 10/min, upload 20/h, url-ingest 10/h, analyze 30/h (per IP).
* Pydantic validation on every body/query (lengths, ranges, enums); clip edits validated
  (`end > start`, within source duration, minimum 3 s, preset tier gating → 402).
* Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`;
  `Cache-Control: no-store` on `/api/*`.
* CORS restricted to configured origins (same-origin proxy in the reference deployment, so CORS is
  effectively unused).
* Media responses are `private` + authenticated and support Range without leaking directory listing.

### Secrets & cost abuse
* API keys only in server env; no `NEXT_PUBLIC_*` secret exists; `/api/providers` reports *whether* a
  provider is configured, never the key.
* Every LLM/ASR call is metered into `ai_usage` (tokens, audio seconds, USD) and surfaced to the user.
* Plan quotas (minutes/month, clips/video, projects, upload MB, video minutes) are enforced server-side,
  not in the UI. Preset tiers are gated server-side too.
* Retries are bounded (3 attempts, exponential backoff + jitter) — no retry storms on a failing provider.

### Logging & errors
* Structured Python logging; provider errors are truncated and stored on the job/clip, never containing
  keys (headers are never logged).
* Rendered/hosted assets are user-prefixed, so a delete removes only that user's prefix.

## 3. Accepted risks (documented, with mitigations)

| Risk | Why accepted | Mitigation in place / next step |
|---|---|---|
| No CSRF token | State-changing routes are JSON-only (multipart for upload), cookies are `SameSite=Lax`, and there are no state-changing GETs | Add double-submit CSRF if you expose cross-site embedding |
| URL ingest can target internal hosts (SSRF) | Needed for customer CDNs | Restrict scheme + content-type today; **add** a deny-list of private/link-local ranges + DNS re-resolution (see gap G1) |
| Redis queue unauthenticated if misconfigured | RQ assumes a trusted network | Bind Redis to a private network, require a password (`REDIS_URL=redis://:pass@…`) |
| No malware scanning of uploads | Media is decoded by FFmpeg, not executed | Containers run as a non-root user with a read-only root FS in the reference deployment |
| In-memory rate limiter | Single-node reference deployment | Swap to Redis `INCR`+`EXPIRE` for multi-node (interface unchanged) |
| No refresh-token rotation | Short product horizon; 7-day token + logout | Add refresh pairs + rotation before public launch |

## 4. Gaps with fixes (prioritised)

1. **G1 — SSRF hardening for `/projects/from-url`.** Add `ipaddress` checks after DNS resolution, block
   RFC1918/loopback/link-local/metadata (169.254.169.254), limit redirects to 2, and only follow redirects
   to public hosts.
2. **G2 — Secrets at rest.** Move provider keys to a secret manager (or Supabase Vault) and read them per
   request instead of process start; rotate on deploy.
3. **G3 — Virus/content scanning.** Pipe uploads through `clamav` or an object-storage scan hook.
4. **G4 — Audit trail.** Add an append-only `audit_log` table for login, delete, and plan changes.
5. **G5 — RLS verification.** `supabase/migrations/0001_init.sql` enables RLS, but the API connects with the
   service role. Add a test suite that exercises the anon/authenticated roles directly.
6. **G6 — S3 lifecycle.** R2 lifecycle rule to expire `work/` scratch objects after 24 h (the API already
   deletes them, but belt-and-braces).
7. **G7 — Dependency scanning.** Wire `pip-audit` / `npm audit` + Dependabot into CI.

## 5. What a reviewer should verify first

```bash
cd apps/api && ../../.venv/bin/python -m pytest tests/test_isolation.py tests/test_auth.py \
  tests/test_upload_validation.py -q
```

Those three files are the machine-checkable core of this audit: tenant isolation, credential handling and
upload validation.
