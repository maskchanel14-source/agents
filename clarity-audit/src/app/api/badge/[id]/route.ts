import { NextRequest, NextResponse } from "next/server";
import { getScanAsync } from "@/lib/store";
import { demoReport } from "@/lib/demo";
import { scoreColor } from "@/lib/scanner";


export async function GET(_req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const clean = id.replace(/\.svg$/, "");
  const report = clean === "demo" ? demoReport() : (await getScanAsync(clean))?.report;
  const score = report?.score ?? 0;
  const label = report ? `${score}/100 · ${report.grade}` : "Check yours free";
  const color = report ? scoreColor(score) : "#111827";
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="280" height="64" role="img" aria-label="Landing Page Clarity Score: ${label}">
<rect width="280" height="64" rx="10" fill="#0b0f17"/>
<text x="16" y="26" font-family="system-ui,sans-serif" font-size="11" fill="#9ca3af" letter-spacing="1.5">CLARITY SCORE</text>
<text x="16" y="48" font-family="system-ui,sans-serif" font-size="20" font-weight="700" fill="${color}">${label}</text>
<text x="264" y="48" text-anchor="end" font-family="system-ui,sans-serif" font-size="10" fill="#6b7280">clarity audit</text>
</svg>`;
  return new NextResponse(svg, { headers: { "Content-Type": "image/svg+xml; charset=utf-8", "Cache-Control": "public, max-age=300" } });
}
