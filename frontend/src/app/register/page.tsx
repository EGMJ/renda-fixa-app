/**
 * app/register/page.tsx
 * Página de cadastro — rota pública /register.
 * Permite que novos usuários criem uma conta.
 */

import { RegisterForm } from "@/features/out/register_form";

export const metadata = {
  title: "Criar conta | Calculadora de Renda Fixa",
  description: "Crie sua conta para acessar a calculadora de renda fixa",
};

export default function RegisterPage() {
  return (
    <main>
      <RegisterForm />
    </main>
  );
}
