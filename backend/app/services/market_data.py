import time
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import (
    BCB_IPCA_URL,
    BCB_SELIC_URL,
    CACHE_TTL_SECONDS,
    POUPANCA_FIXED_MONTHLY,
    POUPANCA_SELIC_THRESHOLD,
)

# Cache simples em memoria: {chave: (valor, timestamp)}
_cache: dict[str, tuple[Any, float]] = {}


def _get_from_cache(key: str) -> Any | None:
    """Retorna valor do cache se ainda valido (TTL nao expirado)."""
    if key in _cache:
        value, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return value
    return None


def _set_cache(key: str, value: Any) -> None:
    """Armazena valor no cache com timestamp atual."""
    _cache[key] = (value, time.time())


def clear_cache() -> None:
    """Limpa o cache. Util para testes."""
    _cache.clear()


async def get_selic_annual_pct() -> float:
    """
    Busca a taxa Selic Meta atual na API do BCB (serie 11).
    Retorna o valor em % a.a. (ex: 10.75).
    Em caso de falha, levanta HTTPException 503 com mensagem clara.
    Implementar cache simples em memoria com TTL de 1 hora para nao
    sobrecarregar a API do BCB a cada requisicao.
    """
    cached = _get_from_cache("selic")
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BCB_SELIC_URL, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            # A API retorna uma lista com um dicionario contendo 'valor'
            if data and len(data) > 0 and "valor" in data[0]:
                selic_value = float(data[0]["valor"].replace(",", "."))
                _set_cache("selic", selic_value)
                return selic_value
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Resposta inesperada da API do BCB para Selic",
                )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao consultar API do BCB (Selic): HTTP {e.response.status_code}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexao com API do BCB (Selic): {str(e)}",
        )
    except (KeyError, ValueError, IndexError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao processar dados da API do BCB (Selic): {str(e)}",
        )


async def get_ipca_annual_pct() -> float:
    """
    Busca o IPCA acumulado dos ultimos 12 meses na API do BCB (serie 13522).
    Retorna o valor em % a.a. (ex: 4.83).
    Mesmo tratamento de erro e cache que get_selic_annual_pct().
    """
    cached = _get_from_cache("ipca")
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BCB_IPCA_URL, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            # A API retorna uma lista com 12 meses de dados
            # Calculamos o acumulado: (1 + m1/100) * (1 + m2/100) * ... - 1
            if data and len(data) >= 12:
                accumulated = 1.0
                for month_data in data[-12:]:  # Ultimos 12 meses
                    if "valor" in month_data:
                        monthly_value = float(month_data["valor"].replace(",", "."))
                        accumulated *= 1 + (monthly_value / 100)
                ipca_annual = (accumulated - 1) * 100
                _set_cache("ipca", ipca_annual)
                return ipca_annual
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Resposta inesperada da API do BCB para IPCA (dados insuficientes)",
                )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao consultar API do BCB (IPCA): HTTP {e.response.status_code}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexao com API do BCB (IPCA): {str(e)}",
        )
    except (KeyError, ValueError, IndexError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao processar dados da API do BCB (IPCA): {str(e)}",
        )


def calculate_poupanca_monthly_rate(selic_annual_pct: float) -> float:
    """
    Regra oficial:
    - Se Selic > 8.5% a.a.: Poupança rende 70% da Selic a.a., convertida para mensal.
    - Se Selic <= 8.5% a.a.: Poupança rende 0.5% a.m. + TR.
    SIMPLIFICACAO: TR ~= 0 (aceitavel para simulacao).
    Retorna a taxa mensal como decimal (ex: 0.00489).
    """
    if selic_annual_pct > POUPANCA_SELIC_THRESHOLD:
        effective_annual = (selic_annual_pct * 0.70) / 100
        return (1 + effective_annual) ** (1 / 12) - 1
    else:
        return POUPANCA_FIXED_MONTHLY  # 0.5% a.m., TR ignorada


def calculate_tesouro_ipca_annual_rate(ipca_pct: float, spread_pct: float) -> float:
    """
    Composicao real do Tesouro IPCA+:
    (1 + IPCA/100) * (1 + spread/100) - 1
    Retorna a taxa composta em decimal (ex: 0.1123 para ~11.23% a.a.).
    """
    return (1 + ipca_pct / 100) * (1 + spread_pct / 100) - 1
