"use client";

import * as React from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatBRL } from "@/shared/lib/formatters";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { CurrencyInput } from "@/shared/ui/CurrencyInput";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { RateInput } from "@/shared/ui/RateInput";
import { Slider } from "@/shared/ui/slider";
import { ASSET_ORDER, assetLabel, isTesouroIpca, usesMarketRateOnly } from "@/entities/asset";
import {
  SummaryCards,
  toSimulationInput,
  type SimulationFormValues,
} from "@/entities/simulation";
import type { ComparisonItem, SimulationInput } from "@/entities/simulation/types";
import { AddAssetButton, useComparison } from "@/features/compare-assets";

const LINE_COLORS = ["#3b82f6", "#22c55e", "#a855f7", "#f97316"];

function TooltipBrl({ active, payload, label }: { active?: boolean; payload?: { name?: string; value?: number; color?: string }[]; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-sm shadow-md">
      <p className="mb-1 font-medium">Mês {label}</p>
      <ul className="space-y-0.5">
        {payload.map((p) => (
          <li key={p.name} className="flex gap-2 tabular-nums">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: p.color }} />
            <span>{p.name}:</span>
            <span>{formatBRL(Number(p.value))}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function itemToFormValues(input: SimulationInput): SimulationFormValues {
  return {
    asset_type: input.asset_type,
    initial_value: input.initial_value,
    monthly_contribution: input.monthly_contribution,
    annual_rate: input.annual_rate === 1 && (input.asset_type === "POUPANCA" || input.asset_type === "TESOURO_SELIC") ? 0 : input.annual_rate,
    period_months: input.period_months,
    ipca_spread: input.ipca_spread ?? 0,
  };
}

function ComparisonRow({
  item,
  onChange,
  onRemove,
  canRemove,
}: {
  item: ComparisonItem;
  onChange: (input: SimulationInput) => void;
  onRemove: () => void;
  canRemove: boolean;
}) {
  const fv = itemToFormValues(item.input);
  const rateDisabled = usesMarketRateOnly(item.input.asset_type);
  const showIpca = isTesouroIpca(item.input.asset_type);

  const patch = (partial: Partial<SimulationFormValues>) => {
    const next: SimulationFormValues = {
      ...fv,
      ...partial,
      asset_type: partial.asset_type ?? fv.asset_type,
    };
    if (partial.asset_type && usesMarketRateOnly(partial.asset_type)) {
      next.annual_rate = 0;
    }
    onChange(toSimulationInput(next));
  };

  return (
    <Card className="min-w-[260px] flex-1">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base">{item.label}</CardTitle>
        {canRemove && (
          <Button type="button" variant="ghost" size="sm" onClick={onRemove}>
            Remover
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-1">
          <Label>Ativo</Label>
          <select
            className={cn(
              "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
            )}
            value={item.input.asset_type}
            onChange={(e) => patch({ asset_type: e.target.value as SimulationFormValues["asset_type"] })}
          >
            {ASSET_ORDER.map((a) => (
              <option key={a} value={a}>
                {assetLabel(a)}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <Label>Valor inicial</Label>
          <CurrencyInput
            value={item.input.initial_value}
            onValueChange={(v) => patch({ initial_value: v })}
          />
        </div>
        <div className="space-y-1">
          <Label>Aporte mensal</Label>
          <CurrencyInput
            value={item.input.monthly_contribution}
            onValueChange={(v) => patch({ monthly_contribution: v })}
          />
        </div>
        <RateInput
          label={showIpca ? "Spread IPCA+ (% a.a.)" : "Taxa (% a.a.)"}
          value={rateDisabled ? 0 : item.input.annual_rate}
          onValueChange={(v) => patch({ annual_rate: v })}
          disabled={rateDisabled}
          hint={rateDisabled ? "Mercado" : undefined}
        />
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <Label>Prazo</Label>
            <span className="text-muted-foreground">{item.input.period_months} meses</span>
          </div>
          <Slider
            min={1}
            max={120}
            step={1}
            value={[item.input.period_months]}
            onValueChange={(v) => patch({ period_months: v[0] })}
          />
          <Input
            type="number"
            min={1}
            max={600}
            value={item.input.period_months}
            onChange={(e) => patch({ period_months: Number(e.target.value) })}
          />
        </div>
        {item.error && <p className="text-xs text-destructive">{item.error}</p>}
      </CardContent>
    </Card>
  );
}

export function ComparisonPanel() {
  const { items, addItem, removeItem, updateItem, runAll } = useComparison();
  const [busy, setBusy] = React.useState(false);

  const handleRun = async () => {
    setBusy(true);
    try {
      await runAll();
    } finally {
      setBusy(false);
    }
  };

  const maxMonths = Math.max(
    0,
    ...items.map((i) => i.result?.monthly_evolution.length ?? 0),
  );
  const chartData = React.useMemo(() => {
    const rows: Record<string, number | string>[] = [];
    for (let m = 1; m <= maxMonths; m++) {
      const row: Record<string, number | string> = { month: m };
      for (const it of items) {
        if (!it.result) continue;
        const ev = it.result.monthly_evolution[m - 1];
        if (ev) row[it.label] = ev.net_balance;
      }
      rows.push(row);
    }
    return rows;
  }, [items, maxMonths]);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start gap-3">
        {items.map((it) => (
          <ComparisonRow
            key={it.id}
            item={it}
            onChange={(input) => updateItem(it.id, input)}
            onRemove={() => removeItem(it.id)}
            canRemove={items.length > 2}
          />
        ))}
        <div className="flex min-h-[120px] min-w-[48px] items-start pt-4">
          <AddAssetButton onClick={addItem} disabled={items.length >= 4} />
        </div>
      </div>

      <Button type="button" size="lg" onClick={handleRun} disabled={busy}>
        {busy ? "Comparando…" : "Comparar todos"}
      </Button>

      {maxMonths > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Saldo líquido por mês</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatBRL(Number(v))} width={72} />
                <Tooltip content={<TooltipBrl />} />
                <Legend />
                {items.map((it, idx) =>
                  it.result ? (
                    <Line
                      key={it.id}
                      type="monotone"
                      dataKey={it.label}
                      name={it.label}
                      stroke={LINE_COLORS[idx % LINE_COLORS.length]}
                      dot={false}
                      strokeWidth={2}
                    />
                  ) : null,
                )}
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {items.map((it) =>
          it.result ? (
            <div key={it.id} className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">{it.label}</h3>
              <SummaryCards data={it.result} animate={false} />
            </div>
          ) : (
            <div key={it.id} className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
              {it.label}
              {it.error ? <p className="mt-2 text-destructive">{it.error}</p> : <p className="mt-2">Sem resultado</p>}
            </div>
          ),
        )}
      </div>
    </div>
  );
}
