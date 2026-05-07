// shared/api/client.ts
// Cliente HTTP centralizado. Injeta automaticamente o token JWT
// em todas as requisições que precisam de autenticação.

import { getToken } from "@/shared/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function detailToMessage(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) =>
        typeof d === "object" && d && "msg" in d
          ? String((d as { msg: string }).msg)
          : String(d),
      )
      .join("; ");
  }
  if (detail && typeof detail === "object" && "message" in detail) {
    return String((detail as { message: string }).message);
  }
  return "Erro desconhecido";
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  // Lê o token JWT do localStorage (salvo no login/cadastro)
  const token = getToken();

  // Monta os headers: sempre JSON + token se disponível
  const authHeader: Record<string, string> = token
    ? { Authorization: `Bearer ${token}` }
    : {};

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeader,          // Injeta o Bearer token
      ...options?.headers,    // Permite sobrescrever se necessário
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, detailToMessage(body?.detail ?? body));
  }

  return res.json() as Promise<T>;
}