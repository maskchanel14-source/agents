import { NextResponse } from "next/server";

/**
 * One-click demo session (only active when DEMO_MODE=1).
 *
 * Signs the visitor into the shared demo account, sets the same HttpOnly cookie
 * the normal login form uses, and returns them to the page they asked for. No
 * credentials are ever typed or exposed to the browser.
 */
const INTERNAL = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";
const EMAIL = process.env.DEMO_EMAIL || "demo@viralclips.example";
const PASSWORD = process.env.DEMO_PASSWORD || "demo-password-123";
const COOKIE_NAME = "vc_token";

function safeNext(raw: string | null): string {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//")) return "/dashboard";
  return raw;
}

/**
 * The proxy in front of us (local dev, or the preview/ingress host) knows the
 * public origin; `request.url` only knows the address the server bound to, which
 * would send the browser to something like https://0.0.0.0:3000.
 */
function publicOrigin(request: Request): string {
  const host = request.headers.get("x-forwarded-host") ?? request.headers.get("host");
  const proto = request.headers.get("x-forwarded-proto") ?? "http";
  return host ? `${proto}://${host}` : new URL(request.url).origin;
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const origin = publicOrigin(request);
  const next = safeNext(url.searchParams.get("next"));

  if (process.env.DEMO_MODE !== "1") {
    return NextResponse.redirect(new URL("/login", origin));
  }

  let token: string | null = null;
  try {
    const res = await fetch(`${INTERNAL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
      cache: "no-store",
    });
    if (res.ok) {
      const data = (await res.json()) as { access_token?: string };
      token = data.access_token ?? null;
    }
  } catch {
    token = null;
  }

  if (!token) {
    // API down or demo account missing: fall back to the real login form.
    return NextResponse.redirect(new URL("/login?demo=unavailable", origin));
  }

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
