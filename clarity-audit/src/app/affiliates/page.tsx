import type { Metadata } from "next";
import AffiliateForm from "@/components/AffiliateForm";
import { Container, Eyebrow, Card } from "@/components/ui";

export const metadata: Metadata = {
  title: "Ambassador Program — Earn 30% Referring the Clarity Audit",
  description: "For coaches, creators, agencies, and newsletter writers: share the free clarity scanner, earn 30% on first paid audits. Human-reviewed, compliance-first.",
};

export default function Affiliates() {
  return (
    <Container className="py-14">
      <div className="grid items-start gap-12 lg:grid-cols-2">
        <div>
          <Eyebrow>Affiliates & ambassadors</Eyebrow>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Your audience has landing pages. Help them fix the blurry ones.</h1>
          <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Share the free scanner (genuinely useful, no email wall) and earn <strong className="text-[color:var(--ink)]">30% of the first paid order</strong> from anyone who upgrades through your link. Built for coaches, course creators, consultants, agencies, template sellers, and newsletter writers.</p>
          <div className="mt-8 space-y-4">
            <Card><h2 className="font-bold">What you get</h2><ul className="mt-2 list-disc space-y-1.5 pl-5 text-[15px] text-[color:var(--ink-2)]"><li>Your tracked link (?ref=you) + embeddable badge/widget</li><li>Swipe copy that leads with value, not hype</li><li>Free Full Audit of your own page at approval</li><li>Co-branded resource page for partners with an audience fit</li></ul></Card>
            <Card><h2 className="font-bold">The compliance deal (non-negotiable)</h2><ul className="mt-2 list-disc space-y-1.5 pl-5 text-[15px] text-[color:var(--ink-2)]"><li>Disclose the relationship wherever you promote (#ad / “I earn a commission”)</li><li>No spam, no fake claims, no income/conversion guarantees</li><li>No self-referrals; commissions pay after the refund window on valid orders</li><li>We review applications by hand — quality of fit over audience size</li></ul></Card>
            <p className="text-xs leading-relaxed text-[color:var(--ink-3)]">Commission rate and payout schedule are confirmed in writing at approval (launch rate 30%). Final program terms are human-approved before first payout; payouts via the payment provider once connected.</p>
          </div>
        </div>
        <AffiliateForm />
      </div>
    </Container>
  );
}
