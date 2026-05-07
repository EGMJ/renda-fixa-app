"use client";

import * as React from "react";
import { toast } from "sonner";
import { ApiError } from "@/shared/api/client";
import { simulateAsset } from "@/features/simulate-asset/api/simulateAsset";
import type { ComparisonItem, SimulationInput } from "@/entities/simulation/types";
import { DEFAULT_SIMULATION_VALUES, makeComparisonLabel } from "@/entities/simulation/model/defaultValues";

const MAX = 4;

function uid() {
  return crypto.randomUUID();
}

export function useComparison() {
  const [items, setItems] = React.useState<ComparisonItem[]>(() => [
    {
      id: uid(),
      label: makeComparisonLabel(DEFAULT_SIMULATION_VALUES.asset_type, 0),
      input: { ...DEFAULT_SIMULATION_VALUES },
      result: null,
      loading: false,
      error: null,
    },
    {
      id: uid(),
      label: makeComparisonLabel("LCI", 1),
      input: { ...DEFAULT_SIMULATION_VALUES, asset_type: "LCI" },
      result: null,
      loading: false,
      error: null,
    },
  ]);

  const itemsRef = React.useRef(items);
  React.useEffect(() => {
    itemsRef.current = items;
  }, [items]);

  const addItem = React.useCallback(() => {
    setItems((prev) => {
      if (prev.length >= MAX) return prev;
      const n = prev.length;
      return [
        ...prev,
        {
          id: uid(),
          label: makeComparisonLabel(DEFAULT_SIMULATION_VALUES.asset_type, n),
          input: { ...DEFAULT_SIMULATION_VALUES },
          result: null,
          loading: false,
          error: null,
        },
      ];
    });
  }, []);

  const removeItem = React.useCallback((id: string) => {
    setItems((prev) => (prev.length <= 2 ? prev : prev.filter((i) => i.id !== id)));
  }, []);

  const updateItem = React.useCallback((id: string, input: SimulationInput) => {
    setItems((prev) =>
      prev.map((i, idx) =>
        i.id === id
          ? {
              ...i,
              input,
              label: makeComparisonLabel(input.asset_type, idx),
            }
          : i,
      ),
    );
  }, []);

  const runAll = React.useCallback(async () => {
    const snapshot = itemsRef.current;
    setItems(snapshot.map((i) => ({ ...i, loading: true, error: null })));

    const settled = await Promise.allSettled(snapshot.map((i) => simulateAsset(i.input)));

    setItems(
      snapshot.map((item, idx) => {
        const s = settled[idx];
        if (s.status === "fulfilled") {
          return { ...item, result: s.value, loading: false, error: null };
        }
        const reason = s.reason;
        let msg = "Falha na simulação";
        if (reason instanceof ApiError) {
          if (reason.status === 503) msg = "Taxas indisponíveis";
          else if (reason.status === 400) msg = reason.message || "Validação";
          else msg = reason.message || msg;
        }
        toast.error(`${item.label}: ${msg}`);
        return { ...item, result: null, loading: false, error: msg };
      }),
    );
  }, []);

  return { items, addItem, removeItem, updateItem, runAll };
}
