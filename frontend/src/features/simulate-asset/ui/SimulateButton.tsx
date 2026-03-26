"use client";

import { Loader2 } from "lucide-react";
import { Button } from "@/shared/ui/button";

interface SimulateButtonProps {
  loading: boolean;
  disabled?: boolean;
}

export function SimulateButton({ loading, disabled }: SimulateButtonProps) {
  return (
    <Button type="submit" className="w-full" disabled={disabled || loading} size="lg">
      {loading ? (
        <>
          <Loader2 className="animate-spin" />
          Simulando…
        </>
      ) : (
        "Simular"
      )}
    </Button>
  );
}
