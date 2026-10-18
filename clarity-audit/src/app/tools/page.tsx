import type { Metadata } from "next";
import Link from "next/link";
import { Container, Eyebrow, Card } from "@/components/ui";
import ScanForm from "@/components/ScanForm";

export const metadata: Metadata = { title: "Free Landing Page Tools", description: "Free micro-tools: headline clarity checker, CTA strength checker, and the full 100-point landing page clarity scanner." };

export default function Tools() {
  return (
    <Container className="py-14">
      <Eyebrow>Free tools</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Fix the blur, one element at a time.</h1>
      <p className="mt-4 max-w-2xl text-lg leading-relaxed text-[color:var(--ink-2)]">Every tool is free and shows its work. More checkers (FAQ coverage, trust signals, form friction) are on the roadmap — the full scanner already covers them today.</p>
      <div className="mt-9 grid gap-5 md:grid-cols-3">
        <Card><h2 className="font-bold">Landing Page Clarity Scanner</h2><p className="mt-2 text-[15px] text-[color:var(--ink-2)]">The full 100-point, evidence-based audit of your live page.</p><p className="mt-3 font-semibold text-[color:var(--accent)]">Use the form below ↓</p></Card>
        <Card><h2 className="font-bold">Headline Clarity Checker</h2><p className="mt-2 text-[15px] text-[color:var(--ink-2)]">Draft-stage feedback on outcome, audience, and length — runs in your browser.</p><Link href="/tools/headline-checker" className="mt-3 inline-block font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Open the checker →</Link></Card>
        <Card><h2 className="font-bold">CTA Strength Checker</h2><p className="mt-2 text-[15px] text-[color:var(--ink-2)]">Score button text against verb + object + outcome.</p><Link href="/tools/cta-checker" className="mt-3 inline-block font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Open the checker →</Link></Card>
      </div>
      <div className="mt-10 max-w-2xl"><ScanForm /></div>
    </Container>
  );
}
