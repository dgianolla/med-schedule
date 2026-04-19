import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function isTokenExpired(token: string) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1] || ""));
    const exp = typeof payload.exp === "number" ? payload.exp : null;

    if (!exp) {
      return true;
    }

    return exp <= Math.floor(Date.now() / 1000);
  } catch {
    return true;
  }
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("med_auth_token")?.value;
  const isLoginRoute = pathname.startsWith("/login");
  const isAuthenticated = token ? !isTokenExpired(token) : false;

  if (!isAuthenticated && !isLoginRoute) {
    const response = NextResponse.redirect(new URL("/login", request.url));
    response.cookies.delete("med_auth_token");
    return response;
  }

  if (isAuthenticated && isLoginRoute) {
    return NextResponse.redirect(new URL("/agenda", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
