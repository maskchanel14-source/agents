export function fmtDuration(seconds: number | null | undefined): string {
  if (seconds == null || Number.isNaN(seconds)) return "—";
  const s = Math.max(0, Math.round(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  return `${m}:${String(sec).padStart(2, "0")}`;
}

export function fmtMinutes(minutes: number | null | undefined): string {
  if (minutes == null) return "—";
  if (minutes < 1) return `${Math.round(minutes * 60)}s`;
  return `${minutes.toFixed(minutes < 10 ? 1 : 0)} min`;
}

export function fmtDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" }) +
    ", " + d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

export function relativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  const diff = Date.now() - then;
  const mins = Math.round(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return days === 1 ? "yesterday" : `${days}d ago`;
}

export function scoreTone(score: number): { text: string; ring: string; label: string } {
  if (score >= 80) return { text: "text-emerald-300", ring: "#34D399", label: "Exceptional" };
  if (score >= 65) return { text: "text-accent-cyan", ring: "#22D3EE", label: "Strong" };
  if (score >= 45) return { text: "text-amber-300", ring: "#FBBF24", label: "Average" };
  return { text: "text-rose-300", ring: "#FB7185", label: "Weak" };
}

export const STATUS_STYLES: Record<string, string> = {
  uploaded: "border-white/10 text-mist-300",
  queued: "border-accent/30 text-accent-soft",
  analyzing: "border-accent/40 text-accent-soft",
  analyzed: "border-accent-cyan/30 text-accent-cyan",
  rendering: "border-amber-400/30 text-amber-300",
  ready: "border-emerald-400/30 text-emerald-300",
  failed: "border-rose-400/30 text-rose-300",
  suggested: "border-white/10 text-mist-300",
};

export function stageLabel(stage: string): string {
  return stage
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
