"use client";
import { useState } from "react";

export default function EmailCapture({ source, scanId, plan, title, blurb, cta = "Email it to me" }: {
  source: string; scanId?: string; plan?: string; title: string; blurb: string; cta?: string;
}) {
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [state, setState] = useState<"idle" | "busy" | "done" | "error">("idle");
  const [msg, setMsg] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setState("busy");
    try {
      const res = await fetch("/api/optin", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, source, scanId, plan, consent }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Something went wrong.");
      setState("done");
    } catch (err) { setState("error"); setMsg(err instanceof Error ? err.message : "Something went wrong."); }
  }

  if (state === "done") {
    return (
      <div className="rounded-2xl border border-[color:var(--good)] bg-[#f0fdf4] p-6" role="status">
        <p className="font-semibold text-[color:var(--good)]">You're on the list ✓</p>
        <p className="mt-1 text-sm text-[color:var(--ink-2)]">We'll only email what you asked for. Unsubscribe anytime — one click, no guilt trip.</p>
      </div>
    );
  }
  return (
    <form onSubmit={submit} className="rounded-2xl border border-[color:var(--line)] bg-white p-6" aria-label={title}>
      <p className="font-semibold">{title}</p>
      <p className="mt-1 text-sm leading-relaxed text-[color:var(--ink-2)]">{blurb}</p>
      <input className="hp" type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden />
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <label className="sr-only" htmlFor={`email-${source}`}>Email address</label>
        <input id={`email-${source}`} type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com"
          className="min-h-[48px] flex-1 rounded-lg border border-[color:var(--line)] px-3.5 text-[15px]" />
        <button disabled={state === "busy"} className="min-h-[48px] rounded-lg bg-[color:var(--ink)] px-5 text-[15px] font-semibold text-white hover:bg-[#232b3a] disabled:opacity-60">
          {state === "busy" ? "Saving…" : cta}
        </button>
      </div>
      <label className="mt-3 flex cursor-pointer items-start gap-2.5 text-xs leading-relaxed text-[color:var(--ink-2)]">
        <input type="checkbox" required checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-0.5 h-4 w-4 shrink-0" />
        <span>Yes, email me about this (and occasional clarity tips). No spam, no list-selling, unsubscribe anytime. <a href="/privacy" className="underline">Privacy</a></span>
      </label>
      {state === "error" && <p className="mt-2 text-sm text-[color:var(--bad)]" role="alert">{msg}</p>}
    </form>
  );
}
