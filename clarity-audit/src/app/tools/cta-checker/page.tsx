import type { Metadata } from "next";
import Link from "next/link";
import MiniChecker from "@/components/MiniCheckers";
import { Container, Eyebrow, FaqList } from "@/components/ui";

export const metadata: Metadata = { title: "CTA Strength Checker (Free)", description: "Free call-to-action checker: does your button say what happens next? Verb + object + outcome scoring, instant and private." };

export default function CtaChecker() {
  return (
    <Container className="max-w-3xl py-14">
      <Eyebrow>Free tool</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">CTA Strength Checker</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">A button's job is to say what happens next. Score yours against the formula — then steal a better one from the <Link href="/resources/cta-examples" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">40 CTA examples</Link>.</p>
      <div className="mt-8"><MiniChecker kind="cta" /></div>
      <section className="prose-audit mt-12">
        <h2 className="mb-3 text-2xl font-bold text-[color:var(--ink)]">The formula: verb + object + outcome</h2>
        <p>“Book” (verb) “my free clarity call” (object) — with the outcome carried by the words around it. Generic text (“Submit”, “Click here”) makes the visitor gamble; specific text lets them decide. Also keep one primary CTA per screen: five competing buttons convert like zero.</p>
      </section>
      <div className="mt-10"><FaqList faqs={[
        { q: "First person or second person?", a: "“Start my plan” sometimes beats “Start your plan” — it's test-worthy, not a law. Clarity of the object matters more than the pronoun." },
        { q: "Where should the CTA sit?", a: "In the hero next to the promise, then repeated after each proof block. The full scanner checks both placement and repetition on your live page." },
      ]} /></div>
    </Container>
  );
}
