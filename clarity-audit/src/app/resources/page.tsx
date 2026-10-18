import type { Metadata } from "next";
import Link from "next/link";
import { RESOURCES } from "@/lib/content";
import { Container, Eyebrow, Card } from "@/components/ui";

export const metadata: Metadata = { title: "Resources — Landing Page Clarity Guides", description: "Practical guides: audit checklists, headline formulas, CTA examples, trust signals, and niche playbooks for coaches, courses, and consultants." };

export default function Resources() {
  return (
    <Container className="py-14">
      <Eyebrow>Resources</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Clarity, in writing.</h1>
      <p className="mt-4 max-w-2xl text-lg leading-relaxed text-[color:var(--ink-2)]">Every guide is built around the same public rubric as the scanner — read the why, then run the check free.</p>
      <div className="mt-9 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {RESOURCES.map((a) => (
          <Card key={a.slug} className="flex flex-col">
            <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--ink-3)]">{a.keyword} · {a.readMins} min</p>
            <h2 className="mt-2 font-bold leading-snug"><Link href={`/resources/${a.slug}`} className="hover:underline underline-offset-4">{a.title}</Link></h2>
            <p className="mt-2 flex-1 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{a.description}</p>
            <Link href={`/resources/${a.slug}`} className="mt-4 font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Read the guide →</Link>
          </Card>
        ))}
      </div>
    </Container>
  );
}
