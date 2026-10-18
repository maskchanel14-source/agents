import type { Metadata } from "next";
import Link from "next/link";
import { Container, Eyebrow, FaqList, jsonLdScript } from "@/components/ui";
import EmailCapture from "@/components/EmailCapture";
import { SITE } from "@/lib/site";

export const metadata: Metadata = {
  title: "Pricing — Quick Audit $19, Full Audit $39, Fix Pack $79",
  description: "Transparent pricing for the Instant Website Clarity Audit: Quick $19, Full $39 (recommended), Fix Pack $79, Template Kit $49. Honest refund policy, no subscriptions.",
};

const FAQS = [
  { q: "What do I actually receive?", a: "A report document generated from your real page: every check with evidence and fixes, plus tier extras (rewrites, FAQ draft, 7-day plan). Delivered by email and a private link. Read the free sample report to see the exact format before paying anything." },
  { q: "How fast is delivery?", a: "The free score is instant. Paid reports are generated automatically right after checkout and emailed — if anything needs a human touch, within 1 business day." },
  { q: "What is the refund policy?", a: "If your report is missing any section listed for your tier, we revise it or refund you in full — your choice, within 14 days. We do not (and cannot honestly) guarantee sales, rankings, or conversion lifts. Full text on the refund page." },
  { q: "Is this a subscription?", a: "No. One-time payments only. No auto-renewing anything, no card kept on file by us (payments run through a major processor)." },
  { q: "Can I audit a client's page?", a: "Yes — any public URL. The Agency 5-Pack covers five Full Audits you can use across clients." },
];

export default function Pricing() {
  const paymentsLive = SITE.paymentsConnected;
  return (
    <Container className="py-14">
      {jsonLdScript({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: FAQS.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })) })}
      <div className="max-w-2xl">
        <Eyebrow>Pricing</Eyebrow>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Pay for depth, not for secrets.</h1>
        <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Your score, top issues, and quick win are always free. Paid tiers add the full breakdown, copy rewrites, and a day-by-day plan. One-time prices in USD, no subscriptions, honest refund policy.</p>
        {!paymentsLive && (
          <p className="mt-5 rounded-xl bg-[#fffbeb] px-5 py-4 text-[15px] leading-relaxed text-[#92400e]">
            <strong>Launch note:</strong> checkout is being connected now. Join the launch list on any tier below to lock launch pricing — we'll email you the moment orders open. No card today, no fake countdown.
          </p>
        )}
      </div>

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {SITE.offers.map((o) => (
          <article key={o.slug} className={`relative flex flex-col rounded-2xl border bg-white p-6 shadow-[0_1px_2px_rgba(11,15,23,0.04)] ${o.recommended ? "border-2 border-[color:var(--accent)]" : "border-[color:var(--line)]"}`}>
            {o.recommended && <p className="absolute -top-3 left-5 rounded-full bg-[color:var(--accent)] px-3 py-0.5 text-xs font-bold text-white">RECOMMENDED</p>}
            <h2 className="text-lg font-bold">{o.name}</h2>
            <p className="mt-2"><span className="text-4xl font-extrabold tracking-tight">${o.price}</span> <span className="text-sm text-[color:var(--ink-3)]">one-time</span></p>
            <p className="mt-2.5 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{o.blurb}</p>
            <ul className="mt-4 flex-1 space-y-2 text-sm leading-relaxed text-[color:var(--ink-2)]">
              {o.includes.map((i) => <li key={i}>✓ {i}</li>)}
            </ul>
            <a href={`#join-${o.slug}`} className={`mt-6 inline-flex min-h-[48px] items-center justify-center rounded-lg px-5 font-semibold ${o.recommended ? "bg-[color:var(--accent)] text-white hover:bg-[#1e40af]" : "bg-[color:var(--ink)] text-white hover:bg-[#232b3a]"}`}>
              {paymentsLive ? `Get the ${o.name}` : `Join launch list — ${o.name}`}
            </a>
          </article>
        ))}
      </div>

      <section className="mt-10" aria-label="Bundles">
        <h2 className="text-2xl font-bold tracking-tight">Bundles (better value, same honesty)</h2>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          {SITE.bundles.map((b) => (
            <div key={b.name} className="rounded-2xl border border-[color:var(--line)] bg-white p-6">
              <h3 className="font-bold">{b.name} — ${b.price}</h3>
              <p className="mt-1.5 text-[15px] text-[color:var(--ink-2)]">{b.note}</p>
              <a href="#join-bundle" className="mt-3 inline-block font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">{paymentsLive ? "Get the bundle →" : "Join launch list →"}</a>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-12 grid gap-5 lg:grid-cols-2" aria-label="Join the launch list">
        <div id="join-full-audit">
          <EmailCapture source="pricing-full-audit" plan="full-audit" title="Most popular: Full Audit ($39)"
            blurb="Launch-list members get first access at launch pricing, plus the free 5-Day Clarity Challenge while you wait." cta="Notify me at launch" />
        </div>
        <div id="join-bundle">
          <EmailCapture source="pricing-bundle" plan="bundle" title="Interested in a bundle or agency pack?"
            blurb="Tell us where to send launch access. Agencies: the 5-Pack is transferable across client pages." cta="Notify me at launch" />
        </div>
      </section>

      <section className="mx-auto mt-14 max-w-3xl">
        <h2 className="mb-5 text-2xl font-bold tracking-tight">Before you pay for anything</h2>
        <FaqList faqs={FAQS} />
        <p className="mt-5 text-[15px] text-[color:var(--ink-2)]">Still deciding? The <Link href="/#scan" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">free scanner</Link> and the <Link href="/sample-report" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">full sample report</Link> show exactly what the paid version builds on.</p>
      </section>
    </Container>
  );
}
