import type { Metadata } from "next";
import "./globals.css";
import { Header, Footer } from "@/components/ui";
import { siteUrl } from "@/lib/site";


export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: { default: "Clarity Audit — Free Landing Page Clarity Score", template: "%s · Clarity Audit" },
  description: "Paste a public landing page URL and get a free, evidence-based clarity score in seconds: headline, CTA, proof, pricing, and form checks — with fixes. Built for coaches, course creators, and consultants.",
  keywords: ["free landing page score", "landing page audit", "website clarity audit", "landing page audit checklist", "conversion audit"],
  openGraph: { title: "Clarity Audit — Would a stranger understand your offer in 5 seconds?", description: "Free instant clarity score for your landing page. Evidence-based 100-point rubric, top issues, quick-win fix.", type: "website" },
  twitter: { card: "summary_large_image", title: "Clarity Audit — Free Landing Page Clarity Score", description: "Paste a URL. Get your clarity score, top 3 issues, and a quick-win fix. Free." },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <a href="#main" className="skip-link">Skip to content</a>
        <Header />
        <main id="main" className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
