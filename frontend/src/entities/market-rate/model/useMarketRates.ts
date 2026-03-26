"use client";

import * as React from "react";
import { ApiError } from "@/shared/api/client";
import { getMarketRates } from "@/entities/market-rate/api/getMarketRates";
import type { MarketRatesView } from "@/entities/market-rate/types";

export function useMarketRates() {
  const [data, setData] = React.useState<MarketRatesView | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const r = await getMarketRates();
        if (cancelled) return;
        setData({
          selicAnnualPct: r.selic_pct,
          ipcaAnnualPct: r.ipca_pct,
          poupancaMonthlyPct: r.poupanca_monthly_pct,
        });
      } catch (e) {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 503) {
          setError("Taxas de mercado indisponíveis.");
        } else {
          setError("Não foi possível carregar as taxas.");
        }
        setData(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}
