from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import router
from app.core.config import API_VERSION
from app.services.market_data import clear_cache, get_ipca_annual_pct, get_selic_annual_pct


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan do aplicativo:
    - Startup: Warm-up do cache de taxas de mercado
    - Shutdown: Limpeza de recursos
    """
    # Warm-up: Busca taxas para preencher o cache
    try:
        await get_selic_annual_pct()
        await get_ipca_annual_pct()
    except Exception:
        # Se falhar no warm-up, continua mesmo assim
        # A requisicao real tentara novamente
        pass

    yield

    # Cleanup
    clear_cache()


app = FastAPI(
    title="Renda Fixa API",
    description="Motor financeiro de simulacao de investimentos em renda fixa brasileira",
    version=API_VERSION,
    lifespan=lifespan,
)

# CORS: permitir localhost:3000 (Next.js dev) e origens de producao
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler generico de excecoes:
    - Loga o erro internamente (em producao, enviaria para servico de logs)
    - Retorna 500 sem expor stack trace
    """
    # Em producao, aqui enviariamos para Sentry/Datadog/etc
    import logging

    logging.error(f"Erro nao tratado: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )


# Registra rotas com prefixo /api/v1
app.include_router(router, prefix="/api/v1")
