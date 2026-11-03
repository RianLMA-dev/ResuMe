import type { Application, Status } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    throw new ApiError(response.status, `Erro ${response.status} ao chamar ${path}`);
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

  const response = await fetch("http://localhost:8000/resume/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || "Erro ao fazer upload do PDF.");
  }

  return response.json();
}