from pydantic import BaseModel


class MonthlySnapshot(BaseModel):
    month: int
    total_invested: float  # Total aportado acumulado ate este mes
    gross_balance: float  # Saldo bruto acumulado
    gross_return: float  # Rendimento bruto gerado NESTE mes
    accumulated_ir: float  # IR estimado acumulado (se resgatasse hoje)
    net_balance: float  # gross_balance - accumulated_ir


class TaxDetail(BaseModel):
    contribution_index: int  # 0 = aporte inicial, 1 = 1o mensal, etc.
    invested_amount: float
    gross_profit: float
    days_held: int
    ir_rate: float  # 0.0 se isento
    ir_amount: float
    net_profit: float


class RateInfo(BaseModel):
    """Taxas reais usadas no calculo — util para o front exibir transparencia."""

    selic_rate_pct: float | None  # Selic usada (so Poupanca / Tesouro Selic) TODO: Ajustar para ter o | None como antes
    ipca_rate_pct: float | None  # IPCA anual usado (so Tesouro IPCA) : Ajustar para ter o | None como antes
    effective_monthly_pct: float  # Taxa mensal efetiva usada
    effective_annual_pct: float  # Taxa anual efetiva usada


class SimulationOutput(BaseModel):
    # Resumo financeiro
    total_invested: float
    gross_balance: float
    gross_return: float
    total_ir: float
    net_balance: float
    net_return: float
    net_return_pct: float  # % liquido sobre total investido
    effective_annual_rate: float  # Taxa efetiva liquida ao ano apos IR
    ir_effective_rate: float  # % do rendimento bruto consumido pelo IR

    # Transparencia sobre taxas utilizadas
    rate_info: RateInfo

    # Detalhamento fiscal por aporte (PEPS)
    tax_breakdown: list[TaxDetail]

    # Serie temporal para grafico (1 entrada por mes)
    monthly_evolution: list[MonthlySnapshot]
