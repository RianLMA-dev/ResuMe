"use client";

import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import { getConfig, isHosted, waitForApi } from "@/lib/api";

interface DemoState {
  enabled: boolean;
  ttlHours: number;
}

const DemoContext = createContext<DemoState>({ enabled: false, ttlHours: 6 });

export const useDemo = () => useContext(DemoContext);

export function DemoProvider({ children }: { children: ReactNode }) {
  const [phase, setPhase] = useState<"waiting" | "ready" | "failed">(isHosted ? "waiting" : "ready");
  const [state, setState] = useState<DemoState>({ enabled: false, ttlHours: 6 });

  useEffect(() => {
    let cancelled = false;

    async function start() {
      if (isHosted && !(await waitForApi())) {
        if (!cancelled) setPhase("failed");
        return;
      }
      try {
        const config = await getConfig();
        if (!cancelled) setState({ enabled: config.demo, ttlHours: config.session_ttl_hours });
      } catch {
        // Sem /config (API antiga ou fora do ar): segue como uso normal.
      }
      if (!cancelled) setPhase("ready");
    }

    start();
    return () => {
      cancelled = true;
    };
  }, []);

  if (phase !== "ready") {
    return (
      <div className="flex min-h-screen items-center justify-center px-6 text-center">
        <div className="max-w-md">
          <p className="text-lg font-semibold">
            {phase === "waiting" ? "Acordando a demonstração..." : "Não consegui acordar o servidor"}
          </p>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            {phase === "waiting"
              ? "O servidor gratuito dorme quando ninguém usa e leva até 1 minuto para acordar. Só no primeiro acesso."
              : "Recarregue a página em instantes. Se continuar, o limite de uso da hospedagem pode ter acabado."}
          </p>
        </div>
      </div>
    );
  }

  return <DemoContext.Provider value={state}>{children}</DemoContext.Provider>;
}
