"use client";

import Link from "next/link";
import { ThemeToggle } from "@/features/toggle-theme";
import { Separator } from "@/shared/ui/separator";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4">
        <div className="flex items-center gap-4">
          <Link href="/" className="font-semibold tracking-tight">
            Calculadora de Renda Fixa
          </Link>
          <Separator orientation="vertical" className="h-6" />
          <nav className="flex items-center gap-3 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground">
              Simular
            </Link>
            <Link href="/comparar" className="hover:text-foreground">
              Comparar
            </Link>
          </nav>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
