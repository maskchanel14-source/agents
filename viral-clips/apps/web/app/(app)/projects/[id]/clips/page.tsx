import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser, serverFetch } from "@/lib/api";
import type { Clip, Project } from "@/lib/types";
import { fmtDuration } from "@/lib/format";
import { Alert, Badge, Card, EmptyState, SectionHeader, StatusBadge } from "@/components/ui";
import ClipCard from "@/components/ClipCard";
import RenderAll from "@/components/RenderAll";

export const dynamic = "force-dynamic";

export default async function ClipsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  await requireUser();
  const project = await serverFetch<Project>(`/projects/${id}`, { allow404: true });
  if (!project) notFound();
  const clips = (await serverFetch<Clip[]>(`/projects/${id}/clips`, { allow404: true })) ?? [];

  const ready = clips.filter((c) => c.status === "ready").length;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="label">Clip library</p>
          <h1 className="mt-1.5 truncate text-2xl font-semibold tracking-tight">{project.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={project.status} />
            <Badge>{clips.length} clips</Badge>
            <Badge tone={ready ? "success" : "default"}>{ready} rendered</Badge>
            <span className="text-xs text-mist-600">Source {fmtDuration(project.duration_s)}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link href={`/projects/${project.id}/analysis`} className="btn-ghost">
            Analysis
          </Link>
          <Link href="/export" className="btn-ghost">
            Export center
          </Link>
          <RenderAll projectId={project.id} />
        </div>
      </header>

      {clips.length === 0 ? (
        <EmptyState
          title="No clips yet"
          description="Analysis has not produced clips for this project. Re-run analysis with different clip length settings."
          action={
            <Link href={`/projects/${project.id}/analysis`} className="btn-primary mt-2">
              Review analysis
            </Link>
          }
        />
      ) : (
        <>
          <Alert tone="info" title="How to read the score">
            Each clip is scored 0–100 across nine signals (hook strength, curiosity, emotion, story
            completeness, shareability, engagement, information value, context independence and
            visual engagement). Open a clip to see the breakdown and adjust cropping or captions
            before you render.
          </Alert>

          <SectionHeader title="Ranked moments" subtitle="Highest estimated potential first" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {clips.map((clip) => (
              <ClipCard key={clip.id} clip={clip} />
            ))}
          </div>

          <Card className="p-5">
            <SectionHeader title="Transcript context" subtitle="What the speaker actually said in each clip" />
            <div className="space-y-3">
              {clips.slice(0, 4).map((c) => (
                <div key={c.id} className="rounded-xl border border-white/[0.06] p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{c.title}</p>
                    <span className="tabular-nums text-xs text-mist-500">{Math.round(c.score)}/100</span>
                  </div>
                  <p className="mt-1.5 text-[13px] leading-relaxed text-mist-400 line-clamp-3">
                    {c.text || "No transcript was available for this run — clip chosen from acoustic and visual signals."}
                  </p>
                  {c.explanation ? (
                    <p className="mt-1.5 text-[11px] text-mist-600">{c.explanation}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
