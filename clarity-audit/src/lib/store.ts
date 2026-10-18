// In-memory store for scan results, leads, affiliates, and rate limits.
// Production note: swap for Supabase (schema in supabase/migrations/0001_init.sql).
// Kept dependency-free so the scanner works before any account is connected.
import { randomBytes } from "node:crypto";
import type { ScanReport } from "./scanner";

export interface StoredScan {
  id: string;
  report: ScanReport;
  isPublic: boolean;
}

// Anchored on globalThis: Next/Turbopack may load this module in separate
// server graphs (route handlers vs RSC pages) — a module-level Map would
// fork into two stores (scans saved by the API invisible to result pages).
interface StoreShape {
  scans: Map<string, StoredScan>;
  windows: Map<string, { count: number; resetAt: number }>;
  leads: Lead[];
  affiliateApplications: AffiliateApplication[];
}
const g = globalThis as unknown as { __clarityStore?: StoreShape };
if (!g.__clarityStore) {
  g.__clarityStore = { scans: new Map(), windows: new Map(), leads: [], affiliateApplications: [] };
}
const store: StoreShape = g.__clarityStore;
const scans = store.scans;
const MAX_SCANS = 300;

export function newScanId(): string {
  return randomBytes(6).toString("base64url").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 10) || "scan";
}

export function saveScan(report: ScanReport): StoredScan {
  const id = newScanId();
  const stored: StoredScan = { id, report, isPublic: true };
  scans.set(id, stored);
  if (scans.size > MAX_SCANS) {
    const first = scans.keys().next().value;
    if (first) scans.delete(first);
  }
  return stored;
}

export function getScan(id: string): StoredScan | undefined {
  return scans.get(id);
}

// --- Rate limiting: fixed window per key ---
const windows = store.windows;
export function rateLimit(key: string, limit: number, windowMs: number): { ok: boolean; retryAfterSec: number } {
  const now = Date.now();
  const w = windows.get(key);
  if (!w || now > w.resetAt) {
    windows.set(key, { count: 1, resetAt: now + windowMs });
    return { ok: true, retryAfterSec: 0 };
  }
  if (w.count >= limit) {
    return { ok: false, retryAfterSec: Math.max(1, Math.ceil((w.resetAt - now) / 1000)) };
  }
  w.count += 1;
  return { ok: true, retryAfterSec: 0 };
}

// --- Leads & affiliates (consent-tracked) ---
export interface Lead {
  email: string;
  source: string;
  scanId?: string;
  plan?: string;
  consent: boolean;
  createdAt: string;
}
export const leads: Lead[] = store.leads;

export interface AffiliateApplication {
  name: string;
  email: string;
  audience: string;
  channelUrl: string;
  createdAt: string;
}
export const affiliateApplications: AffiliateApplication[] = store.affiliateApplications;

// --- Aggregate stats (privacy-safe: counts only, no URLs exposed) ---
export function aggregateStats() {
  const all = Array.from(scans.values());
  const n = all.length;
  const avgScore = n >= 10 ? Math.round(all.reduce((s, x) => s + x.report.score, 0) / n) : null;
  // Most-failed checks across real scans (aggregate counts only — data-study fuel).
  const failCounts = new Map<string, { label: string; fails: number }>();
  for (const s of all) for (const c of s.report.checks) if (c.status !== "pass") {
    const cur = failCounts.get(c.id) ?? { label: c.label, fails: 0 };
    cur.fails += 1; failCounts.set(c.id, cur);
  }
  const topFailedChecks = n >= 5
    ? Array.from(failCounts.values()).sort((a, b) => b.fails - a.fails).slice(0, 8).map((f) => ({ label: f.label, pct: Math.round((f.fails / n) * 100) }))
    : [];
  return {
    scansCompleted: n,
    averageScore: avgScore, // null until >=10 scans: no fake "niche average" claims
    topFailedChecks,
    optIns: leads.length,
    affiliateApplications: affiliateApplications.length,
    updatedAt: new Date().toISOString(),
  };
}

// --- Optional Supabase persistence (REST, service role, server-side only) ---
export async function persistToSupabase(table: string, row: Record<string, unknown>): Promise<void> {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) return; // not connected yet — in-memory only, by design
  try {
    await fetch(`${url.replace(/\/$/, "")}/rest/v1/${table}`, {
      method: "POST",
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify([row]),
    });
  } catch {
    // Persistence failure must never break the scan UX; logged server-side in production.
  }
}
