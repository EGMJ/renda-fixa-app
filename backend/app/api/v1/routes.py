# ============================================================
# app/api/v1/routes.py
# Endpoints de negócio da API de Renda Fixa:
#   POST /api/v1/simulate     → Executa simulação de investimento
#   GET  /api/v1/assets       → Lista ativos disponíveis
#   GET  /api/v1/market-rates → Retorna taxas Selic/IPCA/Poupança
#   GET  /api/v1/health       → Health check da API
#
# Todos os endpoints marcados com Depends(get_current_user)
# exigem um Bearer token válido no header Authorization.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.auth import get_current_user          # Dependência de autenticação
from app.core.config import EXEMPT_ASSETS, TAXED_ASSETS
from app.db.models import User                         # Modelo ORM do usuário
from app.models.input import AssetType, SimulationInput
from app.models.output import SimulationOutput
from app.services.asset_classifier import is_exempt, resolve_monthly_rate
from app.services.calculator import run_simulation
from app.services.market_data import (
    calculate_poupanca_monthly_rate,
    get_ipca_annual_pct,
    get_selic_annual_pct,
)

router = APIRouter()


# ===================================================================
# POST /api/v1/simulate
# ===================================================================

@router.post(
    "/simulate",
    response_model=SimulationOutput,
    summary="Simula investimento em renda fixa",
)
async def simulate(
    input_data: SimulationInput,
    current_user: User = Depends(get_current_user),  # Protegido por JWT
) -> SimulationOutput:
    """
    Executa simulação financeira de um ativo de renda fixa.
    Retorna projeção de rendimentos, IR detalhado (PEPS) e
    evolução mês a mês do saldo.

    Requer: Bearer token válido no header Authorization.
    """
    try:
        # Resolve a taxa mensal do ativo (pode buscar taxa de mercado)
        monthly_rate, rate_info = await resolve_monthly_rate(input_data)

        # Verifica se o ativo é isento de IR
        exempt = is_exempt(input_data.asset_type)

        # Executa o motor de simulação financeira
        result = run_simulation(
            monthly_rate=monthly_rate,
            period_months=input_data.period_months,
            initial_value=input_data.initial_value,
            monthly_contribution=input_data.monthly_contribution,
            is_exempt=exempt,
            rate_info=rate_info,
        )

        return result

    except HTTPException:
        # Re-lança HTTPExceptions sem alterar (400, 401, 404, etc.)
        raise
    except Exception:
        # Exceções genéricas viram 500 sem expor stack trace
        raise HTTPException(
            status_code=500,
            detail="Erro interno no processamento da simulação",
        )


# ===================================================================
# GET /api/v1/assets
# ===================================================================

@router.get(
    "/assets",
    summary="Lista todos os ativos de renda fixa disponíveis",
)
async def list_assets():
    """
    Retorna lista de ativos com categoria tributária e informações
    sobre necessidade de taxa externa (SELIC/IPCA do BCB).
    Não requer autenticação — usado para popular dropdowns no front.
    """
    # Mapa de labels amigáveis para exibição na UI
    asset_labels = {
        AssetType.CDB:                  "CDB (Certificado de Depósito Bancário)",
        AssetType.LC:                   "LC (Letra de Câmbio)",
        AssetType.RDB:                  "RDB (Recibo de Depósito Bancário)",
        AssetType.TESOURO_SELIC:        "Tesouro Selic",
        AssetType.TESOURO_IPCA:         "Tesouro IPCA+",
        AssetType.TESOURO_PREFIXADO:    "Tesouro Prefixado",
        AssetType.DEBENTURE:            "Debênture",
        AssetType.LCI:                  "LCI (Letra de Crédito Imobiliário) – Isenta",
        AssetType.LCA:                  "LCA (Letra de Crédito do Agronegócio) – Isenta",
        AssetType.CRI:                  "CRI (Certificado de Recebíveis Imobiliários) – Isento",
        AssetType.CRA:                  "CRA (Certificado de Recebíveis do Agronegócio) – Isento",
        AssetType.DEBENTURE_INCENTIVADA:"Debênture Incentivada – Isenta",
        AssetType.POUPANCA:             "Poupança",
    }

    assets = []
    for asset_type in AssetType:
        # Ativos que dependem de dados externos (API do Banco Central)
        requires_external = asset_type in {
            AssetType.POUPANCA,
            AssetType.TESOURO_SELIC,
            AssetType.TESOURO_IPCA,
        }

        # Categoria tributária baseada na lista de configuração
        category = "isento" if asset_type.value in EXEMPT_ASSETS else "tributado"

        assets.append({
            "id": asset_type.value,
            "label": asset_labels.get(asset_type, asset_type.value),
            "category": category,
            "requires_external_rate": requires_external,
        })

    return {"assets": assets}


# ===================================================================
# GET /api/v1/market-rates
# ===================================================================

@router.get(
    "/market-rates",
    summary="Retorna taxas de mercado atuais (Selic, IPCA, Poupança)",
)
async def get_market_rates():
    """
    Consulta as taxas Selic e IPCA via API do Banco Central do Brasil.
    Os valores são cacheados por 1 hora para reduzir chamadas externas.
    Não requer autenticação.
    """
    try:
        # Busca taxas com cache automático (TTL = 1h)
        selic_pct = await get_selic_annual_pct()
        ipca_pct  = await get_ipca_annual_pct()

        # Calcula a taxa mensal da poupança com base na regra atual
        poupanca_monthly_pct = calculate_poupanca_monthly_rate(selic_pct) * 100

        return {
            "selic_pct":          round(selic_pct, 2),
            "ipca_pct":           round(ipca_pct, 2),
            "poupanca_monthly_pct": round(poupanca_monthly_pct, 4),
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Erro ao buscar taxas de mercado. Tente novamente em instantes.",
        )


# ===================================================================
# GET /api/v1/health
# ===================================================================

@router.get(
    "/health",
    summary="Health check da API",
)
async def health_check():
    """
    Endpoint de verificação de saúde — usado por load balancers e
    ferramentas de monitoramento (ex: Kubernetes, Render, Railway).
    Sempre retorna 200 OK se a API estiver rodando.
    """
    from app.core.config import API_VERSION
    return {"status": "ok", "version": API_VERSION}
