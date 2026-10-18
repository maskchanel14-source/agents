import { analyzePage, type ScanReport } from "./scanner";

// The sample report is a REAL scan of this illustrative example page,
// labeled clearly as a sample. No invented customer data.
export const SAMPLE_HTML = `<!doctype html><html><head>
<title>Mindset Coaching | Transform Your Life</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body>
<h1>Transform Your Life Today!!!</h1>
<p>Welcome to my coaching practice. I offer many services for people who want change.</p>
<p>I have been a coach for many years and I love helping people.</p>
<a href="/more">Learn more</a>
<p>Services include 1:1 coaching, group coaching, workshops and speaking.</p>
<p>Contact me for pricing and availability.</p>
<form><input type="text" required><input type="text" required><input type="email" required>
<input type="tel" required><textarea required></textarea><input type="text" required>
<button>Submit</button></form>
<img src="/banner.jpg">
</body></html>`;

export function demoReport(): ScanReport {
  return analyzePage({
    url: "https://example-coach-page.sample",
    finalUrl: "https://example-coach-page.sample",
    html: SAMPLE_HTML,
    responseMs: 612,
    htmlBytes: SAMPLE_HTML.length,
    fetchedAt: "2026-10-18T00:00:00.000Z",
  });
}
