import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser, serverFetch } from "@/lib/api";
import type { Clip } from "@/lib/types";
import SubtitleEditor from "@/components/SubtitleEditor";
import { Badge } from "@/components/ui";

export const dynamic = "force-dynamic";

export default async function SubtitlesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  await requireUser();
  const clip = await serverFetch<Clip>(`/clips/${id}`, { allow404: true });
  if (!clip) notFound();

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="label">Subtitle editor</p>
          <h1 className="mt-1.5 text-2xl font-semibold tracking-tight">{clip.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge>{Math.round(clip.duration_s)}s</Badge>
            <Badge>{clip.subtitle_json?.cues?.length ?? 0} cues</Badge>
            <Badge tone={clip.status === "ready" ? "success" : "default"}>{clip.status}</Badge>
          </div>
        </div>
        <Link href={`/clips/${clip.id}/editor`} className="btn-ghost">
          Video editor
        </Link>
      </header>
      <SubtitleEditor clip={clip} />
    </div>
  );
}
