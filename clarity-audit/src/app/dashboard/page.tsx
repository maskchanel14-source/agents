import type { Metadata } from "next";
import DashboardClient from "@/components/DashboardClient";
import { Container, Eyebrow } from "@/components/ui";

export const metadata: Metadata = { title: "Operator Dashboard", robots: { index: false, follow: false } };

export default function Dashboard() {
  return (
    <Container className="py-14">
      <Eyebrow>Operator dashboard</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Growth war room, in numbers.</h1>
      <p className="mt-3 max-w-2xl text-[15px] leading-relaxed text-[color:var(--ink-2)]">Live in-memory metrics for this deployment (Supabase becomes the system of record at launch). North-star order: qualified visitors → scans → opt-ins → orders → payout. Orders/revenue activate when the human connects payments.</p>
      <DashboardClient />
    </Container>
  );
}
