import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { connection } from "next/server";
import { getScanAsync, aggregateStatsAsync } from "@/lib/store";
import { demoReport } from "@/lib/demo";
import { CATEGORIES, type ScanReport } from "@/lib/scanner";
import { Container, Eyebrow, Btn, Card, ScoreRing, StatusPill } from "@/components/ui";
import EmailCapture from "@/components/EmailCapture";
import ShareBar from "@/components/ShareBar";
import ScanForm from "@/components/ScanForm";
import { SITE } from "@/lib/site";

// Result pages are per-scan runtime data (in-memory/Supabase) — blocking route is correct.
export const instant = false;


async function loadReport(id: string): Promise<{ report: ScanReport; isDemo: boolean } | null> {
  if (id === "demo") return { report: demoReport(), isDemo: true };
  const s = await getScanAsync(id);
  return s ? { report: s.report, isDemo: false } : null;
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const loaded = await loadReport(id);
  if (!loaded) return { title: "Scan not found" };
  const { report } = loaded;
  return {
    title: `Clarity Score ${report.score}/100 — ${report.grade}`,
    description: `This landing page scored ${report.score}/100 (${report.grade}) on the free Clarity Audit. Top issue: ${report.topIssues[0]?.label ?? "none"}. Score yours free.`,
    openGraph: { images: [{ url: `/api/og/${id}`, width: 1200, height: 630, alt: `Clarity score ${report.score} out of 100` }] },
    twitter: { card: "summary_large_image", images: [`/api/og/${id}`] },
    robots: { index: false, follow: true },
  };
}

export default async function ScanResult({ params }: { params: Promise<{ id: string }> }) {
  await connection(); // per-request data (live store stats): render at request time
  const { id } = await params;
  const loaded = await loadReport(id);
  if (!loaded) notFound();
  const { report, isDemo } = loaded;
  const stats = await aggregateStatsAsync();
  const paymentsLive = SITE.paymentsConnected;

  return (
    <Container className="py-12">
      <Eyebrow>{isDemo ? "Sample result — illustrative example page" : "Your clarity score"}</Eyebrow>
      <div className="mt-4 grid items-start gap-10 lg:grid-cols-[auto_1fr]">
        <ScoreRing score={report.score} />
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">{report.grade}: {report.score}/100</h1>
          <p className="mt-3 max-w-2xl text-lg leading-relaxed text-[color:var(--ink-2)]">{report.gradeNote}</p>
          <p className="mt-3 break-all text-sm text-[color:var(--ink-3)]">Scanned: <span className="font-medium text-[color:var(--ink-2)]">{report.finalUrl}</span> · {new Date(report.fetchedAt).toLocaleString("en-US")}</p>
          {stats.averageScore !== null ? (
            <p className="mt-2 text-sm text-[color:var(--ink-2)]">Average across {stats.scansCompleted} pages scanned here: <strong>{stats.averageScore}/100</strong>. (Real scans only — no invented benchmarks.)</p>
          ) : (
            <p className="mt-2 text-sm text-[color:var(--ink-3)]">Benchmarks appear here once enough real pages have been scanned — we don't invent “industry averages”.</p>
          )}
          {report.quickWin && (
            <div className="mt-6 rounded-xl border border-[color:var(--accent)] bg-[#eff6ff] p-5">
              <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--accent)]">Your quick win — fix this first</p>
              <p className="mt-1.5 font-bold">{report.quickWin.label}</p>
              <p className="mt-1 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{report.quickWin.fix}</p>
            </div>
          )}
        </div>
      </div>

      <section className="mt-12" aria-label="Top issues">
        <h2 className="text-2xl font-bold tracking-tight">Your top {report.topIssues.length} issues, with fixes</h2>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          {report.topIssues.map((c, i) => (
            <Card key={c.id}>
              <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--ink-3)]">#{i + 1} · {c.category} · {c.impact} impact</p>
              <h3 className="mt-2 font-bold">{c.label}</h3>
              <div className="mt-2"><StatusPill status={c.status} /></div>
              <p className="mt-3 text-sm leading-relaxed text-[color:var(--ink-2)]"><strong className="text-[color:var(--ink)]">Found:</strong> {c.evidence}</p>
              <p className="mt-2 text-sm leading-relaxed text-[color:var(--ink-2)]"><strong className="text-[color:var(--ink)]">Fix:</strong> {c.fix}</p>
            </Card>
          ))}
          {report.topIssues.length === 0 && <Card><p className="font-semibold">No failing checks 🎉</p><p className="mt-1 text-sm text-[color:var(--ink-2)]">Your page passes all 25 automated clarity checks. The paid audit goes deeper: copy quality, section flow, and offer framing.</p></Card>}
        </div>
        {report.lockedFindings > 0 && (
          <p className="mt-4 text-[15px] text-[color:var(--ink-2)]">+ <strong>{report.lockedFindings} more findings</strong> in the full breakdown — plus rewrites for your headline and CTAs in the paid audit. <Link href="/pricing" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">See what's inside →</Link></p>
        )}
      </section>

      <section className="mt-12" aria-label="Category breakdown">
        <h2 className="text-2xl font-bold tracking-tight">Category breakdown</h2>
        <div className="mt-5 space-y-4 rounded-2xl border border-[color:var(--line)] bg-white p-6">
          {CATEGORIES.map((cat) => {
            const cs = report.checks.filter((c) => c.category === cat);
            const pts = cs.reduce((s, c) => s + c.points, 0);
            const max = cs.reduce((s, c) => s + c.maxPoints, 0);
            const pct = Math.round((pts / max) * 100);
            return (
              <div key={cat}>
                <div className="flex items-baseline justify-between gap-4 text-sm">
                  <p className="font-semibold">{cat}</p><p className="text-[color:var(--ink-3)]">{pts}/{max} pts</p>
                </div>
                <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-[color:var(--ring-track,#e5e7eb)]" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label={`${cat}: ${pct}%`}>
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, background: pct >= 80 ? "var(--good)" : pct >= 50 ? "var(--warn)" : "var(--bad)" }} />
                </div>
              </div>
            );
          })}
        </div>
        <details className="faq mt-5 rounded-2xl border border-[color:var(--line)] bg-white p-6">
          <summary className="flex cursor-pointer items-center justify-between font-semibold">All 25 checks — evidence for every point <span className="chev text-[color:var(--ink-3)]" aria-hidden>▾</span></summary>
          <ul className="mt-4 divide-y divide-[color:var(--line)]">
            {report.checks.map((c) => (
              <li key={c.id} className="py-3.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-semibold">{c.label} <span className="ml-1 text-xs font-normal text-[color:var(--ink-3)]">{c.category} · {c.points}/{c.maxPoints} pts</span></p>
                  <StatusPill status={c.status} />
                </div>
                <p className="mt-1 text-sm text-[color:var(--ink-2)]">{c.evidence}</p>
                {c.status !== "pass" && <p className="mt-1 text-sm text-[color:var(--ink-2)]"><strong>Fix:</strong> {c.fix}</p>}
              </li>
            ))}
          </ul>
        </details>
        <p className="mt-3 text-xs text-[color:var(--ink-3)]">Page facts — title: “{report.pageFacts.title || "(missing)"}” · H1: “{report.pageFacts.h1 || "(missing)"}” · ~{report.pageFacts.wordCount} words · {report.pageFacts.ctaCount} CTAs · {(report.pageFacts.htmlBytes / 1024).toFixed(0)} KB HTML · {report.pageFacts.responseMs} ms. Method & limits: <Link href="/methodology" className="underline">methodology</Link>.</p>
      </section>

      <section className="mt-12 grid gap-5 lg:grid-cols-2" aria-label="Next steps">
        <ShareBar score={report.score} grade={report.grade} topIssue={report.topIssues[0]?.label} scanId={id} />
        <EmailCapture source="scan-result" scanId={id} title="Get your top 3 fixes by email (+ rescan reminder)"
          blurb="We'll send this result, the three fixes in checklist form, and one nudge in a few days to rescan and see your improvement. Opt-in only, unsubscribe anytime." cta="Email my fixes" />
      </section>

      <section className="mt-12" aria-label="Upgrade">
        <Card className="border-[color:var(--ink)]">
          <div className="grid items-start gap-8 lg:grid-cols-[1fr_auto]">
            <div>
              <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--accent)]">The paid audit — depth, not secrets</p>
              <h2 className="mt-2 text-2xl font-bold tracking-tight">Want the rewrites done for you?</h2>
              <ul className="mt-4 space-y-2 text-[15px] text-[color:var(--ink-2)]">
                <li>✓ Headline + subheadline options written for <em>your</em> offer</li>
                <li>✓ CTA rewrite set, FAQ draft, trust-gap plan</li>
                <li>✓ 7-day fix plan, one 45-minute fix per day (Fix Pack)</li>
                <li>✓ Missing an agreed section? Revision or refund — <Link href="/refund" className="underline">policy</Link></li>
              </ul>
              {!paymentsLive && <p className="mt-4 rounded-lg bg-[#fffbeb] px-4 py-3 text-sm text-[#92400e]">Checkout opens at launch — join the list below for first access at launch pricing. No card taken today, no fake countdown.</p>}
            </div>
            <div className="flex flex-col gap-3">
              <Btn href="/pricing">{paymentsLive ? "Get the Full Audit — $39" : "See plans & join launch list"}</Btn>
              <Btn href="/sample-report" variant="ghost">Read a full sample first</Btn>
            </div>
          </div>
        </Card>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold tracking-tight">Fix something? Rescan free.</h2>
        <p className="mt-2 max-w-2xl text-[15px] text-[color:var(--ink-2)]">Apply your quick win, then run it again — improvement is the most shareable result there is. Or take the structured route with the <Link href="/challenge" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">5-Day Clarity Challenge</Link>.</p>
        <div className="mt-5 max-w-2xl"><ScanForm compact /></div>
      </section>
    </Container>
  );
}
