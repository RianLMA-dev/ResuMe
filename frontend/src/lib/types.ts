export const STATUSES = [
  "Inscrito",
  "Em Análise",
  "Teste Técnico",
  "Entrevista",
  "Oferta",
  "Rejeitado",
  "Indefinido",
] as const;

export type Status = (typeof STATUSES)[number];

export interface Application {
  id: number;
  company_name: string;
  job_title: string;
  status: Status;
  key_requirements: string[];
  next_steps: string | null;
  confidence: number;
  created_at: string;
  updated_at: string;
}

export const STAGE_COLOR: Record<Status, string> = {
  Inscrito: "var(--stage-inscrito)",
  "Em Análise": "var(--stage-analise)",
  "Teste Técnico": "var(--stage-teste)",
  Entrevista: "var(--stage-entrevista)",
  Oferta: "var(--stage-oferta)",
  Rejeitado: "var(--stage-rejeitado)",
  Indefinido: "var(--stage-indefinido)",
};