import type { Metadata } from "next";
import { Container, Eyebrow, Card, Btn } from "@/components/ui";
import ScanForm from "@/components/ScanForm";

export const metadata: Metadata = {
  title: "For Teachable Coaches — Course Page Clarity Audit",
  description: "Free clarity score for Teachable course pages: curriculum as outcomes, price block, guarantee placement, and the enrollment CTA path.",
};

export default function ForTeachable() {
  return (
    <Container className="py-14">
      <div className="max-w-3xl">
        <Eyebrow>For Teachable creators</Eyebrow>
        <h1 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight">Teachable gives you the checkout. Clarity gets them to it.</h1>
        <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Buyers skim course pages for outcome, curriculum, proof, price, and refund. Paste your Teachable sales page for a free 25-check score with evidence and fixes.</p>
      </div>
      <div className="mt-8 max-w-2xl"><ScanForm /></div>
      <div className="mt-12 grid gap-5 lg:grid-cols-2">
        <Card>
          <h2 className="font-bold">Teachable-page patterns we flag</h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
            <li>Curriculum listed as topics ("Module 3: Email") instead of capabilities</li>
            <li>Price first visible on the Teachable checkout page itself</li>
            <li>Guarantee mentioned nowhere near the enroll button</li>
            <li>No fit/not-fit block — refunds end up doing the filtering</li>
            <li>Author bio with credentials but no student proof</li>
          </ul>
        </Card>
        <Card>
          <h2 className="font-bold">Worked fix pattern</h2>
          <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">Before: "Module 3: Email Marketing". After: "Module 3: Write the 5 emails that sell while you sleep (templates inside)". Rewrite each module title as a capability — it's the highest-leverage hour a course page can get.</p>
          <p className="mt-3 text-sm text-[color:var(--ink-3)]">Not affiliated with Teachable. We audit public pages on any platform.</p>
        </Card>
      </div>
      <div className="mt-10 flex flex-wrap gap-3"><Btn href="/resources/course-sales-page-audit" variant="ghost">Course page audit guide</Btn><Btn href="/pricing">Get the full audit — $39</Btn></div>
    </Container>
  );
}
