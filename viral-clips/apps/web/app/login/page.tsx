import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { COOKIE_NAME } from "@/lib/api";
import { demoMode } from "@/lib/demo";
import LoginForm from "./LoginForm";

export default async function LoginPage() {
  const store = await cookies();
  if (store.get(COOKIE_NAME)?.value || demoMode()) redirect("/dashboard");

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-12">
      <div className="pointer-events-none absolute inset-0 grid-lines opacity-[0.55]" />
      <div className="pointer-events-none absolute -left-40 top-1/3 h-[420px] w-[420px] rounded-full bg-accent/20 blur-[120px]" />
      <div className="pointer-events-none absolute -right-32 top-10 h-[360px] w-[360px] rounded-full bg-accent-cyan/10 blur-[120px]" />

      <div className="relative grid w-full max-w-5xl items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="animate-fade-up">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-mist-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Full-timeline analysis · 1080×1920 exports
          </div>
          <h1 className="text-4xl font-semibold leading-[1.08] tracking-tight sm:text-5xl">
            Long video in.
            <br />
            <span className="bg-gradient-to-r from-accent-soft via-accent-cyan to-emerald-300 bg-clip-text text-transparent">
              Short clips that hold attention.
            </span>
          </h1>
          <p className="mt-5 max-w-lg text-[15px] leading-relaxed text-mist-500">
            Upload a podcast, interview or webinar. We transcribe the whole file, track who is
            speaking, score every candidate moment on nine signals and cut captioned vertical clips
            for Shorts, TikTok and Reels.
          </p>
          <ul className="mt-7 grid max-w-lg gap-2.5 text-sm text-mist-300 sm:grid-cols-2">
            {[
              "Word-level captions",
              "Speaker-aware 9:16 crop",
              "Six caption presets",
              "Transparent score breakdown",
            ].map((item) => (
              <li key={item} className="flex items-center gap-2">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" className="text-accent-soft">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {item}
              </li>
            ))}
          </ul>
        </section>

        <LoginForm />
      </div>
    </div>
  );
}
