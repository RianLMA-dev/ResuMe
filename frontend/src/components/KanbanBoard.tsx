"use client";

import { useEffect, useState } from "react";

import { deleteApplication, listApplications, updateStatus } from "@/lib/api";
import { STAGE_COLOR, STATUSES, type Application, type Status } from "@/lib/types";

const LOW_CONFIDENCE = 0.7;

const AVATAR_COLORS = ["#2f6bff", "#7c3aed", "#0f766e", "#b45309", "#db2777", "#4f46e5"];

const TAG_STYLES = [
  { bg: "rgba(34, 197, 94, 0.15)", fg: "#86efac" },
  { bg: "rgba(234, 179, 8, 0.15)", fg: "#fde047" },
  { bg: "rgba(59, 130, 246, 0.15)", fg: "#93c5fd" },
  { bg: "rgba(167, 139, 250, 0.15)", fg: "#c4b5fd" },
];

// Transforma um texto em um número fixo, para a mesma empresa ter sempre a mesma cor.
function hashIndex(text: string, size: number) {
  let hash = 0;
  for (const char of text) {
    hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  }
  return hash % size;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

function Avatar({ name }: { name: string }) {
  const initial = name.trim().charAt(0).toUpperCase() || "?";
  return (
    <span
      aria-hidden
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-base font-bold text-white"
      style={{ backgroundColor: AVATAR_COLORS[hashIndex(name, AVATAR_COLORS.length)] }}
    >
      {initial}
    </span>
  );
}

export default function KanbanBoard({ refreshKey = 0 }: { refreshKey?: number }) {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overColumn, setOverColumn] = useState<Status | null>(null);

  useEffect(() => {
    listApplications()
      .then(setApplications)
      .catch(() =>
        setError("Não consegui falar com a API. Ela está rodando em localhost:8000?"),
      )
      .finally(() => setLoading(false));
  }, [refreshKey]);

  async function moveCard(id: number, status: Status) {
    const previous = applications;
    const card = previous.find((app) => app.id === id);
    if (!card || card.status === status) return;

    // Atualiza na tela na hora e desfaz se a API recusar.
    setApplications(previous.map((app) => (app.id === id ? { ...app, status } : app)));
    setError(null);
    try {
      await updateStatus(id, status);
    } catch {
      setApplications(previous);
      setError("Não consegui salvar a mudança de status.");
    }
  }

  async function removeCard(id: number) {
    if (!window.confirm("Apagar esta candidatura?")) return;
    const previous = applications;
    setApplications(previous.filter((app) => app.id !== id));
    try {
      await deleteApplication(id);
    } catch {
      setApplications(previous);
      setError("Não consegui apagar a candidatura.");
    }
  }

  if (loading) {
    return <p className="text-[color:var(--muted)]">Carregando candidaturas...</p>;
  }

  return (
    <section
      className="rounded-xl border p-5"
      style={{ backgroundColor: "var(--panel)", borderColor: "var(--line)" }}
    >
      <h2 className="mb-5 text-xl font-semibold">Candidaturas</h2>

      {error && (
        <p className="mb-4 max-w-3xl rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}

      {applications.length === 0 && !error && (
        <p className="mb-5 max-w-xl text-[color:var(--muted)]">
          Nenhuma candidatura ainda. Cole um e-mail de processo seletivo na caixa acima e o
          primeiro cartão aparece aqui.
        </p>
      )}

      <div className="flex gap-4 overflow-x-auto pb-2">
        {STATUSES.map((status) => {
          const cards = applications.filter((app) => app.status === status);
          return (
            <div
              key={status}
              onDragOver={(event) => {
                event.preventDefault();
                setOverColumn(status);
              }}
              onDragLeave={() => setOverColumn(null)}
              onDrop={(event) => {
                event.preventDefault();
                setOverColumn(null);
                const id = Number(event.dataTransfer.getData("text/plain"));
                if (id) moveCard(id, status);
              }}
              className="w-72 shrink-0 rounded-lg p-2 transition-colors"
              style={{
                backgroundColor: overColumn === status ? "rgba(47, 107, 255, 0.12)" : undefined,
              }}
            >
              <h3 className="mb-3 flex items-center gap-2 px-1 text-xs font-semibold uppercase tracking-wide">
                <span
                  aria-hidden
                  className="inline-block h-4 w-4 rounded-[4px]"
                  style={{ backgroundColor: STAGE_COLOR[status] }}
                />
                {status}
                <span className="font-normal text-[color:var(--muted)]">({cards.length})</span>
              </h3>

              <div className="flex flex-col gap-3">
                {cards.length === 0 && applications.length > 0 && (
                  <p
                    className="rounded-lg border border-dashed px-3 py-6 text-center text-sm text-[color:var(--muted)]"
                    style={{ borderColor: "var(--line)" }}
                  >
                    Arraste um cartão para cá
                  </p>
                )}

                {cards.map((app) => (
                  <article
                    key={app.id}
                    draggable
                    onDragStart={(event) =>
                      event.dataTransfer.setData("text/plain", String(app.id))
                    }
                    className="cursor-grab rounded-lg border p-3 active:cursor-grabbing"
                    style={{
                      backgroundColor: "var(--card)",
                      borderColor:
                        status === "Rejeitado" ? "rgba(239, 68, 68, 0.45)" : "var(--line)",
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <Avatar name={app.company_name} />
                      <div className="min-w-0 flex-1">
                        <h4 className="truncate text-sm font-semibold">{app.job_title}</h4>
                        <p className="truncate text-sm text-[color:var(--muted)]">
                          @ {app.company_name}
                        </p>
                      </div>
                      <button
                        onClick={() => removeCard(app.id)}
                        aria-label={`Apagar candidatura em ${app.company_name}`}
                        className="-mr-1 -mt-1 rounded-sm px-1.5 text-[color:var(--muted)] hover:text-red-400"
                      >
                        ✕
                      </button>
                    </div>

                    {app.key_requirements.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {app.key_requirements.map((req) => {
                          const tag = TAG_STYLES[hashIndex(req, TAG_STYLES.length)];
                          return (
                            <span
                              key={req}
                              className="rounded-md px-2 py-0.5 text-xs font-medium"
                              style={{ backgroundColor: tag.bg, color: tag.fg }}
                            >
                              {req}
                            </span>
                          );
                        })}
                      </div>
                    )}

                    {app.next_steps && (
                      <p
                        className="mt-3 rounded-full px-3 py-1 text-xs"
                        style={{ backgroundColor: "var(--line)" }}
                      >
                        {app.next_steps}
                      </p>
                    )}

                    {app.confidence < LOW_CONFIDENCE && (
                      <p className="mt-3 text-xs font-medium text-amber-400">
                        Confira: a IA teve dúvida nesta extração.
                      </p>
                    )}

                    <p className="mt-3 text-xs text-[color:var(--muted)]">
                      Atualizado em {formatDate(app.updated_at)}
                    </p>
                  </article>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}