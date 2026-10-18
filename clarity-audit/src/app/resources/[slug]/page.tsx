import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { RESOURCES } from "@/lib/content";
import { Container, Eyebrow, FaqList, jsonLdScript } from "@/components/ui";
import ScanForm from "@/components/ScanForm";
import EmailCapture from "@/components/EmailCapture";

export function generateStaticParams() { return RESOURCES.map((r) => ({ slug: r.slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const a = RESOURCES.find((r) => r.slug === slug);
  if (!a) return { title: "Not found" };
  return { title: a.title, description: a.description, keywords: [a.keyword] };
}

export default async function ResourceArticle({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const a = RESOURCES.find((r) => r.slug === slug);
  if (!a) notFound();
  const related = RESOURCES.filter((r) => r.slug !== slug).slice(0, 3);
  return (
    <Container className="max-w-3xl py-14">
      {jsonLdScript({ "@context": "https://schema.org", "@type": "Article", headline: a.title, description: a.description })}
      {jsonLdScript({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: a.faqs.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })) })}
      <Eyebrow>Guide · {a.readMins} min read</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight">{a.title}</h1>
      <p className="mt-5 text-lg leading-relaxed text-[color:var(--ink-2)]">{a.intro}</p>
      <div className="my-8 rounded-2xl border border-[color:var(--line)] bg-white p-6">
        <p className="font-semibold">Short on time? Run it automatically.</p>
        <p className="mb-4 mt-1 text-sm text-[color:var(--ink-2)]">The free scanner checks your live page against this guide's criteria in ~10 seconds.</p>
        <ScanForm compact />
      </div>
      {a.sections.map((s) => (
        <section key={s.h} className="prose-audit mt-9">
          <h2 className="mb-3 text-2xl font-bold tracking-tight text-[color:var(--ink)]">{s.h}</h2>
          {s.paras.map((p, i) => <p key={i}>{p}</p>)}
          {s.list && <ul className="list-disc space-y-2 pl-6">{s.list.map((li) => <li key={li}>{li}</li>)}</ul>}
        </section>
      ))}
      <section className="mt-12"><h2 className="mb-4 text-2xl font-bold tracking-tight">FAQ</h2><FaqList faqs={a.faqs} /></section>
      <div className="mt-10">
        <EmailCapture source={`resource-${a.slug}`} title="Get the 5-Day Clarity Challenge (free)"
          blurb="Turn this guide into action: one fix per day, verified by re-scanning. Opt-in only, unsubscribe anytime." cta="Send the challenge" />
      </div>
      <nav className="mt-12" aria-label="Related guides">
        <h2 className="text-xl font-bold">Keep going</h2>
        <ul className="mt-3 space-y-2">
          {related.map((r) => <li key={r.slug}><Link href={`/resources/${r.slug}`} className="font-medium text-[color:var(--accent)] underline-offset-4 hover:underline">{r.title} →</Link></li>)}
          <li><Link href="/methodology" className="font-medium text-[color:var(--accent)] underline-offset-4 hover:underline">The full scoring methodology →</Link></li>
        </ul>
      </nav>
    </Container>
  );
}
