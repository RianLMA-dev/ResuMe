"use client";

import { useEffect, useState } from "react";

import { deleteApplication, listApplications, updateStatus } from "@/lib/api";
import { STATUSES, type Application, type Status } from "@/lib/types";

const LOW_CONFIDENCE = 0.7;

export default function KanbanBoard() {
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
  }, []);

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
    return <p className="text-slate-500">Carregando candidaturas...</p>;
  }

  return (
    <div>
      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      <div className="flex gap-4 overflow-x-auto pb-4">
        {STATUSES.map((status) => {
          const cards = applications.filter((app) => app.status === status);
          return (
            <section
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
              className={`w-72 shrink-0 rounded-lg p-3 transition-colors ${
                overColumn === status ? "bg-blue-100" : "bg-slate-200"
              }`}
            >
              <h2 className="mb-3 flex items-center justify-between text-sm font-semibold text-slate-700">
                {status}
                <span className="rounded-full bg-white px-2 py-0.5 text-xs text-slate-600">
                  {cards.length}
                </span>
              </h2>

              <div className="flex flex-col gap-3">
                {cards.map((app) => (
                  <article
                    key={app.id}
                    draggable
                    onDragStart={(event) =>
                      event.dataTransfer.setData("text/plain", String(app.id))
                    }
                    className="cursor-grab rounded-md bg-white p-3 text-slate-900 shadow-sm active:cursor-grabbing"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-sm font-semibold">{app.company_name}</h3>
                        <p className="text-sm text-slate-600">{app.job_title}</p>
                      </div>
                      <button
                        onClick={() => removeCard(app.id)}
                        aria-label="Apagar candidatura"
                        className="text-slate-400 hover:text-red-600"
                      >
                        ✕
                      </button>
                    </div>

                    {app.key_requirements.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {app.key_requirements.map((req) => (
                          <span
                            key={req}
                            className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-700"
                          >
                            {req}
                          </span>
                        ))}
                      </div>
                    )}

                    {app.next_steps && (
                      <p className="mt-2 text-xs text-slate-500">{app.next_steps}</p>
                    )}

                    {app.confidence < LOW_CONFIDENCE && (
                      <p className="mt-2 inline-block rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800">
                        Revisar: extração pouco confiável
                      </p>
                    )}
                  </article>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}