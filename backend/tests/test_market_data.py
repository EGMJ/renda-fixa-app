import pytest

from app.services.market_data import (
    calculate_poupanca_monthly_rate,
    calculate_tesouro_ipca_annual_rate,
    clear_cache,
    get_ipca_annual_pct,
    get_selic_annual_pct,
)


def test_calculate_poupanca_monthly_rate_selic_high():
    """
    Selic = 10.75% -> Poupança = 70% × 10.75% convertido para mensal
    """
    selic = 10.75
    monthly_rate = calculate_poupanca_monthly_rate(selic)

    # 70% de 10.75% = 7.525% a.a.
    expected_annual = 7.525 / 100
    expected_monthly = (1 + expected_annual) ** (1 / 12) - 1

    assert abs(monthly_rate - expected_monthly) < 0.0001


def test_calculate_poupanca_monthly_rate_selic_low():
    """
    Selic = 6.0% -> Poupança = 0.5% a.m. (regime fixo)
    """
    selic = 6.0
    monthly_rate = calculate_poupanca_monthly_rate(selic)

    assert monthly_rate == 0.005  # 0.5% a.m.


def test_calculate_poupanca_monthly_rate_boundary():
    """
    Selic = 8.5% (fronteira) -> 0.5% a.m. (regime fixo)
    Selic = 8.51% -> 70% da Selic
    """
    # Na fronteira
    monthly_rate_boundary = calculate_poupanca_monthly_rate(8.5)
    assert monthly_rate_boundary == 0.005

    # Acima da fronteira
    monthly_rate_above = calculate_poupanca_monthly_rate(8.51)
    assert monthly_rate_above != 0.005
    assert monthly_rate_above > 0.005


def test_calculate_tesouro_ipca_annual_rate():
    """
    Tesouro IPCA+: (1 + IPCA/100) * (1 + spread/100) - 1
    Exemplo: IPCA = 4.83%, spread = 6.0%
    Resultado esperado: ~11.08% a.a.
    """
    ipca = 4.83
    spread = 6.0

    result = calculate_tesouro_ipca_annual_rate(ipca, spread)

    # (1 + 0.0483) * (1 + 0.06) - 1
    expected = (1 + ipca / 100) * (1 + spread / 100) - 1

    assert abs(result - expected) < 0.0001
    assert abs(result - 0.110198) < 0.001  # ~11.02%


@pytest.mark.asyncio
async def test_selic_cache(mocker):
    """
    Segunda chamada em < 1h nao faz request HTTP (usa cache)
    """
    clear_cache()

    # Mock da resposta da API
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = [{"valor": "10,75"}]
    mock_response.raise_for_status = mocker.MagicMock()

    with mocker.patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        # Primeira chamada - deve fazer request
        result1 = await get_selic_annual_pct()
        assert mock_get.call_count == 1
        assert result1 == 10.75

        # Segunda chamada - deve usar cache
        result2 = await get_selic_annual_pct()
        assert mock_get.call_count == 1  # Nao fez nova request
        assert result2 == 10.75


@pytest.mark.asyncio
async def test_ipca_cache(mocker):
    """
    Segunda chamada em < 1h nao faz request HTTP (usa cache)
    """
    clear_cache()

    # Mock da resposta da API (12 meses de IPCA)
    mock_data = [{"valor": "0,50"} for _ in range(12)]
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = mock_data
    mock_response.raise_for_status = mocker.MagicMock()

    with mocker.patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        # Primeira chamada
        result1 = await get_ipca_annual_pct()
        assert mock_get.call_count == 1

        # Segunda chamada - cache
        result2 = await get_ipca_annual_pct()
        assert mock_get.call_count == 1
        assert result1 == result2


@pytest.mark.asyncio
async def test_selic_api_error(mocker):
    """
    Falha na API BCB -> Levanta excecao controlada (nao silencia)
    """
    clear_cache()

    from httpx import HTTPStatusError, Response
    from fastapi import HTTPException

    # Mock erro HTTP
    mock_response = mocker.MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPStatusError(
        "Server Error",
        request=mocker.MagicMock(),
        response=mock_response,
    )

    with mocker.patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(HTTPException) as exc_info:
            await get_selic_annual_pct()

        assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_ipca_api_error(mocker):
    """
    Falha na API BCB -> Levanta excecao controlada
    """
    clear_cache()

    from httpx import HTTPStatusError
    from fastapi import HTTPException

    mock_response = mocker.MagicMock()
    mock_response.status_code = 503
    mock_response.raise_for_status.side_effect = HTTPStatusError(
        "Service Unavailable",
        request=mocker.MagicMock(),
        response=mock_response,
    )

    with mocker.patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(HTTPException) as exc_info:
            await get_ipca_annual_pct()

        assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_selic_request_error(mocker):
    """
    Erro de conexao -> Levanta HTTPException 503
    """
    clear_cache()

    from httpx import RequestError
    from fastapi import HTTPException

    with mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=RequestError("Connection failed"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_selic_annual_pct()

        assert exc_info.value.status_code == 503
        assert "conexao" in exc_info.value.detail.lower() or "Connection" in exc_info.value.detail


@pytest.mark.asyncio
async def test_selic_invalid_response(mocker):
    """
    Resposta invalida da API -> Levanta HTTPException 503
    """
    clear_cache()

    from fastapi import HTTPException

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []  # Resposta vazia
    mock_response.raise_for_status = mocker.MagicMock()

    with mocker.patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(HTTPException) as exc_info:
            await get_selic_annual_pct()

        assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_ipca_invalid_response(mocker):
    """
    Resposta invalida da API (menos de 12 meses) -> Levanta HTTPException 503
    """
    clear_cache()

    from fastapi import HTTPException

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = [{"valor": "0,50"}]  # So 1 mes
    mock_response.raise_for_status = mocker.MagicMock()

    with mocker.patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(HTTPException) as exc_info:
            await get_ipca_annual_pct()

        assert exc_info.value.status_code == 503
