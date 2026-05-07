import pytest

from app.services.tax_engine import calculate_ir_for_contribution, get_ir_rate


def test_ir_rate_90_days():
    """90 dias -> 22.5%"""
    assert get_ir_rate(90) == 0.225


def test_ir_rate_270_days():
    """270 dias -> 20%"""
    assert get_ir_rate(270) == 0.200


def test_ir_rate_540_days():
    """540 dias -> 17.5%"""
    assert get_ir_rate(540) == 0.175


def test_ir_rate_730_days():
    """730 dias -> 15%"""
    assert get_ir_rate(730) == 0.150


def test_ir_rate_180_boundary():
    """180 dias -> 22.5% (fronteira)"""
    assert get_ir_rate(180) == 0.225


def test_ir_rate_181_boundary():
    """181 dias -> 20% (depois da fronteira)"""
    assert get_ir_rate(181) == 0.200


def test_ir_rate_360_boundary():
    """360 dias -> 20% (fronteira)"""
    assert get_ir_rate(360) == 0.200


def test_ir_rate_361_boundary():
    """361 dias -> 17.5% (depois da fronteira)"""
    assert get_ir_rate(361) == 0.175


def test_ir_rate_720_boundary():
    """720 dias -> 17.5% (fronteira)"""
    assert get_ir_rate(720) == 0.175


def test_ir_rate_721_boundary():
    """721 dias -> 15% (depois da fronteira)"""
    assert get_ir_rate(721) == 0.150


def test_ir_rate_very_long():
    """9999 dias -> 15%"""
    assert get_ir_rate(9999) == 0.150


def test_calculate_ir_tributado_90_dias():
    """Aporte tributado, 90 dias -> 22.5% IR"""
    principal = 1000.0
    final_value = 1100.0
    result = calculate_ir_for_contribution(principal, final_value, 90, is_exempt=False)

    assert result["gross_profit"] == 100.0
    assert result["ir_rate"] == 0.225
    assert result["ir_amount"] == 22.5  # 100 * 0.225
    assert result["net_profit"] == 77.5  # 100 - 22.5


def test_calculate_ir_isento():
    """Aporte isento -> IR = 0"""
    principal = 1000.0
    final_value = 1100.0
    result = calculate_ir_for_contribution(principal, final_value, 90, is_exempt=True)

    assert result["gross_profit"] == 100.0
    assert result["ir_rate"] == 0.0
    assert result["ir_amount"] == 0.0
    assert result["net_profit"] == 100.0


def test_calculate_ir_gross_profit_zero():
    """Lucro zero -> IR = 0"""
    principal = 1000.0
    final_value = 1000.0
    result = calculate_ir_for_contribution(principal, final_value, 90, is_exempt=False)

    assert result["gross_profit"] == 0.0
    assert result["ir_rate"] == 0.0
    assert result["ir_amount"] == 0.0
    assert result["net_profit"] == 0.0


def test_calculate_ir_gross_profit_negative():
    """Prejuizo -> IR = 0"""
    principal = 1000.0
    final_value = 900.0
    result = calculate_ir_for_contribution(principal, final_value, 90, is_exempt=False)

    assert result["gross_profit"] == -100.0
    assert result["ir_rate"] == 0.0
    assert result["ir_amount"] == 0.0
    assert result["net_profit"] == -100.0


def test_calculate_ir_days_held_zero():
    """0 dias de detencao (aporte no mes do resgate) -> IR = 0"""
    principal = 1000.0
    final_value = 1005.0  # Teria algum rendimento, mas 0 dias
    result = calculate_ir_for_contribution(principal, final_value, 0, is_exempt=False)

    assert result["gross_profit"] == 0.0  # Normalizado para 0
    assert result["ir_rate"] == 0.0
    assert result["ir_amount"] == 0.0
    assert result["net_profit"] == 0.0


def test_calculate_ir_days_held_negative():
    """Dias negativos tratados como 0 -> IR = 0"""
    principal = 1000.0
    final_value = 1100.0
    result = calculate_ir_for_contribution(principal, final_value, -5, is_exempt=False)

    assert result["gross_profit"] == 0.0
    assert result["ir_rate"] == 0.0
    assert result["ir_amount"] == 0.0
    assert result["net_profit"] == 0.0
