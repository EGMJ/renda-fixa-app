"use client";

import * as React from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CHART_COLORS } from "@/shared/lib/constants";
import { formatBRL } from "@/shared/lib/formatters";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import type { SimulationOutput } from "@/entities/simulation/types";

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: { readonly?: unknown }[]; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="mb-1 font-medium">Mês {label}</p>
      <ul className="space-y-0.5">
        {payload.map((p) => {
          const pl = p as { name?: string; value?: number; color?: string };
          if (pl.value === undefined) return null;
          return (
            <li key={String(pl.name)} className="flex items-center gap-2 tabular-nums">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: pl.color }} />
              <span className="text-muted-foreground">{pl.name}:</span>
              <span>{formatBRL(pl.value)}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

interface ChartPanelProps {
  data: SimulationOutput;
  periodMonths: number;
}

export function ChartPanel({ data, periodMonths }: ChartPanelProps) {
  const rows = data.monthly_evolution;
  const tickInterval = Math.max(0, Math.floor(periodMonths / 6) - 1);

  const [hidden, setHidden] = React.useState<Record<string, boolean>>({});

  const toggle = (key: string) => {
    setHidden((h) => ({ ...h, [key]: !h[key] }));
  };

  const legendProps = {
    onClick: (e: { payload?: { dataKey?: unknown } | readonly unknown[] }) => {
      const key = e.payload && typeof e.payload === "object" && !Array.isArray(e.payload) && "dataKey" in e.payload
        ? String((e.payload as { dataKey: unknown }).dataKey)
        : undefined;
      if (key) toggle(key);
    },
    wrapperStyle: { cursor: "pointer" as const },
  };

  const chartData = rows.map((m) => ({
    month: m.month,
    invested: m.total_invested,
    netReturn: m.net_balance - m.total_invested,
    gross: m.gross_balance,
    net: m.net_balance,
    ir: m.accumulated_ir,
  }));

  const stackedData = rows.map((m) => ({
    month: m.month,
    invested: m.total_invested,
    netReturn: Math.max(0, m.net_balance - m.total_invested),
  }));

  return (
    <Tabs defaultValue="evolucao" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="evolucao">Evolução</TabsTrigger>
        <TabsTrigger value="bruto">Bruto vs líquido</TabsTrigger>
        <TabsTrigger value="ir">IR acumulado</TabsTrigger>
      </TabsList>
      <TabsContent value="evolucao">
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={stackedData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} interval={tickInterval} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatBRL(Number(v))} width={72} />
            <Tooltip content={<ChartTooltip />} />
            <Legend {...legendProps} />
            {!hidden.invested && (
              <Area
                type="monotone"
                dataKey="invested"
                name="Total investido"
                stackId="1"
                stroke={CHART_COLORS.invested}
                fill={CHART_COLORS.invested}
                fillOpacity={0.35}
              />
            )}
            {!hidden.netReturn && (
              <Area
                type="monotone"
                dataKey="netReturn"
                name="Rendimento líquido"
                stackId="1"
                stroke={CHART_COLORS.net}
                fill={CHART_COLORS.net}
                fillOpacity={0.35}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </TabsContent>
      <TabsContent value="bruto">
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} interval={tickInterval} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatBRL(Number(v))} width={72} />
            <Tooltip content={<ChartTooltip />} />
            <Legend {...legendProps} />
            {!hidden.gross && (
              <Line type="monotone" dataKey="gross" name="Saldo bruto" stroke={CHART_COLORS.gross} dot={false} strokeWidth={2} />
            )}
            {!hidden.net && (
              <Line type="monotone" dataKey="net" name="Saldo líquido" stroke={CHART_COLORS.net} dot={false} strokeWidth={2} />
            )}
            {!hidden.invested && (
              <Line type="monotone" dataKey="invested" name="Total investido" stroke={CHART_COLORS.invested} dot={false} strokeWidth={2} />
            )}
          </LineChart>
        </ResponsiveContainer>
      </TabsContent>
      <TabsContent value="ir">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} interval={tickInterval} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatBRL(Number(v))} width={72} />
            <Tooltip content={<ChartTooltip />} />
            <Legend {...legendProps} />
            {!hidden.ir && <Bar dataKey="ir" name="IR acumulado" fill={CHART_COLORS.ir} radius={[4, 4, 0, 0]} />}
          </BarChart>
        </ResponsiveContainer>
      </TabsContent>
    </Tabs>
  );
}
