import Link from "next/link";
import { requireUser, serverFetch } from "@/lib/api";
import type { Job, Project } from "@/lib/types";
import { fmtDate, fmtDuration, relativeTime } from "@/lib/format";
import { Badge, Card, EmptyState, StatusBadge } from "@/components/ui";

export const dynamic = "force-dynamic";

export default async function HistoryPage() {
  await requireUser();
  const [projects, jobs] = await Promise.all([
    serverFetch<Project[]>("/projects?limit=50", { allow404: true }),
    serverFetch<Job[]>("/jobs?limit=30", { allow404: true }),
  ]);

  const list = projects ?? [];

  return (
    <div className="space-y-6">
      <header>
        <p className="label">History</p>
        <h1 className="mt-1.5 text-2xl font-semibold tracking-tight">Processing history</h1>
        <p className="mt-1.5 text-sm text-mist-500">Every project and job on this account.</p>
      </header>

      {list.length === 0 ? (
        <EmptyState
          title="No history yet"
          description="Once you analyze a video it appears here with its stage, clips and processing time."
          action={
            <Link href="/projects/new" className="btn-primary mt-2">
              Upload a video
            </Link>
          }
        />
      ) : (
        <Card className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead>
              <tr className="border-b border-white/[0.06] text-left text-[11px] uppercase tracking-wider text-mist-600">
                <th className="px-4 py-3 font-medium">Project</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Duration</th>
                <th className="px-4 py-3 font-medium">Clips</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {list.map((p) => (
                <tr key={p.id} className="transition hover:bg-white/[0.02]">
                  <td className="max-w-[280px] truncate px-4 py-3">{p.title}</td>
                  <td className="px-4 py-3"><StatusBadge status={p.status} /></td>
                  <td className="px-4 py-3 tabular-nums text-mist-400">{fmtDuration(p.duration_s)}</td>
                  <td className="px-4 py-3 tabular-nums text-mist-400">{p.clip_count}</td>
                  <td className="px-4 py-3 text-xs text-mist-500">{fmtDate(p.created_at)}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={["analyzed", "ready"].includes(p.status) ? `/projects/${p.id}/clips` : `/projects/${p.id}/analysis`}
                      className="text-xs text-accent-soft hover:underline"
                    >
                      Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {jobs?.length ? (
        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold">Job log</h2>
          <div className="divide-y divide-white/[0.05]">
            {jobs.map((j) => (
              <div key={j.id} className="flex items-center justify-between gap-3 py-2.5 text-[13px]">
                <div className="flex items-center gap-2.5">
                  <Badge tone={j.status === "done" ? "success" : j.status === "failed" ? "danger" : "accent"}>
                    {j.type}
                  </Badge>
                  <span className="text-mist-400">{j.result?.summary ?? j.stage.replace(/_/g, " ")}</span>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-mist-600">
                  {j.error ? <span className="max-w-[320px] truncate text-rose-300">{j.error}</span> : null}
                  <span>{relativeTime(j.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
