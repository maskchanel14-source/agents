import type { Metadata } from "next";
import { Container, Eyebrow, Card } from "@/components/ui";
import ScanForm from "@/components/ScanForm";

export const metadata: Metadata = {
  title: "Clarity Score Widget & Badge — Embed Docs",
  description: "Embed the free Landing Page Clarity Score checker or your score badge on your site. Copy-paste HTML/Markdown, no forced links, no tracking pixels.",
};

const pre = "mt-3 overflow-x-auto whitespace-pre rounded-xl bg-[#0b0f17] p-4 font-mono text-[12.5px] leading-relaxed text-[#e5e7eb]";

export default function WidgetPage() {
  return (
    <Container className="max-w-4xl py-14">
      <Eyebrow>Widget & badge</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Put the free checker where your audience already is.</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Coaches' communities, template galleries, course platforms, agency resource pages: give your visitors a genuinely useful free tool. No forced backlink, no hidden tracking — embeds are plain links/iframes you control.</p>

      <div className="mt-9 space-y-6">
        <Card>
          <h2 className="font-bold">1 · Score badge (show off your improvement)</h2>
          <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">After scanning, your result page gives you a badge snippet. Markdown (GitHub, Notion, blogs):</p>
          <pre className={pre}>{`[![Clarity Score 78/100](YOUR_SITE/api/badge/YOUR_SCAN_ID.svg)](YOUR_SITE/scan/YOUR_SCAN_ID)`}</pre>
          <p className="mt-3 text-[15px] text-[color:var(--ink-2)]">HTML:</p>
          <pre className={pre}>{`<a href="YOUR_SITE/scan/YOUR_SCAN_ID">\n  <img src="YOUR_SITE/api/badge/YOUR_SCAN_ID.svg" alt="My landing page clarity score" width="280" height="64">\n</a>`}</pre>
          <div className="mt-4"><img src="/api/badge/demo.svg" alt="Example clarity score badge" width={280} height={64} /><p className="mt-1.5 text-xs text-[color:var(--ink-3)]">Live preview (sample scan).</p></div>
        </Card>

        <Card>
          <h2 className="font-bold">2 · “Check your page free” text link</h2>
          <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">The simplest embed. Add <code className="rounded bg-[color:var(--line)] px-1.5 py-0.5 font-mono text-[13px]">?ref=yourname</code> and scans from your link are attributed to you (ambassadors: this is your referral link).</p>
          <pre className={pre}>{`<a href="YOUR_SITE/?ref=yourname#scan">Check your landing page clarity — free</a>`}</pre>
        </Card>

        <Card>
          <h2 className="font-bold">3 · Rules (short, because they're simple)</h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-[15px] leading-relaxed text-[color:var(--ink-2)]">
            <li>Don't alter badge scores or imply endorsement you don't have.</li>
            <li>No embedding on deceptive pages; we may disable abusive badge IDs.</li>
            <li>Badges reflect the scan at that moment — rescan after fixes to update.</li>
            <li>We count aggregate embed views for our own metrics; we set no third-party cookies via embeds.</li>
          </ul>
        </Card>
      </div>

      <div className="mt-10 max-w-2xl">
        <h2 className="text-xl font-bold">Get your badge: run a scan</h2>
        <div className="mt-4"><ScanForm compact /></div>
      </div>
    </Container>
  );
}
