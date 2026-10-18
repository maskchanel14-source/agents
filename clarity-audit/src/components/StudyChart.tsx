"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type Stats = { scansCompleted: number; averageScore: number | null; topFailedChecks: { label: string; pct: number }[] };

export default function StudyChart() {
  const [stats, setStats] = useState<Stats | null>(null);
  useEffect(() => { fetch("/api/stats").then((r) => r.json()).then(setStats).catch(() => setStats(null)); }, []);
  if (!stats) return <p className="text-sm text-[color:var(--ink-3)]" role="status">Loading live findings…</p>;
  if (stats.topFailedChecks.length === 0) {
    return (
      <div className="rounded-xl bg-[#fffbeb] px-5 py-4 text-[15px] leading-relaxed text-[#92400e]">
        <strong>Live chart unlocks at 5+ real scans</strong> (currently {stats.scansCompleted}). We publish findings only from pages actually scanned here — <Link href="/#scan" className="underline">run a free scan</Link> and your anonymous check results join the aggregate. The full batch-study protocol is documented below; results will be appended here with the sample frame named.
      </div>
    );
  }
  return (
    <figure>
      <figcaption className="mb-4 text-sm text-[color:var(--ink-2)]">Share of scanned pages failing each check · n = {stats.scansCompleted} real scans on this site</figcaption>
      <div className="space-y-3.5">
        {stats.topFailedChecks.map((f) => (
          <div key={f.label}>
            <div className="flex justify-between gap-4 text-sm"><span className="font-medium">{f.label}</span><span className="font-mono text-[color:var(--ink-3)]">{f.pct}%</span></div>
            <div className="mt-1 h-2.5 rounded-full bg-[color:var(--ring-track,#e5e7eb)]" role="img" aria-label={`${f.label}: ${f.pct}% of pages fail`}><div className="h-full rounded-full bg-[color:var(--accent)]" style={{ width: `${f.pct}%` }} /></div>
          </div>
        ))}
      </div>
      {stats.averageScore !== null && <p className="mt-4 text-sm text-[color:var(--ink-2)]">Average clarity score across these pages: <strong>{stats.averageScore}/100</strong>.</p>}
    </figure>
  );
}
