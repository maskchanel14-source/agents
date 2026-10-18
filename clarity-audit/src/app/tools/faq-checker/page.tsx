import type { Metadata } from "next";
import ExtraChecker from "@/components/ExtraCheckers";
import { Container, Eyebrow } from "@/components/ui";

export const metadata: Metadata = { title: "FAQ Coverage Checker (Free)", description: "Free FAQ checker: does your landing page FAQ answer fit, time, delivery, after-pay, and refund? Instant coverage check." };

export default function FaqChecker() {
  return (
    <Container className="max-w-3xl py-14">
      <Eyebrow>Free tool</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">FAQ Coverage Checker</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">An FAQ is your objection-handling closer. Paste yours and check it covers the five questions that silently decide the sale.</p>
      <div className="mt-8"><ExtraChecker kind="faq" /></div>
    </Container>
  );
}
