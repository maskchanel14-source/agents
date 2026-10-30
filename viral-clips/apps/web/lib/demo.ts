/**
 * Demo session helper (server-side only).
 *
 * Preview environments open the app inside a cross-site frame, where browsers
 * drop third-party cookies. Redirect-based login therefore loops forever, so in
 * DEMO_MODE the server keeps one short-lived token for the seeded demo account
 * and signs requests itself. Production never sets DEMO_MODE.
 */
const INTERNAL = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
const EMAIL = process.env.DEMO_EMAIL || "demo@viralclips.example";
const PASSWORD = process.env.DEMO_PASSWORD || "demo-password-123";

const TTL_MS = 30 * 60 * 1000;

const RETRY_AFTER_FAILURE_MS = 20_000;

let cache: { token: string; at: number } | null = null;
let failedAt = 0;
let inflight: Promise<string | null> | null = null;

export function demoMode(): boolean {
  return process.env.DEMO_MODE === "1";
}

async function login(): Promise<string | null> {
  try {
    const res = await fetch(`${INTERNAL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
      cache: "no-store",
    });
    if (!res.ok) {
      failedAt = Date.now();
      return null;
    }
    const data = (await res.json()) as { access_token?: string };
    if (!data.access_token) return null;
    cache = { token: data.access_token, at: Date.now() };
    return data.access_token;
  } catch {
    failedAt = Date.now();
    return null;
  }
}

/** Cached demo token, or null when demo mode is off / the API is unreachable. */
export async function getDemoToken(): Promise<string | null> {
  if (!demoMode()) return null;
  if (cache && Date.now() - cache.at < TTL_MS) return cache.token;
  // Never hammer the login endpoint: one attempt, then wait before retrying.
  if (failedAt && Date.now() - failedAt < RETRY_AFTER_FAILURE_MS) return null;
  if (!inflight) {
    inflight = login().finally(() => {
      inflight = null;
    });
  }
  return inflight;
}
