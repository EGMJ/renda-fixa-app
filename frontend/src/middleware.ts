/**
 * middleware.ts (Next.js Middleware)
 * Executado no Edge Runtime ANTES de cada requisição às rotas configuradas.
 * Responsável por proteger rotas autenticadas: se o cookie de token não
 * estiver presente, redireciona o usuário para /login.
 *
 * Fluxo:
 *   1. Usuário acessa "/" ou "/comparar"
 *   2. Middleware verifica cookie "auth_token"
 *   3. Sem cookie → redireciona para /login?from=<rota>
 *   4. Com cookie → deixa a requisição prosseguir normalmente
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { AUTH_TOKEN_KEY } from "@/shared/lib/auth";

/**
 * Rotas públicas que NÃO exigem autenticação.
 * Todas as outras rotas são protegidas por padrão.
 */
const PUBLIC_ROUTES = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Verifica se a rota é pública — se for, deixa passar sem checagem
  const isPublicRoute = PUBLIC_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );
  if (isPublicRoute) return NextResponse.next();

  // Lê o token do cookie (definido pelo saveToken() no login/register)
  const token = request.cookies.get(AUTH_TOKEN_KEY)?.value;

  if (!token) {
    // Sem token: redireciona para /login preservando a rota de destino
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname); // Para redirecionar de volta após login
    return NextResponse.redirect(loginUrl);
  }

  // Token presente: deixa a requisição prosseguir
  return NextResponse.next();
}

/**
 * Configuração do matcher: define QUAIS rotas passam pelo middleware.
 * Exclui automaticamente _next/static, _next/image e favicon.ico
 * para não interferir com assets estáticos do Next.js.
 */
export const config = {
  matcher: [
    /*
     * Aplica o middleware a todas as rotas EXCETO:
     * - _next/static  (arquivos estáticos)
     * - _next/image   (otimização de imagens)
     * - favicon.ico
     * - Arquivos com extensão (ex: .png, .svg, .css)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|css|js)$).*)",
  ],
};
