import { Container, Btn } from "@/components/ui";
export default function NotFound() {
  return (
    <Container className="py-24 text-center">
      <p className="font-mono text-sm uppercase tracking-[0.2em] text-[color:var(--ink-3)]">404</p>
      <h1 className="mx-auto mt-4 max-w-xl text-4xl font-extrabold tracking-tight">This page failed its own clarity test — it doesn't exist.</h1>
      <p className="mx-auto mt-4 max-w-lg text-[color:var(--ink-2)]">The scan you wanted may have expired from this session. Run a fresh one — it takes about 10 seconds.</p>
      <div className="mt-8 flex justify-center gap-3"><Btn href="/#scan" variant="accent">Scan a page free</Btn><Btn href="/" variant="ghost">Back home</Btn></div>
    </Container>
  );
}
