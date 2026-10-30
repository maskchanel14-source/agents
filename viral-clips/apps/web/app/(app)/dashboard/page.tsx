import Link from "next/link";
import { requireUser, serverFetch } from "@/lib/api";
import type { Job, Project, ProviderStatus, Usage } from "@/lib/types";
import { fmtDuration, fmtMinutes, relativeTime } from "@/lib/format";
import { Alert, Badge, Card, EmptyState, ProgressBar, SectionHeader, StatCard, StatusBadge } from "@/components/ui";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const user = await requireUser();
  const [usage, projects, jobs, providers] = await Promise.all([
    serverFetch<Usage>("/usage", { allow404: true }),
    serverFetch<Project[]>("/projects?limit=6", { allow404: true }),
    serverFetch<Job[]>("/jobs?limit=5", { allow404: true }),
    serverFetch<ProviderStatus>("/providers", { allow404: true }),
  ]);

  const recent = projects ?? [];
  const totalMinutes = usage?.minutes_used ?? 0;
  const active = recent.filter((p) => ["analyzing", "queued", "rendering", "uploading"].includes(p.status));

  return (
    <div className="space-y-7">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="label">Overview</p>
          <h1 className="mt-1.5 text-2xl font-semibold tracking-tight sm:text-3xl">
            Welcome back, {user.display_name?.split(" ")[0] ?? "creator"}
          </h1>
          <p className="mt-1.5 text-sm text-mist-500">
            Paste a video, let the engine read the whole timeline, then export the moments worth
            posting.
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/projects/new" className="btn-primary">
            New project
          </Link>
          <Link href="/export" className="btn-ghost">
            Export center
          </Link>
        </div>
      </header>

      {providers?.warnings?.length ? (
        <Alert tone="warn" title="Engine capabilities">
          <ul className="mt-1 list-disc space-y-1 pl-4">
            {providers.warnings.slice(0, 3).map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </Alert>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Processed videos"
          value={usage?.projects ?? 0}
          hint="All-time projects"
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><path d="M4 6h16v12H4z" strokeLinejoin="round" /></svg>}
        />
        <StatCard
          label="Generated clips"
          value={usage?.clips ?? 0}
          hint={`${usage?.clips_rendered ?? 0} rendered to MP4`}
          accent="text-accent-cyan"
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><path d="M4 5h16M4 12h10M4 19h13" strokeLinecap="round" /></svg>}
        />
        <StatCard
          label="Processing minutes"
          value={fmtMinutes(totalMinutes)}
          hint={`of ${usage?.plan.minutes_per_month ?? 0} included`}
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><circle cx="12" cy="12" r="8" /><path d="M12 8v4l3 2" strokeLinecap="round" /></svg>}
        />
        <StatCard
          label="Remaining credits"
          value={fmtMinutes(usage?.minutes_remaining ?? 0)}
          hint={`${usage?.plan.label ?? "Free"} plan · $${usage?.ai_cost_usd?.toFixed(3) ?? "0.000"} AI spend`}
          accent="text-emerald-300"
          icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><path d="M12 3l2.6 5.6 6.1.8-4.5 4.2 1.1 6-5.3-3-5.3 3 1.1-6L3.3 9.4l6.1-.8z" strokeLinejoin="round" /></svg>}
        />
      </section>

      {active.length ? (
        <Card className="p-5">
          <SectionHeader title="In progress" subtitle="Live processing status" />
          <div className="space-y-3">
            {active.map((p) => (
              <Link key={p.id} href={`/projects/${p.id}/analysis`} className="block rounded-xl border border-white/[0.06] p-3 transition hover:border-white/[0.14]">
                <div className="flex items-center justify-between gap-3">
                  <p className="truncate text-sm font-medium">{p.title}</p>
                  <StatusBadge status={p.status} />
                </div>
                <div className="mt-2.5">
                  <ProgressBar value={p.progress} tone={p.status === "rendering" ? "warn" : "accent"} />
                </div>
                <p className="mt-1.5 text-[11px] text-mist-600">
                  {p.stage.replace(/_/g, " ")} · {p.progress}%
                </p>
              </Link>
            ))}
          </div>
        </Card>
      ) : null}

      <section>
        <SectionHeader
          title="Recent projects"
          subtitle="Every file you analysed, newest first"
          action={
            <Link href="/history" className="text-sm text-accent-soft hover:underline">
              View all
            </Link>
          }
        />
        {recent.length === 0 ? (
          <EmptyState
            title="No projects yet"
            description="Upload a podcast, interview or webinar to generate your first set of vertical clips."
            action={
              <Link href="/projects/new" className="btn-primary mt-2">
                Upload a video
              </Link>
            }
          />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {recent.map((p) => (
              <Link
                key={p.id}
                href={p.status === "analyzed" || p.status === "ready" ? `/projects/${p.id}/clips` : `/projects/${p.id}/analysis`}
                className="card card-hover animate-fade-up flex gap-4 p-4"
              >
                <div className="relative h-[74px] w-[52px] shrink-0 overflow-hidden rounded-lg border border-white/10 bg-ink-800">
                  {p.poster_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={p.poster_url} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <div className="grid h-full place-items-center text-mist-700">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
                        <path d="M4 6h16v12H4z" strokeLinejoin="round" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <p className="truncate text-sm font-medium">{p.title}</p>
                    <StatusBadge status={p.status} />
                  </div>
                  <p className="mt-1 text-xs text-mist-500">
                    {fmtDuration(p.duration_s)} · {p.clip_count} clips · {relativeTime(p.created_at)}
                  </p>
                  <div className="mt-2 flex flex-wrap items-center gap-1.5">
                    <Badge>{p.source_type === "url" ? "URL import" : "Upload"}</Badge>
                    {p.language ? <Badge>{p.language.toUpperCase()}</Badge> : null}
                    {p.width ? <Badge>{p.width}×{p.height}</Badge> : null}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {jobs?.length ? (
        <section>
          <SectionHeader title="Recent activity" subtitle="Job log for this account" />
          <Card className="divide-y divide-white/[0.06]">
            {jobs.map((j) => (
              <div key={j.id} className="flex items-center justify-between gap-3 px-4 py-3 text-sm">
                <div className="flex items-center gap-3">
                  <Badge tone={j.status === "done" ? "success" : j.status === "failed" ? "danger" : "accent"}>
                    {j.type}
                  </Badge>
                  <span className="text-mist-300">{j.result?.summary ?? j.stage.replace(/_/g, " ")}</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-mist-600">
                  {j.error ? <span className="max-w-[280px] truncate text-rose-300">{j.error}</span> : null}
                  <span>{relativeTime(j.created_at)}</span>
                </div>
              </div>
            ))}
          </Card>
        </section>
      ) : null}
    </div>
  );
}
