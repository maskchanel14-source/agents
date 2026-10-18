// Generates the paid-report document (Markdown → print/PDF-ready) from a scan.
// Evidence-based only: every line traces back to a check result. No invented facts.
import type { ScanReport } from "./scanner";

const HEADLINE_TEMPLATES = [
  "I help [audience] [specific outcome] without [biggest pain].",
  "[Outcome] for [audience] — in [timeframe], even if [common objection].",
  "Stop [painful status quo]. Start [desired outcome].",
];

export function buildReportMarkdown(report: ScanReport, tier: "quick" | "full" | "fixpack"): string {
  const lines: string[] = [];
  lines.push(`# Instant Website Clarity Audit`);
  lines.push(`**Page audited:** ${report.finalUrl}`);
  lines.push(`**Date:** ${new Date(report.fetchedAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}`);
  lines.push(`**Clarity Score:** ${report.score}/100 — ${report.grade}`);
  lines.push("");
  lines.push(`> ${report.gradeNote}`);
  lines.push("");
  lines.push(`## What the scanner found on your page`);
  lines.push(`- Title tag: “${report.pageFacts.title || "(missing)"}”`);
  lines.push(`- Headline (H1): “${report.pageFacts.h1 || "(missing)"}”`);
  lines.push(`- Words on page: ~${report.pageFacts.wordCount} · CTA buttons: ${report.pageFacts.ctaCount} · Forms: ${report.pageFacts.formCount}`);
  lines.push(`- HTML size: ${(report.pageFacts.htmlBytes / 1024).toFixed(0)} KB · Response: ${report.pageFacts.responseMs} ms · HTTPS: ${report.pageFacts.https ? "yes" : "no"}`);
  lines.push("");
  lines.push(`## Full findings (${report.checks.length} checks, 6 categories)`);
  for (const c of report.checks) {
    const mark = c.status === "pass" ? "✅" : c.status === "warn" ? "⚠️" : "❌";
    lines.push(`### ${mark} ${c.label} — ${c.points}/${c.maxPoints} (${c.category}, ${c.impact} impact)`);
    lines.push(`**Evidence:** ${c.evidence}`);
    if (c.status !== "pass") lines.push(`**Fix:** ${c.fix}`);
    lines.push("");
  }

  if (tier !== "quick") {
    lines.push(`## Rewrite pack (paste-ready starting points)`);
    lines.push(`Your current headline: “${report.pageFacts.h1 || "(none)"}”`);
    lines.push(`Try these structures, filled with your specifics:`);
    HEADLINE_TEMPLATES.forEach((t, i) => lines.push(`${i + 1}. ${t}`));
    lines.push("");
    lines.push(`**CTA upgrades:** replace any generic button text with *verb + object + outcome* — e.g. “Learn more” → “See the full curriculum”, “Submit” → “Get my free audit”.`);
    lines.push("");
    lines.push(`## FAQ draft (answer these 5 on your page)`);
    lines.push(`1. Who is this for — and who should NOT buy/book?`);
    lines.push(`2. How much time does it take, and what do I need before starting?`);
    lines.push(`3. How exactly is it delivered (format, schedule, access)?`);
    lines.push(`4. What happens right after I click the button / pay?`);
    lines.push(`5. What is your refund/reschedule policy?`);
    lines.push("");
  }

  if (tier === "fixpack") {
    const problems = report.checks.filter((c) => c.status !== "pass");
    lines.push(`## Your 7-day fix plan (~45 minutes/day)`);
    problems.slice(0, 7).forEach((c, i) => {
      lines.push(`**Day ${i + 1} — ${c.label}** (${c.impact} impact)`);
      lines.push(`${c.fix}`);
      lines.push(`Done when: the change is live and you have re-scanned to confirm this check passes.`);
      lines.push("");
    });
    if (problems.length === 0) {
      lines.push(`No failing checks. Spend the week on proof depth: add one specific testimonial and one case-study paragraph, then re-scan.`);
      lines.push("");
    }
    lines.push(`**Day 7 ritual:** re-run the free scanner, compare scores, and share your improvement badge.`);
    lines.push("");
  }

  lines.push(`---`);
  lines.push(`## Method & limits`);
  lines.push(`This audit reads your page's public HTML against a documented 100-point rubric (see /methodology). It does not see behind logins, does not measure your actual traffic or revenue, and cannot guarantee any business outcome. Automated checks catch structural clarity problems; pair them with one real human reading your page cold. If any agreed section is missing from this report, contact support for a revision or refund per the refund policy.`);
  return lines.join("\n");
}
