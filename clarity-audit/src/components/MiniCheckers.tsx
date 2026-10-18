"use client";
import { useState } from "react";
import Link from "next/link";

interface Finding { ok: boolean; label: string; tip: string }

function evaluateHeadline(h: string): Finding[] {
  const t = h.trim();
  return [
    { ok: t.length >= 20 && t.length <= 90, label: `Length: ${t.length} characters`, tip: "Aim for 20–90. Detail belongs in the subheadline." },
    { ok: /\b(get|gain|grow|build|learn|master|achieve|stop|finally|without|so you can|launch|book|earn|save|become)\b/i.test(t), label: "Names an outcome", tip: "Add the change: what will they be able to do/have/stop?" },
    { ok: /\b(for|helping|coaches|creators|consultants|founders|freelancers|owners|you|women|men|parents|who)\b/i.test(t), label: "Names (or implies) the audience", tip: "Try “For [group] who…”. Specificity is trust." },
    { ok: !/^(welcome|home|untitled|my (website|business))/i.test(t), label: "Not a placeholder headline", tip: "“Welcome to my website” spends your most valuable line on nothing." },
    { ok: !/(!!!|amazing|incredible|ultimate|revolutionary|game-?changer)/i.test(t), label: "No hype filler", tip: "Swap adjectives for specifics: numbers, timeframes, observable results." },
  ];
}

function evaluateCta(c: string): Finding[] {
  const t = c.trim();
  return [
    { ok: /\b(book|start|get|buy|join|enroll|register|download|claim|schedule|apply|try|order|reserve|sign|grab|unlock|access|see|check|score|send)\b/i.test(t), label: "Starts with (or contains) an action verb", tip: "Begin with Book, Get, Start, Claim…" },
    { ok: !/^(click here|submit|send|learn more|more info|read more|go|here)$/i.test(t), label: "Isn't generic (Submit / Click here)", tip: "Say what happens next: “Get my audit”, “See the curriculum”." },
    { ok: t.split(/\s+/).length >= 3, label: "Includes an object (what they get)", tip: "Verb + object: “Download the checklist” beats “Download”." },
    { ok: t.length <= 42, label: `Fits a button (${t.length} chars)`, tip: "Over ~42 characters, buttons wrap and stall. Move qualifiers under the button." },
    { ok: !/!!/.test(t), label: "Calm confidence, no shouting", tip: "Multiple exclamation marks read as desperation, not energy." },
  ];
}

export default function MiniChecker({ kind }: { kind: "headline" | "cta" }) {
  const [value, setValue] = useState("");
  const [findings, setFindings] = useState<Finding[] | null>(null);
  const isHeadline = kind === "headline";
  function run(e: React.FormEvent) {
    e.preventDefault();
    setFindings(isHeadline ? evaluateHeadline(value) : evaluateCta(value));
  }
  const passed = findings?.filter((f) => f.ok).length ?? 0;
  return (
    <div>
      <form onSubmit={run} className="rounded-2xl border border-[color:var(--line)] bg-white p-6">
        <label className="block text-sm font-semibold" htmlFor={`${kind}-input`}>{isHeadline ? "Paste your headline draft" : "Paste your button / CTA text"}</label>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row">
          <input id={`${kind}-input`} value={value} onChange={(e) => setValue(e.target.value)} required maxLength={200}
            placeholder={isHeadline ? "e.g. I help coaches book 3 calls a week without ads" : "e.g. Book my free clarity call"}
            className="min-h-[52px] flex-1 rounded-lg border border-[color:var(--line)] px-3.5 text-base" />
          <button className="min-h-[52px] rounded-lg bg-[color:var(--accent)] px-6 font-semibold text-white hover:bg-[#1e40af]">{isHeadline ? "Check headline" : "Check CTA"}</button>
        </div>
        <p className="mt-2.5 text-xs text-[color:var(--ink-3)]">Runs entirely in your browser — nothing is sent or stored.</p>
      </form>
      {findings && (
        <div className="mt-5 rounded-2xl border border-[color:var(--line)] bg-white p-6" role="status" aria-live="polite">
          <p className="font-bold">{passed}/{findings.length} clarity checks passed {passed === findings.length ? "— ship it 🎉" : ""}</p>
          <ul className="mt-4 space-y-3.5">
            {findings.map((f) => (
              <li key={f.label} className="flex gap-3">
                <span aria-hidden className={f.ok ? "text-[color:var(--good)]" : "text-[color:var(--bad)]"}>{f.ok ? "✓" : "✗"}</span>
                <span><strong>{f.label}</strong>{!f.ok && <span className="block text-sm text-[color:var(--ink-2)]">{f.tip}</span>}</span>
              </li>
            ))}
          </ul>
          <p className="mt-5 text-sm text-[color:var(--ink-2)]">Want this for your whole page? <Link href="/#scan" className="font-semibold text-[color:var(--accent)] underline-offset-4 hover:underline">Run the free 100-point scan →</Link></p>
        </div>
      )}
    </div>
  );
}
