"use client";

import { Plus } from "lucide-react";
import { Button } from "@/shared/ui/button";

interface AddAssetButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function AddAssetButton({ onClick, disabled }: AddAssetButtonProps) {
  return (
    <Button type="button" variant="outline" size="icon" onClick={onClick} disabled={disabled} aria-label="Adicionar ativo">
      <Plus className="h-5 w-5" />
    </Button>
  );
}
