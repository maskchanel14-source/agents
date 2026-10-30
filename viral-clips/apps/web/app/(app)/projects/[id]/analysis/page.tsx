import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser, serverFetch } from "@/lib/api";
import type { Clip, Job, Project } from "@/lib/types";
import { fmtDuration } from "@/lib/format";
import { Badge, Card, KeyValue, ProgressBar, SectionHeader, StatusBadge } from "@/components/ui";
import JobProgress from "@/components/JobProgress";

export const dynamic = "force-dynamic";

interface AnalysisReport {
  project_id: string;
  status: string;
  warnings: string[];
  analysis: {
    media?: { duration_s: number; width: number; height: number; fps: number; video_codec?: string; has_audio?: boolean };
    audio?: { speech_regions: number; speech_seconds: number; dynamic_range_db: number };
    transcript?: { provider: string; language: string | null; segments: number; words: number; error: string | null };
    visuals?: { available: boolean; face_coverage: number; mean_motion: number; sampled_fps?: number };
    scenes?: { count: number };
    candidates?: {
      candidates_generated: number;
      candidates_scored: number;
      scoring_source: string;
      selected: number;
      llm_model: string | null;
      mean_score: number;
    };
  } | null;
}

export default async function AnalysisPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  await requireUser();
  const project = await serverFetch<Project>(`/projects/${id}`, { allow404: true });
  if (!project) notFound();
  const [report, jobs, clips] = await Promise.all([
    serverFetch<AnalysisReport>(`/projects/${id}/analysis`, { allow404: true }),
    serverFetch<Job[]>(`/jobs?project_id=${id}&limit=5`, { allow404: true }),
    serverFetch<Clip[]>(`/projects/${id}/clips`, { allow404: true }),
  ]);

  const latest = (jobs ?? [])[0] ?? null;
  const processing = ["queued", "analyzing", "rendering", "uploading"].includes(project.status);
  const a = report?.analysis;
  const transcriptMissing = a?.transcript && a.transcript.words === 0;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="label">Analysis</p>
          <h1 className="mt-1.5 truncate text-2xl font-semibold tracking-tight">{project.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-mist-500">
            <StatusBadge status={project.status} />
            <Badge>{fmtDuration(project.duration_s)}</Badge>
            {project.width ? <Badge>{project.width}×{project.height}</Badge> : null}
            {project.language ? <Badge>{project.language.toUpperCase()}</Badge> : null}
            <Badge>{project.clip_count} clips</Badge>
          </div>
        </div>
        <div className="flex gap-2">
          <Link href={`/projects/${project.id}/clips`} className="btn-primary">
            View clips
          </Link>
          <Link href="/history" className="btn-ghost">
            History
          </Link>
        </div>
      </header>

      {processing || latest ? (
        <div className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
          <JobProgress initialJob={latest} kind={project.status === "rendering" ? "render" : "analyze"} />
          <Card className="p-5">
            <p className="label">Source</p>
            <div className="mt-3 overflow-hidden rounded-xl border border-white/10 bg-black">
              {project.source_url_playable ? (
                <video
                  src={project.source_url_playable}
                  controls
                  preload="metadata"
                  className="aspect-video w-full"
                />
              ) : (
                <div className="grid aspect-video place-items-center text-xs text-mist-600">
                  Preview unavailable
                </div>
              )}
            </div>
            <div className="mt-4 space-y-0.5">
              <KeyValue label="Source" value={project.source_type === "url" ? "URL import" : "Upload"} />
              <KeyValue label="Duration" value={fmtDuration(project.duration_s)} />
              <KeyValue label="Frames" value={project.fps ? `${project.fps.toFixed(1)} fps` : "—"} />
              <KeyValue label="Progress" value={<span className="tabular-nums">{project.progress}%</span>} />
            </div>
            {project.error ? (
              <p className="mt-3 rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-[13px] text-rose-200">
                {project.error}
              </p>
            ) : null}
          </Card>
        </div>
      ) : null}

      {a ? (
        <>
          <section className="grid gap-4 md:grid-cols-3">
            <Card className="p-5">
              <p className="label">Transcript</p>
              <p className="mt-2 text-2xl font-semibold tabular-nums">{a.transcript?.words ?? 0}</p>
              <p className="text-xs text-mist-500">timed words</p>
              <div className="mt-3 space-y-0.5">
                <KeyValue label="Provider" value={a.transcript?.provider ?? "none"} />
                <KeyValue label="Segments" value={a.transcript?.segments ?? 0} />
                <KeyValue label="Language" value={a.transcript?.language ?? "—"} />
              </div>
            </Card>
            <Card className="p-5">
              <p className="label">Speech activity</p>
              <p className="mt-2 text-2xl font-semibold tabular-nums">
                {fmtDuration(a.audio?.speech_seconds ?? 0)}
              </p>
              <p className="text-xs text-mist-500">across {a.audio?.speech_regions ?? 0} regions</p>
              <div className="mt-3 space-y-0.5">
                <KeyValue label="Dynamic range" value={`${a.audio?.dynamic_range_db ?? 0} dB`} />
                <KeyValue label="Scene cuts" value={a.scenes?.count ?? 0} />
                <KeyValue label="Audio track" value={a.media?.has_audio ? "yes" : "no"} />
              </div>
            </Card>
            <Card className="p-5">
              <p className="label">Moment scoring</p>
              <p className="mt-2 text-2xl font-semibold tabular-nums">{a.candidates?.selected ?? 0}</p>
              <p className="text-xs text-mist-500">
                of {a.candidates?.candidates_scored ?? 0} scored candidates
              </p>
              <div className="mt-3 space-y-0.5">
                <KeyValue label="Engine" value={a.candidates?.scoring_source ?? "heuristic"} />
                <KeyValue label="Mean score" value={a.candidates?.mean_score ?? 0} />
                <KeyValue
                  label="Face coverage"
                  value={a.visuals?.available ? `${Math.round((a.visuals.face_coverage ?? 0) * 100)}%` : "n/a"}
                />
              </div>
            </Card>
          </section>

          {report?.warnings?.length ? (
            <Card className="p-5">
              <SectionHeader title="Engine notes" subtitle="What was available for this run" />
              <ul className="space-y-2 text-[13px] text-mist-300">
                {report.warnings.map((w) => (
                  <li key={w} className="flex gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400/70" />
                    {w}
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}

          {transcriptMissing ? (
            <Card className="p-5">
              <p className="text-sm text-mist-300">
                No transcript for this run, so clips were chosen from acoustic energy, scene changes
                and subject motion. Configure a transcription provider to unlock captions and
                transcript-based scoring.
              </p>
            </Card>
          ) : null}
        </>
      ) : project.status === "failed" ? (
        <Card className="p-6">
          <p className="text-sm text-rose-200">Analysis failed.</p>
          <p className="mt-1 text-sm text-mist-500">{project.error}</p>
        </Card>
      ) : (
        <Card className="p-6">
          <p className="text-sm text-mist-500">No analysis report yet.</p>
          <div className="mt-3">
            <ProgressBar value={project.progress} />
          </div>
        </Card>
      )}

      {clips?.length ? (
        <Card className="p-5">
          <SectionHeader
            title="Top moments"
            subtitle="Ranked by estimated short-form potential"
            action={
              <Link href={`/projects/${project.id}/clips`} className="text-sm text-accent-soft hover:underline">
                Open clip library
              </Link>
            }
          />
          <div className="space-y-2">
            {clips.slice(0, 5).map((c) => (
              <div key={c.id} className="flex items-center justify-between gap-3 rounded-xl border border-white/[0.06] px-3 py-2.5">
                <div className="min-w-0">
                  <p className="truncate text-sm">{c.title}</p>
                  <p className="text-[11px] text-mist-600">
                    {fmtDuration(c.start_s)} → {fmtDuration(c.end_s)} · {Math.round(c.duration_s)}s
                  </p>
                </div>
                <span className="tabular-nums text-sm font-semibold text-accent-soft">
                  {Math.round(c.score)}
                </span>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
