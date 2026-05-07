"use client";

import { Badge } from "@/shared/ui/badge";
import { Card, CardContent } from "@/shared/ui/card";
import { formatBRL, formatPct } from "@/shared/lib/formatters";
import { useCountUp } from "@/shared/lib/useCountUp";
import type { SimulationOutput } from "@/entities/simulation/types";

function pctOf(part: number, whole: number) {
  if (!whole) return 0;
  return (part / whole) * 100;
}

interface SummaryCardsProps {
  data: SimulationOutput;
  animate?: boolean;
}

export function SummaryCards({ data, animate = true }: SummaryCardsProps) {
  const net = useCountUp(data.net_balance, 900, animate);
  const invested = useCountUp(data.total_invested, 900, animate);
  const gross = useCountUp(data.gross_return, 900, animate);
  const ir = useCountUp(data.total_ir, 900, animate);

  const grossPct = pctOf(data.gross_return, data.total_invested);
  const irPct = pctOf(data.total_ir, data.gross_return);

  const cards = [
    {
      title: "Valor líquido final",
      value: net,
      sub: formatPct(data.net_return_pct),
      tone: "text-emerald-600 dark:text-emerald-400",
      border: "border-l-4 border-emerald-500",
    },
    {
      title: "Total investido",
      value: invested,
      sub: "Base do cálculo",
      tone: "text-foreground",
      border: "border-l-4 border-muted-foreground/40",
    },
    {
      title: "Rendimento bruto",
      value: gross,
      sub: formatPct(grossPct),
      tone: "text-green-600/90 dark:text-green-400/90",
      border: "border-l-4 border-[var(--color-chart-gross)]",
    },
    {
      title: "IR total pago",
      value: ir,
      sub: data.total_ir === 0 ? "isento" : formatPct(irPct),
      tone: "text-red-600/90 dark:text-red-400/90",
      border: "border-l-4 border-[var(--color-chart-ir)]",
      isIr: true,
    },
  ] as const;

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {cards.map((c) => (
        <Card key={c.title} className={`overflow-hidden ${c.border}`}>
          <CardContent className="space-y-1 p-4">
            <p className="text-xs font-medium text-muted-foreground">{c.title}</p>
            <div className={`text-lg font-semibold tabular-nums ${c.tone}`}>
              {"isIr" in c && c.isIr && data.total_ir === 0 ? (
                <Badge variant="success">Isento</Badge>
              ) : (
                formatBRL(c.value)
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {"isIr" in c && c.isIr && data.total_ir === 0 ? "Sem tributação regressiva" : c.sub}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
