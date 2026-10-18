import type { Metadata } from "next";
import Link from "next/link";
import StudyChart from "@/components/StudyChart";
import EmailCapture from "@/components/EmailCapture";
import { Container, Eyebrow, Card } from "@/components/ui";

export const metadata: Metadata = {
  title: "Coach Landing Page Study 2026: The Most Common Clarity Mistakes",
  description: "An open-methods study of coaching landing pages against a public 100-point clarity rubric. Live aggregate findings, method, sample frame, and limits.",
};

export default function DataStudy() {
  return (
    <Container className="max-w-4xl py-14">
      <Eyebrow>Data study · Open methods</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight">Coach landing pages: the most common clarity mistakes</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">A living study, not a press release. Findings below come from real pages scanned with the same public rubric anyone can run free. When the batch study (protocol below) completes, its dataset summary will be appended here — with the sample frame named and the limits stated.</p>

      <Card className="mt-9">
        <h2 className="font-bold">Live findings (updates with every real scan)</h2>
        <div className="mt-4"><StudyChart /></div>
      </Card>


      <Card className="mt-6">
        <h2 className="font-bold">Pilot batch — 18 Oct 2026 (n = 6 scanned, 2 unreachable)</h2>
        <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
          First run of the protocol: 8 public coach/course offer pages from search results for “business coaching program” and “online course sales page”. Six were scannable; two blocked automated fetching (itself a finding — if our politely-identified scanner can't read a page, some crawlers and slow devices fare worse). Individual sites are never scored-and-named; aggregates only.
        </p>
        <ul className="mt-4 space-y-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
          <li><strong className="text-[color:var(--ink)]">100% (6/6)</strong> failed to name their audience explicitly in the hero (“for [who]”) — the single most common clarity gap.</li>
          <li><strong className="text-[color:var(--ink)]">83% (5/6)</strong> had no email-capture step for non-buyers, and <strong className="text-[color:var(--ink)]">83%</strong> buried the first CTA deep in the page.</li>
          <li><strong className="text-[color:var(--ink)]">67% (4/6)</strong> used no outcome language above the fold.</li>
          <li>Median score <strong className="text-[color:var(--ink)]">80.5/100</strong> — top-ranking pages skew strong (survivorship bias, noted below); the one JavaScript-rendered page scored 28 because its HTML ships almost no readable content, which is precisely what search crawlers see first.</li>
        </ul>
        <p className="mt-3 text-sm text-[color:var(--ink-3)]">Pilot limits: tiny n, search-top sample (visible businesses skew competent), HTML-structural checks only. The full 50-page batch with the documented frame comes next; the runner script is open in our repo.</p>
      </Card>

      <section className="prose-audit mt-10">
        <h2 className="mb-3 text-2xl font-bold text-[color:var(--ink)]">Batch-study protocol (pilot done, full batch next)</h2>
        <p><strong>Sample frame:</strong> 50 publicly linked coaching offer/booking pages, gathered from public directories and search results for “business coach”, “life coach”, “mindset coach” — no login-walled, paywalled, or private pages. URLs will be listed in an appendix by category only; no page is publicly scored-and-named without its own scan being user-shared.</p>
        <p><strong>Instrument:</strong> the published 100-point rubric (<Link href="/methodology" className="underline">methodology</Link>), run by the same scanner available free on this site. Every check is deterministic and evidence-cited; results are reproducible by re-running any URL.</p>
        <p><strong>Analysis:</strong> failure frequency per check, median score, and co-occurrence of failures (e.g., “no price visible” × “no FAQ”). Aggregates only — no individual business is called out.</p>
        <h2 className="mb-3 mt-8 text-2xl font-bold text-[color:var(--ink)]">Limits, stated up front</h2>
        <p>Automated checks read HTML structure, not rendered design or real conversion data. JavaScript-heavy pages may be under-credited. This study measures <em>clarity signals</em>, not business quality — a page can score modestly and sell well on warm traffic, and score highly yet offer something nobody wants. Sampled pages skew toward English-speaking solo/small coaching businesses; findings should not be generalized beyond that frame.</p>
        <h2 className="mb-3 mt-8 text-2xl font-bold text-[color:var(--ink)]">Embed & cite</h2>
        <p>You may embed the live chart by linking this page; an embeddable snapshot ships with the batch-study PDF. Suggested citation: “Clarity Audit — Coach Landing Page Clarity Study (2026), live aggregate, methodology at /methodology.”</p>
      </section>

      <div className="mt-10">
        <EmailCapture source="data-study" title="Get the batch-study PDF when it drops"
          blurb="Full charts, appendix, and the anonymized failure-frequency tables. One email on publication, plus the 5-Day Challenge if you want it." cta="Notify me" />
      </div>
      <p className="mt-8 text-[15px] text-[color:var(--ink-2)]">Curious where your page lands? <Link href="/#scan" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Score it free →</Link></p>
    </Container>
  );
}
