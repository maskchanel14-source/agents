import Link from "next/link";
import { requireUser, serverFetch } from "@/lib/api";
import type { Clip, Project } from "@/lib/types";
import { fmtDuration } from "@/lib/format";
import { Badge, Card, EmptyState, SectionHeader, StatusBadge } from "@/components/ui";
import RenderAll from "@/components/RenderAll";

export const dynamic = "force-dynamic";

export default async function ExportPage({
  searchParams,
}: {
  searchParams: Promise<{ project?: string }>;
}) {
  await requireUser();
  const { project: selectedId } = await searchParams;
  const projects = (await serverFetch<Project[]>("/projects?limit=50", { allow404: true })) ?? [];
  const selected = projects.find((p) => p.id === selectedId) ?? projects[0] ?? null;
  const clips = selected
    ? (await serverFetch<Clip[]>(`/projects/${selected.id}/clips`, { allow404: true })) ?? []
    : [];
  const ready = clips.filter((c) => c.status === "ready" && c.video_url);

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="label">Export center</p>
          <h1 className="mt-1.5 text-2xl font-semibold tracking-tight">Deliver to Shorts, TikTok, Reels</h1>
          <p className="mt-1.5 max-w-2xl text-sm text-mist-500">
            Every render is 1080×1920, H.264 High profile with AAC audio, loudness-normalised to
            −14 LUFS and written with a fast-start moov atom so platforms accept it immediately.
          </p>
        </div>
        {selected ? <RenderAll projectId={selected.id} label="Render all clips" /> : null}
      </header>

      {projects.length === 0 ? (
        <EmptyState
          title="Nothing to export yet"
          description="Analyze a video first; rendered clips will show up here for download."
          action={
            <Link href="/projects/new" className="btn-primary mt-2">
              New project
            </Link>
          }
        />
      ) : (
        <>
          <div className="flex flex-wrap gap-1.5">
            {projects.map((p) => (
              <Link
                key={p.id}
                href={`/export?project=${p.id}`}
                className={`rounded-lg border px-3 py-1.5 text-xs transition ${
                  selected?.id === p.id
                    ? "border-accent/50 bg-accent/10 text-accent-soft"
                    : "border-white/10 text-mist-400 hover:border-white/20"
                }`}
              >
                {p.title}
              </Link>
            ))}
          </div>

          {selected ? (
            <>
              <Card className="flex flex-wrap items-center justify-between gap-4 p-5">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold">{selected.title}</p>
                    <StatusBadge status={selected.status} />
                  </div>
                  <p className="mt-1 text-xs text-mist-500">
                    {fmtDuration(selected.duration_s)} source · {clips.length} clips · {ready.length} rendered
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <a
                    href={`/api/projects/${selected.id}/export`}
                    className={`btn-primary ${ready.length ? "" : "pointer-events-none opacity-50"}`}
                  >
                    Download all ({ready.length}) as ZIP
                  </a>
                  <Link href={`/projects/${selected.id}/clips`} className="btn-ghost">
                    Clip library
                  </Link>
                </div>
              </Card>

              {ready.length === 0 ? (
                <Card className="p-6">
                  <p className="text-sm text-mist-300">No rendered clips for this project yet.</p>
                  <p className="mt-1 text-xs text-mist-500">
                    Rendering takes the length of the clip plus a little overhead. Use “Render all
                    clips” above.
                  </p>
                </Card>
              ) : (
                <Card className="overflow-hidden">
                  <div className="border-b border-white/[0.06] px-5 py-3">
                    <SectionHeader title="Rendered files" subtitle="Individual downloads" />
                  </div>
                  <div className="divide-y divide-white/[0.06]">
                    {ready.map((c, i) => (
                      <div key={c.id} className="flex flex-wrap items-center justify-between gap-3 px-5 py-3">
                        <div className="flex min-w-0 items-center gap-3">
                          <span className="w-6 text-xs tabular-nums text-mist-600">{i + 1}</span>
                          {c.thumb_url ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={c.thumb_url} alt="" className="h-14 w-9 rounded-md object-cover" />
                          ) : null}
                          <div className="min-w-0">
                            <p className="truncate text-sm">{c.title}</p>
                            <p className="text-[11px] text-mist-600">
                              {Math.round(c.duration_s)}s · score {Math.round(c.score)} ·{" "}
                              {c.preset.replace(/_/g, " ")}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge tone="success">MP4</Badge>
                          <a href={c.video_url!} download className="btn-ghost !px-3 !py-1.5 text-xs">
                            Download
                          </a>
                          <Link href={`/clips/${c.id}/editor`} className="btn-subtle !px-2.5 !py-1.5 text-xs">
                            Edit
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </>
          ) : null}
        </>
      )}
    </div>
  );
}
