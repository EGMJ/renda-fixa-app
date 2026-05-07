# ============================================================
# app/main.py
# Ponto de entrada da aplicação FastAPI.
# Responsável por:
#   - Configurar o ciclo de vida (lifespan) do app
#   - Registrar middlewares (CORS, tratamento de erros)
#   - Incluir os routers com seus prefixos
#   - Inicializar o banco de dados na startup
# ============================================================

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router      # Endpoints de autenticação
from app.api.v1.routes import router as business_router # Endpoints de negócio
from app.core.config import API_VERSION
from app.db.database import init_db
from app.services.market_data import clear_cache, get_ipca_annual_pct, get_selic_annual_pct

# Configuração básica de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------
# Lifespan: executa código de inicialização e encerramento.
# Usando o contexto assíncrono (recomendado a partir do FastAPI 0.93)
# -----------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:
      1. Inicializa as tabelas no banco MySQL (cria se não existirem)
      2. Faz warm-up do cache de taxas de mercado para a primeira
         requisição ser mais rápida

    Shutdown:
      1. Limpa o cache de taxas de mercado
    """
    # --- Startup ---
    logger.info("Iniciando aplicação...")

    # Cria tabelas no MySQL se não existirem
    init_db()
    logger.info("Banco de dados inicializado.")

    # Warm-up: pré-carrega taxas do BCB no cache
    try:
        await get_selic_annual_pct()
        await get_ipca_annual_pct()
        logger.info("Cache de taxas de mercado aquecido.")
    except Exception as exc:
        # Falha no warm-up não deve impedir o startup
        logger.warning(f"Falha ao aquecer cache de taxas: {exc}")

    yield  # A aplicação roda aqui

    # --- Shutdown ---
    clear_cache()
    logger.info("Cache limpo. Aplicação encerrada.")


# -----------------------------------------------------------------
# Criação da instância FastAPI
# -----------------------------------------------------------------
app = FastAPI(
    title="Renda Fixa API",
    description=(
        "Motor financeiro de simulação de investimentos em renda fixa brasileira. "
        "Inclui autenticação JWT, integração com o Banco Central e cálculo de IR regressivo."
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",         # Swagger UI em /docs
    redoc_url="/redoc",       # ReDoc em /redoc
)


# -----------------------------------------------------------------
# Middleware CORS
# Permite que o frontend (Next.js em localhost:3000) acesse a API.
# Em produção, substitua os origins pelo domínio real.
# -----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
    ],
    allow_credentials=True,   # Necessário para cookies e headers Authorization
    allow_methods=["*"],      # Permite GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],      # Permite Content-Type, Authorization, etc.
)


# -----------------------------------------------------------------
# Handler global de exceções não tratadas
# Previne que stack traces vazem para o cliente em produção.
# -----------------------------------------------------------------
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Captura qualquer exceção não tratada pelos endpoints.
    Loga o erro internamente (em produção, envie para Sentry/Datadog)
    e retorna um JSON genérico 500 sem expor detalhes internos.
    """
    logger.error(f"Erro não tratado em {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )


# -----------------------------------------------------------------
# Registro dos routers
# Todos os endpoints ficam sob o prefixo /api/v1
# -----------------------------------------------------------------

# Autenticação: /api/v1/auth/login, /api/v1/auth/register, /api/v1/auth/me
app.include_router(auth_router, prefix="/api/v1")

# Negócio: /api/v1/simulate, /api/v1/assets, /api/v1/market-rates, /api/v1/health
app.include_router(business_router, prefix="/api/v1")
