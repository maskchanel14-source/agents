import Link from "next/link";
import ScanForm from "@/components/ScanForm";
import EmailCapture from "@/components/EmailCapture";
import { Container, Eyebrow, Btn, Card, FaqList, jsonLdScript } from "@/components/ui";
import { SITE } from "@/lib/site";

const FAQS = [
  { q: "Is the clarity score really free?", a: "Yes — score, top 3 issues, and a quick-win fix, with no email required. Paid tiers ($19–$79) add the full 25-check breakdown with rewrites and a 7-day fix plan." },
  { q: "What does the scanner actually do to my page?", a: "It fetches your public HTML once, on your request, and checks it against a documented 100-point rubric (headline, CTA, proof, pricing, forms, mobile basics). It never logs in, never submits forms, and blocks private/internal addresses." },
  { q: "Who is this built for?", a: "Coaches, course creators, consultants, and small service businesses selling through landing pages. The rubric weights what those buyers check in the first five seconds." },
  { q: "Will a better score guarantee more sales?", a: "No — and beware anyone who promises that. Clarity removes friction between a qualified visitor and your offer; it cannot create demand for an offer nobody wants. It makes sure the demand you earn is not leaked by confusion." },
  { q: "How is this different from a generic website grader?", a: "Every finding cites evidence from your actual page and ships with a concrete fix. The full rubric is public on the methodology page — no black-box score." },
];

export default function Home() {
  return (
    <>
      {jsonLdScript({ "@context": "https://schema.org", "@type": "WebApplication", name: SITE.product, applicationCategory: "BusinessApplication", offers: { "@type": "Offer", price: "0", priceCurrency: "USD" } })}
      {jsonLdScript({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: FAQS.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })) })}

      <section className="border-b border-[color:var(--line)]">
        <Container className="py-16 sm:py-24">
          <div className="max-w-3xl">
            <Eyebrow>Free landing page clarity score</Eyebrow>
            <h1 className="mt-4 text-4xl font-extrabold leading-[1.05] tracking-tight sm:text-6xl">
              Would a stranger understand your offer in 5 seconds?
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-relaxed text-[color:var(--ink-2)]">
              Paste your public landing page. Get an instant, evidence-based clarity score — your top issues, one quick win, and the exact fixes, scored against a public 100-point rubric. Built for coaches, course creators, and consultants.
            </p>
          </div>
          <div id="scan" className="mt-9 max-w-2xl scroll-mt-24">
            <ScanForm />
          </div>
          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Btn href="/sample-report" variant="ghost">See a sample audit first</Btn>
            <Link href="/methodology" className="text-sm font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">How scoring works (full rubric) →</Link>
          </div>
          <dl className="mt-12 grid max-w-2xl grid-cols-3 gap-6 border-t border-[color:var(--line)] pt-7">
            {[["25", "evidence-based checks"], ["~10s", "from URL to score"], ["$0", "score + top issues free"]].map(([n, l]) => (
              <div key={l}><dt className="sr-only">{l}</dt><dd className="text-2xl font-extrabold tracking-tight">{n}</dd><dd className="mt-0.5 text-sm text-[color:var(--ink-3)]">{l}</dd></div>
            ))}
          </dl>
        </Container>
      </section>

      <section>
        <Container className="py-16">
          <Eyebrow>How it works</Eyebrow>
          <h2 className="mt-3 max-w-2xl text-3xl font-bold tracking-tight">Three steps. No account, no sales call.</h2>
          <div className="mt-9 grid gap-5 md:grid-cols-3">
            {[
              ["1 · Paste your URL", "Any public landing page. The scanner reads it once — securely, with private/internal addresses blocked by design."],
              ["2 · Get your score", "A 0–100 clarity score across six categories, each finding backed by what was literally found on your page."],
              ["3 · Fix & rescan", "Apply the quick win, rescan free, watch the check flip to pass. Want rewrites done for you? That's the paid audit."],
            ].map(([t, d]) => (
              <Card key={t}><h3 className="font-bold">{t}</h3><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{d}</p></Card>
            ))}
          </div>
        </Container>
      </section>

      <section className="border-y border-[color:var(--line)] bg-white">
        <Container className="py-16">
          <Eyebrow>What gets checked</Eyebrow>
          <h2 className="mt-3 max-w-2xl text-3xl font-bold tracking-tight">The 5-second test, turned into 25 checks</h2>
          <div className="mt-9 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[
              ["Message clarity · 25 pts", "Headline presence, glance-length, outcome language, named audience, title↔headline match."],
              ["CTA & next step · 20 pts", "A real action button, visible early, saying what happens next, repeated after proof."],
              ["Trust & proof · 15 pts", "Testimonials/reviews, reachable human, privacy link, a face and a story."],
              ["Offer transparency · 15 pts", "Visible price path, concrete deliverables, objection-killing FAQ, honest risk reversal."],
              ["Form friction · 10 pts", "A way to act that asks for little, early — plus a smaller “yes” for non-buyers."],
              ["Mobile & basics · 15 pts", "Viewport, page weight, alt text, HTTPS, response speed. The unglamorous conversion killers."],
            ].map(([t, d]) => (
              <Card key={t}><h3 className="font-bold">{t}</h3><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{d}</p></Card>
            ))}
          </div>
          <p className="mt-7 text-[15px] text-[color:var(--ink-2)]">Weights, evidence rules, and honest limits are published in full — <Link href="/methodology" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">read the methodology</Link>. No black box, no invented benchmarks.</p>
        </Container>
      </section>

      <section>
        <Container className="py-16">
          <div className="grid items-start gap-10 lg:grid-cols-2">
            <div>
              <Eyebrow>From free score to fixed page</Eyebrow>
              <h2 className="mt-3 text-3xl font-bold tracking-tight">Free tells you <em className="not-italic underline decoration-[color:var(--accent)] decoration-4 underline-offset-4">what's unclear</em>. The audit hands you the rewrites.</h2>
              <ul className="mt-6 space-y-3 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
                <li>✓ Every one of the 25 checks, with evidence from your page</li>
                <li>✓ Headline, subheadline, and CTA rewrite options (Full Audit)</li>
                <li>✓ FAQ draft answering your top 5 objections</li>
                <li>✓ 7-day, one-fix-per-day plan (Fix Pack)</li>
                <li>✓ Honest policy: missing an agreed section? We revise or refund</li>
              </ul>
              <div className="mt-7 flex flex-wrap gap-3">
                <Btn href="/pricing">See pricing — from $19</Btn>
                <Btn href="/sample-report" variant="ghost">Read a full sample</Btn>
              </div>
            </div>
            <EmailCapture source="homepage-challenge" title="Not ready to scan? Take the 5-Day Clarity Challenge"
              blurb="One short email a day: scan → headline → CTA → FAQ → rescan. Free, useful even if you never buy anything." cta="Start the free challenge" />
          </div>
        </Container>
      </section>

      <section className="border-t border-[color:var(--line)]">
        <Container className="py-16">
          <Eyebrow>Free micro-tools</Eyebrow>
          <h2 className="mt-3 text-3xl font-bold tracking-tight">Fix one element at a time</h2>
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            <Card><h3 className="font-bold">Headline Clarity Checker</h3><p className="mt-2 text-[15px] text-[color:var(--ink-2)]">Paste a headline draft; get instant feedback on outcome, audience, and length.</p><Link href="/tools/headline-checker" className="mt-3 inline-block font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Check a headline →</Link></Card>
            <Card><h3 className="font-bold">CTA Strength Checker</h3><p className="mt-2 text-[15px] text-[color:var(--ink-2)]">Is your button text earning the click? Score it against the verb + object + outcome formula.</p><Link href="/tools/cta-checker" className="mt-3 inline-block font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Check a CTA →</Link></Card>
            <Card><h3 className="font-bold">Data: Coach Pages Study</h3><p className="mt-2 text-[15px] text-[color:var(--ink-2)]">We audited our published rubric against real public pages. Method and limits included.</p><Link href="/data/coach-landing-pages-2026" className="mt-3 inline-block font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Read the study →</Link></Card>
          </div>
        </Container>
      </section>

      <section>
        <Container className="max-w-3xl py-8">
          <h2 className="mb-6 text-3xl font-bold tracking-tight">Questions, answered straight</h2>
          <FaqList faqs={FAQS} />
          <div className="mt-10">
            <ScanForm compact />
          </div>
        </Container>
      </section>
    </>
  );
}
