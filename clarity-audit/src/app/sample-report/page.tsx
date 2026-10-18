import type { Metadata } from "next";
import Link from "next/link";
import { demoReport } from "@/lib/demo";
import { buildReportMarkdown } from "@/lib/reportMarkdown";
import { Container, Eyebrow, Btn, Card, ScoreRing, StatusPill } from "@/components/ui";

export const metadata: Metadata = {
  title: "Sample Audit Report — See Exactly What You'd Buy",
  description: "A complete sample Clarity Audit generated from an illustrative coach page: all 25 checks, evidence, fixes, rewrite pack, FAQ draft, and 7-day plan.",
};

export default function SampleReport() {
  const report = demoReport();
  const doc = buildReportMarkdown(report, "fixpack");
  return (
    <Container className="py-14">
      <Eyebrow>Sample report</Eyebrow>
      <h1 className="mt-3 max-w-3xl text-4xl font-extrabold tracking-tight">Exactly what a paid audit looks like — before you pay.</h1>
      <p className="mt-4 max-w-3xl text-lg leading-relaxed text-[color:var(--ink-2)]">
        This is a real output of our generator, run on an <strong>illustrative example coaching page</strong> (labeled as such — not a customer). It shows the Fix Pack tier: full findings, rewrite pack, FAQ draft, and the 7-day plan. Your report runs on your real page.
      </p>

      <div className="mt-9 grid items-center gap-8 rounded-2xl border border-[color:var(--line)] bg-white p-8 sm:grid-cols-[auto_1fr]">
        <ScoreRing score={report.score} />
        <div>
          <p className="text-xl font-bold">{report.grade} — the example page's verdict</p>
          <p className="mt-2 leading-relaxed text-[color:var(--ink-2)]">{report.gradeNote}</p>
          <p className="mt-3 text-sm text-[color:var(--ink-3)]">Example headline found: “{report.pageFacts.h1}” · {report.pageFacts.ctaCount} CTA(s) · {report.pageFacts.formCount} form(s)</p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Btn href="/scan/demo" variant="accent">Open the interactive sample result</Btn>
            <a href="/api/report?scan=demo&tier=fixpack" className="inline-flex min-h-[48px] items-center rounded-xl border border-[color:var(--line)] bg-white px-6 text-[15px] font-semibold hover:border-[color:var(--ink-3)]">Download sample document (.md)</a>
          </div>
        </div>
      </div>

      <div className="mt-10 grid gap-5 lg:grid-cols-2">
        <Card>
          <h2 className="font-bold">Top issues in the sample</h2>
          <ul className="mt-4 space-y-4">
            {report.topIssues.map((c) => (
              <li key={c.id}>
                <div className="flex flex-wrap items-center gap-2"><span className="font-semibold">{c.label}</span><StatusPill status={c.status} /></div>
                <p className="mt-1 text-sm leading-relaxed text-[color:var(--ink-2)]"><strong>Found:</strong> {c.evidence}</p>
                <p className="text-sm leading-relaxed text-[color:var(--ink-2)]"><strong>Fix:</strong> {c.fix}</p>
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <h2 className="font-bold">What's in each tier (this sample = Fix Pack)</h2>
          <ul className="mt-4 space-y-2.5 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
            <li><strong className="text-[color:var(--ink)]">Quick Audit · $19</strong> — all {report.checks.length} checks with evidence + fixes, ranked.</li>
            <li><strong className="text-[color:var(--ink)]">Full Audit · $39</strong> — + headline/CTA rewrite pack and an FAQ draft for your offer.</li>
            <li><strong className="text-[color:var(--ink)]">Fix Pack · $79</strong> — + a 7-day plan (one fix/day) and a before/after rescan.</li>
            <li>Missing an agreed section? Revision or refund — <Link href="/refund" className="underline">policy</Link>.</li>
          </ul>
          <Btn href="/pricing" className="mt-6">See pricing</Btn>
        </Card>
      </div>

      <section className="mt-12" aria-label="Full sample document">
        <h2 className="text-2xl font-bold tracking-tight">The full sample document</h2>
        <p className="mt-2 text-[15px] text-[color:var(--ink-2)]">Plain-text rendering below; paid delivery arrives as a formatted document + email.</p>
        <pre className="mt-5 max-h-[640px] overflow-auto whitespace-pre-wrap rounded-2xl border border-[color:var(--line)] bg-[#0b0f17] p-6 font-mono text-[13px] leading-relaxed text-[#e5e7eb]">{doc}</pre>
      </section>

      <p className="mt-10 text-[15px] text-[color:var(--ink-2)]">Like the format? <Link href="/#scan" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Run the free version on your own page →</Link></p>
    </Container>
  );
}
