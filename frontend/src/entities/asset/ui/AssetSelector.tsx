"use client";

import { Check } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { cn } from "@/shared/lib/utils";
import type { AssetType } from "@/entities/simulation/types";
import { ASSET_ORDER, assetLabel, isExempt } from "@/entities/asset/model/assetOptions";

interface AssetSelectorProps {
  value: AssetType;
  onChange: (asset: AssetType) => void;
}

export function AssetSelector({ value, onChange }: AssetSelectorProps) {
  const taxed = ASSET_ORDER.filter((a) => !isExempt(a));
  const exempt = ASSET_ORDER.filter((a) => isExempt(a));

  const renderGrid = (items: AssetType[]) => (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {items.map((id) => {
        const selected = value === id;
        return (
          <button
            key={id}
            type="button"
            onClick={() => onChange(id)}
            className={cn(
              "relative flex items-center justify-center rounded-lg border px-2 py-3 text-center text-sm font-medium transition-colors",
              selected
                ? "border-primary bg-primary/10 text-foreground ring-2 ring-primary"
                : "border-border bg-card hover:bg-muted/50",
            )}
          >
            {selected && <Check className="absolute right-2 top-2 h-4 w-4 text-primary" aria-hidden />}
            <span className="px-2">{assetLabel(id)}</span>
          </button>
        );
      })}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Tributados</span>
          <Badge variant="destructive">IR regressivo</Badge>
        </div>
        {renderGrid(taxed)}
      </div>
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Isentos</span>
          <Badge variant="success">Isento de IR</Badge>
        </div>
        {renderGrid(exempt)}
      </div>
    </div>
  );
}
