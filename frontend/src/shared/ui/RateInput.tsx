"use client";

import * as React from "react";
import { cn } from "@/shared/lib/utils";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export interface RateInputProps extends Omit<React.ComponentProps<typeof Input>, "value" | "onChange" | "type"> {
  value: number;
  onValueChange: (value: number) => void;
  label: string;
  hint?: string | null;
  disabled?: boolean;
}

/** Taxa em % a.a. (número, ex.: 12 para 12%). */
export function RateInput({ value, onValueChange, label, hint, disabled, className, id, ...props }: RateInputProps) {
  const inputId = id ?? "rate-input";

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value.replace(",", ".");
    if (v === "" || v === "-") {
      onValueChange(0);
      return;
    }
    const n = Number.parseFloat(v);
    if (!Number.isNaN(n)) onValueChange(n);
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-2">
        <Label htmlFor={inputId}>{label}</Label>
        {hint ? <span className="text-xs text-muted-foreground">{hint}</span> : null}
      </div>
      <div className="relative">
        <Input
          id={inputId}
          type="number"
          step="0.01"
          min={0}
          value={Number.isFinite(value) ? value : 0}
          onChange={handleChange}
          disabled={disabled}
          className={cn("pr-8 tabular-nums", className)}
          {...props}
        />
        <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
          %
        </span>
      </div>
    </div>
  );
}
