/**
 * shared/lib/auth.ts
 * Utilitários de autenticação compartilhados entre componentes e middleware.
 * Centraliza toda a lógica de token para facilitar manutenção.
 */

/** Nome do cookie/localStorage onde o token JWT é armazenado */
export const AUTH_TOKEN_KEY = "auth_token";

/**
 * Armazena o token JWT em dois lugares:
 *   1. localStorage — leitura rápida nos componentes React
 *   2. Cookie        — leitura pelo middleware Next.js (server-side)
 *
 * O cookie é definido sem HttpOnly para permitir leitura pelo JS
 * do middleware (que roda no edge, não no browser).
 * Em produção, prefira cookies HttpOnly com um endpoint /api/set-cookie.
 */
export function saveToken(token: string): void {
  if (typeof window === "undefined") return;

  // Salva no localStorage para uso nos componentes
  localStorage.setItem(AUTH_TOKEN_KEY, token);

  // Salva como cookie para o middleware Next.js poder ler
  const maxAge = 60 * 60; // 1 hora em segundos (deve bater com o backend)
  document.cookie = `${AUTH_TOKEN_KEY}=${token}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

/**
 * Remove o token de ambos os armazenamentos (logout).
 */
export function removeToken(): void {
  if (typeof window === "undefined") return;

  localStorage.removeItem(AUTH_TOKEN_KEY);

  // Expira o cookie imediatamente definindo max-age=0
  document.cookie = `${AUTH_TOKEN_KEY}=; path=/; max-age=0; SameSite=Lax`;
}

/**
 * Lê o token do localStorage.
 * Retorna null se não estiver logado ou estiver em SSR.
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Verifica se o usuário está autenticado verificando a existência do token.
 * ATENÇÃO: não valida a assinatura do JWT — isso é responsabilidade do backend.
 */
export function isAuthenticated(): boolean {
  return Boolean(getToken());
}
