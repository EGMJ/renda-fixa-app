/** Resposta GET /api/v1/market-rates */
export interface MarketRatesResponse {
  selic_pct: number;
  ipca_pct: number;
  poupanca_monthly_pct: number;
}

export interface MarketRatesView {
  selicAnnualPct: number;
  ipcaAnnualPct: number;
  /** Taxa mensal da poupança em % (valor informado pelo backend). */
  poupancaMonthlyPct: number;
}
