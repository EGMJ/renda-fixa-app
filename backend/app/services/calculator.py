from dataclasses import dataclass

from app.models.output import MonthlySnapshot, RateInfo, SimulationOutput, TaxDetail
from app.services.tax_engine import calculate_ir_for_contribution


@dataclass
class ContributionTracker:
    index: int  # 0 = aporte inicial
    principal: float  # valor original aportado
    current_value: float  # valor corrigido no mes atual
    months_held: int  # meses que este aporte esta aplicado


def _round_output(value: float) -> float:
    """Arredonda valor para 2 casas decimais na saida."""
    return round(value, 2)


def run_simulation(
    monthly_rate: float,
    period_months: int,
    initial_value: float,
    monthly_contribution: float,
    is_exempt: bool,
    rate_info: RateInfo,
) -> SimulationOutput:
    """
    Motor principal de simulacao usando metodo PEPS.

    ENTRADA: monthly_rate (decimal), period_months, initial_value,
             monthly_contribution, is_exempt

    LOOP mes a mes (PEPS):
        1. Cada aporte cresce pelo monthly_rate
        2. Adiciona novo aporte (exceto no ultimo mes)
        3. Snapshot mensal
        4. No ultimo mes, calcula IR de cada aporte
    """
    pool: list[ContributionTracker] = []
    monthly_evolution: list[MonthlySnapshot] = []

    # Aporte inicial
    if initial_value > 0:
        pool.append(
            ContributionTracker(
                index=0,
                principal=initial_value,
                current_value=initial_value,
                months_held=0,
            )
        )

    # Loop mês a mês
    for month in range(1, period_months + 1):
        # 1. CRESCIMENTO: Cada aporte cresce
        for contribution in pool:
            contribution.current_value *= 1 + monthly_rate
            contribution.months_held += 1

        # 2. NOVO APORTE (exceto no último mês)
        if monthly_contribution > 0 and month < period_months:
            pool.append(
                ContributionTracker(
                    index=len(pool),
                    principal=monthly_contribution,
                    current_value=monthly_contribution,
                    months_held=0,
                )
            )

        # 3. SNAPSHOT MENSAL
        # Total investido ate este mes
        months_with_contribution = min(month, period_months - 1)
        total_invested = initial_value + monthly_contribution * months_with_contribution

        # Saldo bruto
        gross_balance = sum(c.current_value for c in pool)

        # Rendimento deste mes
        gross_balance_anterior = (
            monthly_evolution[-1].gross_balance if monthly_evolution else initial_value
        )
        monthly_return = gross_balance - gross_balance_anterior

        # IR estimado acumulado (se resgatasse hoje)
        accumulated_ir = 0.0
        for contribution in pool:
            days_held = contribution.months_held * 30
            ir_result = calculate_ir_for_contribution(
                contribution.principal,
                contribution.current_value,
                days_held,
                is_exempt,
            )
            accumulated_ir += ir_result["ir_amount"]

        net_balance = gross_balance - accumulated_ir

        monthly_evolution.append(
            MonthlySnapshot(
                month=month,
                total_invested=_round_output(total_invested),
                gross_balance=_round_output(gross_balance),
                gross_return=_round_output(monthly_return),
                accumulated_ir=_round_output(accumulated_ir),
                net_balance=_round_output(net_balance),
            )
        )

    # 4. RESGATE FINAL: Calcula detalhamento fiscal de cada aporte
    tax_breakdown: list[TaxDetail] = []
    total_ir = 0.0

    for contribution in pool:
        days_held = contribution.months_held * 30
        ir_result = calculate_ir_for_contribution(
            contribution.principal,
            contribution.current_value,
            days_held,
            is_exempt,
        )

        tax_breakdown.append(
            TaxDetail(
                contribution_index=contribution.index,
                invested_amount=_round_output(contribution.principal),
                gross_profit=_round_output(ir_result["gross_profit"]),
                days_held=days_held,
                ir_rate=ir_result["ir_rate"],
                ir_amount=_round_output(ir_result["ir_amount"]),
                net_profit=_round_output(ir_result["net_profit"]),
            )
        )
        total_ir += ir_result["ir_amount"]

    # Valores finais
    final_gross_balance = monthly_evolution[-1].gross_balance
    final_total_invested = monthly_evolution[-1].total_invested
    gross_return = final_gross_balance - final_total_invested
    net_balance = final_gross_balance - total_ir
    net_return = net_balance - final_total_invested

    # Guarda-chuva: protege divisao por zero
    if final_total_invested > 0:
        net_return_pct = (net_return / final_total_invested) * 100
        effective_annual_rate = ((net_balance / final_total_invested) ** (12 / period_months) - 1) * 100
    else:
        net_return_pct = 0.0
        effective_annual_rate = 0.0

    if gross_return > 0:
        ir_effective_rate = (total_ir / gross_return) * 100
    else:
        ir_effective_rate = 0.0

    # Arredonda rate_info tambem
    rounded_rate_info = RateInfo(
        selic_rate_pct=_round_output(rate_info.selic_rate_pct) if rate_info.selic_rate_pct is not None else None,
        ipca_rate_pct=_round_output(rate_info.ipca_rate_pct) if rate_info.ipca_rate_pct is not None else None,
        effective_monthly_pct=_round_output(rate_info.effective_monthly_pct),
        effective_annual_pct=_round_output(rate_info.effective_annual_pct),
    )

    return SimulationOutput(
        total_invested=_round_output(final_total_invested),
        gross_balance=_round_output(final_gross_balance),
        gross_return=_round_output(gross_return),
        total_ir=_round_output(total_ir),
        net_balance=_round_output(net_balance),
        net_return=_round_output(net_return),
        net_return_pct=_round_output(net_return_pct),
        effective_annual_rate=_round_output(effective_annual_rate),
        ir_effective_rate=_round_output(ir_effective_rate),
        rate_info=rounded_rate_info,
        tax_breakdown=tax_breakdown,
        monthly_evolution=monthly_evolution,
    )
