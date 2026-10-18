import type { Metadata } from "next";
import Link from "next/link";
import { Container, Eyebrow, Card } from "@/components/ui";

export const metadata: Metadata = {
  title: "Methodology — The 100-Point Clarity Rubric, Fully Public",
  description: "How the Clarity Audit score works: all 25 checks, weights, evidence rules, and honest limits. No black-box scoring.",
};

const RUBRIC = [
  ["Message clarity", 25, [["H1 present", "A single <h1> exists in the HTML"], ["Headline length", "20–90 characters = one glance"], ["Outcome language", "Benefit words near the top (get, build, without, so you can…)"], ["Audience named", "“For…”, “helping…” + a group noun in the hero"], ["Title ↔ H1 alignment", "Shared keywords between tab title and headline"]]],
  ["CTA & next step", 20, [["CTA present", "Button/link with an action verb exists"], ["CTA early", "First CTA in the top ~15 KB of HTML (above-fold proxy)"], ["CTA specific", "Not “Submit/Click here/Learn more” alone"], ["CTA repeated", "Same primary action appears ≥2×"]]],
  ["Trust & proof", 15, [["Social proof", "Testimonial/review/rating language present"], ["Contact path", "Email, phone, or contact link detectable"], ["Privacy linked", "A privacy reference exists"], ["Human presence", "About/intro language or imagery"]]],
  ["Offer transparency", 15, [["Price visible", "A currency amount or pricing reference exists"], ["Deliverables listed", "≥4 list items (what-you-get proxy)"], ["FAQ present", "FAQ section or FAQPage schema"], ["Risk reversal", "Guarantee/refund language present"]]],
  ["Form friction", 10, [["Form/booking exists", "A <form> or booking reference exists"], ["Form short", "≤5 required attributes, ≤8 inputs"], ["Email capture", "An email input offers a smaller first yes"]]],
  ["Mobile & basics", 15, [["Viewport", "meta viewport tag present"], ["HTML weight", "Document ≤ 500 KB"], ["Image alt text", "≥70% of images have non-empty alt"], ["HTTPS", "Final URL is https://"], ["Response time", "HTML fetched in ≤ 3s from the scanner"]]],
] as const;

export default function Methodology() {
  return (
    <Container className="max-w-4xl py-14">
      <Eyebrow>Methodology</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">The whole rubric. No black box.</h1>
      <p className="prose-audit mt-5 text-lg">
        <p>The Clarity Score operationalizes the <strong>5-second test</strong>: show a page to a stranger for five seconds; can they say what's offered, who it's for, and what to do next? Twenty deterministic checks, each citing literal evidence from your public HTML. Weights reflect how early in the skim-path each element is encountered by buyers of coaching, course, and consulting offers.</p>
      </p>

      <div className="mt-10 space-y-6">
        {RUBRIC.map(([cat, pts, checks]) => (
          <Card key={cat}>
            <h2 className="font-bold">{cat} <span className="ml-1 text-sm font-normal text-[color:var(--ink-3)]">{pts} of 100 points</span></h2>
            <ul className="mt-3 space-y-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
              {checks.map(([name, rule]) => <li key={name}><strong className="text-[color:var(--ink)]">{name}:</strong> {rule}</li>)}
            </ul>
          </Card>
        ))}
      </div>

      <section className="prose-audit mt-12">
        <h2 className="mb-3 text-2xl font-bold tracking-tight text-[color:var(--ink)]">Evidence rules</h2>
        <p>Every point is earned by something <em>found</em>, never assumed. If the scanner can't see it in the HTML, it isn't scored as present — and the report says exactly what was looked for. Pages that render critical content only via client-side JavaScript may score lower than they look; that's disclosed here rather than hidden, and it also happens to reflect what search crawlers and slow phones experience.</p>
        <h2 className="mb-3 mt-8 text-2xl font-bold tracking-tight text-[color:var(--ink)]">What the score cannot do</h2>
        <p>It cannot measure demand for your offer, the quality of your teaching or coaching, your traffic sources, or rendered visual design. It does not predict or guarantee revenue, rankings, or conversion rates. A high score means “a cold visitor can understand this fast” — nothing more, and nothing less useful.</p>
        <h2 className="mb-3 mt-8 text-2xl font-bold tracking-tight text-[color:var(--ink)]">Benchmarks & averages</h2>
        <p>We show an on-site average only when at least 10 real scans back it, and we say how many. We never publish “industry averages” we didn't measure. The public data study documents its own sample and limits on its page.</p>
        <h2 className="mb-3 mt-8 text-2xl font-bold tracking-tight text-[color:var(--ink)]">Scanner safety</h2>
        <p>The scanner fetches a page only when a user submits its URL. It blocks private, loopback, link-local, and cloud-metadata addresses, follows at most 3 redirects (re-validating each), caps downloads at 1.5 MB, times out at 10 seconds, and never submits forms or logs in. Fetched content is analyzed as data, never executed.</p>
      </section>

      <p className="mt-10 text-[15px]">Ready when you are: <Link href="/#scan" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">score your page free →</Link> or inspect the <Link href="/sample-report" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">sample report</Link> first.</p>
    </Container>
  );
}
