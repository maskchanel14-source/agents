import { NextRequest, NextResponse } from "next/server";
import { leads, rateLimit, persistToSupabase } from "@/lib/store";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export async function POST(req: NextRequest) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (!rateLimit(`optin:${ip}`, 20, 60 * 60 * 1000).ok) return NextResponse.json({ error: "rate_limited", message: "Too many attempts — try again later." }, { status: 429 });
  let body: { email?: string; source?: string; scanId?: string; plan?: string; consent?: boolean; website?: string };
  try { body = await req.json(); } catch { return NextResponse.json({ error: "bad_json" }, { status: 400 }); }
  if (body.website) return NextResponse.json({ ok: true }); // honeypot: silently accept bots
  const email = String(body.email ?? "").trim().toLowerCase();
  if (!EMAIL_RE.test(email)) return NextResponse.json({ error: "bad_email", message: "That email does not look complete — mind checking it?" }, { status: 422 });
  if (!body.consent) return NextResponse.json({ error: "no_consent", message: "Tick the consent box so we may email you — we never mail without it." }, { status: 422 });
  const lead = { email, source: String(body.source ?? "site").slice(0, 60), scanId: body.scanId, plan: body.plan, consent: true, createdAt: new Date().toISOString() };
  leads.push(lead);
  persistToSupabase("leads", { email, source: lead.source, scan_id: lead.scanId ?? null, plan_interest: lead.plan ?? null });
  persistToSupabase("consent_events", { email, purpose: lead.source, granted: true });
  return NextResponse.json({ ok: true });
}
