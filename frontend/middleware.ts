import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  console.log("MIDDLEWARE ATIVO:", req.nextUrl.pathname);

  const token = req.cookies.get("auth_token")?.value;

  const isProtectedRoute =
    req.nextUrl.pathname.startsWith("/simular") ||
    req.nextUrl.pathname.startsWith("/comparar");

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/simular/:path*", "/comparar/:path*", "/"],
};