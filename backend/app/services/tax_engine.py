from app.core.config import IR_TABLE


def get_ir_rate(days_held: int) -> float:
    """Consulta IR_TABLE e retorna aliquota para o prazo em dias."""
    for threshold_days, rate in IR_TABLE:
        if days_held <= threshold_days:
            return rate
    return IR_TABLE[-1][1]  # Fallback para o ultimo valor (infinito)


def calculate_ir_for_contribution(
    principal: float,
    final_value: float,
    days_held: int,
    is_exempt: bool,
) -> dict:
    """
    Calcula IR de um unico aporte.
    Retorna: {gross_profit, ir_rate, ir_amount, net_profit}

    Regras:
    - IR incide APENAS sobre gross_profit (final_value - principal)
    - Se is_exempt=True: ir_rate=0, ir_amount=0
    - Se gross_profit <= 0: ir_amount=0 (nao ha imposto sobre prejuizo)
    - days_held=0 (aporte no mes do resgate): gross_profit=0, ir_amount=0
    """
    gross_profit = final_value - principal

    # Se isento, nao ha IR
    if is_exempt:
        return {
            "gross_profit": gross_profit,
            "ir_rate": 0.0,
            "ir_amount": 0.0,
            "net_profit": gross_profit,
        }

    # Se dias de detencao = 0 (aporte no mes do resgate), nao rendeu nada
    if days_held <= 0:
        return {
            "gross_profit": 0.0,
            "ir_rate": 0.0,
            "ir_amount": 0.0,
            "net_profit": 0.0,
        }

    # Se prejuizo, nao ha IR
    if gross_profit <= 0:
        return {
            "gross_profit": gross_profit,
            "ir_rate": 0.0,
            "ir_amount": 0.0,
            "net_profit": gross_profit,
        }

    # Calcula IR normalmente
    ir_rate = get_ir_rate(days_held)
    ir_amount = gross_profit * ir_rate
    net_profit = gross_profit - ir_amount

    return {
        "gross_profit": gross_profit,
        "ir_rate": ir_rate,
        "ir_amount": ir_amount,
        "net_profit": net_profit,
    }
