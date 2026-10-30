import { requireUser, serverFetch } from "@/lib/api";
import type { ProviderStatus, Usage } from "@/lib/types";
import UploadForm from "@/components/UploadForm";
import { Alert } from "@/components/ui";

export const dynamic = "force-dynamic";

export default async function NewProjectPage() {
  await requireUser();
  const [usage, providers] = await Promise.all([
    serverFetch<Usage>("/usage", { allow404: true }),
    serverFetch<ProviderStatus>("/providers", { allow404: true }),
  ]);

  return (
    <div className="space-y-6">
      <header>
        <p className="label">New project</p>
        <h1 className="mt-1.5 text-2xl font-semibold tracking-tight sm:text-3xl">Analyze a video</h1>
        <p className="mt-1.5 max-w-2xl text-sm text-mist-500">
          The engine reads the entire file — audio, transcript, scene changes and speaker position —
          then proposes clips with a transparent score. Nothing is cut until you render.
        </p>
      </header>

      {!providers?.asr_configured || !providers?.llm_configured ? (
        <Alert tone="info" title="Local analysis mode">
          {providers?.asr_configured
            ? "No LLM key configured: scoring uses the deterministic local heuristic model."
            : "No transcription provider configured: clips are found from acoustic and visual signals, without captions."}{" "}
          Add keys in <code className="rounded bg-white/10 px-1">.env</code> to enable the full AI
          pipeline.
        </Alert>
      ) : null}

      <UploadForm
        maxUploadMb={usage?.plan.max_upload_mb ?? 256}
        maxClips={usage?.plan.max_clips_per_video ?? 3}
      />
    </div>
  );
}
