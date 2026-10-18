import type { Metadata } from "next";
import ExtraChecker from "@/components/ExtraCheckers";
import { Container, Eyebrow } from "@/components/ui";

export const metadata: Metadata = { title: "Form Friction Checker (Free)", description: "Free form friction checker: how many fields stand between interest and action on your landing page? Instant first-step audit." };

export default function FormChecker() {
  return (
    <Container className="max-w-3xl py-14">
      <Eyebrow>Free tool</Eyebrow>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Form Friction Checker</h1>
      <p className="mt-4 text-lg leading-relaxed text-[color:var(--ink-2)]">Every field is a toll booth. List your first-step fields and see what to cut, move, or reorder.</p>
      <div className="mt-8"><ExtraChecker kind="form" /></div>
    </Container>
  );
}
