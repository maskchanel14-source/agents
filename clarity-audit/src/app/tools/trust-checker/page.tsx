import type { Metadata } from "next";
import ExtraChecker from "@/components/ExtraCheckers";
import { Container, Eyebrow } from "@/components/ui";

export const metadata: Metadata = { title: "Trust Signal Checker (Free)", description: "Free trust-signal checker for landing pages: proof, reachability, price anchor, risk reversal, human presence — scored instantly." };

export default function TrustChecker() {
  return (
    <Container className="max-w-3xl py-14">
      <Eyebrow>Free tool</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Trust Signal Checker</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Strangers buy when six quiet questions are answered. Paste your page copy and see which trust signals are missing.</p>
      <div className="mt-8"><ExtraChecker kind="trust" /></div>
    </Container>
  );
}
