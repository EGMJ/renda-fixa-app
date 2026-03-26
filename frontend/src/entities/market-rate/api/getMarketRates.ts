import { apiFetch } from "@/shared/api/client";
import type { MarketRatesResponse } from "@/entities/market-rate/types";

export async function getMarketRates(): Promise<MarketRatesResponse> {
  return apiFetch<MarketRatesResponse>("/api/v1/market-rates");
}
