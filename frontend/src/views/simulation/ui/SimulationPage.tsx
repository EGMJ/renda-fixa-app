"use client";

import * as React from "react";
import { TrendingUp } from "lucide-react";
import { useSimulation } from "@/features/simulate-asset";
import { SimulationForm } from "@/widgets/simulation-form";
import { ResultsDashboard } from "@/widgets/results-dashboard";
import type { SimulationInput } from "@/entities/simulation/types";

export function SimulationPage() {
  const { result, loading, simulate } = useSimulation();
  const [last, setLast] = React.useState<SimulationInput | null>(null);

  const onSubmit = (input: SimulationInput) => {
    setLast(input);
    simulate(input);
  };

  const asset = last?.asset_type ?? "CDB";
  const periodMonths = last?.period_months ?? 24;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">Simulação de renda fixa</h1>
        <p className="text-muted-foreground">Projete saldo líquido, IR regressivo e evolução mês a mês.</p>
      </div>

      <div className="flex flex-col gap-8 lg:grid lg:grid-cols-[380px_minmax(0,1fr)] lg:items-start lg:gap-10">
        <aside className="w-full lg:sticky lg:top-24">
          <SimulationForm onSubmitSimulation={onSubmit} loading={loading} />
        </aside>

        <section className="min-h-[320px]" aria-label="Resultados">
          {loading && (
            <ResultsDashboard asset={asset} periodMonths={periodMonths} data={null} loading />
          )}
          {!loading && result && last && (
            <ResultsDashboard
              asset={last.asset_type}
              periodMonths={last.period_months}
              data={result}
              loading={false}
            />
          )}
          {!loading && !result && (
            <div className="flex min-h-[360px] flex-col items-center justify-center gap-4 rounded-xl border border-dashed bg-muted/20 p-10 text-center">
              <TrendingUp className="h-14 w-14 text-muted-foreground" aria-hidden />
              <div className="space-y-2">
                <p className="text-lg font-medium">Preencha os dados e clique em Simular</p>
                <p className="max-w-md text-sm text-muted-foreground">
                  Os gráficos, o detalhamento de IR (PEPS) e as taxas efetivas aparecem aqui após a simulação.
                </p>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
