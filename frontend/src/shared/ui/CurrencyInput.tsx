"use client";

import * as React from "react";
import { formatBRL } from "@/shared/lib/formatters";
import { cn } from "@/shared/lib/utils";
import { Input } from "@/shared/ui/input";

export interface CurrencyInputProps extends Omit<React.ComponentProps<typeof Input>, "value" | "onChange"> {
  value: number;
  onValueChange: (value: number) => void;
}

/** Valor sempre em reais (number). Máscara BRL no campo. */
export function CurrencyInput({ value, onValueChange, className, disabled, ...props }: CurrencyInputProps) {
  const [digits, setDigits] = React.useState(() => Math.round(value * 100).toString());

  React.useEffect(() => {
    setDigits(Math.round(value * 100).toString());
  }, [value]);

  const display = formatBRL(parseInt(digits || "0", 10) / 100);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, "");
    setDigits(raw);
    onValueChange(parseInt(raw || "0", 10) / 100);
  };

  return (
    <Input
      type="text"
      inputMode="numeric"
      autoComplete="off"
      value={display}
      onChange={handleChange}
      disabled={disabled}
      className={cn("tabular-nums", className)}
      {...props}
    />
  );
}
