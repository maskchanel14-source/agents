import type { ReactNode } from "react";
import { STATUS_STYLES, scoreTone, stageLabel } from "@/lib/format";

export function Card({
  children,
  className = "",
  hover = false,
}: {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}) {
  return <div className={`card ${hover ? "card-hover" : ""} ${className}`}>{children}</div>;
}

export function StatCard({
  label,
  value,
  hint,
  accent = "text-mist-100",
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  accent?: string;
  icon?: ReactNode;
}) {
  return (
    <Card className="animate-fade-up p-5" hover>
      <div className="flex items-start justify-between">
        <p className="label">{label}</p>
        {icon ? <span className="text-mist-600">{icon}</span> : null}
      </div>
      <p className={`mt-3 text-3xl font-semibold tracking-tight tabular-nums ${accent}`}>{value}</p>
      {hint ? <p className="mt-1 text-xs text-mist-500">{hint}</p> : null}
    </Card>
  );
}

export function Badge({
  children,
  tone = "default",
  className = "",
}: {
  children: ReactNode;
  tone?: "default" | "accent" | "success" | "warn" | "danger";
  className?: string;
}) {
  const tones: Record<string, string> = {
    default: "border-white/10 text-mist-300",
    accent: "border-accent/30 text-accent-soft bg-accent/10",
    success: "border-emerald-400/30 text-emerald-300 bg-emerald-400/10",
    warn: "border-amber-400/30 text-amber-300 bg-amber-400/10",
    danger: "border-rose-400/30 text-rose-300 bg-rose-400/10",
  };
  return <span className={`chip ${tones[tone]} ${className}`}>{children}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const tone =
    status === "ready" || status === "analyzed"
      ? "success"
      : status === "failed"
        ? "danger"
        : status === "rendering" || status === "analyzing"
          ? "warn"
          : status === "queued"
            ? "accent"
            : "default";
  return (
    <Badge tone={tone as "default"}>
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === "analyzing" || status === "rendering"
            ? "animate-pulse bg-current"
            : "bg-current opacity-70"
        }`}
      />
      {stageLabel(status)}
    </Badge>
  );
}

export function ProgressBar({
  value,
  tone = "accent",
  thin = false,
}: {
  value: number;
  tone?: "accent" | "success" | "warn";
  thin?: boolean;
}) {
  const grad: Record<string, string> = {
    accent: "from-accent to-accent-cyan",
    success: "from-emerald-400 to-emerald-300",
    warn: "from-amber-400 to-amber-300",
  };
  return (
    <div className={`w-full overflow-hidden rounded-full bg-white/[0.07] ${thin ? "h-1" : "h-1.5"}`}>
      <div
        className={`h-full rounded-full bg-gradient-to-r ${grad[tone]} transition-all duration-500`}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
}

export function ScoreRing({ score, size = 64 }: { score: number; size?: number }) {
  const { ring, text, label } = scoreTone(score);
  const r = (size - 8) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, score));
  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
      title={`${label} — estimated short-form potential, not a guarantee`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(255,255,255,0.08)" strokeWidth="5" fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={ring}
          strokeWidth="5"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c - (pct / 100) * c}
        />
      </svg>
      <span className={`absolute text-sm font-semibold tabular-nums ${text}`}>{Math.round(score)}</span>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Card className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-2xl border border-white/10 bg-white/[0.03]">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="text-accent-soft">
          <path d="M4 6h16v12H4z" strokeLinejoin="round" />
          <path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none" />
        </svg>
      </div>
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="max-w-sm text-sm text-mist-500">{description}</p>
      {action}
    </Card>
  );
}

export function SectionHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-mist-500">{subtitle}</p> : null}
      </div>
      {action}
    </div>
  );
}

export function Alert({ tone = "warn", title, children }: { tone?: "warn" | "danger" | "info"; title: string; children?: ReactNode }) {
  const tones = {
    warn: "border-amber-400/25 bg-amber-400/[0.07] text-amber-200",
    danger: "border-rose-400/25 bg-rose-400/[0.07] text-rose-200",
    info: "border-accent/25 bg-accent/[0.07] text-accent-soft",
  } as const;
  return (
    <div className={`rounded-xl border px-4 py-3 text-sm ${tones[tone]}`}>
      <p className="font-semibold">{title}</p>
      {children ? <div className="mt-1 text-[13px] leading-relaxed opacity-90">{children}</div> : null}
    </div>
  );
}

export function KeyValue({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-white/[0.06] py-2.5 last:border-0">
      <span className="text-xs uppercase tracking-wider text-mist-500">{label}</span>
      <span className="text-right text-sm text-mist-100">{value}</span>
    </div>
  );
}

export function statusClass(status: string): string {
  return STATUS_STYLES[status] ?? "border-white/10 text-mist-300";
}
