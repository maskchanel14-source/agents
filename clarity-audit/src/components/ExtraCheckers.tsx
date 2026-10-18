"use client";
import { useState } from "react";
import Link from "next/link";

interface Finding { ok: boolean; label: string; tip: string }

function evaluateFaq(t: string): Finding[] {
  const x = t.toLowerCase();
  const q = (t.match(/\?/g) || []).length;
  return [
    { ok: q >= 4, label: `${q} question(s) detected`, tip: "Aim for 5–9 FAQs. Fewer leaves objections unanswered; more belongs on a support page." },
    { ok: /who|for me|fit|right for|not for|beginner|advanced/.test(x), label: "Answers “who is this for (and not for)”", tip: "Add an honest fit/not-fit answer — it converts the right people and refunds-proof the rest." },
    { ok: /how long|time|hours|weeks|per week|schedule|pace/.test(x), label: "Answers time commitment", tip: "State hours/week and total duration plainly." },
    { ok: /deliver|access|format|live|record|download|when do i get|start/.test(x), label: "Answers delivery & access", tip: "How + when they get it, and how long access lasts." },
    { ok: /after i (pay|book|buy|enroll)|what happens (next|after)|once i/.test(x), label: "Answers “what happens after I pay/book”", tip: "Walk through the first 10 minutes after checkout. Uncertainty here kills clicks." },
    { ok: /refund|guarantee|money[- ]back|cancel|reschedule/.test(x), label: "Answers refund/cancellation", tip: "One honest sentence near the price beats a buried policy page." },
  ];
}

function evaluateTrust(t: string): Finding[] {
  const x = t.toLowerCase();
  return [
    { ok: /testimonial|review|★|star|client|student|member|case stud|results/.test(x), label: "Social proof language present", tip: "Add 2–3 specific, real testimonials (who + starting point + change). No proof yet? Use a methodology/sample instead — never invent quotes." },
    { ok: /@|contact|support|email us|call us/.test(x), label: "A human is reachable", tip: "Add a visible support email/contact link." },
    { ok: /\$\s?\d|£\s?\d|€\s?\d|price|pricing|investment|from \$/.test(x), label: "Price anchor visible", tip: "Hidden pricing filters out your best buyers. Show a price or “from $X”." },
    { ok: /guarantee|refund|money[- ]back/.test(x), label: "Risk reversal stated", tip: "State an honest policy (e.g. revise-or-refund). Never promise outcomes." },
    { ok: /about|i'm |im |my name|founder|coach|meet /.test(x), label: "A real person is visible", tip: "Face + two lines of story near the offer." },
    { ok: /privacy|terms|secure checkout|encrypted/.test(x), label: "Legal/security reassurance", tip: "Link privacy/terms; one plain line about secure payment beats clip-art badges." },
  ];
}

function evaluateForm(t: string): Finding[] {
  const fields = t.split(/\n|,/).map((s) => s.trim().toLowerCase()).filter(Boolean);
  const sensitive = fields.filter((f) => /phone|address|dob|birth|income|salary|budget|company size|website url|instagram|linkedin/.test(f));
  return [
    { ok: fields.length > 0 && fields.length <= 4, label: `${fields.length} field(s) in the first step`, tip: "First step: name + email (or email only). Every extra field is a toll booth — qualify after commitment." },
    { ok: fields.some((f) => /email/.test(f)), label: "Email is captured", tip: "Email is the one field that lets you follow up — it should be first or only." },
    { ok: sensitive.length === 0, label: "No high-friction fields upfront", tip: sensitive.length ? `Move later: ${sensitive.join(", ")}. Ask these after the first yes, with a reason.` : "Good — nothing nosy before trust exists." },
    { ok: !fields.some((f) => /password|confirm/.test(f)), label: "No account-creation wall before value", tip: "Let them act first; create accounts after the win." },
    { ok: fields.length <= 2 || /name/.test(fields.join(" ")), label: "Starts with the easiest field", tip: "Order easy → hard: name/email first, open-ended questions last (momentum is real)." },
  ];
}

const CONFIG = {
  faq: { label: "Paste your FAQ section text (questions + answers)", placeholder: "How long does it take? …\nWhat if it's not for me? …", run: evaluateFaq, guide: "/resources/faq-examples-landing-page", guideName: "the 9-question FAQ guide" },
  trust: { label: "Paste your page copy (hero + offer + footer text)", placeholder: "Paste the main text of your landing page…", run: evaluateTrust, guide: "/resources/trust-signals-landing-page", guideName: "trust signals guide" },
  form: { label: "List your first-step form fields (one per line)", placeholder: "First name\nEmail\nPhone\n…", run: evaluateForm, guide: "/resources/landing-page-audit-checklist", guideName: "the full audit checklist" },
} as const;

export default function ExtraChecker({ kind }: { kind: keyof typeof CONFIG }) {
  const cfg = CONFIG[kind];
  const [value, setValue] = useState("");
  const [findings, setFindings] = useState<Finding[] | null>(null);
  const passed = findings?.filter((f) => f.ok).length ?? 0;
  return (
    <div>
      <form onSubmit={(e) => { e.preventDefault(); setFindings(cfg.run(value)); }} className="rounded-2xl border border-[color:var(--line)] bg-white p-6">
        <label className="block text-sm font-semibold" htmlFor={`${kind}-input`}>{cfg.label}</label>
        <textarea id={`${kind}-input`} required rows={7} value={value} onChange={(e) => setValue(e.target.value)} placeholder={cfg.placeholder}
          className="mt-3 w-full rounded-lg border border-[color:var(--line)] px-3.5 py-3 text-[15px] leading-relaxed" />
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button className="min-h-[48px] rounded-lg bg-[color:var(--accent)] px-6 font-semibold text-white hover:bg-[#1e40af]">Run the check</button>
          <p className="text-xs text-[color:var(--ink-3)]">Runs entirely in your browser — nothing is sent or stored.</p>
        </div>
      </form>
      {findings && (
        <div className="mt-5 rounded-2xl border border-[color:var(--line)] bg-white p-6" role="status" aria-live="polite">
          <p className="font-bold">{passed}/{findings.length} checks passed{passed === findings.length ? " — ship it 🎉" : ""}</p>
          <ul className="mt-4 space-y-3.5">
            {findings.map((f) => (
              <li key={f.label} className="flex gap-3">
                <span aria-hidden className={f.ok ? "text-[color:var(--good)]" : "text-[color:var(--bad)]"}>{f.ok ? "✓" : "✗"}</span>
                <span><strong>{f.label}</strong>{!f.ok && <span className="block text-sm text-[color:var(--ink-2)]">{f.tip}</span>}</span>
              </li>
            ))}
          </ul>
          <p className="mt-5 text-sm text-[color:var(--ink-2)]">Go deeper with <Link href={cfg.guide} className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">{cfg.guideName}</Link> — or check the whole page with the <Link href="/#scan" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">free 25-check scan →</Link></p>
        </div>
      )}
    </div>
  );
}
