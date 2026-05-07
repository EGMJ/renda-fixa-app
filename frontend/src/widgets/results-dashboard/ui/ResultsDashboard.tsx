"use client";

import * as React from "react";
import { ChartPanel, SummaryCards, TaxBreakdownTable } from "@/entities/simulation";
import type { AssetType, SimulationOutput } from "@/entities/simulation/types";
import { RateInfoBanner, useMarketRates } from "@/entities/market-rate";
import { ExportPDFButton } from "@/features/export-pdf";
import { ResultsSkeleton } from "./ResultsSkeleton";

interface ResultsDashboardProps {
  asset: AssetType;
  periodMonths: number;
  data: SimulationOutput | null;
  loading: boolean;
}

export function ResultsDashboard({ asset, periodMonths, data, loading }: ResultsDashboardProps) {
  const { data: rates, error: ratesError } = useMarketRates();
  const containerRef = React.useRef<HTMLDivElement>(null);

  if (loading) {
    return <ResultsSkeleton />;
  }

  if (!data) return null;

  return (
    <div className="space-y-4">
      <div ref={containerRef} className="space-y-6">
        <RateInfoBanner asset={asset} rates={rates} marketUnavailable={!!ratesError} />
        <SummaryCards data={data} />
        <ChartPanel data={data} periodMonths={periodMonths} />
        <TaxBreakdownTable data={data} />
      </div>
      <ExportPDFButton
        targetRef={containerRef}
        assetType={asset}
        periodMonths={periodMonths}
        disabled={!data}
      />
    </div>
  );
}
