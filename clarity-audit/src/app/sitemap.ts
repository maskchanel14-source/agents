import type { MetadataRoute } from "next";
import { RESOURCES, NICHES } from "@/lib/content";
import { siteUrl } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteUrl();
  const now = new Date("2026-10-18T00:00:00Z"); // fixed build date: bump on content releases
  const staticPaths: [string, number][] = [
    ["/", 1], ["/pricing", 0.9], ["/methodology", 0.8], ["/sample-report", 0.9], ["/resources", 0.8],
    ["/tools", 0.8], ["/tools/headline-checker", 0.7], ["/tools/cta-checker", 0.7],
    ["/challenge", 0.8], ["/widget", 0.6], ["/affiliates", 0.6], ["/data/coach-landing-pages-2026", 0.8],
    ["/privacy", 0.3], ["/terms", 0.3], ["/refund", 0.4], ["/support", 0.4],
  ];
  return [
    ...staticPaths.map(([path, priority]) => ({ url: `${base}${path}`, lastModified: now, priority })),
    ...RESOURCES.map((r) => ({ url: `${base}/resources/${r.slug}`, lastModified: now, priority: 0.75 })),
    ...NICHES.map((n) => ({ url: `${base}/niche/${n.slug}`, lastModified: now, priority: 0.8 })),
  ];
}
