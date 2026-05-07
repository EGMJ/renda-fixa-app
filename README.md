# Calculadora de Renda Fixa 📈

Aplicação full-stack para simulação de investimentos em renda fixa brasileira com autenticação JWT e banco de dados MySQL.

---

## Arquitetura

```
renda-fixa-app/
├── backend/          → FastAPI + SQLAlchemy + MySQL
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py     # Endpoints: /login, /register, /me
│   │   │   └── routes.py   # Endpoints: /simulate, /assets, /market-rates
│   │   ├── core/
│   │   │   ├── security.py # JWT, bcrypt
│   │   │   └── config.py   # Constantes financeiras
│   │   ├── db/
│   │   │   ├── database.py # Engine SQLAlchemy + get_db()
│   │   │   └── models.py   # Modelo ORM User (tabela users)
│   │   ├── models/
│   │   │   └── auth.py     # Schemas Pydantic (UserCreate, Token, etc.)
│   │   └── services/       # Calculadora, taxas BCB, etc.
│   ├── .env.example
│   └── requirements.txt
│
└── frontend/         → Next.js 15 + TypeScript + Tailwind
    └── src/
        ├── app/
        │   ├── page.tsx         # "/" → SimulationPage (protegida)
        │   ├── comparar/        # "/comparar" → ComparisonPage (protegida)
        │   ├── login/           # "/login" → LoginForm (pública)
        │   └── register/        # "/register" → RegisterForm (pública)
        ├── middleware.ts         # Proteção de rotas por JWT cookie
        ├── features/out/
        │   ├── login_form.tsx
        │   └── register_form.tsx
        └── shared/lib/auth.ts   # Utilitários de token
```

---

## Pré-requisitos

- Python 3.11+
- Node.js 20+
- MySQL 8.0+

---

## Setup do Backend

### 1. Criar o banco de dados MySQL

```sql
CREATE DATABASE renda_fixa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configurar variáveis de ambiente

```bash
cd backend
cp .env.example .env
# Edite o .env com suas credenciais MySQL e gere uma SECRET_KEY forte
```

Gerar SECRET_KEY segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Instalar dependências e rodar

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# As tabelas são criadas automaticamente no startup
uvicorn app.main:app --reload --port 8000
```

A API estará em: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

---

## Setup do Frontend

```bash
cd frontend
cp .env.local.example .env.local  # Ajuste a URL da API se necessário
npm install
npm run dev
```

A aplicação estará em: http://localhost:3000

---

## Fluxo de Autenticação

1. Usuário acessa `/` → middleware detecta ausência de cookie → redireciona para `/login`
2. Login bem-sucedido → backend retorna JWT → frontend salva em `localStorage` + cookie
3. Middleware lê o cookie em cada requisição → permite acesso às rotas protegidas
4. Logout → token removido de ambos os armazenamentos → redireciona para `/login`

---

## Endpoints da API

| Método | Rota                      | Auth | Descrição                     |
|--------|---------------------------|------|-------------------------------|
| POST   | /api/v1/auth/login        | ❌   | Login (OAuth2 form-data)      |
| POST   | /api/v1/auth/register     | ❌   | Cadastro de novo usuário      |
| GET    | /api/v1/auth/me           | ✅   | Dados do usuário logado       |
| POST   | /api/v1/simulate          | ✅   | Simula investimento           |
| GET    | /api/v1/assets            | ❌   | Lista ativos disponíveis      |
| GET    | /api/v1/market-rates      | ❌   | Taxas Selic/IPCA/Poupança     |
| GET    | /api/v1/health            | ❌   | Health check                  |

---

## Segurança

- Senhas hasheadas com **bcrypt** (nunca armazenadas em texto plano)
- Tokens **JWT** assinados com HS256 e expiração configurável
- Chaves sensíveis em **variáveis de ambiente** (nunca no código)
- Validação de entrada com **Pydantic** (username, email, força de senha)
- Verificação de duplicidade de username e e-mail no cadastro
- Rotas protegidas no **Edge Runtime** do Next.js via middleware
