import { NextResponse, type NextRequest } from "next/server";
import { getDemoToken } from "@/lib/demo";

/**
 * Preview mode (DEMO_MODE=1).
 *
 * Browser requests to `/api/*` and `/media/*` are proxied to FastAPI by a
 * rewrite. Inside a cross-site preview frame the auth cookie is not sent, so in
 * demo mode we attach the shared demo token here instead. Page rendering is
 * handled separately by `getDemoToken()` in `lib/api.ts`.
 *
 * No redirects: a cookie the browser refuses to store would bounce forever.
 */
const COOKIE_NAME = "vc_token";

export async function middleware(request: NextRequest) {
  if (process.env.DEMO_MODE !== "1") return NextResponse.next();
  if (request.cookies.get(COOKIE_NAME)?.value) return NextResponse.next();

  const { pathname } = request.nextUrl;
  if (!pathname.startsWith("/api") && !pathname.startsWith("/media")) {
    return NextResponse.next();
  }

  const token = await getDemoToken();
  if (!token) return NextResponse.next();

  const headers = new Headers(request.headers);
  headers.set("authorization", `Bearer ${token}`);
  // Let the backend see the real client address rather than the Next process.
  if (!headers.get("x-forwarded-for")) headers.set("x-forwarded-for", "127.0.0.1");

  return NextResponse.next({ request: { headers } });
}

export const config = {
  matcher: ["/api/:path*", "/media/:path*"],
};
