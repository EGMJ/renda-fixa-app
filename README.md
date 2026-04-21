# renda-fixa-app

Aplicação para simular rentabilidade de renda fixa (IR regressivo, PEPS, taxas de mercado).

## Estrutura

- **`backend/`** — API FastAPI (`/api/v1/simulate`, `/api/v1/market-rates`, etc.).
- **`frontend/`** — Next.js 15, FSD em `src/` (camada de telas em `src/views/` para não conflitar com o Pages Router).

## Desenvolvimento

1. Suba o backend (porta padrão `8000`).
2. No `frontend/`: copie `.env.example` para `.env.local`, rode `npm install` e `npm run dev`.

Documentação detalhada do frontend: [frontend/README.md](frontend/README.md).

### Possiveis Evoluções:
1. Balanceador de aportes
2. Registrador de Ativos
3. Carteira de investimentos (Menos provavel)


### Evolução no Design:
- Facilicar para o cliente leigo, deixando um tooltip do que é cada coisa
- Aprimorar o Design
- Priorizar o light mode
