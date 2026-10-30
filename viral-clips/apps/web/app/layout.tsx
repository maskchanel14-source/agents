import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Viral Clip Generator — long videos to vertical shorts",
  description:
    "Paste a video, analyze the whole timeline, find the strongest moments, auto-caption them and export vertical clips for Shorts, TikTok and Reels.",
};

export const viewport: Viewport = {
  themeColor: "#07080C",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
