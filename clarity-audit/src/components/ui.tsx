import Link from "next/link";
import type { ReactNode } from "react";

export function Container({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`mx-auto w-full max-w-6xl px-5 sm:px-8 ${className}`}>{children}</div>;
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent)]">{children}</p>;
}

export function Btn({ href, children, variant = "primary", className = "" }: { href: string; children: ReactNode; variant?: "primary" | "ghost" | "accent"; className?: string }) {
  const styles =
    variant === "primary"
      ? "bg-[color:var(--ink)] text-white hover:bg-[#232b3a]"
      : variant === "accent"
        ? "bg-[color:var(--accent)] text-white hover:bg-[#1e40af]"
        : "bg-white text-[color:var(--ink)] border border-[color:var(--line)] hover:border-[color:var(--ink-3)]";
  return <Link href={href} className={`inline-flex min-h-[48px] items-center justify-center rounded-xl px-6 py-3 text-[15px] font-semibold transition-colors ${styles} ${className}`}>{children}</Link>;
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-2xl border border-[color:var(--line)] bg-white p-6 shadow-[0_1px_2px_rgba(11,15,23,0.04)] ${className}`}>{children}</div>;
}

export function FaqList({ faqs }: { faqs: { q: string; a: string }[] }) {
  return (
    <div className="divide-y divide-[color:var(--line)] rounded-2xl border border-[color:var(--line)] bg-white">
      {faqs.map((f) => (
        <details key={f.q} className="faq px-6 py-4">
          <summary className="flex items-center justify-between gap-4 font-semibold text-[color:var(--ink)]">
            <span>{f.q}</span>
            <span className="chev text-[color:var(--ink-3)] transition-transform" aria-hidden>▾</span>
          </summary>
          <p className="pt-3 leading-relaxed text-[color:var(--ink-2)]">{f.a}</p>
        </details>
      ))}
    </div>
  );
}

export function Header() {
  const links: [string, string][] = [["Methodology", "/methodology"], ["Sample report", "/sample-report"], ["Pricing", "/pricing"], ["Resources", "/resources"], ["Tools", "/tools"], ["Affiliates", "/affiliates"]];
  return (
    <header className="sticky top-0 z-40 border-b border-[color:var(--line)] bg-[rgba(251,251,250,0.9)] backdrop-blur">
      <Container className="flex h-16 items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-2.5 font-bold tracking-tight text-[color:var(--ink)]" aria-label="Clarity Audit home">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-[color:var(--ink)] font-mono text-sm text-white">◉</span>
          Clarity&nbsp;Audit
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium text-[color:var(--ink-2)] lg:flex" aria-label="Main">
          {links.map(([label, href]) => <Link key={href} href={href} className="hover:text-[color:var(--ink)]">{label}</Link>)}
        </nav>
        <Link href="/#scan" className="inline-flex min-h-[44px] items-center rounded-lg bg-[color:var(--accent)] px-4 py-2 text-sm font-semibold text-white hover:bg-[#1e40af]">Free score →</Link>
      </Container>
    </header>
  );
}

export function Footer() {
  const cols: { h: string; links: [string, string][] }[] = [
    { h: "Product", links: [["Free scanner", "/#scan"], ["Pricing", "/pricing"], ["Sample report", "/sample-report"], ["Methodology", "/methodology"], ["Widget & badge", "/widget"], ["5-Day Challenge", "/challenge"]] },
    { h: "Free tools", links: [["Headline Checker", "/tools/headline-checker"], ["CTA Checker", "/tools/cta-checker"], ["All tools", "/tools"], ["Data study", "/data/coach-landing-pages-2026"]] },
    { h: "For", links: [["Coaches", "/niche/coaches"], ["Course creators", "/niche/course-creators"], ["Consultants", "/niche/consultants"], ["Affiliates & ambassadors", "/affiliates"]] },
    { h: "Trust", links: [["Privacy", "/privacy"], ["Terms", "/terms"], ["Refund policy", "/refund"], ["Support", "/support"], ["Operator dashboard", "/dashboard"]] },
  ];
  return (
    <footer className="mt-24 border-t border-[color:var(--line)] bg-white">
      <Container className="grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-5">
        <div>
          <p className="font-bold tracking-tight">Clarity Audit</p>
          <p className="mt-3 text-sm leading-relaxed text-[color:var(--ink-3)]">Instant Website Clarity Audit. Paste a public URL, get an evidence-based clarity score, fix what matters.</p>
          <p className="mt-4 text-xs text-[color:var(--ink-3)]">No fake proof. No dark patterns. Ever.</p>
        </div>
        {cols.map((c) => (
          <nav key={c.h} aria-label={c.h}>
            <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--ink-3)]">{c.h}</p>
            <ul className="mt-4 space-y-2.5 text-sm">
              {c.links.map(([label, href]) => <li key={href}><Link href={href} className="text-[color:var(--ink-2)] hover:text-[color:var(--ink)]">{label}</Link></li>)}
            </ul>
          </nav>
        ))}
      </Container>
      <Container className="flex flex-wrap items-center justify-between gap-3 border-t border-[color:var(--line)] py-5 text-xs text-[color:var(--ink-3)]">
        <p>© 2026 Clarity Audit. Automated clarity checks — not a guarantee of business results.</p>
        <p>Scanner reads only public pages, on request. <Link href="/privacy" className="underline">Privacy</Link></p>
      </Container>
    </footer>
  );
}

export function ScoreRing({ score, size = 168 }: { score: number; size?: number }) {
  const r = 76, c = 2 * Math.PI * r;
  const color = score >= 80 ? "var(--good)" : score >= 60 ? "var(--warn)" : score >= 40 ? "#c2410c" : "var(--bad)";
  return (
    <div className="relative inline-grid place-items-center" style={{ width: size, height: size }} role="img" aria-label={`Clarity score ${score} out of 100`}>
      <svg width={size} height={size} viewBox="0 0 180 180" className="-rotate-90">
        <circle cx="90" cy="90" r={r} fill="none" stroke="var(--ring-track)" strokeWidth="12" />
        <circle cx="90" cy="90" r={r} fill="none" stroke={color} strokeWidth="12" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c - (c * score) / 100} />
      </svg>
      <div className="absolute text-center">
        <p className="text-5xl font-extrabold tracking-tight">{score}</p>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[color:var(--ink-3)]">/ 100 clarity</p>
      </div>
    </div>
  );
}

export function StatusPill({ status }: { status: "pass" | "warn" | "fail" }) {
  const map = { pass: ["Pass", "var(--good)"], warn: ["Improve", "var(--warn)"], fail: ["Missing", "var(--bad)"] } as const;
  const [label, color] = map[status];
  return <span className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold" style={{ color, borderColor: color }}><span aria-hidden>{status === "pass" ? "●" : status === "warn" ? "◐" : "○"}</span>{label}</span>;
}

export function jsonLdScript(data: object) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
