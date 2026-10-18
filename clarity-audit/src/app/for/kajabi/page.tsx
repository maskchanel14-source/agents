import type { Metadata } from "next";
import { Container, Eyebrow, Card, Btn } from "@/components/ui";
import ScanForm from "@/components/ScanForm";

export const metadata: Metadata = {
  title: "For Kajabi Creators — Landing Page Clarity Audit",
  description: "Kajabi pages convert on clarity, not blocks. Free 25-check clarity score tuned for Kajabi sales and opt-in pages: offer block, checkout trust, hero outcome.",
};

export default function ForKajabi() {
  return (
    <Container className="py-14">
      <div className="max-w-3xl">
        <Eyebrow>For Kajabi creators</Eyebrow>
        <h1 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight">Your Kajabi page has every block. Does it pass the 5-second test?</h1>
        <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Kajabi makes it easy to add sections — and easy to bury the offer under them. Paste your public Kajabi page URL for a free clarity score across headline, CTA, proof, pricing, and form friction.</p>
      </div>
      <div className="mt-8 max-w-2xl"><ScanForm /></div>
      <div className="mt-12 grid gap-5 lg:grid-cols-2">
        <Card>
          <h2 className="font-bold">Kajabi-specific patterns we flag</h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
            <li>Hero block headline that's a course name, not an outcome</li>
            <li>Offer block price visible only after "Enroll" → checkout</li>
            <li>Three CTAs competing (watch video / download / enroll) in one screen</li>
            <li>Testimonial blocks with names but no specific change</li>
            <li>Opt-in forms asking 5+ fields before the lead magnet</li>
          </ul>
        </Card>
        <Card>
          <h2 className="font-bold">Worked fix pattern</h2>
          <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">Before: hero says "The Abundant Creator Academy". After: "Turn your expertise into a launched course in 8 weeks — for Kajabi creators starting from zero." Same page, same blocks; the first screen finally answers <em>what, for whom, what next</em>.</p>
          <p className="mt-3 text-sm text-[color:var(--ink-3)]">Not affiliated with Kajabi. We audit public pages built on any platform.</p>
        </Card>
      </div>
      <div className="mt-10 flex flex-wrap gap-3"><Btn href="/niche/course-creators" variant="ghost">Course creator playbook</Btn><Btn href="/pricing">Get the full audit — $39</Btn></div>
    </Container>
  );
}
