export type AssetType =
  | "CDB"
  | "LC"
  | "RDB"
  | "TESOURO_SELIC"
  | "TESOURO_IPCA"
  | "TESOURO_PREFIXADO"
  | "DEBENTURE"
  | "LCI"
  | "LCA"
  | "CRI"
  | "CRA"
  | "DEBENTURE_INCENTIVADA"
  | "POUPANCA";

export interface SimulationInput {
  asset_type: AssetType;
  initial_value: number;
  monthly_contribution: number;
  annual_rate: number;
  period_months: number;
  ipca_spread?: number;
}

export interface MonthlySnapshot {
  month: number;
  total_invested: number;
  gross_balance: number;
  gross_return: number;
  accumulated_ir: number;
  net_balance: number;
}

export interface TaxDetail {
  contribution_index: number;
  invested_amount: number;
  gross_profit: number;
  days_held: number;
  ir_rate: number;
  ir_amount: number;
  net_profit: number;
}

export interface RateInfo {
  selic_rate_pct: number | null;
  ipca_rate_pct: number | null;
  effective_monthly_pct: number;
  effective_annual_pct: number;
}

export interface SimulationOutput {
  total_invested: number;
  gross_balance: number;
  gross_return: number;
  total_ir: number;
  net_balance: number;
  net_return: number;
  net_return_pct: number;
  effective_annual_rate: number;
  ir_effective_rate: number;
  rate_info: RateInfo;
  tax_breakdown: TaxDetail[];
  monthly_evolution: MonthlySnapshot[];
}

export interface ComparisonItem {
  id: string;
  label: string;
  input: SimulationInput;
  result: SimulationOutput | null;
  loading: boolean;
  error: string | null;
}
