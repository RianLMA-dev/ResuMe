"use client";

import { useEffect, useState } from "react";

import {
  ApiError,
  getResume,
  listApplications,
  optimizeResume,
  saveResume,
  uploadResumePdf, // Import da nova função
  type ResumeOptimization,
} from "@/lib/api";
import type { Application } from "@/lib/types";

type Message = { kind: "ok" | "info" | "error"; text: string };

const STYLES: Record<Message["kind"], string> = {
  ok: "border-green-500/40 bg-green-500/10 text-green-700 dark:text-green-300",
  info: "border-slate-500/40 bg-slate-500/10 text-slate-700 dark:text-slate-300",
  error: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
};

const FIELD_STYLE = {
  backgroundColor: "var(--bg)",
  borderColor: "var(--line)",
  color: "var(--text)",
};

function scoreColor(score: number) {
  if (score < 40) return "#ef4444";
  if (score < 70) return "#f59e0b";
  return "#22c55e";
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ResumePanel() {
  const [open, setOpen] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const [resumeText, setResumeText] = useState("");
  const [savedText, setSavedText] = useState("");
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploadingPdf, setUploadingPdf] = useState(false); // Estado de carregamento do PDF
  const [resumeMessage, setResumeMessage] = useState<Message | null>(null);

  const [job, setJob] = useState("");
  const [applications, setApplications] = useState<Application[]>([]);
  const [applicationId, setApplicationId] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisMessage, setAnalysisMessage] = useState<Message | null>(null);
  const [result, setResult] = useState<ResumeOptimization | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  useEffect(() => {
    if (!open || loaded) return;
    setLoaded(true);

    getResume()
      .then((resume) => {
        setResumeText(resume.content);
        setSavedText(resume.content);
        setSavedAt(resume.updated_at);
      })
      .catch((error) => {
        if (!(error instanceof ApiError && error.status === 404)) {
          setResumeMessage({ kind: "error", text: "Não consegui carregar o currículo salvo." });
        }
      });

    listApplications()
      .then(setApplications)
      .catch(() => {});
  }, [open, loaded]);

  const hasSavedResume = savedText.trim().length > 0;
  const hasUnsavedChanges = resumeText !== savedText;
  const canAnalyze =
    hasSavedResume && !analyzing && (job.trim().length >= 20 || applicationId !== "");

  async function handleSaveResume() {
    setSaving(true);
    setResumeMessage(null);
    try {
      const saved = await saveResume(resumeText);
      setSavedText(saved.content);
      setSavedAt(saved.updated_at);
      setResumeMessage({ kind: "ok", text: "Currículo salvo." });
    } catch (error) {
      if (error instanceof ApiError && error.status === 422) {
        setResumeMessage({
          kind: "error",
          text: "O currículo precisa ter pelo menos 50 caracteres.",
        });
      } else {
        setResumeMessage({ kind: "error", text: "Não consegui salvar. A API está rodando?" });
      }
    } finally {
      setSaving(false);
    }
  }

  // Handler para processar o upload do PDF
  async function handlePdfUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setResumeMessage({ kind: "error", text: "Por favor, selecione um arquivo no formato PDF." });
      return;
    }

    setUploadingPdf(true);
    setResumeMessage(null);

    try {
      const data = await uploadResumePdf(file);
      setResumeText(data.content);
      setSavedText(data.content);
      setSavedAt(data.updated_at);
      setResumeMessage({ kind: "ok", text: "PDF lido e currículo salvo com sucesso!" });
    } catch (error: any) {
      setResumeMessage({
        kind: "error",
        text: error.message || "Erro ao ler o arquivo PDF.",
      });
    } finally {
      setUploadingPdf(false);
      event.target.value = ""; // Limpa o input
    }
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalysisMessage(null);
    setResult(null);

    const description = job.trim();
    try {
      const data = await optimizeResume(
        description ? { job_description: description } : { application_id: Number(applicationId) },
      );
      setResult(data);
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setAnalysisMessage({ kind: "error", text: "Salve o seu currículo antes de analisar." });
      } else if (error instanceof ApiError && error.status === 404) {
        setAnalysisMessage({ kind: "error", text: "Essa candidatura não existe mais." });
      } else {
        setAnalysisMessage({ kind: "error", text: "Não consegui analisar. A API está rodando?" });
      }
    } finally {
      setAnalyzing(false);
    }
  }

  async function copy(text: string, index: number) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 1500);
    } catch {}
  }

  return (
    <section
      className="rounded-xl border transition-colors duration-200"
      style={{ backgroundColor: "var(--panel)", borderColor: "var(--line)" }}
    >
      <button
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-4 p-4 text-left"
      >
        <span>
          <span className="block text-sm font-semibold">Otimizar currículo</span>
          <span className="block text-xs text-[color:var(--muted)]">
            Compare o seu currículo com uma vaga e veja o que falta.
          </span>
        </span>
        <span aria-hidden className="text-lg text-[color:var(--muted)]">
          {open ? "−" : "+"}
        </span>
      </button>

      {open && (
        <div className="grid gap-6 border-t p-4 lg:grid-cols-2" style={{ borderColor: "var(--line)" }}>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between gap-2">
              <label htmlFor="resume-text" className="text-sm font-semibold">
                Seu currículo base
              </label>

              {/* Botão de Upload de PDF Padronizado */}
              <label
                className="cursor-pointer inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-all hover:opacity-90 active:scale-95 disabled:pointer-events-none disabled:opacity-50"
                style={{ backgroundColor: "var(--accent)" }}
              >
                <svg
                  className="h-3.5 w-3.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
                <span>{uploadingPdf ? "Lendo Curriculo..." : "Importar Curriculo"}</span>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  disabled={uploadingPdf}
                  className="hidden"
                />
              </label>
            </div>

            <textarea
              id="resume-text"
              value={resumeText}
              onChange={(event) => setResumeText(event.target.value)}
              rows={12}
              placeholder="Cole aqui o texto do seu currículo ou importe um arquivo PDF acima..."
              className="w-full rounded-lg border p-3 text-sm"
              style={FIELD_STYLE}
            />

            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-xs text-[color:var(--muted)]">
                {savedAt ? `Salvo em ${formatDateTime(savedAt)}.` : "Ainda não salvo."}
                {hasUnsavedChanges && hasSavedResume && " Há alterações não salvas."}
              </p>
              <button
                onClick={handleSaveResume}
                disabled={saving || resumeText.trim().length < 50 || !hasUnsavedChanges}
                className="rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                style={{ backgroundColor: "var(--accent)" }}
              >
                {saving ? "Salvando..." : "Salvar currículo"}
              </button>
            </div>

            {resumeMessage && (
              <p className={`rounded-lg border px-3 py-2 text-sm ${STYLES[resumeMessage.kind]}`}>
                {resumeMessage.text}
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="job-text" className="text-sm font-semibold">
              Descrição da vaga
            </label>
            <textarea
              id="job-text"
              value={job}
              onChange={(event) => setJob(event.target.value)}
              rows={7}
              placeholder="Cole aqui a descrição completa da vaga, com os requisitos..."
              className="w-full rounded-lg border p-3 text-sm"
              style={FIELD_STYLE}
            />

            <label htmlFor="application-select" className="mt-1 text-xs text-[color:var(--muted)]">
              Ou use uma candidatura do quadro
            </label>
            <select
              id="application-select"
              value={applicationId}
              onChange={(event) => setApplicationId(event.target.value)}
              className="w-full rounded-lg border p-2 text-sm"
              style={FIELD_STYLE}
            >
              <option value="">Nenhuma</option>
              {applications.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.company_name} - {app.job_title}
                </option>
              ))}
            </select>

            <button
              onClick={handleAnalyze}
              disabled={!canAnalyze}
              className="mt-1 self-start rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
              style={{ backgroundColor: "var(--accent)" }}
            >
              {analyzing ? "Analisando..." : "Analisar compatibilidade"}
            </button>

            {analysisMessage && (
              <p className={`rounded-lg border px-3 py-2 text-sm ${STYLES[analysisMessage.kind]}`}>
                {analysisMessage.text}
              </p>
            )}
          </div>

          {result && (
            <div className="flex flex-col gap-5 border-t pt-5 lg:col-span-2" style={{ borderColor: "var(--line)" }}>
              <div>
                <p className="mb-1 text-sm font-semibold">
                  Compatibilidade estimada: {result.matching_score}/100
                </p>
                <div
                  role="progressbar"
                  aria-valuenow={result.matching_score}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  className="h-2 w-full overflow-hidden rounded-full"
                  style={{ backgroundColor: "var(--line)" }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${result.matching_score}%`,
                      backgroundColor: scoreColor(result.matching_score),
                    }}
                  />
                </div>
              </div>

              <div>
                <h3 className="mb-2 text-sm font-semibold">
                  Palavras da vaga que faltam no currículo ({result.missing_keywords.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.missing_keywords.map((word) => (
                    <span
                      key={word}
                      className="rounded-full border px-3 py-1 text-xs"
                      style={{ borderColor: "var(--line)" }}
                    >
                      {word}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="mb-2 text-sm font-semibold">Sugestões de frases</h3>
                <ul className="flex flex-col gap-2">
                  {result.suggested_bullet_points.map((point, index) => (
                    <li
                      key={index}
                      className="flex items-start justify-between gap-3 rounded-lg border p-3 text-sm"
                      style={{ borderColor: "var(--line)", backgroundColor: "var(--bg)" }}
                    >
                      <span>{point}</span>
                      <button
                        onClick={() => copy(point, index)}
                        className="shrink-0 text-xs font-semibold"
                        style={{ color: "var(--accent)" }}
                      >
                        {copiedIndex === index ? "Copiado" : "Copiar"}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}