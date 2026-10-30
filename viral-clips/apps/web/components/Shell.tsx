import Link from "next/link";
import type { ReactNode } from "react";
import type { Usage, User } from "@/lib/types";
import { fmtMinutes } from "@/lib/format";
import { ProgressBar } from "./ui";
import LogoutButton from "./LogoutButton";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "M4 13h6V4H4v9zm10 7h6v-9h-6v9zM4 20h6v-4H4v4zm10-11h6V4h-6v5z" },
  { href: "/projects/new", label: "New project", icon: "M12 5v14M5 12h14" },
  { href: "/export", label: "Export center", icon: "M12 3v12m0 0l4-4m-4 4l-4-4M4 21h16" },
  { href: "/history", label: "History", icon: "M12 8v5l3 2m6-2a9 9 0 11-9-9" },
  { href: "/settings", label: "Settings", icon: "M12 15a3 3 0 100-6 3 3 0 000 6zM4 12h2m12 0h2M12 4v2m0 12v2" },
];

export default function Shell({
  user,
  usage,
  children,
}: {
  user: User;
  usage: Usage | null;
  children: ReactNode;
}) {
  const used = usage ? usage.minutes_used : 0;
  const total = usage?.plan.minutes_per_month ?? 0;
  const pct = total ? Math.min(100, (used / total) * 100) : 0;

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-[248px] shrink-0 flex-col border-r border-white/[0.06] bg-ink-900/70 px-4 py-6 backdrop-blur-xl lg:flex">
        <Link href="/dashboard" className="mb-8 flex items-center gap-3 px-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-accent to-accent-cyan text-ink-950 shadow-glow">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <span className="leading-tight">
            <span className="block text-[13px] font-semibold tracking-tight">Viral Clip</span>
            <span className="block text-[10px] uppercase tracking-[0.18em] text-mist-600">Generator</span>
          </span>
        </Link>

        <Link href="/projects/new" className="btn-primary mb-6 w-full">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
            <path d="M12 5v14M5 12h14" strokeLinecap="round" />
          </svg>
          New project
        </Link>

        <nav className="flex flex-col gap-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-mist-500 transition hover:bg-white/[0.05] hover:text-mist-100"
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="opacity-70 group-hover:opacity-100">
                <path d={item.icon} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="mt-auto space-y-3">
          <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
            <div className="flex items-center justify-between text-xs">
              <span className="uppercase tracking-wider text-mist-600">{usage?.plan.label ?? "Free"} plan</span>
              <span className="tabular-nums text-mist-300">
                {fmtMinutes(used)} / {total} min
              </span>
            </div>
            <div className="mt-2">
              <ProgressBar value={pct} thin tone={pct > 90 ? "warn" : "accent"} />
            </div>
            <p className="mt-2 text-[11px] text-mist-600">
              {usage ? `${fmtMinutes(usage.minutes_remaining)} processing left` : "Loading usage…"}
            </p>
          </div>
          <div className="flex items-center justify-between gap-2 rounded-xl px-2 py-1.5">
            <div className="min-w-0">
              <p className="truncate text-xs font-medium">{user.display_name || user.email}</p>
              <p className="truncate text-[11px] text-mist-600">{user.email}</p>
            </div>
            <LogoutButton />
          </div>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-white/[0.06] bg-ink-950/80 px-4 py-3 backdrop-blur-xl lg:px-10">
          <div className="flex items-center gap-3 lg:hidden">
            <Link href="/dashboard" className="text-sm font-semibold">Viral Clip</Link>
          </div>
          <div className="hidden items-center gap-2 lg:flex">
            <span className="chip">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              Processing engine online
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/projects/new" className="btn-primary !px-3 !py-2 text-[13px] lg:hidden">
              New
            </Link>
            <div className="hidden items-center gap-2 text-xs text-mist-500 sm:flex">
              <span className="tabular-nums">{usage?.clips ?? 0}</span> clips ·
              <span className="tabular-nums">{usage?.projects ?? 0}</span> projects
            </div>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1240px] px-4 py-6 lg:px-10 lg:py-9">{children}</main>
      </div>
    </div>
  );
}
