export const SITE = {
  name: "Clarity Audit",
  product: "Instant Website Clarity Audit",
  tagline: "Would a stranger understand your offer in 5 seconds?",
  // Placeholder until the human connects a payment provider — sales run as
  // honest waitlist/intent capture until then. Never fake a checkout.
  paymentsConnected: false,
  supportEmail: "support@example.com", // TODO(human): replace with real support inbox
  offers: [
    {
      slug: "quick-audit", name: "Quick Audit", price: 19, recommended: false,
      blurb: "Your full score breakdown, every issue ranked, with the exact fix for each.",
      includes: ["All 25 checks with evidence from your page", "Top-issue fixes written for your copy", "Delivered as a shareable report page + PDF-ready document", "Re-scan link to verify your fixes"],
    },
    {
      slug: "full-audit", name: "Full Audit", price: 39, recommended: true,
      blurb: "Everything in Quick, plus section-by-section rewrites you can paste in.",
      includes: ["Everything in Quick Audit", "Headline + subheadline rewrite options (3 each)", "CTA rewrite set for every button", "FAQ draft answering your top 5 objections", "Trust-signal gap plan"],
    },
    {
      slug: "fix-pack", name: "Fix Pack", price: 79, recommended: false,
      blurb: "The full audit plus a 7-day, day-by-day implementation plan.",
      includes: ["Everything in Full Audit", "7-day action plan (one fix per day, ~45 min each)", "Before/after rescan comparison", "Priority order by expected impact", "Email support for implementation questions (7 days)"],
    },
    {
      slug: "template-kit", name: "Template Kit", price: 49, recommended: false,
      blurb: "Fill-in landing page templates for coaches, courses, and consultants.",
      includes: ["Hero, offer, proof, FAQ, and pricing section templates", "10 headline formulas with worked examples", "CTA swipe file (40 tested patterns)", "Pre-publish clarity checklist"],
    },
  ],
  bundles: [
    { name: "Clarity Bundle", price: 99, note: "Full Audit + Template Kit (save $29 vs separate)" },
    { name: "Creator Pack", price: 129, note: "Fix Pack + Template Kit + 30-day content checklist" },
    { name: "Agency 5-Pack", price: 149, note: "5 × Full Audits for client pages (transferable)" },
  ],
} as const;

export function siteUrl(): string {
  return process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "") || "http://localhost:3000";
}
