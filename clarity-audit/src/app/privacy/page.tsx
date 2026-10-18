import type { Metadata } from "next";
import { Container, Eyebrow } from "@/components/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Privacy Policy", description: "What Clarity Audit collects, why, and how to delete it. Draft pending final legal review." };

export default function Privacy() {
  return (
    <Container className="prose-audit max-w-3xl py-14">
      <Eyebrow>Legal</Eyebrow>
      <h1 className="mb-4 mt-3 text-4xl font-extrabold tracking-tight text-[color:var(--ink)]">Privacy Policy</h1>
      <p className="rounded-xl bg-[#eff6ff] px-4 py-3 text-sm text-[color:var(--accent)]">Plain-language draft — final version subject to the operator's legal review before commercial launch.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">What we collect</h2>
      <p><strong>Scans:</strong> when you submit a URL, we fetch that public page once and store the resulting scores/findings so your result link works. We do not crawl beyond the submitted URL, log in anywhere, or submit forms. <strong>Email opt-ins:</strong> if you subscribe, we store your email, the form you used, your consent, and timestamps. <strong>Orders (at launch):</strong> payment is processed by a major payment provider; we receive order confirmations, never full card numbers. <strong>Server logs:</strong> standard technical logs (IP address for rate-limiting/security, user agent, timestamps).</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Why</h2>
      <p>To run the scanner, deliver reports and requested emails, prevent abuse, and compute anonymous aggregate statistics (e.g., “most-failed checks”) that never identify your page publicly unless you share your own result link.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">What we never do</h2>
      <p>Sell personal data. Send marketing email without explicit opt-in. Buy or scrape email lists. Share your individual scan publicly without you sharing its link.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Your controls</h2>
      <p>Unsubscribe from any email in one click. To delete your scans or email record, contact {SITE.supportEmail} — we action deletion requests within 30 days (typically much faster). You may also ask what we hold about you.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Cookies</h2>
      <p>This site is designed to work without advertising or cross-site tracking cookies. If privacy-respecting analytics are added later, they will be disclosed here first.</p>
      <h2 className="mb-2 mt-7 text-xl font-bold text-[color:var(--ink)]">Contact</h2>
      <p>{SITE.supportEmail}</p>
    </Container>
  );
}
