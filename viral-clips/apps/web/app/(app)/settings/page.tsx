import { requireUser, serverFetch } from "@/lib/api";
import type { ProviderStatus, Usage } from "@/lib/types";
import { fmtMinutes } from "@/lib/format";
import { Alert, Badge, Card, KeyValue, ProgressBar, SectionHeader } from "@/components/ui";

export const dynamic = "force-dynamic";

interface PlanRow {
  name: string;
  label: string;
  minutes_per_month: number;
  max_clips_per_video: number;
  max_projects: number;
  max_upload_mb: number;
  max_video_minutes: number;
  features: string[];
}

interface AiRow {
  provider: string;
  model: string;
  task: string;
  calls: number;
  cost_usd: number;
  tokens: number;
}

export default async function SettingsPage() {
  const user = await requireUser();
  const [usage, providers, plans, ai] = await Promise.all([
    serverFetch<Usage>("/usage", { allow404: true }),
    serverFetch<ProviderStatus>("/providers", { allow404: true }),
    serverFetch<PlanRow[]>("/plans", { allow404: true }),
    serverFetch<AiRow[]>("/usage/ai-breakdown", { allow404: true }),
  ]);

  const pct = usage ? Math.min(100, (usage.minutes_used / usage.plan.minutes_per_month) * 100) : 0;

  return (
    <div className="space-y-6">
      <header>
        <p className="label">Settings</p>
        <h1 className="mt-1.5 text-2xl font-semibold tracking-tight">Account & engine</h1>
        <p className="mt-1.5 text-sm text-mist-500">
          Plan, usage, AI spend and the providers this deployment is wired to.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5">
          <SectionHeader title="Account" subtitle="Identity and session" />
          <KeyValue label="Name" value={user.display_name ?? "—"} />
          <KeyValue label="Email" value={user.email} />
          <KeyValue label="Plan" value={<Badge tone="accent">{user.plan}</Badge>} />
          <KeyValue label="Member since" value={new Date(user.created_at).toLocaleDateString()} />
          <p className="mt-3 text-[11px] leading-relaxed text-mist-600">
            Sessions are signed HS256 JWTs stored in an HttpOnly, SameSite=Lax cookie. Set
            SUPABASE_JWT_SECRET to accept Supabase Auth-issued tokens instead (the API verifies
            them server-side and maps them to a local profile).
          </p>
        </Card>

        <Card className="p-5">
          <SectionHeader title="Usage this cycle" subtitle="Credits are processing minutes" />
          <div className="flex items-end justify-between">
            <p className="text-3xl font-semibold tabular-nums">{fmtMinutes(usage?.minutes_used ?? 0)}</p>
            <p className="text-xs text-mist-500">of {usage?.plan.minutes_per_month ?? 0} min</p>
          </div>
          <div className="mt-2">
            <ProgressBar value={pct} tone={pct > 90 ? "warn" : "accent"} />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-center">
            <div className="rounded-xl border border-white/[0.06] p-3">
              <p className="text-xl font-semibold tabular-nums">{usage?.clips ?? 0}</p>
              <p className="text-[11px] uppercase tracking-wider text-mist-600">clips</p>
            </div>
            <div className="rounded-xl border border-white/[0.06] p-3">
              <p className="text-xl font-semibold tabular-nums">{usage?.projects ?? 0}</p>
              <p className="text-[11px] uppercase tracking-wider text-mist-600">projects</p>
            </div>
          </div>
          <KeyValue label="AI calls" value={usage?.ai_calls ?? 0} />
          <KeyValue label="AI spend" value={`$${(usage?.ai_cost_usd ?? 0).toFixed(4)}`} />
        </Card>
      </div>

      {providers?.warnings?.length ? (
        <Alert tone="warn" title="Deployment notes">
          <ul className="mt-1 list-disc space-y-1 pl-4">
            {providers.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </Alert>
      ) : null}

      <Card className="p-5">
        <SectionHeader title="Engine providers" subtitle="Selected via environment variables, never hardcoded" />
        <div className="grid gap-x-8 gap-y-1 md:grid-cols-2">
          <KeyValue label="LLM provider" value={providers?.llm_provider ?? "—"} />
          <KeyValue
            label="LLM configured"
            value={providers?.llm_configured ? <Badge tone="success">yes</Badge> : <Badge tone="warn">heuristic only</Badge>}
          />
          <KeyValue label="Fast model" value={providers?.llm_model_fast ?? "—"} />
          <KeyValue label="Deep model" value={providers?.llm_model_deep ?? "—"} />
          <KeyValue label="ASR provider" value={providers?.asr_provider ?? "—"} />
          <KeyValue
            label="ASR configured"
            value={providers?.asr_configured ? <Badge tone="success">yes</Badge> : <Badge tone="warn">disabled</Badge>}
          />
          <KeyValue label="Storage" value={providers?.storage_backend ?? "—"} />
          <KeyValue label="Queue" value={providers?.queue_backend ?? "—"} />
          <KeyValue label="Vision analysis" value={providers?.vision_enabled ? "on" : "off"} />
          <KeyValue label="YouTube ingest" value={providers?.youtube_ingest ? "enabled" : "disabled"} />
          <KeyValue label="Supabase auth" value={providers?.supabase_auth ? "enabled" : "off"} />
          <KeyValue label="FFmpeg" value={<span className="text-[11px] text-mist-400">{providers?.ffmpeg_version?.slice(0, 48)}</span>} />
        </div>
      </Card>

      <Card className="p-5">
        <SectionHeader title="Plans" subtitle="Credit-based; billing is not activated in this build" />
        <div className="grid gap-3 md:grid-cols-3">
          {(plans ?? []).map((p) => {
            const current = p.name === user.plan;
            return (
              <div
                key={p.name}
                className={`rounded-2xl border p-4 ${current ? "border-accent/50 bg-accent/[0.07]" : "border-white/10"}`}
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold">{p.label}</p>
                  {current ? <Badge tone="accent">current</Badge> : null}
                </div>
                <p className="mt-2 text-2xl font-semibold tabular-nums">
                  {p.minutes_per_month}
                  <span className="ml-1 text-xs font-normal text-mist-500">min / month</span>
                </p>
                <ul className="mt-3 space-y-1 text-[12px] text-mist-400">
                  <li>{p.max_clips_per_video} clips per video</li>
                  <li>{p.max_projects} projects</li>
                  <li>{p.max_upload_mb} MB uploads · {p.max_video_minutes} min video</li>
                  {p.features.slice(0, 3).map((f) => (
                    <li key={f} className="text-mist-500">{f.replace(/_/g, " ")}</li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
        <p className="mt-3 text-[11px] leading-relaxed text-mist-600">
          Payment integration points exist (plan field + usage metering + per-plan quotas). Real
          billing is intentionally not enabled: connect Stripe Checkout/webhooks before charging.
        </p>
      </Card>

      {ai?.length ? (
        <Card className="p-5">
          <SectionHeader title="AI cost breakdown" subtitle="Per provider, model and task" />
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-sm">
              <thead>
                <tr className="border-b border-white/[0.06] text-left text-[11px] uppercase tracking-wider text-mist-600">
                  <th className="py-2 font-medium">Provider</th>
                  <th className="py-2 font-medium">Model</th>
                  <th className="py-2 font-medium">Task</th>
                  <th className="py-2 text-right font-medium">Calls</th>
                  <th className="py-2 text-right font-medium">Tokens</th>
                  <th className="py-2 text-right font-medium">Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05]">
                {ai.map((row) => (
                  <tr key={`${row.provider}-${row.model}-${row.task}`}>
                    <td className="py-2 text-mist-300">{row.provider}</td>
                    <td className="py-2 text-mist-400">{row.model}</td>
                    <td className="py-2 text-mist-500">{row.task}</td>
                    <td className="py-2 text-right tabular-nums">{row.calls}</td>
                    <td className="py-2 text-right tabular-nums text-mist-400">{row.tokens}</td>
                    <td className="py-2 text-right tabular-nums">${row.cost_usd.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}
    </div>
  );
}
