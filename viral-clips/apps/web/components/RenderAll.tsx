"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function RenderAll({
  projectId,
  clipIds,
  label = "Render all clips",
}: {
  projectId: string;
  clipIds?: string[];
  label?: string;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const res = await fetch(`/api/projects/${projectId}/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ clip_ids: clipIds ?? null }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Render failed");
      setMessage("Render queued — this page updates automatically.");
      router.refresh();
      const jobId = data.id as string;
      for (let i = 0; i < 240; i++) {
        await new Promise((r) => setTimeout(r, 1500));
        const job = await fetch(`/api/jobs/${jobId}`, { credentials: "same-origin" }).then((r) => r.json());
        setMessage(`Rendering… ${job.progress}%`);
        if (job.status === "done") {
          setMessage("Rendering complete.");
          router.refresh();
          break;
        }
        if (job.status === "failed") throw new Error(job.error ?? "Render failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Render failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button onClick={run} disabled={busy} className="btn-primary">
        {busy ? "Rendering…" : label}
      </button>
      {message ? <span className="text-[11px] text-mist-500">{message}</span> : null}
      {error ? <span className="text-[11px] text-rose-300">{error}</span> : null}
    </div>
  );
}
