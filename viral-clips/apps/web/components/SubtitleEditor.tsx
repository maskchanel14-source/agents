"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Clip, SubtitleCue } from "@/lib/types";
import { Badge, Card } from "./ui";

function fmt(t: number): string {
  const m = Math.floor(t / 60);
  const s = t % 60;
  return `${m}:${s.toFixed(2).padStart(5, "0")}`;
}

export default function SubtitleEditor({ clip }: { clip: Clip }) {
  const router = useRouter();
  const initial = clip.subtitle_json?.cues?.length
    ? clip.subtitle_json.cues.map((c) => ({ ...c }))
    : [];
  const [cues, setCues] = useState<SubtitleCue[]>(initial);
  const [busy, setBusy] = useState<null | "save" | "render">(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const keywords = clip.subtitle_json?.keywords ?? [];

  function update(index: number, patch: Partial<SubtitleCue>) {
    setCues((prev) => prev.map((c, i) => (i === index ? { ...c, ...patch } : c)));
  }

  function addCue() {
    const last = cues[cues.length - 1];
    const start = last ? last.end : 0;
    setCues([...cues, { start, end: start + 2, text: "" }]);
  }

  async function persist(): Promise<boolean> {
    const clean = cues
      .map((c) => ({ ...c, text: c.text.trim() }))
      .filter((c) => c.text.length > 0 && c.end > c.start);
    const res = await fetch(`/api/clips/${clip.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ subtitle_json: { cues: clean, edited: true } }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      setError(typeof data?.detail === "string" ? data.detail : "Could not save captions");
      return false;
    }
    return true;
  }

  async function save() {
    setBusy("save");
    setError(null);
    setMessage(null);
    if (await persist()) {
      setMessage("Captions saved.");
      router.refresh();
    }
    setBusy(null);
  }

  async function saveAndRender() {
    setBusy("render");
    setError(null);
    setMessage("Saving captions…");
    if (!(await persist())) {
      setBusy(null);
      return;
    }
    try {
      const res = await fetch(`/api/clips/${clip.id}/render`, { method: "POST", credentials: "same-origin" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Render failed");
      const jobId = data.id as string;
      for (let i = 0; i < 240; i++) {
        await new Promise((r) => setTimeout(r, 1500));
        const job = await fetch(`/api/jobs/${jobId}`, { credentials: "same-origin" }).then((r) => r.json());
        setMessage(`Burning captions… ${job.progress}%`);
        if (job.status === "done") {
          setMessage("Captions burned into the MP4.");
          router.refresh();
          break;
        }
        if (job.status === "failed") throw new Error(job.error ?? "Render failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Render failed");
      setMessage(null);
    }
    setBusy(null);
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
      <Card className="p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="label">Caption cues</p>
            <p className="mt-1 text-xs text-mist-500">
              Timings are relative to the clip start. Empty cues are dropped on save.
            </p>
          </div>
          <button onClick={addCue} className="btn-ghost !px-3 !py-1.5 text-xs">
            Add cue
          </button>
        </div>

        {cues.length === 0 ? (
          <div className="rounded-xl border border-white/10 bg-white/[0.02] p-6 text-center">
            <p className="text-sm text-mist-300">No caption cues for this clip.</p>
            <p className="mx-auto mt-1 max-w-md text-xs text-mist-500">
              Captions come from the transcription provider. You can also write them by hand — add a
              cue, type the line, then save and render.
            </p>
            <button onClick={addCue} className="btn-primary mt-3 !py-2 text-xs">
              Write the first caption
            </button>
          </div>
        ) : (
          <div className="space-y-2.5">
            {cues.map((cue, i) => (
              <div key={i} className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
                <div className="flex items-center gap-2">
                  <span className="w-6 text-[11px] tabular-nums text-mist-600">{i + 1}</span>
                  <label className="flex items-center gap-1 text-[11px] text-mist-600">
                    in
                    <input
                      type="number"
                      step={0.05}
                      min={0}
                      value={Number(cue.start.toFixed(2))}
                      onChange={(e) => update(i, { start: Number(e.target.value) })}
                      className="input !w-[76px] !px-2 !py-1 text-[12px]"
                    />
                  </label>
                  <label className="flex items-center gap-1 text-[11px] text-mist-600">
                    out
                    <input
                      type="number"
                      step={0.05}
                      min={0}
                      value={Number(cue.end.toFixed(2))}
                      onChange={(e) => update(i, { end: Number(e.target.value) })}
                      className="input !w-[76px] !px-2 !py-1 text-[12px]"
                    />
                  </label>
                  <span className="ml-auto text-[10px] tabular-nums text-mist-700">
                    {fmt(cue.start)} → {fmt(cue.end)}
                  </span>
                  <button
                    onClick={() => setCues(cues.filter((_, idx) => idx !== i))}
                    className="rounded-md px-1.5 py-1 text-mist-600 transition hover:bg-white/[0.06] hover:text-rose-300"
                    aria-label="Remove cue"
                  >
                    ×
                  </button>
                </div>
                <textarea
                  value={cue.text}
                  onChange={(e) => update(i, { text: e.target.value })}
                  rows={2}
                  className="input mt-2 resize-none text-[13px]"
                  placeholder="Caption text…"
                />
              </div>
            ))}
          </div>
        )}

        {message ? <p className="mt-4 text-[12px] text-mist-400">{message}</p> : null}
        {error ? (
          <p className="mt-4 rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-[13px] text-rose-200">{error}</p>
        ) : null}

        <div className="mt-5 flex flex-wrap gap-2">
          <button onClick={saveAndRender} disabled={busy !== null} className="btn-primary">
            {busy === "render" ? "Rendering…" : "Save & burn into video"}
          </button>
          <button onClick={save} disabled={busy !== null} className="btn-ghost">
            {busy === "save" ? "Saving…" : "Save captions"}
          </button>
          <Link href={`/clips/${clip.id}/editor`} className="btn-ghost">
            Back to editor
          </Link>
        </div>
      </Card>

      <div className="space-y-4">
        <Card className="p-4">
          <p className="label">Preview</p>
          <div className="mt-3 overflow-hidden rounded-xl bg-black">
            {clip.video_url ? (
              <video src={clip.video_url} controls playsInline className="aspect-[9/16] w-full object-cover" />
            ) : clip.thumb_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={clip.thumb_url} alt="" className="aspect-[9/16] w-full object-cover" />
            ) : (
              <div className="grid aspect-[9/16] place-items-center text-xs text-mist-600">No preview</div>
            )}
          </div>
          <p className="mt-2 text-[11px] text-mist-600">
            Burned-in captions only appear after a render. Use “Save & burn into video”.
          </p>
        </Card>

        <Card className="p-4">
          <p className="label">Style</p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <Badge tone="accent">{clip.preset.replace(/_/g, " ")}</Badge>
            <Badge>{clip.subtitle_json?.edited ? "hand-edited" : "auto"}</Badge>
          </div>
          {keywords.length ? (
            <>
              <p className="label mt-4">Highlighted keywords</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {keywords.slice(0, 10).map((k) => (
                  <span key={k} className="rounded-md bg-accent-cyan/10 px-1.5 py-0.5 text-[11px] text-accent-cyan">
                    {k}
                  </span>
                ))}
              </div>
            </>
          ) : null}
          <p className="mt-4 text-[11px] leading-relaxed text-mist-600">
            Change the preset (font, weight, colour, outline, animation) in the video editor.
          </p>
        </Card>
      </div>
    </div>
  );
}
