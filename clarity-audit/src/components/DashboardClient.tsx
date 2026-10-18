"use client";
import { useEffect, useState } from "react";

type Stats = { scansCompleted: number; averageScore: number | null; optIns: number; affiliateApplications: number; updatedAt: string };

export default function DashboardClient() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    fetch("/api/stats").then((r) => r.json()).then(setStats).catch(() => setErr(true));
  }, []);
  const cell = (label: string, value: string, note: string) => (
    <div className="rounded-2xl border border-[color:var(--line)] bg-white p-6">
      <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--ink-3)]">{label}</p>
      <p className="mt-2 text-4xl font-extrabold tracking-tight">{value}</p>
      <p className="mt-1 text-sm text-[color:var(--ink-3)]">{note}</p>
    </div>
  );
  if (err) return <p className="mt-8 text-[color:var(--bad)]">Stats unavailable right now.</p>;
  if (!stats) return <p className="mt-8 text-[color:var(--ink-3)]" role="status">Loading metrics…</p>;
  const conv = stats.scansCompleted > 0 ? `${Math.min(100, Math.round((stats.optIns / stats.scansCompleted) * 100))}%` : "—";
  return (
    <div className="mt-9">
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {cell("Free scans completed", String(stats.scansCompleted), "North star #2 — target: first 100")}
        {cell("Email opt-ins (consented)", String(stats.optIns), `Scan→opt-in: ${conv}`)}
        {cell("Average score", stats.averageScore === null ? "Not yet" : `${stats.averageScore}/100`, stats.averageScore === null ? "Shown only after ≥10 real scans" : `Across ${stats.scansCompleted} real scans`)}
        {cell("Affiliate applications", String(stats.affiliateApplications), "Human-reviewed before approval")}
      </div>
      <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {cell("Paid orders", "—", "Activates when payments connect (human)")}
        {cell("Revenue / payout", "—", "No fake numbers. Ever.")}
        {cell("Avg. order value", "—", "Tiers: $19 / $39 / $79 / bundles")}
        {cell("Refund rate", "—", "Target < 5% via honest expectations")}
      </div>
      <p className="mt-6 text-xs text-[color:var(--ink-3)]">Updated {new Date(stats.updatedAt).toLocaleString("en-US")} · Source: /api/stats (aggregate counts only, no personal data).</p>
    </div>
  );
}
