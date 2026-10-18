#!/usr/bin/env node
/**
 * Batch data-study runner (human-operated, post-deploy).
 *
 * Usage:
 *   SITE=https://your-deployed-site.example node scripts/study-runner.mjs urls.txt
 *
 * urls.txt: one PUBLIC landing-page URL per line (you curate the sample frame
 * from public directories/search results — never login-walled/paywalled pages).
 * The runner calls the deployed /api/scan politely (1 req / 6s per rate limits),
 * then writes study-results.json + a summary of failure frequencies.
 * Publish aggregates only; never name-and-shame individual pages.
 */
import { readFileSync, writeFileSync } from "node:fs";

const SITE = (process.env.SITE || "http://localhost:3000").replace(/\/$/, "");
const file = process.argv[2] || "urls.txt";
const urls = readFileSync(file, "utf8").split("\n").map((s) => s.trim()).filter((s) => s && !s.startsWith("#"));
console.log(`Study runner: ${urls.length} URLs via ${SITE}`);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const results = [];
for (const url of urls) {
  process.stdout.write(`→ ${url} … `);
  try {
    const res = await fetch(`${SITE}/api/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, ref: "data-study" }),
    });
    const data = await res.json();
    if (!res.ok) { console.log(`SKIP (${data.error})`); results.push({ url, skipped: data.error }); }
    else {
      console.log(`${data.report.score}/100`);
      results.push({ url, id: data.id, score: data.report.score, grade: data.report.grade,
        failed: data.report.checks.filter((c) => c.status !== "pass").map((c) => c.id) });
    }
  } catch (e) { console.log(`ERROR ${e.message}`); results.push({ url, skipped: "fetch-error" }); }
  await sleep(6500); // stay well under the 10/hour/IP scanner limit per batch; run across sessions for 50+
}
writeFileSync("study-results.json", JSON.stringify(results, null, 2));

const ok = results.filter((r) => typeof r.score === "number");
if (ok.length) {
  const freq = {};
  for (const r of ok) for (const id of r.failed) freq[id] = (freq[id] || 0) + 1;
  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
  const avg = Math.round(ok.reduce((s, r) => s + r.score, 0) / ok.length);
  console.log(`\n=== SUMMARY (n=${ok.length}, avg score ${avg}/100) ===`);
  for (const [id, n] of sorted) console.log(`${Math.round((n / ok.length) * 100)}%  ${id}`);
  console.log("\nWrote study-results.json — update /data/coach-landing-pages-2026 with aggregates + sample frame + date.");
}
