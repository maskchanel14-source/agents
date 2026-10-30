"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import type { Clip, Preset, ScoreBreakdown } from "@/lib/types";
import { fmtDuration, scoreTone } from "@/lib/format";
import { Badge, Card, ProgressBar, ScoreRing } from "./ui";

const FIT_MODES = [
  { id: "crop", label: "Smart crop", hint: "Fill the frame, follow the speaker" },
  { id: "blur", label: "Blurred fit", hint: "Keep the whole frame, blur the sides" },
] as const;

const DIMENSION_LABELS: Record<keyof ScoreBreakdown, string> = {
  hook_strength: "Hook strength",
  curiosity: "Curiosity",
  emotional_impact: "Emotional impact",
  story_completeness: "Story completeness",
  shareability: "Shareability",
  engagement: "Engagement",
  information_value: "Information value",
  context_independence: "Context independence",
  visual_engagement: "Visual engagement",
};

export default function ClipEditor({
  clip,
  presets,
  plan,
  sourceUrl,
}: {
  clip: Clip;
  presets: Preset[];
  plan: string;
  sourceUrl: string | null;
}) {
  const router = useRouter();
  const [cropX, setCropX] = useState(clip.crop_x ?? 0.5);
  const [fitMode, setFitMode] = useState<"crop" | "blur">(clip.fit_mode);
  const [preset, setPreset] = useState(clip.preset);
  const [title, setTitle] = useState(clip.title);
  const [hook, setHook] = useState(clip.hook ?? "");
  const [busy, setBusy] = useState<"save" | "render" | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rendered, setRendered] = useState(clip.video_url);

  const tierOrder: Record<string, number> = { free: 0, pro: 1, business: 2 };
  const allowed = (tier: string) => (tierOrder[plan] ?? 0) >= (tierOrder[tier] ?? 0);
  const tone = scoreTone(clip.score);

  const cropStyle = useMemo(() => {
    // the source frame is ~16:9; a 9:16 window sees ~31.6% of its width
    return { width: `316%`, left: `${-cropX * 216}%` } as React.CSSProperties;
  }, [cropX]);

  async function save() {
    setBusy("save");
    setError(null);
    setMessage(null);
    try {
      const res = await fetch(`/api/clips/${clip.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          title,
          hook,
          crop_x: cropX,
          fit_mode: fitMode,
          preset,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Save failed");
      setMessage("Saved. Re-render to apply to the MP4.");
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(null);
    }
  }

  async function render() {
    setBusy("render");
    setError(null);
    setMessage("Queueing render…");
    try {
      await save();
      const res = await fetch(`/api/clips/${clip.id}/render`, {
        method: "POST",
        credentials: "same-origin",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Render failed");
      const jobId = data.id as string;
      for (let i = 0; i < 240; i++) {
        await new Promise((r) => setTimeout(r, 1500));
        const job = await fetch(`/api/jobs/${jobId}`, { credentials: "same-origin" }).then((r) => r.json());
        setMessage(`Rendering… ${job.progress}%`);
        if (job.status === "done") {
          const fresh: Clip = await fetch(`/api/clips/${clip.id}`, { credentials: "same-origin" }).then((r) => r.json());
          setRendered(fresh.video_url ? `${fresh.video_url}?v=${Date.now()}` : null);
          setMessage("Render complete.");
          router.refresh();
          break;
        }
        if (job.status === "failed") throw new Error(job.error ?? "Render failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Render failed");
      setMessage(null);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[360px_1fr]">
      <div className="space-y-4">
        <Card className="p-3">
          <div className="relative aspect-[9/16] overflow-hidden rounded-xl bg-black">
            {rendered ? (
              <video key={rendered} src={rendered} controls playsInline className="h-full w-full object-cover" />
            ) : clip.thumb_url ? (
              <div className="relative h-full w-full overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={clip.thumb_url} alt="" className="absolute top-0 h-full max-w-none object-cover opacity-90" style={cropStyle} />
                <div className="absolute inset-x-0 top-0 flex justify-center p-2">
                  <span className="rounded-md bg-black/70 px-2 py-1 text-[10px] uppercase tracking-wider text-mist-400">
                    9:16 crop preview
                  </span>
                </div>
              </div>
            ) : (
              <div className="grid h-full place-items-center text-xs text-mist-600">No preview</div>
            )}
          </div>
          <div className="mt-3 flex items-center justify-between px-1 text-[11px] text-mist-500">
            <span className="tabular-nums">
              {fmtDuration(clip.start_s)} → {fmtDuration(clip.end_s)}
            </span>
            <span className="tabular-nums">{Math.round(clip.duration_s)}s · 1080×1920</span>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <p className="label">Potential</p>
            <span className={`text-xs font-medium ${tone.text}`}>{tone.label}</span>
          </div>
          <div className="mt-3 flex items-center gap-4">
            <ScoreRing score={clip.score} size={72} />
            <div className="text-xs text-mist-500">
              Estimated short-form potential across nine signals. Not a guarantee of performance.
            </div>
          </div>
          {clip.score_breakdown ? (
            <div className="mt-4 space-y-2">
              {(Object.keys(DIMENSION_LABELS) as (keyof ScoreBreakdown)[]).map((key) => (
                <div key={key}>
                  <div className="mb-1 flex justify-between text-[11px] text-mist-500">
                    <span>{DIMENSION_LABELS[key]}</span>
                    <span className="tabular-nums text-mist-400">{Math.round(clip.score_breakdown![key])}</span>
                  </div>
                  <ProgressBar value={clip.score_breakdown![key]} thin />
                </div>
              ))}
            </div>
          ) : null}
          {clip.explanation ? (
            <p className="mt-3 border-t border-white/[0.06] pt-3 text-[11px] leading-relaxed text-mist-600">
              {clip.explanation}
            </p>
          ) : null}
        </Card>
      </div>

      <div className="space-y-4">
        <Card className="p-5">
          <p className="label mb-3">Clip details</p>
          <div className="space-y-3">
            <div>
              <label className="mb-1.5 block text-xs text-mist-500" htmlFor="title">
                Title
              </label>
              <input id="title" className="input" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} />
            </div>
            <div>
              <label className="mb-1.5 block text-xs text-mist-500" htmlFor="hook">
                Opening hook (shown in the first two seconds)
              </label>
              <input id="hook" className="input" value={hook} onChange={(e) => setHook(e.target.value)} maxLength={300} />
            </div>
          </div>

          <div className="mt-5">
            <div className="flex items-center justify-between">
              <p className="label">Crop position</p>
              <span className="tabular-nums text-[11px] text-mist-500">
                {cropX < 0.34 ? "left" : cropX > 0.66 ? "right" : "centre"} · {Math.round(cropX * 100)}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={cropX}
              onChange={(e) => setCropX(Number(e.target.value))}
              className="mt-2 w-full accent-accent"
              aria-label="Crop horizontal position"
            />
            <div className="mt-2 flex gap-2">
              {[0.25, 0.5, 0.75].map((v) => (
                <button key={v} onClick={() => setCropX(v)} className="btn-subtle !px-2 !py-1 text-[11px]">
                  {v === 0.25 ? "Left" : v === 0.5 ? "Centre" : "Right"}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5">
            <p className="label mb-2">Framing</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {FIT_MODES.map((m) => (
                <button
                  key={m.id}
                  onClick={() => setFitMode(m.id)}
                  className={`rounded-xl border p-3 text-left transition ${
                    fitMode === m.id
                      ? "border-accent/50 bg-accent/10"
                      : "border-white/10 hover:border-white/20"
                  }`}
                >
                  <p className="text-sm font-medium">{m.label}</p>
                  <p className="mt-0.5 text-[11px] text-mist-500">{m.hint}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5">
            <p className="label mb-2">Caption preset</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {presets.map((p) => {
                const ok = allowed(p.tier);
                return (
                  <button
                    key={p.id}
                    disabled={!ok}
                    onClick={() => setPreset(p.id)}
                    className={`flex items-center justify-between rounded-xl border px-3 py-2.5 text-left transition ${
                      preset === p.id ? "border-accent/50 bg-accent/10" : "border-white/10 hover:border-white/20"
                    } ${ok ? "" : "cursor-not-allowed opacity-40"}`}
                  >
                    <span className="text-[13px]">{p.label}</span>
                    {p.tier !== "free" ? <Badge>{p.tier}</Badge> : null}
                  </button>
                );
              })}
            </div>
          </div>

          {message ? <p className="mt-4 text-[12px] text-mist-400">{message}</p> : null}
          {error ? (
            <p className="mt-4 rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-[13px] text-rose-200">
              {error}
            </p>
          ) : null}

          <div className="mt-5 flex flex-wrap gap-2">
            <button onClick={render} disabled={busy !== null} className="btn-primary">
              {busy === "render" ? "Rendering…" : "Save & render"}
            </button>
            <button onClick={save} disabled={busy !== null} className="btn-ghost">
              {busy === "save" ? "Saving…" : "Save only"}
            </button>
            <Link href={`/clips/${clip.id}/subtitles`} className="btn-ghost">
              Edit captions
            </Link>
            {rendered ? (
              <a href={rendered} download className="btn-ghost">
                Download MP4
              </a>
            ) : null}
          </div>
        </Card>

        <Card className="p-5">
          <p className="label mb-2">Transcript</p>
          <p className="text-[13px] leading-relaxed text-mist-300">
            {clip.text || "No transcript for this run — this clip was selected from acoustic and visual signals."}
          </p>
          {clip.subtitle_json?.cues?.length ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              <Badge tone="accent">{clip.subtitle_json.cues.length} caption cues</Badge>
              {clip.subtitle_json.edited ? <Badge tone="warn">hand-edited</Badge> : <Badge>auto-generated</Badge>}
            </div>
          ) : (
            <p className="mt-3 text-[11px] text-mist-600">
              Captions appear when a transcription provider is configured.
            </p>
          )}
          {sourceUrl ? (
            <p className="mt-3 text-[11px] text-mist-600">
              Source timeline: clip starts at {fmtDuration(clip.start_s)} of the original file.
            </p>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
