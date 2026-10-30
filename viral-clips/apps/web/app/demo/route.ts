import { NextResponse } from "next/server";
import { getDemoToken } from "@/lib/demo";

/**
 * Optional entry point that also stores the token as a cookie, for browsers
 * where cookies work. Rendering never depends on it: `lib/api.ts` and
 * `middleware.ts` fall back to the shared demo token when the cookie is absent
 * (preview frames block third-party cookies).
 */
const COOKIE_NAME = "vc_token";

function safeNext(raw: string | null): string {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//")) return "/dashboard";
  return raw;
}

function publicOrigin(request: Request): string {
  const host = request.headers.get("x-forwarded-host") ?? request.headers.get("host");
  const proto = request.headers.get("x-forwarded-proto") ?? "http";
  return host ? `${proto}://${host}` : new URL(request.url).origin;
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const origin = publicOrigin(request);
  const next = safeNext(url.searchParams.get("next"));
  const token = await getDemoToken();

  if (!token) return NextResponse.redirect(new URL("/login", origin));

  const response = NextResponse.redirect(new URL(next, origin));
  response.cookies.set(COOKIE_NAME, token, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.COOKIE_SECURE === "true",
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}
