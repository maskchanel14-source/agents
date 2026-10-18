import type { Metadata } from "next";
import { Container, Eyebrow } from "@/components/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Refund Policy", description: "Simple and honest: missing an agreed report section? We revise or refund within 14 days. No outcome guarantees, no fine-print games." };

export default function Refund() {
  return (
    <Container className="prose-audit max-w-3xl py-14">
      <Eyebrow>Legal</Eyebrow>
      <h1 className="mb-4 mt-3 text-4xl font-extrabold tracking-tight text-[color:var(--ink)]">Refund Policy</h1>
      <p className="rounded-xl bg-[#eff6ff] px-4 py-3 text-sm text-[color:var(--accent)]">Plain-language draft — final version subject to the operator's approval before commercial launch.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">The commitment</h2>
      <p>If your paid report is missing any section listed for your tier on the pricing page, tell us within <strong>14 days</strong> of delivery. Your choice: we <strong>revise</strong> the report to include it, or we <strong>refund you in full</strong>. No exit interview, no retention script.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Also covered</h2>
      <p>Duplicate charges, failed delivery we cannot fix, and purchases made in clear error (e.g., wrong tier) reported promptly — email {SITE.supportEmail} and a human will sort it out.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">What no audit can promise</h2>
      <p>We do not guarantee sales, leads, rankings, or conversion improvements, so “my sales didn't rise” is not itself a refund ground — clarity is one input among offer, traffic, and market. What we do stand behind: completeness, evidence-based findings, and delivery as described. The free scanner and full sample report exist so you can judge the format before spending anything.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">How refunds are paid</h2>
      <p>Back to the original payment method via the payment processor, typically within 5–10 business days of approval. Final refund decisions rest with the human operator.</p>
    </Container>
  );
}
