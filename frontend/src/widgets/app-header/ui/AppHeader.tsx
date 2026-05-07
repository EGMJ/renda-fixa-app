/**
 * widgets/app-header/ui/AppHeader.tsx
 * Cabeçalho fixo da aplicação com:
 *   - Nome/logo da aplicação (link para home)
 *   - Links de navegação (Simular, Comparar)
 *   - Alternador de tema claro/escuro
 *   - Botão de logout (remove o token e redireciona para /login)
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { ThemeToggle } from "@/features/toggle-theme";
import { Separator } from "@/shared/ui/separator";
import { Button } from "@/shared/ui/button";
import { removeToken } from "@/shared/lib/auth";
import { toast } from "sonner";

export function AppHeader() {
  const router = useRouter();

  /**
   * Realiza o logout do usuário:
   *   1. Remove o token do localStorage e do cookie
   *   2. Exibe toast de confirmação
   *   3. Redireciona para /login
   */
  function handleLogout() {
    removeToken();
    toast.success("Você saiu da conta");
    router.push("/login");
    router.refresh(); // Faz o middleware reavaliarem o cookie ausente
  }

  return (
    <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4">
        {/* --- Lado esquerdo: logo + navegação --- */}
        <div className="flex items-center gap-4">
          {/* Nome da aplicação com link para a home */}
          <Link href="/" className="font-semibold tracking-tight">
            Calculadora de Renda Fixa
          </Link>

          <Separator orientation="vertical" className="h-6" />

          {/* Links de navegação principal */}
          <nav className="flex items-center gap-3 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground transition-colors">
              Simular
            </Link>
            <Link href="/comparar" className="hover:text-foreground transition-colors">
              Comparar
            </Link>
          </nav>
        </div>

        {/* --- Lado direito: tema + logout --- */}
        <div className="flex items-center gap-2">
          {/* Alternador de tema claro/escuro */}
          <ThemeToggle />

          {/* Botão de logout */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="gap-1.5 text-muted-foreground hover:text-foreground"
            title="Sair da conta"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Sair</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
