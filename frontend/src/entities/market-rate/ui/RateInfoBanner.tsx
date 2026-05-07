"use client";

import { formatPct } from "@/shared/lib/formatters";
import { cn } from "@/shared/lib/utils";
import type { AssetType } from "@/entities/simulation/types";
import { isTesouroIpca } from "@/entities/asset/model/assetOptions";
import type { MarketRatesView } from "@/entities/market-rate/types";

function poupancaAnnualFromMonthly(monthlyPct: number) {
  const m = monthlyPct / 100;
  return ((1 + m) ** 12 - 1) * 100;
}

interface RateInfoBannerProps {
  asset: AssetType;
  rates: MarketRatesView | null;
  marketUnavailable?: boolean;
}

export function RateInfoBanner({ asset, rates, marketUnavailable }: RateInfoBannerProps) {
  if (marketUnavailable) {
    return (
      <div
        className={cn(
          "rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950",
          "dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100",
        )}
        role="status"
      >
        Taxas de mercado indisponíveis. A simulação pode usar valores em cache ou falhar ao depender do backend.
      </div>
    );
  }

  const needsMarket = asset === "POUPANCA" || asset === "TESOURO_SELIC" || isTesouroIpca(asset);
  if (!needsMarket) return null;
  if (!rates) return null;

  const selic = rates.selicAnnualPct;
  const poupAnual = poupancaAnnualFromMonthly(rates.poupancaMonthlyPct);
  const share = selic > 0 ? (poupAnual / selic) * 100 : 0;

  return (
    <div
      className={cn(
        "border-l-4 border-blue-500 bg-blue-50 p-4 text-sm text-blue-950",
        "dark:border-blue-400 dark:bg-blue-950/50 dark:text-blue-50",
      )}
      role="status"
    >
      {asset === "POUPANCA" && (
        <p>
          📊 Simulação baseada em Selic atual: <strong>{formatPct(selic)}</strong> a.a. | Poupança rendendo aprox.{" "}
          <strong>{share.toFixed(0)}%</strong> da Selic ≈ <strong>{formatPct(poupAnual)}</strong> a.a.
        </p>
      )}
      {asset === "TESOURO_SELIC" && (
        <p>
          📊 Simulação baseada em Selic atual: <strong>{formatPct(selic)}</strong> a.a. (Tesouro Selic).
        </p>
      )}
      {isTesouroIpca(asset) && (
        <p className={asset === "TESOURO_IPCA" ? "" : "mt-2"}>
          IPCA de referência: <strong>{formatPct(rates.ipcaAnnualPct)}</strong> a.a. O spread informado soma a essa taxa no
          cálculo do Tesouro IPCA+.
        </p>
      )}
    </div>
  );
}
