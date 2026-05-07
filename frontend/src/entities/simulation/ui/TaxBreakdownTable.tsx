"use client";

import { HelpCircle } from "lucide-react";
import { formatBRL, formatPct } from "@/shared/lib/formatters";
import { Badge } from "@/shared/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import type { SimulationOutput } from "@/entities/simulation/types";

interface TaxBreakdownTableProps {
  data: SimulationOutput;
}

export function TaxBreakdownTable({ data }: TaxBreakdownTableProps) {
  const rows = data.tax_breakdown;
  const totals = rows.reduce(
    (acc, r) => ({
      invested: acc.invested + r.invested_amount,
      ir: acc.ir + r.ir_amount,
      net: acc.net + r.net_profit,
    }),
    { invested: 0, ir: 0, net: 0 },
  );

  return (
    <TooltipProvider delayDuration={200}>
      <div className="w-full overflow-x-auto rounded-lg border">
        <table className="w-full min-w-[640px] text-sm">
          <thead className="bg-muted/50">
            <tr className="text-left">
              <th className="p-3 font-medium">
                <span className="inline-flex items-center gap-1">
                  Aporte #
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button type="button" className="text-muted-foreground hover:text-foreground" aria-label="Sobre PEPS">
                        <HelpCircle className="h-4 w-4" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      PEPS (Primeiro que Entra, Primeiro que Sai): cada aporte é resgatado na ordem cronológica para fins de
                      cálculo do IR regressivo.
                    </TooltipContent>
                  </Tooltip>
                </span>
              </th>
              <th className="p-3 font-medium">Valor investido</th>
              <th className="p-3 font-medium">Prazo (dias)</th>
              <th className="p-3 font-medium">Alíquota IR</th>
              <th className="p-3 font-medium">IR pago</th>
              <th className="p-3 font-medium">Lucro líquido</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.contribution_index} className="border-t">
                <td className="p-3 tabular-nums">{r.contribution_index + 1}</td>
                <td className="p-3 tabular-nums">{formatBRL(r.invested_amount)}</td>
                <td className="p-3 tabular-nums">{r.days_held}</td>
                <td className="p-3">
                  {r.ir_rate === 0 ? (
                    <Badge variant="success">Isento</Badge>
                  ) : (
                    <span className="tabular-nums">{formatPct(r.ir_rate * 100)}</span>
                  )}
                </td>
                <td className="p-3 tabular-nums">{formatBRL(r.ir_amount)}</td>
                <td className="p-3 tabular-nums">{formatBRL(r.net_profit)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="sticky bottom-0 border-t-2 bg-background font-semibold">
            <tr>
              <td className="p-3">Totais</td>
              <td className="p-3 tabular-nums">{formatBRL(totals.invested)}</td>
              <td className="p-3">—</td>
              <td className="p-3">—</td>
              <td className="p-3 tabular-nums">{formatBRL(totals.ir)}</td>
              <td className="p-3 tabular-nums">{formatBRL(totals.net)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </TooltipProvider>
  );
}
