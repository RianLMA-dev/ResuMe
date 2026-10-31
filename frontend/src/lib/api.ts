import type { Application, Status } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(`Erro ${response.status} ao chamar ${path}`);
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
