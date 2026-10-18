import { NextRequest, NextResponse } from "next/server";
import { affiliateApplications, rateLimit, persistToSupabase } from "@/lib/store";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export async function POST(req: NextRequest) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (!rateLimit(`aff:${ip}`, 10, 60 * 60 * 1000).ok) return NextResponse.json({ error: "rate_limited", message: "Too many attempts — try again later." }, { status: 429 });
  let b: { name?: string; email?: string; audience?: string; channelUrl?: string; website?: string };
  try { b = await req.json(); } catch { return NextResponse.json({ error: "bad_json" }, { status: 400 }); }
  if (b.website) return NextResponse.json({ ok: true });
  const name = String(b.name ?? "").trim().slice(0, 80);
  const email = String(b.email ?? "").trim().toLowerCase();
  const audience = String(b.audience ?? "").trim().slice(0, 300);
  const channelUrl = String(b.channelUrl ?? "").trim().slice(0, 300);
  if (!name || !EMAIL_RE.test(email) || !audience) return NextResponse.json({ error: "incomplete", message: "Add your name, a valid email, and a line about your audience." }, { status: 422 });
  affiliateApplications.push({ name, email, audience, channelUrl, createdAt: new Date().toISOString() });
  persistToSupabase("affiliates", { name, email, audience, channel_url: channelUrl, status: "applied" });
  return NextResponse.json({ ok: true });
}
