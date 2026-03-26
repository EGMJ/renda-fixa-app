"use client";

import * as React from "react";
import { FileDown, Loader2 } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import { generatePdf } from "@/features/export-pdf/lib/generatePdf";

interface ExportPDFButtonProps {
  targetRef: React.RefObject<HTMLElement | null>;
  assetType: string;
  periodMonths: number;
  disabled?: boolean;
}

export function ExportPDFButton({ targetRef, assetType, periodMonths, disabled }: ExportPDFButtonProps) {
  const [loading, setLoading] = React.useState(false);

  const handle = async () => {
    const el = targetRef.current;
    if (!el) return;
    setLoading(true);
    try {
      await generatePdf(el, { assetType, periodMonths });
    } finally {
      setLoading(false);
    }
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="inline-flex w-full sm:w-auto">
            <Button type="button" variant="secondary" className="w-full gap-2" disabled={disabled || loading} onClick={handle}>
              {loading ? <Loader2 className="animate-spin" /> : <FileDown />}
              Exportar PDF
            </Button>
          </span>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs">
          Exporte em tema claro para melhor leitura ao imprimir ou arquivar o PDF.
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
