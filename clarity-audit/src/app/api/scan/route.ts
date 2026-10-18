import { NextRequest, NextResponse } from "next/server";
import { fetchPublicPage, ScanError } from "@/lib/fetchPage";
import { analyzePage } from "@/lib/scanner";
import { saveScan, rateLimit, persistToSupabase } from "@/lib/store";


export async function POST(req: NextRequest) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  const rl = rateLimit(`scan:${ip}`, 10, 60 * 60 * 1000);
  if (!rl.ok) {
    return NextResponse.json(
      { error: "rate_limited", message: `You've run several scans in a row — give it a few minutes and try again. (Free tier: 10/hour.)` },
      { status: 429, headers: { "Retry-After": String(rl.retryAfterSec) } }
    );
  }
  let body: { url?: string; ref?: string };
  try { body = await req.json(); } catch { return NextResponse.json({ error: "bad_json", message: "Invalid request." }, { status: 400 }); }

  try {
    const page = await fetchPublicPage(String(body.url ?? ""));
    const report = analyzePage({ url: String(body.url), finalUrl: page.finalUrl, html: page.html, responseMs: page.responseMs, htmlBytes: page.htmlBytes });
    const stored = saveScan(report);
    // Awaited deliberately: unawaited fetches die when serverless freezes post-response.
    await persistToSupabase("scans", { id: stored.id, url: report.url, final_url: report.finalUrl, score: report.score, grade: report.grade, source_ref: body.ref ?? null });
    await persistToSupabase("scan_results", { scan_id: stored.id, report });
    return NextResponse.json({ id: stored.id, report });
  } catch (e) {
    if (e instanceof ScanError) return NextResponse.json({ error: e.code, message: e.message }, { status: 422 });
    return NextResponse.json({ error: "unknown", message: "Something went wrong reading that page. Try again in a moment." }, { status: 500 });
  }
}
