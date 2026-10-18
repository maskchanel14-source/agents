import type { Metadata } from "next";
import Link from "next/link";
import { Container, Eyebrow, Card, FaqList } from "@/components/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Support", description: "Get help with scans, reports, billing, and deletion requests. A human reads support email." };

export default function Support() {
  return (
    <Container className="max-w-3xl py-14">
      <Eyebrow>Support</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">A human reads this inbox.</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Email <a href={`mailto:${SITE.supportEmail}`} className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">{SITE.supportEmail}</a> — aim: first reply within 1 business day. Include your scan/report link if your question is about a specific result.</p>
      <div className="mt-9 grid gap-5 sm:grid-cols-2">
        <Card><h2 className="font-bold">Scan problems</h2><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">“Could not be fetched” usually means the page blocks automated checks, needs login, or is down. Try the final public URL. Still failing? Email us the URL.</p></Card>
        <Card><h2 className="font-bold">Reports & billing</h2><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">Missing section, wrong tier, duplicate charge — see the <Link href="/refund" className="underline">refund policy</Link>, then email us. Humans make final billing decisions.</p></Card>
        <Card><h2 className="font-bold">Privacy & deletion</h2><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">Ask what we hold or request deletion any time: {SITE.supportEmail}. Unsubscribe links are in every email.</p></Card>
        <Card><h2 className="font-bold">Partnerships & press</h2><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">Widget embeds, directory listings, data-study citations — same inbox, subject line “Partner”. Ambassadors: <Link href="/affiliates" className="underline">apply here</Link>.</p></Card>
      </div>
      <section className="mt-12"><h2 className="mb-4 text-2xl font-bold tracking-tight">Quick answers</h2>
        <FaqList faqs={[
          { q: "Why did my page score lower than it looks?", a: "The scanner reads HTML like a crawler. Content injected late by JavaScript, or meaning carried only by images, can be under-credited. The methodology page explains each rule; paid reports note where human review should override a check." },
          { q: "Can I rescan after fixing things?", a: "Yes — free, up to 10/hour. Rescanning is the point: fix, verify, share the improvement." },
          { q: "Do you store my page content?", a: "We store the extracted findings (scores, evidence snippets) so result links work, per the privacy policy. Deletion on request." },
        ]} />
      </section>
    </Container>
  );
}
