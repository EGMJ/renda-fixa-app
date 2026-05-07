/**
 * features/out/login_form.tsx
 * Formulário de login da aplicação.
 * Envia credenciais para o backend FastAPI no formato OAuth2 (form-urlencoded),
 * armazena o token recebido e redireciona o usuário.
 */

"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Loader2, Lock } from "lucide-react";
import { saveToken } from "@/shared/lib/auth";

/** URL base da API — usa variável de ambiente se disponível */
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function LoginForm() {
  // Estado de carregamento para o botão (evita duplo envio)
  const [loading, setLoading] = React.useState(false);

  const router = useRouter();
  const searchParams = useSearchParams();

  /**
   * Lida com o envio do formulário de login.
   * O FastAPI espera os dados em formato x-www-form-urlencoded
   * para o endpoint OAuth2PasswordRequestForm.
   */
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); // Previne reload da página
    setLoading(true);

    // Extrai os campos do formulário HTML
    const formData = new FormData(event.currentTarget);
    const username = formData.get("username") as string;
    const password = formData.get("password") as string;

    // Validação básica no cliente (antes de ir ao servidor)
    if (!username.trim() || !password.trim()) {
      toast.error("Preencha todos os campos");
      setLoading(false);
      return;
    }

    try {
      // Monta o body no formato application/x-www-form-urlencoded
      // exigido pelo OAuth2PasswordRequestForm do FastAPI
      const body = new URLSearchParams({
        username,
        password,
        grant_type: "password",
      }).toString();

      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      // Trata erros HTTP (401, 403, etc.)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail ?? "Usuário ou senha inválidos");
      }

      // Extrai o token da resposta
      const data = await response.json();

      // Salva o token no localStorage E no cookie (para o middleware)
      saveToken(data.access_token);

      toast.success("Login realizado com sucesso!");

      // Redireciona para a página original solicitada (ou para "/" por padrão)
      const from = searchParams.get("from") ?? "/";
      router.push(from);
      router.refresh(); // Força re-render para o middleware reconhecer o cookie

    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Erro ao fazer login";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          {/* Ícone de cadeado centralizado */}
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-primary/10 p-3">
              <Lock className="h-6 w-6 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl text-center">Entrar</CardTitle>
          <CardDescription className="text-center">
            Entre com suas credenciais para acessar a calculadora
          </CardDescription>
        </CardHeader>

        {/* Formulário HTML — onSubmit chama handleSubmit */}
        <form onSubmit={handleSubmit} noValidate>
          <CardContent className="space-y-4">
            {/* Campo de usuário */}
            <div className="space-y-2">
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                name="username"
                placeholder="Seu nome de usuário"
                autoComplete="username"
                required
              />
            </div>

            {/* Campo de senha */}
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            {/* Botão de submit — desabilitado durante carregamento */}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Entrando..." : "Entrar"}
            </Button>

            {/* Link para a tela de cadastro */}
            <p className="text-sm text-muted-foreground text-center">
              Não tem uma conta?{" "}
              <Link
                href="/register"
                className="text-primary underline underline-offset-4 hover:text-primary/80"
              >
                Criar conta
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
