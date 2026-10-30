import { NextResponse, type NextRequest } from "next/server";

/**
 * Preview mode (DEMO_MODE=1).
 *
 * A shared hosting preview has no way to know who is watching, so instead of a
 * login wall the middleware sends visitors through `/demo`, which signs them
 * into the seeded demo account and comes straight back. Production deployments
 * leave DEMO_MODE unset, so this file is inert there and the normal cookie
 * guard in `requireUser()` applies.
 */
const COOKIE_NAME = "vc_token";

export function middleware(request: NextRequest) {
  if (process.env.DEMO_MODE !== "1") return NextResponse.next();

  const { pathname } = request.nextUrl;
  if (pathname === "/demo" || pathname.startsWith("/api") || pathname.startsWith("/media")) {
    return NextResponse.next();
  }
  if (request.cookies.get(COOKIE_NAME)?.value) return NextResponse.next();

  const url = request.nextUrl.clone();
  url.pathname = "/demo";
  url.search = "";
  url.searchParams.set("next", `${pathname}${request.nextUrl.search}`);
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
