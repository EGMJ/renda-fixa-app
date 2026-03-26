import { apiFetch } from "@/shared/api/client";
import type { SimulationInput, SimulationOutput } from "@/entities/simulation/types";

export async function simulateAsset(input: SimulationInput): Promise<SimulationOutput> {
  return apiFetch<SimulationOutput>("/api/v1/simulate", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
