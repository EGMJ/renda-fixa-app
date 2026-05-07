/**
 * app/page.tsx
 * Página principal da aplicação — rota "/" (raiz).
 * Renderiza a tela de simulação de investimentos.
 *
 * Esta rota é PROTEGIDA pelo middleware (middleware.ts):
 * usuários não autenticados são redirecionados para /login.
 */

export { SimulationPage as default } from "@/views/simulation";
