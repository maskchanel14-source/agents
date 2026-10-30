/**
 * Server-side API client.
 *
 * Server Components talk to FastAPI directly with the HttpOnly token forwarded
 * as a Bearer header. Browser code uses relative `/api/*` URLs, which Next
 * rewrites to the same backend (same-origin, cookie auth, no CORS).
 */
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const INTERNAL = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
export const COOKIE_NAME = "vc_token";

async function authHeaders(): Promise<Record<string, string>> {
  const store = await cookies();
  const token = store.get(COOKIE_NAME)?.value;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function serverFetch<T>(
  path: string,
  init: RequestInit & { allow404?: boolean } = {},
): Promise<T | null> {
  const { allow404, ...rest } = init;
  const res = await fetch(`${INTERNAL}/api${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(await authHeaders()),
      ...(rest.headers as Record<string, string> | undefined),
    },
    cache: "no-store",
  });
  if (res.status === 401) redirect("/login");
  if (res.status === 404 && allow404) return null;
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* keep statusText */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return null as T;
  return (await res.json()) as T;
}

export async function requireUser() {
  const user = await serverFetch<import("./types").User>("/auth/me", { allow404: true });
  if (!user) redirect("/login");
  return user;
}
