import type { AssetType, SimulationInput } from "@/entities/simulation/types";

export const DEFAULT_SIMULATION_VALUES: SimulationInput = {
  asset_type: "CDB",
  initial_value: 1000,
  monthly_contribution: 100,
  annual_rate: 12,
  period_months: 24,
  ipca_spread: 0,
};

export function makeComparisonLabel(asset: AssetType, index: number) {
  return `Ativo ${index + 1} (${asset})`;
}
