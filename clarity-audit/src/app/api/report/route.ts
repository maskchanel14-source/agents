import { NextRequest, NextResponse } from "next/server";
import { getScan } from "@/lib/store";
import { demoReport } from "@/lib/demo";
import { buildReportMarkdown } from "@/lib/reportMarkdown";


// Preview of the paid deliverable generator. In production this endpoint is
// gated behind a verified paid order (webhook-checked entitlement); here it
// serves the fully-labeled SAMPLE so buyers can inspect format before paying.
export async function GET(req: NextRequest) {
  const id = req.nextUrl.searchParams.get("scan") || "demo";
  const tier = (req.nextUrl.searchParams.get("tier") || "full") as "quick" | "full" | "fixpack";
  const report = id === "demo" ? demoReport() : getScan(id)?.report;
  if (!report) return NextResponse.json({ error: "not_found", message: "That scan is no longer available in this session." }, { status: 404 });
  const md = buildReportMarkdown(report, ["quick", "full", "fixpack"].includes(tier) ? tier : "full");
  const watermark = id === "demo" ? "> **SAMPLE REPORT** — generated from an illustrative example page to show the format. Paid reports run on your real page.\n\n" : "";
  return new NextResponse(watermark + md, { headers: { "Content-Type": "text/markdown; charset=utf-8" } });
}
