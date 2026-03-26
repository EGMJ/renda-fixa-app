import { ComparisonPanel } from "@/widgets/comparison-panel";

export function ComparisonPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">Comparar ativos</h1>
        <p className="text-muted-foreground">Simule até quatro cenários lado a lado com o mesmo fluxo de aportes.</p>
      </div>
      <ComparisonPanel />
    </div>
  );
}
