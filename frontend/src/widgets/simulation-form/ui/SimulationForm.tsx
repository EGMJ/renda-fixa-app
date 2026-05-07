"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { CurrencyInput } from "@/shared/ui/CurrencyInput";
import { Label } from "@/shared/ui/label";
import { RateInput } from "@/shared/ui/RateInput";
import { Slider } from "@/shared/ui/slider";
import { AssetSelector } from "@/entities/asset";
import { isTesouroIpca, usesMarketRateOnly } from "@/entities/asset/model/assetOptions";
import {
  DEFAULT_SIMULATION_VALUES,
  simulationFormSchema,
  toSimulationInput,
  type SimulationFormValues,
} from "@/entities/simulation";
import type { SimulationInput } from "@/entities/simulation/types";
import { SimulateButton } from "@/features/simulate-asset";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";

interface SimulationFormProps {
  onSubmitSimulation: (input: SimulationInput) => void;
  loading: boolean;
}

export function SimulationForm({ onSubmitSimulation, loading }: SimulationFormProps) {
  const form = useForm<SimulationFormValues>({
    resolver: zodResolver(simulationFormSchema),
    defaultValues: {
      asset_type: DEFAULT_SIMULATION_VALUES.asset_type,
      initial_value: DEFAULT_SIMULATION_VALUES.initial_value,
      monthly_contribution: DEFAULT_SIMULATION_VALUES.monthly_contribution,
      annual_rate: DEFAULT_SIMULATION_VALUES.annual_rate,
      period_months: DEFAULT_SIMULATION_VALUES.period_months,
      ipca_spread: DEFAULT_SIMULATION_VALUES.ipca_spread,
    },
  });

  const assetType = form.watch("asset_type");
  const rateDisabled = usesMarketRateOnly(assetType);
  const showIpca = isTesouroIpca(assetType);

  return (
    <Card className="w-full lg:max-w-[380px] lg:shrink-0">
      <CardHeader>
        <CardTitle className="text-lg">Parâmetros</CardTitle>
      </CardHeader>
      <CardContent>
        <form
          className="space-y-6"
          onSubmit={form.handleSubmit((values) => onSubmitSimulation(toSimulationInput(values)))}
        >
          <div className="space-y-2">
            <Label>Tipo de ativo</Label>
            <Controller
              name="asset_type"
              control={form.control}
              render={({ field }) => <AssetSelector value={field.value} onChange={field.onChange} />}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="initial">Valor inicial</Label>
            <Controller
              name="initial_value"
              control={form.control}
              render={({ field }) => (
                <CurrencyInput id="initial" value={field.value} onValueChange={field.onChange} />
              )}
            />
            {form.formState.errors.initial_value && (
              <p className="text-xs text-destructive">{form.formState.errors.initial_value.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="monthly">Aporte mensal</Label>
            <Controller
              name="monthly_contribution"
              control={form.control}
              render={({ field }) => (
                <CurrencyInput id="monthly" value={field.value} onValueChange={field.onChange} />
              )}
            />
          </div>

          <Controller
            name="annual_rate"
            control={form.control}
            render={({ field }) => (
              <RateInput
                label={showIpca ? "Spread IPCA+ (% a.a.)" : "Taxa contratada (% a.a.)"}
                value={field.value}
                onValueChange={field.onChange}
                disabled={rateDisabled}
                hint={rateDisabled ? "Usa taxa de mercado (Selic / regra da poupança)" : null}
              />
            )}
          />
          {form.formState.errors.annual_rate && (
            <p className="text-xs text-destructive">{form.formState.errors.annual_rate.message}</p>
          )}

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Prazo (meses)</Label>
              <span className="text-sm tabular-nums text-muted-foreground">{form.watch("period_months")} meses</span>
            </div>
            <Controller
              name="period_months"
              control={form.control}
              render={({ field }) => (
                <>
                  <Slider
                    min={1}
                    max={120}
                    step={1}
                    value={[field.value]}
                    onValueChange={(v) => field.onChange(v[0])}
                  />
                  <Input
                    type="number"
                    min={1}
                    max={600}
                    className="mt-2"
                    value={field.value}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  />
                </>
              )}
            />
          </div>

          <SimulateButton loading={loading} />
        </form>
      </CardContent>
    </Card>
  );
}
