import { requireUser, serverFetch } from "@/lib/api";
import type { Usage } from "@/lib/types";
import Shell from "@/components/Shell";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const user = await requireUser();
  const usage = await serverFetch<Usage>("/usage", { allow404: true });
  return (
    <Shell user={user} usage={usage}>
      {children}
    </Shell>
  );
}
