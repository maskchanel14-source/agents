import type { Metadata } from "next";
import { Container, Eyebrow } from "@/components/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Terms of Service", description: "Terms for using the Clarity Audit scanner and buying audit reports. Draft pending final legal review." };

export default function Terms() {
  return (
    <Container className="prose-audit max-w-3xl py-14">
      <Eyebrow>Legal</Eyebrow>
      <h1 className="mb-4 mt-3 text-4xl font-extrabold tracking-tight text-[color:var(--ink)]">Terms of Service</h1>
      <p className="rounded-xl bg-[#eff6ff] px-4 py-3 text-sm text-[color:var(--accent)]">Plain-language draft — final version subject to the operator's legal review before commercial launch.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">The service</h2>
      <p>Clarity Audit provides automated clarity checks of public web pages against a published rubric, plus paid report tiers. Results are informational. We do not guarantee sales, traffic, rankings, conversion rates, or any business outcome.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Acceptable use</h2>
      <p>Submit only URLs you own, manage, or have a legitimate reason to review (e.g., your own or a client's public page). Do not use the scanner to probe private/internal systems (it blocks them by design), overwhelm targets, or violate any site's terms. Rate limits apply; abuse may be blocked.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Paid reports</h2>
      <p>One-time purchases in USD via a major payment processor. Delivery by email/link after payment, generated automatically (human follow-up within 1 business day if needed). See the Refund Policy for the revision/refund commitment. Report content is licensed for your business use; you may share your report with your team and clients for the audited project.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Affiliate program</h2>
      <p>Ambassadors must disclose commissions, avoid spam and false claims, and never self-refer. Commissions are paid on valid, non-refunded first orders after the refund window, per the written terms provided at approval. Violations void commissions.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Liability</h2>
      <p>The service is provided “as is” within the limits of applicable law. To the extent permitted, liability is limited to amounts paid for the relevant report. Nothing here limits liability that cannot legally be limited.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Contact</h2>
      <p>{SITE.supportEmail}</p>
    </Container>
  );
}
