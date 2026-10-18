// SSRF-hardened page fetcher for the free scanner.
// Defenses: http(s) only, hostname allowlist shape, DNS resolution with
// private/loopback/link-local/metadata IP blocking, per-redirect re-validation,
// timeout, response-size cap, HTML-only. See reports/RISK_LOG.md for residual risk notes.
import { lookup } from "node:dns/promises";
import net from "node:net";

const MAX_BYTES = 1_500_000;
const TIMEOUT_MS = 10_000;
const MAX_REDIRECTS = 3;

export class ScanError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

function ipToInt(ip: string): number | null {
  const parts = ip.split(".");
  if (parts.length !== 4) return null;
  let n = 0;
  for (const p of parts) {
    const v = Number(p);
    if (!Number.isInteger(v) || v < 0 || v > 255) return null;
    n = n * 256 + v;
  }
  return n;
}

function inCidr(ipInt: number, base: string, bits: number): boolean {
  const b = ipToInt(base);
  if (b === null) return false;
  if (bits === 0) return true;
  const shift = 32 - bits;
  return ipInt >>> shift === b >>> shift;
}

export function isPrivateIp(ip: string): boolean {
  if (net.isIPv6(ip)) {
    const v = ip.toLowerCase();
    if (v === "::1" || v === "::") return true;
    if (v.startsWith("fe8") || v.startsWith("fe9") || v.startsWith("fea") || v.startsWith("feb")) return true; // link-local fe80::/10
    if (v.startsWith("fc") || v.startsWith("fd")) return true; // unique local fc00::/7
    if (v.startsWith("::ffff:")) {
      const mapped = v.replace("::ffff:", "");
      if (net.isIPv4(mapped)) return isPrivateIp(mapped);
    }
    return false;
  }
  const n = ipToInt(ip);
  if (n === null) return true; // unparseable → block
  return (
    inCidr(n, "10.0.0.0", 8) ||
    inCidr(n, "127.0.0.0", 8) ||
    inCidr(n, "172.16.0.0", 12) ||
    inCidr(n, "192.168.0.0", 16) ||
    inCidr(n, "169.254.0.0", 16) || // link-local incl. 169.254.169.254 cloud metadata
    inCidr(n, "0.0.0.0", 8) ||
    inCidr(n, "100.64.0.0", 10) || // CGNAT shared space
    inCidr(n, "192.0.0.0", 24) ||
    inCidr(n, "198.18.0.0", 15) ||
    inCidr(n, "240.0.0.0", 4)
  );
}

const BLOCKED_HOST_SUFFIXES = [".local", ".internal", ".intranet", ".home", ".corp", ".lan"];
const BLOCKED_HOSTS = new Set(["localhost", "metadata.google.internal", "metadata.google", "instance-data"]);

export function normalizeScanUrl(raw: string): URL {
  let s = (raw ?? "").trim();
  if (!s) throw new ScanError("empty_url", "Paste a public landing page URL to scan.");
  if (!/^https?:\/\//i.test(s)) s = "https://" + s;
  let u: URL;
  try {
    u = new URL(s);
  } catch {
    throw new ScanError("bad_url", "That does not look like a valid URL. Try something like https://yourpage.com");
  }
  if (u.protocol !== "http:" && u.protocol !== "https:") {
    throw new ScanError("bad_scheme", "Only http:// and https:// pages can be scanned.");
  }
  if (u.username || u.password) {
    throw new ScanError("credentials", "URLs with embedded credentials cannot be scanned. Paste a public page URL instead.");
  }
  const host = u.hostname.toLowerCase();
  if (!host.includes(".") && !net.isIP(host)) {
    throw new ScanError("bad_host", "Paste a full public domain, e.g. https://yourpage.com — bare words cannot be scanned.");
  }
  if (BLOCKED_HOSTS.has(host) || BLOCKED_HOST_SUFFIXES.some((suf) => host.endsWith(suf))) {
    throw new ScanError("blocked_host", "That looks like a private or internal address. The scanner only reads public pages.");
  }
  if (net.isIP(host) && isPrivateIp(host)) {
    throw new ScanError("private_ip", "That address is private/internal. The scanner only reads public pages.");
  }
  if (u.port && !["80", "443", "8080", "8443"].includes(u.port)) {
    throw new ScanError("bad_port", "Only standard web ports (80/443) can be scanned.");
  }
  return u;
}

async function assertPublicHost(u: URL): Promise<void> {
  const host = u.hostname;
  if (net.isIP(host)) {
    if (isPrivateIp(host)) throw new ScanError("private_ip", "That address is private/internal and cannot be scanned.");
    return;
  }
  let records: { address: string }[];
  try {
    records = await lookup(host, { all: true, verbatim: true });
  } catch {
    throw new ScanError("dns_fail", "That domain could not be resolved. Check the spelling — or the site may be down.");
  }
  if (!records.length) throw new ScanError("dns_fail", "That domain could not be resolved. Check the spelling.");
  for (const r of records) {
    if (isPrivateIp(r.address)) {
      throw new ScanError("private_ip", "That domain resolves to a private/internal address and cannot be scanned.");
    }
  }
}

export interface FetchedPage {
  html: string;
  finalUrl: string;
  responseMs: number;
  htmlBytes: number;
}

export async function fetchPublicPage(rawUrl: string): Promise<FetchedPage> {
  let current = normalizeScanUrl(rawUrl);
  const started = Date.now();

  for (let hop = 0; hop <= MAX_REDIRECTS; hop++) {
    await assertPublicHost(current);
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
    let res: Response;
    try {
      res = await fetch(current.toString(), {
        method: "GET",
        redirect: "manual",
        signal: ctrl.signal,
        headers: {
          "User-Agent": "ClarityAuditScanner/1.0 (+https://clarity-audit-five.vercel.app) user-requested public page check",
          Accept: "text/html,application/xhtml+xml",
        },
      });
    } catch (e) {
      clearTimeout(timer);
      // Server-side diagnostics only — users get the friendly message below.
      const cause = (e as { cause?: { code?: string; message?: string } })?.cause;
      console.error("[scanner] fetch failed for", current.hostname, cause?.code ?? (e as Error)?.message ?? "unknown");
      if ((e as Error)?.name === "AbortError") {
        throw new ScanError("timeout", "The page took longer than 10 seconds to respond. Try again, or check the URL.");
      }
      throw new ScanError("fetch_fail", "The page could not be fetched. It may block automated checks or be temporarily down.");
    }

    if ([301, 302, 303, 307, 308].includes(res.status)) {
      clearTimeout(timer);
      const loc = res.headers.get("location");
      if (!loc) throw new ScanError("bad_redirect", "The page redirected without a destination.");
      if (hop === MAX_REDIRECTS) throw new ScanError("too_many_redirects", "Too many redirects. Paste the final page URL directly.");
      current = normalizeScanUrl(new URL(loc, current).toString());
      continue;
    }

    const ct = res.headers.get("content-type") ?? "";
    if (!ct.includes("text/html") && !ct.includes("application/xhtml")) {
      clearTimeout(timer);
      throw new ScanError("not_html", "That URL did not return a web page (HTML). Paste a landing page URL.");
    }
    if (!res.ok) {
      clearTimeout(timer);
      throw new ScanError("http_error", `The page returned HTTP ${res.status}. Check the URL is public and live.`);
    }

    // Read with hard size cap.
    const reader = res.body?.getReader();
    if (!reader) {
      clearTimeout(timer);
      throw new ScanError("empty_body", "The page returned no content.");
    }
    const chunks: Uint8Array[] = [];
    let total = 0;
    try {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        if (value) {
          total += value.byteLength;
          if (total > MAX_BYTES) {
            await reader.cancel();
            break;
          }
          chunks.push(value);
        }
      }
    } finally {
      clearTimeout(timer);
    }
    const buf = Buffer.concat(chunks.map((c) => Buffer.from(c.buffer, c.byteOffset, c.byteLength)));
    return {
      html: buf.toString("utf8"),
      finalUrl: current.toString(),
      responseMs: Date.now() - started,
      htmlBytes: buf.byteLength,
    };
  }
  throw new ScanError("too_many_redirects", "Too many redirects. Paste the final page URL directly.");
}
