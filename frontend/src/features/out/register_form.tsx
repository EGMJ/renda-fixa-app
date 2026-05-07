/**
 * features/out/register_form.tsx
 * Formulário de criação de conta.
 * Envia dados para o endpoint POST /api/v1/auth/register do backend,
 * recebe o token JWT e redireciona o usuário para a aplicação.
 */

"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { Loader2, UserPlus } from "lucide-react";
import { saveToken } from "@/shared/lib/auth";

/** URL base da API */
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function RegisterForm() {
  const [loading, setLoading] = React.useState(false);
  const router = useRouter();

  /**
   * Valida os campos e envia a requisição de cadastro.
   * Em caso de sucesso, o backend retorna um token JWT e o usuário
   * já fica logado (sem precisar passar pela tela de login).
   */
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const username = formData.get("username") as string;
    const email    = formData.get("email")    as string;
    const password = formData.get("password") as string;
    const confirm  = formData.get("confirm")  as string;

    // --- Validações no cliente (feedback imediato sem ir ao servidor) ---

    if (password !== confirm) {
      toast.error("As senhas não coincidem");
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      toast.error("A senha deve ter no mínimo 6 caracteres");
      setLoading(false);
      return;
    }

    if (!/\d/.test(password)) {
      toast.error("A senha deve conter pelo menos um número");
      setLoading(false);
      return;
    }

// Valida o formato do username antes de enviar ao servidor
if (!/^[a-zA-Z0-9_]+$/.test(username)) {
  toast.error("Nome de usuário inválido. Use apenas letras, números e _ (underscore)");
  setLoading(false);
  return;
}

if (username.length < 3) {
  toast.error("Nome de usuário deve ter no mínimo 3 caracteres");
  setLoading(false);
  return;
}

// Valida formato do e-mail antes de enviar ao servidor
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
  toast.error("E-mail inválido. Use o formato: nome@dominio.com");
  setLoading(false);
  return;
}

    try {
      // Envia dados como JSON para o endpoint de registro
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail ?? "Erro ao criar conta");
      }

      const data = await response.json();

      // Armazena o token (o usuário já está logado após cadastro)
      saveToken(data.access_token);

      toast.success("Conta criada com sucesso! Bem-vindo(a)!");

      // Redireciona para a página principal
      router.push("/");
      router.refresh(); // Força o middleware a reconhecer o novo cookie

    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Erro ao criar conta";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          {/* Ícone centralizado */}
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-primary/10 p-3">
              <UserPlus className="h-6 w-6 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl text-center">Criar conta</CardTitle>
          <CardDescription className="text-center">
            Preencha os dados abaixo para começar a usar a calculadora
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit} noValidate>
          <CardContent className="space-y-4">
            {/* Nome de usuário */}
            <div className="space-y-2">
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                name="username"
                placeholder="ex: joao_silva"
                autoComplete="username"
                minLength={3}
                maxLength={50}
                pattern="^[a-zA-Z0-9_]+$"
                title="Apenas letras, números e underscore (_)"
                required
              />
              <p className="text-xs text-muted-foreground">
                3–50 caracteres. Apenas letras, números e _ (underscore).
              </p>
            </div>

            {/* E-mail */}
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="seu@email.com"
                autoComplete="email"
                required
              />
            </div>

            {/* Senha */}
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="Mínimo 6 caracteres com 1 número"
                autoComplete="new-password"
                minLength={6}
                required
              />
            </div>

            {/* Confirmação de senha */}
            <div className="space-y-2">
              <Label htmlFor="confirm">Confirmar senha</Label>
              <Input
                id="confirm"
                name="confirm"
                type="password"
                placeholder="Repita a senha"
                autoComplete="new-password"
                required
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Criando conta..." : "Criar conta"}
            </Button>

            {/* Link para login */}
            <p className="text-sm text-muted-foreground text-center">
              Já tem uma conta?{" "}
              <Link
                href="/login"
                className="text-primary underline underline-offset-4 hover:text-primary/80"
              >
                Fazer login
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
