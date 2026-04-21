from fastapi import APIRouter, HTTPException, Depends

from app.core.config import EXEMPT_ASSETS, TAXED_ASSETS
from app.models.input import AssetType, SimulationInput
from app.models.output import SimulationOutput
from app.services.asset_classifier import is_exempt, resolve_monthly_rate
from app.services.calculator import run_simulation
from app.services.market_data import (
    calculate_poupanca_monthly_rate,
    get_ipca_annual_pct,
    get_selic_annual_pct,
)

# Importa autenticação
from app.api.v1.auth import router as auth_router
from app.core.security import get_current_user

router = APIRouter()

# inclui rota de login
router.include_router(auth_router)


@router.post("/simulate", response_model=SimulationOutput)
async def simulate(
    input_data: SimulationInput,
    current_user: str = Depends(get_current_user)
):
    """
    Executa simulacao de investimento em renda fixa.
    Protegido por autenticação JWT.
    """
    try:
        monthly_rate, rate_info = await resolve_monthly_rate(input_data)

        exempt = is_exempt(input_data.asset_type)

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
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno no processamento da simulação",
        )


@router.get("/assets")
async def list_assets():
    assets = []

    asset_labels = {
        AssetType.CDB: "CDB (Certificado de Deposito Bancario)",
        AssetType.LC: "LC (Letra de Cambio)",
        AssetType.RDB: "RDB (Recibo de Deposito Bancario)",
        AssetType.TESOURO_SELIC: "Tesouro Selic",
        AssetType.TESOURO_IPCA: "Tesouro IPCA+",
        AssetType.TESOURO_PREFIXADO: "Tesouro Prefixado",
        AssetType.DEBENTURE: "Debenture",
        AssetType.LCI: "LCI - Isenta",
        AssetType.LCA: "LCA - Isenta",
        AssetType.CRI: "CRI - Isento",
        AssetType.CRA: "CRA - Isento",
        AssetType.DEBENTURE_INCENTIVADA: "Debenture Incentivada - Isenta",
        AssetType.POUPANCA: "Poupança",
    }

    for asset_type in AssetType:
        requires_external = asset_type in {
            AssetType.POUPANCA,
            AssetType.TESOURO_SELIC,
            AssetType.TESOURO_IPCA,
        }

        category = "isento" if asset_type.value in EXEMPT_ASSETS else "tributado"

        assets.append({
            "id": asset_type.value,
            "label": asset_labels.get(asset_type, asset_type.value),
            "category": category,
            "requires_external_rate": requires_external,
        })

    return {"assets": assets}


@router.get("/market-rates")
async def get_market_rates():
    try:
        selic_pct = await get_selic_annual_pct()
        ipca_pct = await get_ipca_annual_pct()
        poupanca_monthly_pct = calculate_poupanca_monthly_rate(selic_pct) * 100

        return {
            "selic_pct": round(selic_pct, 2),
            "ipca_pct": round(ipca_pct, 2),
            "poupanca_monthly_pct": round(poupanca_monthly_pct, 4),
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Erro ao buscar taxas de mercado",
        )


@router.get("/health")
async def health_check():
    from app.core.config import API_VERSION
    return {"status": "ok", "version": API_VERSION}


# 🔥 Rota de teste (fora de qualquer função!)
@router.get("/test")
async def test():
    return {"ok": True}