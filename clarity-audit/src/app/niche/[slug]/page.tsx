import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { NICHES } from "@/lib/content";
import { Container, Eyebrow, Card, Btn } from "@/components/ui";
import ScanForm from "@/components/ScanForm";

export function generateStaticParams() { return NICHES.map((n) => ({ slug: n.slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const n = NICHES.find((x) => x.slug === slug);
  return n ? { title: n.title, description: n.description } : { title: "Not found" };
}

export default async function NichePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const n = NICHES.find((x) => x.slug === slug);
  if (!n) notFound();
  return (
    <Container className="py-14">
      <div className="max-w-3xl">
        <Eyebrow>For {n.audience}</Eyebrow>
        <h1 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight">{n.hero}</h1>
        <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">The free Clarity Scanner is tuned for {n.audience.toLowerCase()} selling through landing pages. Paste yours — score, top issues, and a quick win in about 10 seconds.</p>
      </div>
      <div className="mt-8 max-w-2xl"><ScanForm /></div>

      <div className="mt-12 grid gap-5 lg:grid-cols-2">
        <Card>
          <h2 className="font-bold">Patterns we keep flagging on {n.audience.toLowerCase()} pages</h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{n.pains.map((p) => <li key={p}>{p}</li>)}</ul>
        </Card>
        <Card>
          <h2 className="font-bold">What the scanner checks for you</h2>
          <ul className="mt-3 space-y-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{n.checks.map((c) => <li key={c}>✓ {c}</li>)}</ul>
        </Card>
      </div>

      <Card className="mt-5">
        <h2 className="font-bold">Example fix (illustrative)</h2>
        <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{n.exampleFix}</p>
        <p className="mt-3 text-sm text-[color:var(--ink-3)]">The paid Full Audit writes three options in this style for your actual offer.</p>
      </Card>

      <div className="mt-10 flex flex-wrap gap-3">
        <Btn href="/sample-report" variant="ghost">See a sample audit</Btn>
        <Btn href="/pricing">Pricing — from $19</Btn>
      </div>
      <p className="mt-6 text-sm text-[color:var(--ink-3)]">Selling to this audience? <Link href="/affiliates" className="underline">Become an ambassador</Link> and earn 30% on referrals.</p>
    </Container>
  );
}
