# Frontend — Calculadora de Renda Fixa

Aplicação Next.js (App Router) organizada em **Feature-Sliced Design**. A dependência flui: `app → views → widgets → features → entities → shared`.

> **Nota:** a camada FSD chamada “pages” no playbook está em `src/views/`, porque o Next.js reserva a pasta `src/pages/` para o roteador antigo (Pages Router).

## Scripts

```bash
npm run dev    # desenvolvimento
npm run build  # build de produção
npm run start  # servir build
```

## Variáveis de ambiente

Copie `.env.example` para `.env.local` e ajuste a URL da API:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Stack

Next.js 15+, TypeScript strict, Tailwind CSS v4, shadcn-style (Radix + CVA), Recharts, `react-hook-form` + Zod, `next-themes`, exportação PDF com `html2canvas` + `jsPDF`.

## Rotas

| Rota        | Descrição        |
| ----------- | ---------------- |
| `/`         | Simulação        |
| `/comparar` | Comparação 2–4 ativos |
