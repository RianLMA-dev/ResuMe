"use client";

import { useDemo } from "./DemoProvider";

const REPO_URL = "https://github.com/RianLMA-dev/ResuMe";

export default function DemoBanner() {
  const { enabled, ttlHours } = useDemo();
  if (!enabled) return null;

  return (
    <div
      className="border-b px-6 py-2 text-center text-xs"
      style={{ borderColor: "var(--line)", backgroundColor: "var(--panel)" }}
      role="note"
    >
      <strong>Demonstração com dados fictícios.</strong> Seus cartões e currículo somem em até {ttlHours} h.
      Não cole dados reais: o texto é enviado a provedores de IA.{" "}
      <a href={REPO_URL} className="underline" target="_blank" rel="noreferrer">
        Rode na sua máquina, com o Gmail e sem limites
      </a>
      .
    </div>
  );
}
