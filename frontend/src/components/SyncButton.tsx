"use client";

import { useState } from "react";

import { ApiError, syncGmail } from "@/lib/api";

type Message = { kind: "ok" | "info" | "error"; text: string };

const STYLES: Record<Message["kind"], string> = {
  ok: "border-green-500/40 bg-green-500/10 text-green-300",
  info: "border-slate-500/40 bg-slate-500/10 text-slate-300",
  error: "border-red-500/40 bg-red-500/10 text-red-300",
};

export default function SyncButton({ onSynced }: { onSynced: () => void }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);

  async function handleSync() {
    setLoading(true);
    setMessage(null);

    try {
      const result = await syncGmail();

      if (result.checked > 0) onSynced();

      if (result.stopped_by_error) {
        setMessage({
          kind: "error",
          text: `A IA parou no meio (provavelmente o limite por minuto do Gemini). ${result.saved} cartão(ões) criado(s) até aqui. Espere um minuto e clique de novo.`,
        });
      } else if (result.checked === 0) {
        setMessage({ kind: "info", text: "Nenhum e-mail novo no marcador Vagas." });
      } else {
        const extra =
          result.remaining > 0
            ? ` Ainda há ${result.remaining} e-mail(s) na fila: clique de novo para continuar.`
            : "";
        setMessage({
          kind: "ok",
          text: `${result.checked} e-mail(s) analisado(s): ${result.saved} viraram cartão e ${result.discarded} foram descartados.${extra}`,
        });
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setMessage({
          kind: "error",
          text: "A autorização do Gmail expirou. No terminal do back-end, rode: python try_gmail.py",
        });
      } else if (error instanceof ApiError && error.status === 404) {
        setMessage({ kind: "error", text: "O marcador Vagas não foi encontrado no Gmail." });
      } else {
        setMessage({ kind: "error", text: "Não consegui sincronizar. A API está rodando?" });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="mb-4 rounded-xl border p-4"
      style={{ backgroundColor: "var(--panel)", borderColor: "var(--line)" }}
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold">Gmail</h2>
          <p className="text-xs text-[color:var(--muted)]">
            Lê só os e-mails com o marcador Vagas. Cada e-mail passa pela IA uma única vez.
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={loading}
          className="shrink-0 rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          style={{ backgroundColor: "var(--accent)" }}
        >
          {loading ? "Sincronizando... pode levar um minuto" : "Sincronizar Gmail"}
        </button>
      </div>
      {message && (
        <p className={`mt-3 rounded-lg border px-3 py-2 text-sm ${STYLES[message.kind]}`}>
          {message.text}
        </p>
      )}
    </div>
  );
}