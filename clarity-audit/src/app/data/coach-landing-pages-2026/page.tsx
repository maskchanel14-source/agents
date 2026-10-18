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

      <section className="prose-audit mt-10">
        <h2 className="mb-3 text-2xl font-bold text-[color:var(--ink)]">Batch-study protocol (in progress)</h2>
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
