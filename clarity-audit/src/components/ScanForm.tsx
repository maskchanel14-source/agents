"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const STEPS = ["Fetching your public page…", "Reading headline & hero…", "Checking CTAs and proof…", "Scoring against the 100-point rubric…"];

export default function ScanForm({ compact = false }: { compact?: boolean }) {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (!busy) return;
    const t = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 1400);
    return () => clearInterval(t);
  }, [busy]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null); setBusy(true); setStep(0);
    try {
      const ref = new URLSearchParams(window.location.search).get("ref") ?? undefined;
      const res = await fetch("/api/scan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url, ref }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "That page could not be scanned.");
      router.push(`/scan/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Try again.");
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="w-full" aria-label="Free landing page clarity scanner">
      <div className="flex flex-col gap-3 sm:flex-row">
        <label className="sr-only" htmlFor={compact ? "scan-url-c" : "scan-url"}>Your public landing page URL</label>
        <input
          id={compact ? "scan-url-c" : "scan-url"} type="text" inputMode="url" autoComplete="url"
          placeholder="yourlandingpage.com/offer" value={url} onChange={(e) => setUrl(e.target.value)}
          required disabled={busy}
          className="min-h-[56px] flex-1 rounded-xl border border-[color:var(--line)] bg-white px-4 text-base text-[color:var(--ink)] placeholder:text-[color:var(--ink-3)] disabled:opacity-60"
        />
        <button type="submit" disabled={busy}
          className="min-h-[56px] shrink-0 rounded-xl bg-[color:var(--accent)] px-7 text-base font-semibold text-white transition-colors hover:bg-[#1e40af] disabled:opacity-60">
          {busy ? "Scanning…" : "Get my free score →"}
        </button>
      </div>
      {busy && (
        <p className="mt-3 text-sm text-[color:var(--ink-2)]" role="status" aria-live="polite">
          <span aria-hidden>◌ </span>{STEPS[step]}
        </p>
      )}
      {error && (
        <div className="mt-3 rounded-lg border border-[color:var(--bad)] bg-[#fef2f2] px-4 py-3 text-sm text-[color:var(--bad)]" role="alert">
          {error}{" "}
          <span className="text-[color:var(--ink-2)]">Tip: use the live public URL (not a login or preview link). Still stuck? <a href="/sample-report" className="underline">See a sample result</a>.</span>
        </div>
      )}
      <p className="mt-3 text-xs leading-relaxed text-[color:var(--ink-3)]">
        Free · No email needed for your score · Reads only the public page you submit · 10 free scans/hour
      </p>
    </form>
  );
}
