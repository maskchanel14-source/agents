import { describe, it, expect } from "vitest";
import { analyzePage } from "./scanner";
import { isPrivateIp, normalizeScanUrl } from "./fetchPage";

const GOOD = `<!doctype html><html><head><title>Launch Your Course in 6 Weeks — For Coaches</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A 6-week program helping coaches launch their first course."></head>
<body><h1>Launch your course in 6 weeks, without a team</h1>
<p>For coaches who want a clear outcome: get your first 20 students.</p>
<a href="/buy">Enroll now — $497</a>
<ul><li>6 live sessions</li><li>Templates</li><li>Community</li><li>Lifetime access</li><li>Weekly Q&A</li></ul>
<p>Testimonials: “I launched in 5 weeks” — Sarah, Business Coach. Rated 4.9 stars.</p>
<p>Price: $497. 14-day money-back guarantee. FAQ: frequently asked questions below.</p>
<form><input type="email" required><button>Get the free checklist</button></form>
<img src="/me.jpg" alt="Photo of Sarah, course creator">
<p>About: Hi, I'm Sarah. Contact: hello@example.com · Privacy · Refund policy</p>
<a href="/buy">Get started today</a></body></html>`;

const BAD = `<!doctype html><html><head><title>Welcome</title></head><body>
<p>Welcome to my website. I do coaching and stuff.</p><a href="#">Click here</a></body></html>`;

describe("analyzePage", () => {
  it("scores a strong page high and a weak page low", () => {
    const good = analyzePage({ url: "https://x.com", finalUrl: "https://x.com", html: GOOD, responseMs: 400, htmlBytes: 8000 });
    const bad = analyzePage({ url: "http://x.com", finalUrl: "http://x.com", html: BAD, responseMs: 400, htmlBytes: 800 });
    expect(good.score).toBeGreaterThanOrEqual(75);
    expect(bad.score).toBeLessThan(35);
    expect(good.score).toBeLessThanOrEqual(100);
    expect(bad.topIssues.length).toBeGreaterThan(0);
    expect(bad.quickWin).not.toBeNull();
  });
  it("weights sum to 100", () => {
    const r = analyzePage({ url: "https://x.com", finalUrl: "https://x.com", html: GOOD, responseMs: 1, htmlBytes: 1 });
    expect(r.checks.reduce((s, c) => s + c.maxPoints, 0)).toBe(100);
  });
});

describe("SSRF guards", () => {
  it("blocks private & metadata IPs", () => {
    for (const ip of ["127.0.0.1", "10.0.0.5", "172.16.0.1", "192.168.1.1", "169.254.169.254", "::1", "fe80::1", "fd00::1"]) {
      expect(isPrivateIp(ip), ip).toBe(true);
    }
    expect(isPrivateIp("93.184.216.34")).toBe(false);
    expect(isPrivateIp("8.8.8.8")).toBe(false);
  });
  it("rejects localhost, credentials, non-web schemes/ports", () => {
    expect(() => normalizeScanUrl("http://localhost:3000/x")).toThrow();
    expect(() => normalizeScanUrl("http://user:pass@example.com/")).toThrow();
    expect(() => normalizeScanUrl("ftp://example.com/")).toThrow();
    expect(() => normalizeScanUrl("http://example.com:22/")).toThrow();
    expect(() => normalizeScanUrl("http://192.168.0.1/admin")).toThrow();
    expect(normalizeScanUrl("example.com/page").toString()).toBe("https://example.com/page");
  });
});
