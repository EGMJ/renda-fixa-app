import { z } from "zod";
import type { AssetType } from "@/entities/simulation/types";

const assetTypeEnum = z.enum([
  "CDB",
  "LC",
  "RDB",
  "TESOURO_SELIC",
  "TESOURO_IPCA",
  "TESOURO_PREFIXADO",
  "DEBENTURE",
  "LCI",
  "LCA",
  "CRI",
  "CRA",
  "DEBENTURE_INCENTIVADA",
  "POUPANCA",
]);

export const simulationFormSchema = z
  .object({
    asset_type: assetTypeEnum,
    initial_value: z.number().min(0),
    monthly_contribution: z.number().min(0),
    /** % a.a. informada pelo usuário; para Selic/Poupança é ignorada na API (enviamos placeholder). */
    annual_rate: z.number(),
    period_months: z.number().min(1).max(600),
    ipca_spread: z.number().min(0).optional(),
  })
  .superRefine((data, ctx) => {
    if (data.initial_value === 0 && data.monthly_contribution === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Informe valor inicial ou aporte mensal.",
        path: ["initial_value"],
      });
    }
    const needsRate = data.asset_type !== "POUPANCA" && data.asset_type !== "TESOURO_SELIC";
    if (needsRate && data.annual_rate <= 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Informe uma taxa válida.",
        path: ["annual_rate"],
      });
    }
    if (data.asset_type === "TESOURO_IPCA" && data.annual_rate < 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Spread inválido.",
        path: ["annual_rate"],
      });
    }
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

export function toSimulationInput(values: SimulationFormValues): import("@/entities/simulation/types").SimulationInput {
  const base = {
    asset_type: values.asset_type as AssetType,
    initial_value: values.initial_value,
    monthly_contribution: values.monthly_contribution,
    period_months: values.period_months,
  };

  if (values.asset_type === "POUPANCA" || values.asset_type === "TESOURO_SELIC") {
    return {
      ...base,
      annual_rate: 1,
      ipca_spread: values.ipca_spread ?? 0,
    };
  }

  if (values.asset_type === "TESOURO_IPCA") {
    return {
      ...base,
      annual_rate: values.annual_rate,
      ipca_spread: values.ipca_spread ?? 0,
    };
  }

  return {
    ...base,
    annual_rate: values.annual_rate,
    ipca_spread: values.ipca_spread ?? 0,
  };
}
