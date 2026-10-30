"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LogoutButton() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  return (
    <button
      className="rounded-lg px-2 py-1.5 text-mist-600 transition hover:bg-white/[0.06] hover:text-rose-300"
      title="Sign out"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
        router.replace("/login");
        router.refresh();
      }}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M15 12H4m0 0l3-3m-3 3l3 3M14 4h5v16h-5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}
