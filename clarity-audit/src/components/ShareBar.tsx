"use client";
import { useState } from "react";

export default function ShareBar({ score, grade, topIssue, scanId }: { score: number; grade: string; topIssue?: string; scanId: string }) {
  const [copied, setCopied] = useState<"link" | "badge" | null>(null);
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  const resultUrl = `${origin}/scan/${scanId}`;
  const badgeMd = `[![Clarity Score ${score}/100](${origin}/api/badge/${scanId}.svg)](${resultUrl})`;
  const text = encodeURIComponent(`My landing page scored ${score}/100 (${grade}) on the free Clarity Audit.${topIssue ? ` Biggest fix: ${topIssue}.` : ""} Can yours beat it?`);
  const urlEnc = encodeURIComponent(resultUrl);

  async function copy(what: "link" | "badge", value: string) {
    try { await navigator.clipboard.writeText(value); setCopied(what); setTimeout(() => setCopied(null), 2000); } catch { /* clipboard unavailable */ }
  }

  const btn = "inline-flex min-h-[44px] items-center rounded-lg border border-[color:var(--line)] bg-white px-4 text-sm font-semibold hover:border-[color:var(--ink-3)]";
  return (
    <div className="rounded-2xl border border-[color:var(--line)] bg-white p-6">
      <p className="font-semibold">Share your score — challenge a peer</p>
      <p className="mt-1 text-sm text-[color:var(--ink-2)]">Honest scores travel. “Can your page score above 70?” starts better conversations than any ad.</p>
      <div className="mt-4 flex flex-wrap gap-2.5">
        <a className={btn} target="_blank" rel="noreferrer" href={`https://twitter.com/intent/tweet?text=${text}&url=${urlEnc}`}>Post on X</a>
        <a className={btn} target="_blank" rel="noreferrer" href={`https://www.linkedin.com/sharing/share-offsite/?url=${urlEnc}`}>Share on LinkedIn</a>
        <button type="button" className={btn} onClick={() => copy("link", resultUrl)}>{copied === "link" ? "Copied ✓" : "Copy result link"}</button>
        <button type="button" className={btn} onClick={() => copy("badge", badgeMd)}>{copied === "badge" ? "Copied ✓" : "Copy badge (Markdown)"}</button>
      </div>
      <div className="mt-4">
        
        <img src={`/api/badge/${scanId}.svg`} alt={`Clarity score badge: ${score} out of 100`} width={280} height={64} />
        <p className="mt-2 text-xs text-[color:var(--ink-3)]">Badge preview — embed it on your site/README to show your score. <a href="/widget" className="underline">Widget docs</a></p>
      </div>
    </div>
  );
}
