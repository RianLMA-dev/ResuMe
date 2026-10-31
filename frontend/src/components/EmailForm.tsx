"use client";

import { useState } from "react";

import { ApiError, analyzeEmail } from "@/lib/api";

type Message = { kind: "ok" | "info" | "error"; text: string };

const STYLES: Record<Message["kind"], string> = {
  ok: "border-green-500/40 bg-green-500/10 text-green-300",
  info: "border-slate-500/40 bg-slate-500/10 text-slate-300",
  error: "border-red-500/40 bg-red-500/10 text-red-300",
};

export default function EmailForm({ onSaved }: { onSaved: () => void }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const result = await analyzeEmail(text);

      if (result.application) {
        const app = result.application;
        setMessage({
          kind: "ok",
          text: `Salvo: ${app.company_name}, ${app.job_title} (${app.status}).`,
        });
        setText("");
        onSaved();
      } else {
        setMessage({
          kind: "info",
          text: `Este e-mail não parece ser de um processo seletivo. ${result.reason}`,
        });
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 422) {
        setMessage({ kind: "error", text: "O texto está curto demais. Cole o e-mail completo." });
      } else if (error instanceof ApiError && error.status === 502) {
        setMessage({
          kind: "error",
          text: "A IA não conseguiu processar agora. Pode ser o limite por minuto do Gemini: espere um pouco e tente de novo.",
        });
      } else {
        setMessage({ kind: "error", text: "Não consegui falar com a API. Ela está rodando?" });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-6 rounded-xl border p-4"
      style={{ backgroundColor: "var(--panel)", borderColor: "var(--line)" }}
    >
      <label htmlFor="email-text" className="mb-2 block text-sm font-semibold">
        Cole o e-mail de uma vaga
      </label>
      <textarea
        id="email-text"
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={4}
        placeholder="Cole aqui o texto do e-mail..."
        className="w-full rounded-lg border p-3 text-sm placeholder:text-[color:var(--muted)]"
        style={{ backgroundColor: "var(--bg)", borderColor: "var(--line)", color: "var(--text)" }}
      />
      <div className="mt-3 flex items-center justify-between gap-4">
        <p className="text-xs text-[color:var(--muted)]">
          E-mails, telefones, CPFs e links são trocados por marcadores antes de ir para a IA.
        </p>
        <button
          type="submit"
          disabled={loading || text.trim().length < 10}
          className="shrink-0 rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          style={{ backgroundColor: "var(--accent)" }}
        >
          {loading ? "Analisando..." : "Analisar e-mail"}
        </button>
      </div>
      {message && (
        <p className={`mt-3 rounded-lg border px-3 py-2 text-sm ${STYLES[message.kind]}`}>
          {message.text}
        </p>
      )}
    </form>
  );
}