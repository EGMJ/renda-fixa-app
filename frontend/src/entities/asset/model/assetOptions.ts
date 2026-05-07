import type { AssetType } from "@/entities/simulation/types";

export const ASSET_ORDER: AssetType[] = [
  "CDB",
  "LC",
  "RDB",
  "TESOURO_SELIC",
  "TESOURO_IPCA",
  "TESOURO_PREFIXADO",
  "DEBENTURE",
  "LCI",
  "LCA",
  "CRI",
  "CRA",
  "DEBENTURE_INCENTIVADA",
  "POUPANCA",
];

const LABELS: Record<AssetType, string> = {
  CDB: "CDB",
  LC: "LC",
  RDB: "RDB",
  TESOURO_SELIC: "Tesouro Selic",
  TESOURO_IPCA: "Tesouro IPCA+",
  TESOURO_PREFIXADO: "Tesouro Prefixado",
  DEBENTURE: "Debênture",
  LCI: "LCI",
  LCA: "LCA",
  CRI: "CRI",
  CRA: "CRA",
  DEBENTURE_INCENTIVADA: "Deb. incentivada",
  POUPANCA: "Poupança",
};

const TAXED: AssetType[] = [
  "CDB",
  "LC",
  "RDB",
  "TESOURO_SELIC",
  "TESOURO_IPCA",
  "TESOURO_PREFIXADO",
  "DEBENTURE",
  "POUPANCA",
];

export function isExempt(asset: AssetType): boolean {
  return !TAXED.includes(asset);
}

export function assetLabel(asset: AssetType): string {
  return LABELS[asset];
}

export function usesMarketRateOnly(asset: AssetType): boolean {
  return asset === "POUPANCA" || asset === "TESOURO_SELIC";
}

export function isTesouroIpca(asset: AssetType): boolean {
  return asset === "TESOURO_IPCA";
}
