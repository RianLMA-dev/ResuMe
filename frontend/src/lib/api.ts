import type { Application, Status } from "./types";

const REMOTE_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Hospedado (a demonstração): o servidor gratuito dorme e leva cerca de 1 minuto para acordar.
export const isHosted = !/^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/.test(REMOTE_API_URL);

// Hospedado, as chamadas vão para /backend no próprio site (ver rewrites em next.config.mjs).
const API_URL = isHosted ? "/backend" : REMOTE_API_URL;

const SESSION_KEY = "resume-demo-session";

/** Identificador do visitante na demonstração. Fora dela, o back-end ignora o cabeçalho. */
function demoSessionId(): string {
  try {
    const saved = window.localStorage.getItem(SESSION_KEY);
    if (saved) return saved;
    const created = crypto.randomUUID();
    window.localStorage.setItem(SESSION_KEY, created);
    return created;
  } catch {
    return crypto.randomUUID();
  }
}

function sessionHeaders(): Record<string, string> {
  return typeof window === "undefined" ? {} : { "X-Demo-Session": demoSessionId() };
}

export interface PublicConfig {
  demo: boolean;
  session_ttl_hours: number;
  max_email_chars: number;
  max_job_chars: number;
}

export const getConfig = () => request<PublicConfig>("/config", { cache: "no-store" });

/** Espera a API responder (acordar o servidor gratuito). Devolve false se passar do tempo. */
export async function waitForApi(timeoutMs = 150_000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      // Cada tentativa tem limite próprio: uma chamada travada não pode gastar a espera inteira.
      const response = await fetch(`${API_URL}/health`, {
        cache: "no-store",
        signal: AbortSignal.timeout(12_000),
      });
      if (response.ok) return true;
    } catch {
      // ainda dormindo: tenta de novo
    }
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
  return false;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export interface EmailAnalysis {
  is_job_related: boolean;
  reason: string;
  application: Application | null;
}

export interface GmailSyncResult {
  checked: number;
  saved: number;
  discarded: number;
  remaining: number;
  stopped_by_error: boolean;
}

async function errorMessage(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => null);
  return typeof body?.detail === "string" ? body.detail : fallback;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { ...sessionHeaders(), ...(init?.headers as Record<string, string> | undefined) },
  });
  if (!response.ok) {
    throw new ApiError(
      response.status,
      await errorMessage(response, `Erro ${response.status} ao chamar ${path}`),
    );
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const listApplications = () =>
  request<Application[]>("/applications", { cache: "no-store" });

export const updateStatus = (id: number, status: Status) =>
  request<Application>(`/applications/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });

export const deleteApplication = (id: number) =>
  request<void>(`/applications/${id}`, { method: "DELETE" });

export const analyzeEmail = (rawText: string) =>
  request<EmailAnalysis>("/emails", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText }),
  });

export const syncGmail = () => request<GmailSyncResult>("/gmail/sync", { method: "POST" });

export interface ResumeRead {
  content: string;
  updated_at: string;
}

export interface ResumeOptimization {
  matching_score: number;
  missing_keywords: string[];
  suggested_bullet_points: string[];
}

export const getResume = () => request<ResumeRead>("/resume", { cache: "no-store" });

export const saveResume = (content: string) =>
  request<ResumeRead>("/resume", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });

export const optimizeResume = (payload: { job_description?: string; application_id?: number }) =>
  request<ResumeOptimization>("/optimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

export async function uploadResumePdf(file: File): Promise<{ id: number; content: string; updated_at: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/resume/upload`, {
    method: "POST",
    headers: sessionHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response, "Erro ao fazer upload do PDF."));
  }

  return response.json();
}

export const optimizeForApplication = (applicationId: number) =>
  optimizeResume({ application_id: applicationId });
