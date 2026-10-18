import { ImageResponse } from "next/og";
import { getScan } from "@/lib/store";
import { demoReport } from "@/lib/demo";

export async function GET(_req: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const report = id === "demo" ? demoReport() : getScan(id)?.report;
  const score = report?.score ?? 0;
  const grade = report?.grade ?? "Score yours free";
  const issue = report?.topIssues[0]?.label ?? "";
  const color = score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : score >= 40 ? "#fb923c" : "#ef4444";
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", background: "#0b0f17", color: "#fff", padding: 64, fontFamily: "system-ui, sans-serif" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 44, height: 44, borderRadius: 22, border: "5px solid #fff", display: "flex" }} />
          <div style={{ fontSize: 26, fontWeight: 700 }}>Clarity Audit</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
            <span style={{ fontSize: 150, fontWeight: 800, lineHeight: 1, color }}>{score}</span>
            <span style={{ fontSize: 56, color: "#9ca3af" }}>/100</span>
          </div>
          <div style={{ fontSize: 34, marginTop: 10 }}>{grade}</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {issue ? <div style={{ fontSize: 26, color: "#d1d5db" }}>{"Biggest fix: " + issue}</div> : null}
          <div style={{ fontSize: 24, color: "#9ca3af" }}>Can your landing page score above 70? Free scan</div>
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}
