import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """GET /api/v1/health -> status ok"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_list_assets():
    """GET /api/v1/assets -> lista de ativos"""
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert len(data["assets"]) > 0

    # Verifica estrutura de cada ativo
    for asset in data["assets"]:
        assert "id" in asset
        assert "label" in asset
        assert "category" in asset
        assert asset["category"] in ["tributado", "isento"]
        assert "requires_external_rate" in asset


def test_simulate_cdb_valid():
    """POST /api/v1/simulate com input valido CDB -> 200"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 1000.0,
        "monthly_contribution": 100.0,
        "annual_rate": 12.0,
        "period_months": 24,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "total_invested" in data
    assert "gross_balance" in data
    assert "net_balance" in data
    assert "total_ir" in data
    assert "tax_breakdown" in data
    assert "monthly_evolution" in data
    assert "rate_info" in data


def test_simulate_both_values_zero():
    """Ambos valores zerados -> deve falhar na validacao (422)"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 0,
        "monthly_contribution": 0,
        "annual_rate": 12.0,
        "period_months": 12,
    }

    response = client.post("/api/v1/simulate", json=payload)
    # Pydantic vai rejeitar pelo model_validator
    assert response.status_code == 422


def test_simulate_period_months_zero():
    """period_months=0 -> 422 (validacao Pydantic)"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 1000.0,
        "monthly_contribution": 0,
        "annual_rate": 12.0,
        "period_months": 0,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_annual_rate_negative():
    """annual_rate=-1 -> 422 (validacao Pydantic)"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 1000.0,
        "monthly_contribution": 0,
        "annual_rate": -1.0,
        "period_months": 12,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 422


def test_simulate_lci_isento():
    """LCI e isento -> total_ir = 0"""
    payload = {
        "asset_type": "LCI",
        "initial_value": 10000.0,
        "monthly_contribution": 0,
        "annual_rate": 12.0,
        "period_months": 24,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_ir"] == 0.0


def test_simulate_rate_info_structure():
    """Verifica estrutura completa de rate_info"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 1000.0,
        "monthly_contribution": 0,
        "annual_rate": 12.0,
        "period_months": 12,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    rate_info = data["rate_info"]

    assert "selic_rate_pct" in rate_info
    assert "ipca_rate_pct" in rate_info
    assert "effective_monthly_pct" in rate_info
    assert "effective_annual_pct" in rate_info

    # Para CDB, nao usa taxas externas
    assert rate_info["selic_rate_pct"] is None
    assert rate_info["ipca_rate_pct"] is None
    assert rate_info["effective_annual_pct"] == 12.0


def test_simulate_tax_breakdown_structure():
    """Verifica estrutura de tax_breakdown"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 1000.0,
        "monthly_contribution": 100.0,
        "annual_rate": 12.0,
        "period_months": 6,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    tax_breakdown = data["tax_breakdown"]

    assert len(tax_breakdown) > 0

    for detail in tax_breakdown:
        assert "contribution_index" in detail
        assert "invested_amount" in detail
        assert "gross_profit" in detail
        assert "days_held" in detail
        assert "ir_rate" in detail
        assert "ir_amount" in detail
        assert "net_profit" in detail


def test_simulate_monthly_evolution_structure():
    """Verifica estrutura de monthly_evolution"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 1000.0,
        "monthly_contribution": 0,
        "annual_rate": 12.0,
        "period_months": 3,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    evolution = data["monthly_evolution"]

    assert len(evolution) == 3  # Exatamente 3 meses

    for i, snapshot in enumerate(evolution):
        assert snapshot["month"] == i + 1
        assert "total_invested" in snapshot
        assert "gross_balance" in snapshot
        assert "gross_return" in snapshot
        assert "accumulated_ir" in snapshot
        assert "net_balance" in snapshot


def test_market_rates_structure(mocker):
    """GET /api/v1/market-rates -> retorna taxas"""
    # Mock das taxas para evitar chamada externa
    mocker.patch(
        "app.api.v1.routes.get_selic_annual_pct",
        return_value=10.75,
    )
    mocker.patch(
        "app.api.v1.routes.get_ipca_annual_pct",
        return_value=4.83,
    )

    response = client.get("/api/v1/market-rates")
    assert response.status_code == 200

    data = response.json()
    assert "selic_pct" in data
    assert "ipca_pct" in data
    assert "poupanca_monthly_pct" in data


def test_market_rates_bcb_offline(mocker):
    """BCB offline -> 503 com mensagem legivel"""
    from fastapi import HTTPException

    mocker.patch(
        "app.api.v1.routes.get_selic_annual_pct",
        side_effect=HTTPException(status_code=503, detail="BCB indisponivel"),
    )

    response = client.get("/api/v1/market-rates")
    assert response.status_code == 503


def test_cors_headers():
    """Verifica que CORS esta configurado"""
    # Preflight request
    response = client.options(
        "/api/v1/simulate",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_simulate_only_initial_value():
    """Apenas initial_value, sem monthly_contribution"""
    payload = {
        "asset_type": "CDB",
        "initial_value": 5000.0,
        "monthly_contribution": 0,
        "annual_rate": 10.0,
        "period_months": 12,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_invested"] == 5000.0
    assert len(data["tax_breakdown"]) == 1


def test_simulate_only_monthly_contribution():
    """Apenas monthly_contribution, sem initial_value"""
    payload = {
        "asset_type": "LCI",
        "initial_value": 0,
        "monthly_contribution": 200.0,
        "annual_rate": 12.0,
        "period_months": 6,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    # 5 aportes mensais (mes 6 nao entra)
    assert data["total_invested"] == 200.0 * 5


def test_simulate_tesouro_prefixado():
    """Tesouro Prefixado usa annual_rate diretamente"""
    payload = {
        "asset_type": "TESOURO_PREFIXADO",
        "initial_value": 1000.0,
        "monthly_contribution": 0,
        "annual_rate": 11.5,
        "period_months": 12,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["rate_info"]["effective_annual_pct"] == 11.5


def test_simulate_debenture_incentivada_isenta():
    """Debenture Incentivada e isenta de IR"""
    payload = {
        "asset_type": "DEBENTURE_INCENTIVADA",
        "initial_value": 10000.0,
        "monthly_contribution": 0,
        "annual_rate": 9.0,
        "period_months": 24,
    }

    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_ir"] == 0.0
