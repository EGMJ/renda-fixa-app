"use client";

import * as React from "react";
import { toast } from "sonner";
import { ApiError } from "@/shared/api/client";
import { simulateAsset } from "@/features/simulate-asset/api/simulateAsset";
import type { SimulationInput, SimulationOutput } from "@/entities/simulation/types";

export function useSimulation() {
  const [result, setResult] = React.useState<SimulationOutput | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const simulate = React.useCallback(async (input: SimulationInput) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const out = await simulateAsset(input);
      setResult(out);
    } catch (e) {
      let msg = "Erro interno, tente novamente";
      if (e instanceof ApiError) {
        if (e.status === 503) {
          msg = "Não foi possível buscar as taxas de mercado.";
        } else if (e.status === 400 || e.status === 422) {
          msg = e.message || "Dados inválidos para simulação.";
        } else if (e.status >= 500) {
          msg = "Erro interno. Tente novamente.";
        } else {
          msg = e.message || msg;
        }
        toast.error(msg);
      } else {
        toast.error(msg);
      }
      setError(msg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, simulate };
}
