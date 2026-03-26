import type { AssetType } from "@/entities/simulation/types";

export type { AssetType };

export interface AssetOption {
  id: AssetType;
  label: string;
  category: "tributado" | "isento";
}
