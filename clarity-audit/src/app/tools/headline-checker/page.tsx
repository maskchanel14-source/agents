import type { Metadata } from "next";
import Link from "next/link";
import MiniChecker from "@/components/MiniCheckers";
import { Container, Eyebrow, FaqList } from "@/components/ui";

export const metadata: Metadata = { title: "Headline Clarity Checker (Free)", description: "Free headline checker for landing pages: outcome, audience, length, and hype — instant feedback, runs in your browser." };

export default function HeadlineChecker() {
  return (
    <Container className="max-w-3xl py-14">
      <Eyebrow>Free tool</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Headline Clarity Checker</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Your headline is the five-second filter. Test a draft against the five checks our full scanner weights most — then read the <Link href="/resources/headline-formulas" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">10 headline formulas</Link> if you need a rewrite.</p>
      <div className="mt-8"><MiniChecker kind="headline" /></div>
      <section className="prose-audit mt-12">
        <h2 className="mb-3 text-2xl font-bold text-[color:var(--ink)]">What “clear” means here</h2>
        <p>A clear headline names an <strong>outcome</strong> (what changes), an <strong>audience</strong> (who it's for), fits in <strong>one glance</strong> (20–90 characters), and skips hype filler. It is a comprehension check, not a creativity grade — a passing headline can still be boring, and that's what the subheadline is for.</p>
      </section>
      <div className="mt-10"><FaqList faqs={[
        { q: "Does this use AI?", a: "No. Transparent rules, running locally in your browser — the same philosophy as the full scanner's public rubric." },
        { q: "My headline passes but conversions are low. Now what?", a: "The headline gets them to read line two; it can't rescue a weak offer or missing proof. Run the full free scan to find the next leak." },
      ]} /></div>
    </Container>
  );
}
