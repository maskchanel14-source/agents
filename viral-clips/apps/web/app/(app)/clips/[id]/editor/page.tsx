import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser, serverFetch } from "@/lib/api";
import type { Clip, Preset, Project, Usage } from "@/lib/types";
import ClipEditor from "@/components/ClipEditor";
import { Badge } from "@/components/ui";

export const dynamic = "force-dynamic";

export default async function EditorPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await requireUser();
  const clip = await serverFetch<Clip>(`/clips/${id}`, { allow404: true });
  if (!clip) notFound();
  const [project, presetData, usage] = await Promise.all([
    serverFetch<Project>(`/projects/${clip.project_id}`, { allow404: true }),
    serverFetch<{ presets: Preset[] }>("/presets", { allow404: true }),
    serverFetch<Usage>("/usage", { allow404: true }),
  ]);

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="label">Video editor</p>
          <h1 className="mt-1.5 truncate text-2xl font-semibold tracking-tight">{clip.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge>{project?.title ?? "Project"}</Badge>
            <Badge>{Math.round(clip.duration_s)}s</Badge>
            <Badge tone={clip.status === "ready" ? "success" : "default"}>{clip.status}</Badge>
            <span className="text-xs text-mist-600">{user.plan} plan</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Link href={`/projects/${clip.project_id}/clips`} className="btn-ghost">
            All clips
          </Link>
          <Link href={`/clips/${clip.id}/subtitles`} className="btn-ghost">
            Subtitles
          </Link>
        </div>
      </header>

      <ClipEditor
        clip={clip}
        presets={presetData?.presets ?? []}
        plan={usage?.plan.name ?? user.plan}
        sourceUrl={project?.source_url_playable ?? null}
      />
    </div>
  );
}
