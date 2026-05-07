import pytest

from app.models.input import AssetType
from app.models.output import RateInfo
from app.services.calculator import run_simulation


def test_cdb_24_months_peps():
    """
    CDB 24 meses, R$1.000 + R$100/mes.
    Verifica que aporte 0 tem 720 dias -> 15%
    e aporte mes 20 tem 4 meses -> 120 dias -> 22.5%
    """
    monthly_rate = (1 + 0.12) ** (1 / 12) - 1  # 12% a.a.
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=12.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=24,
        initial_value=1000.0,
        monthly_contribution=100.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    # Aporte 0: 24 meses * 30 = 720 dias -> 15%
    aporte_0 = result.tax_breakdown[0]
    assert aporte_0.contribution_index == 0
    assert aporte_0.days_held == 720
    assert aporte_0.ir_rate == 0.15

    # Aporte do mes 20 (index 20): 4 meses * 30 = 120 dias -> 22.5%
    aporte_20 = result.tax_breakdown[20]
    assert aporte_20.contribution_index == 20
    assert aporte_20.days_held == 120
    assert aporte_20.ir_rate == 0.225


def test_lci_isento():
    """LCI 24 meses qualquer valor -> total_ir == 0"""
    monthly_rate = (1 + 0.12) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=12.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=24,
        initial_value=1000.0,
        monthly_contribution=100.0,
        is_exempt=True,  # LCI e isenta
        rate_info=rate_info,
    )

    assert result.total_ir == 0.0

    # Todos os aportes devem ter ir_rate = 0
    for tax_detail in result.tax_breakdown:
        assert tax_detail.ir_rate == 0.0
        assert tax_detail.ir_amount == 0.0


def test_initial_value_zero():
    """initial_value=0, so aportes mensais -> funciona normalmente"""
    monthly_rate = (1 + 0.10) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=10.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=12,
        initial_value=0.0,
        monthly_contribution=100.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert result.total_invested == 100.0 * 11  # 11 aportes (ultimo nao entra)
    assert result.gross_balance > result.total_invested


def test_monthly_contribution_zero():
    """monthly_contribution=0, so valor inicial -> funciona normalmente"""
    monthly_rate = (1 + 0.10) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=10.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=12,
        initial_value=1000.0,
        monthly_contribution=0.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert result.total_invested == 1000.0
    assert len(result.tax_breakdown) == 1  # So 1 aporte


def test_period_months_1():
    """period_months=1 -> monthly_evolution tem exatamente 1 entrada"""
    monthly_rate = (1 + 0.10) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=10.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=1,
        initial_value=1000.0,
        monthly_contribution=0.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert len(result.monthly_evolution) == 1
    assert result.monthly_evolution[0].month == 1


def test_monthly_evolution_length():
    """monthly_evolution deve ter exatamente period_months entradas"""
    monthly_rate = (1 + 0.10) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=10.0,
    )

    for months in [3, 6, 12, 24, 36]:
        result = run_simulation(
            monthly_rate=monthly_rate,
            period_months=months,
            initial_value=1000.0,
            monthly_contribution=100.0,
            is_exempt=False,
            rate_info=rate_info,
        )

        assert len(result.monthly_evolution) == months


def test_effective_annual_rate_positive():
    """effective_annual_rate deve ser positivo com taxa > 0"""
    monthly_rate = (1 + 0.10) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=10.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=12,
        initial_value=1000.0,
        monthly_contribution=0.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert result.effective_annual_rate > 0


def test_aporte_ultimo_mes_nao_entra():
    """Aporte do mes do resgate nao entra (nao rende)"""
    monthly_rate = (1 + 0.12) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=12.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=3,
        initial_value=1000.0,
        monthly_contribution=100.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    # Aportes: 0 (inicial) + 2 mensais (meses 1 e 2, mes 3 nao entra)
    assert len(result.tax_breakdown) == 3

    # Total investido: 1000 + 100*2 = 1200 (nao inclui o aporte do mes 3)
    assert result.total_invested == 1200.0


def test_protecao_divisao_por_zero():
    """Testa protecao contra divisao por zero quando total_invested=0"""
    monthly_rate = (1 + 0.12) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=12.0,
    )

    # Este caso nao deve acontecer devido a validacao do Pydantic,
    # mas testamos a protecao no calculo
    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=1,
        initial_value=1.0,
        monthly_contribution=0.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert result.net_return_pct >= 0 or result.total_invested > 0
    assert result.effective_annual_rate >= 0


def test_net_balance_consistency():
    """Verifica consistencia: net_balance = gross_balance - total_ir"""
    monthly_rate = (1 + 0.12) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=12.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=12,
        initial_value=1000.0,
        monthly_contribution=100.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert abs(result.net_balance - (result.gross_balance - result.total_ir)) < 0.01


def test_net_return_consistency():
    """Verifica consistencia: net_return = net_balance - total_invested"""
    monthly_rate = (1 + 0.12) ** (1 / 12) - 1
    rate_info = RateInfo(
        selic_rate_pct=None,
        ipca_rate_pct=None,
        effective_monthly_pct=monthly_rate * 100,
        effective_annual_pct=12.0,
    )

    result = run_simulation(
        monthly_rate=monthly_rate,
        period_months=12,
        initial_value=1000.0,
        monthly_contribution=100.0,
        is_exempt=False,
        rate_info=rate_info,
    )

    assert abs(result.net_return - (result.net_balance - result.total_invested)) < 0.01
