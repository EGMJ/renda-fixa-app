"use client";

import * as React from "react";

/** Anima de 0 até `target` quando `target` ou `enabled` mudam. */
export function useCountUp(target: number, durationMs = 800, enabled = true) {
  const [value, setValue] = React.useState(() => (enabled ? 0 : target));

  React.useEffect(() => {
    if (!enabled) {
      setValue(target);
      return;
    }
    let raf = 0;
    const start = performance.now();

    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = 1 - (1 - t) ** 3;
      setValue(target * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };

    setValue(0);
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, durationMs, enabled]);

  return value;
}
