import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

export interface GeneratePdfMeta {
  assetType: string;
  periodMonths: number;
}

/**
 * Gera PDF a partir do painel de resultados.
 * Preferir tema claro (light mode) para melhor contraste na impressão.
 */
export async function generatePdf(element: HTMLElement, meta: GeneratePdfMeta): Promise<void> {
  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: "#ffffff",
  });

  const imgData = canvas.toDataURL("image/png");
  const pdf = new jsPDF({ orientation: "p", unit: "mm", format: "a4" });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const headerY = margin;
  const date = new Date().toISOString().slice(0, 10);
  pdf.setFontSize(10);
  pdf.text(`Simulação ${meta.assetType} — ${meta.periodMonths} meses — ${date}`, margin, headerY);
  const y = headerY + 6;

  const imgWidth = pageWidth - margin * 2;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;
  const availableH = pageHeight - y - margin;

  let drawW = imgWidth;
  let drawH = imgHeight;
  if (drawH > availableH) {
    const r = availableH / drawH;
    drawH *= r;
    drawW *= r;
  }

  pdf.addImage(imgData, "PNG", margin, y, drawW, drawH);

  const name = `simulacao-${meta.assetType}-${meta.periodMonths}m-${date}.pdf`;
  pdf.save(name);
}
