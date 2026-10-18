import type { Metadata } from "next";
import EmailCapture from "@/components/EmailCapture";
import { Container, Eyebrow, Card } from "@/components/ui";
import ScanForm from "@/components/ScanForm";

export const metadata: Metadata = {
  title: "The 5-Day Clarity Challenge (Free)",
  description: "Five days, one fix a day: scan, headline, CTA, FAQ, rescan. Free email challenge for coaches, course creators, and consultants.",
};

const DAYS = [
  ["Day 1 — See your page like a stranger", "Run the free scan. Write down your score and your one-sentence reaction. That discomfort is data.", "🎯 Badge: First Scan"],
  ["Day 2 — Fix the headline", "Rewrite your H1 with the formula: audience + outcome + without-the-pain. Use the Headline Checker until it passes.", "🏅 Badge: Headline Fixed"],
  ["Day 3 — Fix the button", "One primary CTA, above the fold, verb + object + outcome. Kill every “Submit” and orphan “Learn more”.", "🏅 Badge: CTA Fixed"],
  ["Day 4 — Answer the silent objections", "Add the 5-question FAQ: fit, time, delivery, after-I-pay, refund. Honest answers, plain words.", "🏅 Badge: Objections Answered"],
  ["Day 5 — Rescan & share", "Run the scan again. Compare. Share your before/after (only if you want to — your result page is yours).", "🏆 Badge: Clarity Improved"],
] as const;

export default function Challenge() {
  return (
    <Container className="py-14">
      <div className="max-w-3xl">
        <Eyebrow>Free 5-Day Clarity Challenge</Eyebrow>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Can your page score above 70 by Friday?</h1>
        <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">One focused fix per day, about 45 minutes each. No leaderboard, no public shaming — just your own before/after, verified by re-scanning. Join free; the emails include the templates.</p>
      </div>
      <div className="mt-9 max-w-2xl"><ScanForm /></div>
      <ol className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {DAYS.map(([t, d, b]) => (
          <Card key={t}><h2 className="font-bold">{t}</h2><p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ink-2)]">{d}</p><p className="mt-3 inline-block rounded-full bg-[#eff6ff] px-3 py-1 text-xs font-semibold text-[color:var(--accent)]">{b}</p></Card>
        ))}
        <EmailCapture source="challenge-page" title="Get the 5 daily emails + templates"
          blurb="Day-by-day guidance, the headline formulas, and the FAQ template. Free. Unsubscribe anytime; the challenge works even if you only use the scanner." cta="Join the free challenge" />
      </ol>
    </Container>
  );
}
