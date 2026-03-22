from app.core.config import EXEMPT_ASSETS, TAXED_ASSETS
from app.models.input import AssetType, SimulationInput
from app.models.output import RateInfo
from app.services.market_data import (
    calculate_poupanca_monthly_rate,
    calculate_tesouro_ipca_annual_rate,
    get_ipca_annual_pct,
    get_selic_annual_pct,
)


def is_exempt(asset_type: AssetType) -> bool:
    """Retorna True se o ativo e isento de IR."""
    return asset_type.value in EXEMPT_ASSETS


def _annual_to_monthly_rate(annual_rate_pct: float) -> float:
    """Converte taxa anual em % para taxa mensal em decimal."""
    annual_decimal = annual_rate_pct / 100
    return (1 + annual_decimal) ** (1 / 12) - 1


async def resolve_monthly_rate(input_data: SimulationInput) -> tuple[float, RateInfo]:
    """
    Recebe o input e retorna (taxa_mensal_decimal, RateInfo).
    Roteamento por tipo de ativo:

    POUPANCA:
        -> Busca Selic via market_data.get_selic_annual_pct()
        -> Aplica calculate_poupanca_monthly_rate()

    TESOURO_SELIC:
        -> Busca Selic, usa como taxa anual diretamente
        -> Converte para mensal com formula padrao

    TESOURO_IPCA:
        -> Busca IPCA via market_data.get_ipca_annual_pct()
        -> Compoe com ipca_spread via calculate_tesouro_ipca_annual_rate()
        -> Converte para mensal

    TESOURO_PREFIXADO / todos os outros:
        -> Usa annual_rate do input diretamente
        -> Converte para mensal: (1 + annual_rate/100)^(1/12) - 1
    """
    asset_type = input_data.asset_type

    if asset_type == AssetType.POUPANCA:
        selic_pct = await get_selic_annual_pct()
        monthly_rate = calculate_poupanca_monthly_rate(selic_pct)
        # Calcula a taxa anual efetiva equivalente
        effective_annual_pct = ((1 + monthly_rate) ** 12 - 1) * 100
        rate_info = RateInfo(
            selic_rate_pct=selic_pct,
            ipca_rate_pct=None,
            effective_monthly_pct=monthly_rate * 100,
            effective_annual_pct=effective_annual_pct,
        )
        return monthly_rate, rate_info

    elif asset_type == AssetType.TESOURO_SELIC:
        selic_pct = await get_selic_annual_pct()
        # Tesouro Selic rende ~100% da Selic
        monthly_rate = _annual_to_monthly_rate(selic_pct)
        rate_info = RateInfo(
            selic_rate_pct=selic_pct,
            ipca_rate_pct=None,
            effective_monthly_pct=monthly_rate * 100,
            effective_annual_pct=selic_pct,
        )
        return monthly_rate, rate_info

    elif asset_type == AssetType.TESOURO_IPCA:
        ipca_pct = await get_ipca_annual_pct()
        spread_pct = input_data.annual_rate  # annual_rate e o spread para IPCA
        effective_annual_decimal = calculate_tesouro_ipca_annual_rate(ipca_pct, spread_pct)
        effective_annual_pct = effective_annual_decimal * 100
        monthly_rate = _annual_to_monthly_rate(effective_annual_pct)
        rate_info = RateInfo(
            selic_rate_pct=None,
            ipca_rate_pct=ipca_pct,
            effective_monthly_pct=monthly_rate * 100,
            effective_annual_pct=effective_annual_pct,
        )
        return monthly_rate, rate_info

    else:
        # Todos os outros ativos usam annual_rate diretamente
        annual_rate_pct = input_data.annual_rate
        monthly_rate = _annual_to_monthly_rate(annual_rate_pct)
        rate_info = RateInfo(
            selic_rate_pct=None,
            ipca_rate_pct=None,
            effective_monthly_pct=monthly_rate * 100,
            effective_annual_pct=annual_rate_pct,
        )
        return monthly_rate, rate_info
