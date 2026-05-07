/**
 * app/login/page.tsx
 * Página de login — rota pública /login.
 * Renderiza o formulário de autenticação.
 * O middleware (middleware.ts) redireciona para cá usuários
 * não autenticados que tentam acessar rotas protegidas.
 */

import { LoginForm } from "@/features/out/login_form";
import { Suspense } from "react";

export const metadata = {
  title: "Login | Calculadora de Renda Fixa",
  description: "Acesse sua conta para usar a calculadora de renda fixa",
};

export default function LoginPage() {
  return (
    <main>
      {/*
       * Suspense é necessário porque LoginForm usa useSearchParams(),
       * que pode causar erros de hidratação sem o boundary.
       */}
      <Suspense>
        <LoginForm />
      </Suspense>
    </main>
  );
}
