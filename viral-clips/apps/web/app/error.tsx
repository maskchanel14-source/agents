"use client";

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="grid min-h-[60vh] place-items-center p-6">
      <div className="card max-w-md p-8 text-center">
        <p className="text-lg font-semibold">Something went wrong</p>
        <p className="mt-2 text-sm text-mist-500">{error.message}</p>
        <button onClick={reset} className="btn-primary mt-4">
          Try again
        </button>
      </div>
    </div>
  );
}
