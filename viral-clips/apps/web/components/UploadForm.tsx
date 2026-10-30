"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import type { Project } from "@/lib/types";

const LANGUAGES = [
  { value: "", label: "Auto detect (ID / EN / …)" },
  { value: "id", label: "Indonesian" },
  { value: "en", label: "English" },
];

export default function UploadForm({
  maxUploadMb,
  maxClips,
  presets = [3, 5, 8, 10],
}: {
  maxUploadMb: number;
  maxClips: number;
  presets?: number[];
}) {
  const router = useRouter();
  const [tab, setTab] = useState<"upload" | "url">("upload");
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [rights, setRights] = useState(false);
  const [title, setTitle] = useState("");
  const [targetClips, setTargetClips] = useState(Math.min(5, maxClips));
  const [minSeconds, setMinSeconds] = useState(15);
  const [maxSeconds, setMaxSeconds] = useState(60);
  const [language, setLanguage] = useState("");
  const [deep, setDeep] = useState(true);
  const [progress, setProgress] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function pickFile(f: File | null) {
    setError(null);
    if (!f) return;
    if (f.size > maxUploadMb * 1024 * 1024) {
      setError(`File is ${(f.size / 1024 / 1024).toFixed(0)} MB — your plan allows ${maxUploadMb} MB.`);
      return;
    }
    setFile(f);
    if (!title) setTitle(f.name.replace(/\.[^.]+$/, ""));
  }

  function analysisOptions() {
    return {
      target_clips: targetClips,
      min_seconds: minSeconds,
      max_seconds: maxSeconds,
      language: language || null,
      use_deep_model: deep,
    };
  }

  async function startAnalysis(projectId: string) {
    const res = await fetch(`/api/projects/${projectId}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(analysisOptions()),
      credentials: "same-origin",
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(typeof data?.detail === "string" ? data.detail : "Could not start analysis");
    }
  }

  async function submitUpload(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!file) {
      setError("Choose a video file first.");
      return;
    }
    setBusy(true);
    setProgress(0);
    try {
      const form = new FormData();
      form.append("file", file);
      const project = await new Promise<Project>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `/api/projects/upload?auto_analyze=false&title=${encodeURIComponent(title)}`);
        xhr.withCredentials = true;
        xhr.upload.onprogress = (evt) => {
          if (evt.lengthComputable) setProgress(Math.round((evt.loaded / evt.total) * 100));
        };
        xhr.onload = () => {
          try {
            const data = JSON.parse(xhr.responseText);
            if (xhr.status >= 200 && xhr.status < 300) resolve(data);
            else reject(new Error(data?.detail ?? `Upload failed (${xhr.status})`));
          } catch {
            reject(new Error("Unexpected server response"));
          }
        };
        xhr.onerror = () => reject(new Error("Network error during upload"));
        xhr.send(form);
      });
      await startAnalysis(project.id);
      router.push(`/projects/${project.id}/analysis`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setBusy(false);
    }
  }

  async function submitUrl(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!rights) {
      setError("Confirm you own or are authorised to process this video.");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch("/api/projects/from-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ url, attests_rights: rights, title: title || undefined }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Import failed");
      router.push(`/projects/${data.id}/analysis`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
      <div className="card p-5 sm:p-6">
        <div className="mb-5 flex rounded-xl border border-white/10 bg-ink-900/70 p-1 text-sm">
          {(["upload", "url"] as const).map((t) => (
            <button
              key={t}
              onClick={() => {
                setTab(t);
                setError(null);
              }}
              className={`flex-1 rounded-lg px-3 py-2 font-medium transition ${
                tab === t ? "bg-white/[0.08] text-mist-100" : "text-mist-500 hover:text-mist-300"
              }`}
            >
              {t === "upload" ? "Upload a file" : "Import from URL"}
            </button>
          ))}
        </div>

        {tab === "upload" ? (
          <form onSubmit={submitUpload} className="space-y-4">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                pickFile(e.dataTransfer.files?.[0] ?? null);
              }}
              onClick={() => inputRef.current?.click()}
              className={`grid cursor-pointer place-items-center rounded-2xl border border-dashed px-6 py-12 text-center transition ${
                dragging
                  ? "border-accent bg-accent/[0.08]"
                  : "border-white/15 bg-white/[0.02] hover:border-white/25 hover:bg-white/[0.04]"
              }`}
            >
              <input
                ref={inputRef}
                type="file"
                accept="video/mp4,video/quicktime,video/webm,video/x-matroska,video/x-m4v"
                className="hidden"
                onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
              />
              <div className="grid h-11 w-11 place-items-center rounded-xl border border-white/10 bg-white/[0.04]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent-soft">
                  <path d="M12 16V4m0 0L7 9m5-5l5 5M4 20h16" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <p className="mt-3 text-sm font-medium">
                {file ? file.name : "Drop a video here, or click to browse"}
              </p>
              <p className="mt-1 text-xs text-mist-600">
                {file
                  ? `${(file.size / 1024 / 1024).toFixed(1)} MB · ${file.type || "video"}`
                  : `MP4, MOV, WEBM, MKV · up to ${maxUploadMb} MB`}
              </p>
            </div>

            <div>
              <label className="label mb-1.5 block" htmlFor="title">
                Project title
              </label>
              <input
                id="title"
                className="input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Episode 42 — hiring in a downturn"
              />
            </div>

            {busy ? (
              <div>
                <div className="mb-1.5 flex justify-between text-xs text-mist-500">
                  <span>Uploading…</span>
                  <span className="tabular-nums">{progress}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.07]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-accent to-accent-cyan transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            ) : null}

            {error ? (
              <p className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-[13px] text-rose-200">
                {error}
              </p>
            ) : null}

            <button className="btn-primary w-full" disabled={busy || !file}>
              {busy ? "Uploading…" : "Analyze video"}
            </button>
          </form>
        ) : (
          <form onSubmit={submitUrl} className="space-y-4">
            <div>
              <label className="label mb-1.5 block" htmlFor="url">
                Video URL
              </label>
              <input
                id="url"
                className="input"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://cdn.example.com/episode-42.mp4"
              />
              <p className="mt-2 text-[11px] leading-relaxed text-mist-600">
                Direct media links (MP4/MOV/WEBM/MKV) work today. YouTube ingestion is an operator
                setting and stays disabled unless the deployment is authorised for it — uploading a
                file you own is always the most reliable route.
              </p>
            </div>
            <label className="flex items-start gap-2.5 rounded-xl border border-white/10 bg-white/[0.02] p-3 text-[13px] text-mist-300">
              <input
                type="checkbox"
                checked={rights}
                onChange={(e) => setRights(e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-white/20 bg-ink-900 accent-accent"
              />
              I own this video or have permission to process and republish clips from it.
            </label>
            {error ? (
              <p className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-[13px] text-rose-200">
                {error}
              </p>
            ) : null}
            <button className="btn-primary w-full" disabled={busy || !url}>
              {busy ? "Importing…" : "Import and analyze"}
            </button>
          </form>
        )}
      </div>

      <div className="card space-y-5 p-5 sm:p-6">
        <div>
          <h2 className="text-sm font-semibold">Analysis settings</h2>
          <p className="mt-1 text-xs text-mist-500">Applied to this project only.</p>
        </div>

        <div>
          <p className="label mb-2">Clips to generate (max {maxClips})</p>
          <div className="flex flex-wrap gap-1.5">
            {presets.filter((p) => p <= maxClips).map((p) => (
              <button
                key={p}
                onClick={() => setTargetClips(p)}
                className={`rounded-lg border px-3 py-1.5 text-sm transition ${
                  targetClips === p
                    ? "border-accent/50 bg-accent/15 text-accent-soft"
                    : "border-white/10 text-mist-400 hover:border-white/20"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="label mb-2">Clip length</p>
          <div className="grid grid-cols-2 gap-2">
            <label className="text-xs text-mist-500">
              Min (s)
              <input
                type="number"
                min={8}
                max={120}
                value={minSeconds}
                onChange={(e) => setMinSeconds(Number(e.target.value))}
                className="input mt-1"
              />
            </label>
            <label className="text-xs text-mist-500">
              Max (s)
              <input
                type="number"
                min={10}
                max={180}
                value={maxSeconds}
                onChange={(e) => setMaxSeconds(Number(e.target.value))}
                className="input mt-1"
              />
            </label>
          </div>
        </div>

        <div>
          <p className="label mb-2">Spoken language</p>
          <select className="input" value={language} onChange={(e) => setLanguage(e.target.value)}>
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        <label className="flex items-start gap-2.5 text-[13px] text-mist-300">
          <input
            type="checkbox"
            checked={deep}
            onChange={(e) => setDeep(e.target.checked)}
            className="mt-0.5 h-4 w-4 accent-accent"
          />
          <span>
            Deep scoring model
            <span className="mt-0.5 block text-[11px] text-mist-600">
              Uses the higher-capability model for moment ranking. Higher accuracy, higher cost.
            </span>
          </span>
        </label>

        <p className="border-t border-white/[0.06] pt-4 text-[11px] leading-relaxed text-mist-600">
          Scores estimate short-form potential from nine signals. They are not a guarantee of
          performance — no tool can promise virality.
        </p>
      </div>
    </div>
  );
}
