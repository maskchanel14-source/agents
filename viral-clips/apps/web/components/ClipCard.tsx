"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Clip } from "@/lib/types";
import { fmtDuration, scoreTone } from "@/lib/format";
import { Badge, ScoreRing } from "./ui";

export default function ClipCard({ clip, onChanged }: { clip: Clip; onChanged?: () => void }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const tone = scoreTone(clip.score);

  async function render() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`/api/clips/${clip.id}/render`, {
        method: "POST",
        credentials: "same-origin",
      });
      if (!res.ok) throw new Error((await res.json().catch(() => ({})))?.detail ?? "Render failed");
      router.refresh();
      onChanged?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Render failed");
      setBusy(false);
    }
  }

  async function remove() {
    if (!confirm("Delete this clip? The rendered MP4 is removed too.")) return;
    setBusy(true);
    const res = await fetch(`/api/clips/${clip.id}`, { method: "DELETE", credentials: "same-origin" });
    setBusy(false);
    if (res.ok) router.refresh();
    else setError("Delete failed");
  }

  return (
    <div className="card card-hover animate-fade-up overflow-hidden">
      <div className="relative aspect-[9/16] w-full overflow-hidden bg-ink-900">
        {clip.thumb_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={clip.thumb_url} alt={clip.title} className="h-full w-full object-cover" />
        ) : (
          <div className="grid h-full place-items-center text-[11px] text-mist-700">no preview</div>
        )}
        <div className="absolute inset-x-0 top-0 flex items-start justify-between gap-2 bg-gradient-to-b from-black/70 to-transparent p-3">
          <span className="rounded-md bg-black/60 px-1.5 py-0.5 text-[11px] font-medium tabular-nums text-mist-300">
            {fmtDuration(clip.start_s)} – {fmtDuration(clip.end_s)}
          </span>
          <ScoreRing score={clip.score} size={48} />
        </div>
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="rounded-md bg-black/60 px-1.5 py-0.5 text-[11px] tabular-nums text-mist-300">
              {Math.round(clip.duration_s)}s
            </span>
            {clip.status === "ready" ? (
              <Badge tone="success">MP4 ready</Badge>
            ) : clip.status === "failed" ? (
              <Badge tone="danger">Render failed</Badge>
            ) : clip.status === "rendering" ? (
              <Badge tone="warn">Rendering</Badge>
            ) : (
              <Badge>Not rendered</Badge>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-3 p-4">
        <div>
          <p className="line-clamp-2 text-sm font-semibold leading-snug">{clip.title}</p>
          <p className={`mt-1 text-[11px] font-medium ${tone.text}`}>
            {tone.label} · {Math.round(clip.score)}/100 short-form potential
          </p>
        </div>

        {clip.tags?.length ? (
          <div className="flex flex-wrap gap-1">
            {clip.tags.slice(0, 3).map((t) => (
              <span key={t} className="rounded-md bg-white/[0.05] px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-mist-500">
                {t.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        ) : null}

        {error ? <p className="text-[11px] text-rose-300">{error}</p> : null}

        <div className="flex flex-wrap items-center gap-1.5">
          {clip.video_url ? (
            <a href={clip.video_url} download className="btn-ghost !px-2.5 !py-1.5 text-[12px]">
              Download
            </a>
          ) : (
            <button onClick={render} disabled={busy} className="btn-primary !px-2.5 !py-1.5 text-[12px]">
              {busy ? "Rendering…" : "Render"}
            </button>
          )}
          <Link href={`/clips/${clip.id}/editor`} className="btn-subtle !px-2.5 !py-1.5 text-[12px]">
            Editor
          </Link>
          <Link href={`/clips/${clip.id}/subtitles`} className="btn-subtle !px-2.5 !py-1.5 text-[12px]">
            Captions
          </Link>
          <button onClick={remove} disabled={busy} className="btn-subtle !px-2 !py-1.5 text-[12px] text-mist-600 hover:text-rose-300">
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
