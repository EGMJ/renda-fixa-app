export const formatBRL = (v: number) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);

export const formatPct = (v: number, decimals = 2) =>
  new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(v / 100);

export const formatPrazo = (months: number) =>
  months >= 12 && months % 12 === 0
    ? `${months / 12} ${months / 12 === 1 ? "ano" : "anos"}`
    : `${months} meses`;
