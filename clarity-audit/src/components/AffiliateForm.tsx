"use client";
import { useState } from "react";

export default function AffiliateForm() {
  const [form, setForm] = useState({ name: "", email: "", audience: "", channelUrl: "" });
  const [state, setState] = useState<"idle" | "busy" | "done" | "error">("idle");
  const [msg, setMsg] = useState("");
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setState("busy");
    try {
      const res = await fetch("/api/affiliate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Something went wrong.");
      setState("done");
    } catch (err) { setState("error"); setMsg(err instanceof Error ? err.message : "Something went wrong."); }
  }
  if (state === "done") return <div className="rounded-2xl border border-[color:var(--good)] bg-[#f0fdf4] p-6" role="status"><p className="font-semibold text-[color:var(--good)]">Application received ✓</p><p className="mt-1 text-sm text-[color:var(--ink-2)]">We review every application by hand and reply with your link, swipe copy, and the compliance guidelines. No spammy promotion — ever.</p></div>;
  const input = "min-h-[48px] w-full rounded-lg border border-[color:var(--line)] px-3.5 text-[15px]";
  return (
    <form onSubmit={submit} className="space-y-4 rounded-2xl border border-[color:var(--line)] bg-white p-6" aria-label="Affiliate application">
      <div><label className="mb-1.5 block text-sm font-semibold" htmlFor="a-name">Your name</label><input id="a-name" required className={input} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
      <div><label className="mb-1.5 block text-sm font-semibold" htmlFor="a-email">Email</label><input id="a-email" type="email" required className={input} value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
      <div><label className="mb-1.5 block text-sm font-semibold" htmlFor="a-aud">Who is your audience? (one line)</label><input id="a-aud" required className={input} placeholder="e.g. 4,000 business coaches on my newsletter" value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} /></div>
      <div><label className="mb-1.5 block text-sm font-semibold" htmlFor="a-url">Channel URL (optional)</label><input id="a-url" className={input} placeholder="https://…" value={form.channelUrl} onChange={(e) => setForm({ ...form, channelUrl: e.target.value })} /></div>
      <button disabled={state === "busy"} className="min-h-[48px] w-full rounded-lg bg-[color:var(--accent)] font-semibold text-white hover:bg-[#1e40af] disabled:opacity-60">{state === "busy" ? "Sending…" : "Apply for the ambassador program"}</button>
      {state === "error" && <p className="text-sm text-[color:var(--bad)]" role="alert">{msg}</p>}
      <p className="text-xs text-[color:var(--ink-3)]">30% of first paid order (launch rate, human-confirmed at approval). Payouts after the refund window. Self-referrals and spam promotion void commissions — full rules in the program terms after approval.</p>
    </form>
  );
}
