"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { Job } from "@/lib/types";
import { ProgressBar } from "./ui";

const ANALYSIS_STAGES = [
  ["probing_media", "Reading media info"],
  ["extracting_audio", "Extracting audio"],
  ["transcribing", "Transcribing speech"],
  ["analyzing_visuals", "Scene & audio analysis"],
  ["tracking_subjects", "Tracking speakers"],
  ["generating_candidates", "Generating candidates"],
  ["scoring_moments", "Scoring moments"],
  ["building_clips", "Building clips"],
  ["generating_thumbnails", "Creating thumbnails"],
  ["completed", "Done"],
];

const RENDER_STAGES = [
  ["queued", "Queued"],
  ["rendering_clips", "Rendering 1080×1920"],
  ["completed", "Done"],
];

export default function JobProgress({
  initialJob,
  kind = "analyze",
  onDoneRedirect,
}: {
  initialJob: Job | null;
  kind?: "analyze" | "render";
  onDoneRedirect?: string;
}) {
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(initialJob);
  const doneRef = useRef(false);

  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") return;
    const timer = setInterval(async () => {
      try {
        const res = await fetch(`/api/jobs/${job.id}`, { credentials: "same-origin" });
        if (!res.ok) return;
        const next: Job = await res.json();
        setJob(next);
      } catch {
        /* transient */
      }
    }, 1500);
    return () => clearInterval(timer);
  }, [job]);

  useEffect(() => {
    if (!job) return;
    if (job.status === "done" && !doneRef.current) {
      doneRef.current = true;
      if (onDoneRedirect) router.push(onDoneRedirect);
      router.refresh();
    }
    if (job.status === "failed") router.refresh();
  }, [job, onDoneRedirect, router]);

  if (!job) return null;

  const stages = kind === "render" ? RENDER_STAGES : ANALYSIS_STAGES;
  const activeIndex = Math.max(
    0,
    stages.findIndex(([key]) => job.stage === key || job.stage.startsWith(key)),
  );
  const failed = job.status === "failed";
  const done = job.status === "done";

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold">
            {failed ? "Processing failed" : done ? "Processing complete" : "Processing"}
          </p>
          <p className="mt-0.5 text-xs text-mist-500">
            {job.stage.replace(/_/g, " ")} · {job.progress}%
          </p>
        </div>
        <span
          className={`tabular-nums text-2xl font-semibold ${failed ? "text-rose-300" : done ? "text-emerald-300" : "text-mist-100"}`}
        >
          {job.progress}%
        </span>
      </div>

      <div className="mt-3">
        <ProgressBar value={job.progress} tone={failed ? "warn" : done ? "success" : "accent"} />
      </div>

      {failed && job.error ? (
        <p className="mt-3 rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-[13px] text-rose-200">
          {job.error}
        </p>
      ) : null}

      <ol className="mt-4 space-y-1.5">
        {stages.map(([key, label], idx) => {
          const finished = done || idx < activeIndex || job.progress === 100;
          const current = !finished && idx === activeIndex;
          return (
            <li key={key} className="flex items-center gap-2.5 text-[13px]">
              <span
                className={`grid h-4 w-4 place-items-center rounded-full border ${
                  finished
                    ? "border-emerald-400/40 bg-emerald-400/20 text-emerald-300"
                    : current
                      ? "animate-pulse-ring border-accent/50 bg-accent/20 text-accent-soft"
                      : "border-white/10 text-mist-700"
                }`}
              >
                {finished ? (
                  <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4">
                    <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : null}
              </span>
              <span className={finished ? "text-mist-300" : current ? "text-mist-100" : "text-mist-600"}>
                {label}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
