import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const protectedPaths = ["/dashboard", "/practice", "/quiz", "/leaderboard", "/profile"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = protectedPaths.some((path) => pathname === path || pathname.startsWith(`${path}/`));

  if (!isProtected) {
    return NextResponse.next();
  }

  const token = request.cookies.get("bitjudge_token")?.value;
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/practice/:path*", "/quiz/:path*", "/leaderboard/:path*", "/profile/:path*"],
};
