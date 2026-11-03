'use client'

import { STAGE_COLOR, type Application } from "@/lib/types"

interface HeaderMetricsProps {
  applications: Application[]
}

export function HeaderMetrics({ applications }: HeaderMetricsProps) {
  const total = applications.length
  const emAnaliseOuTeste = applications.filter(
    (app) => app.status === "Em Análise" || app.status === "Teste Técnico"
  ).length

  return (
    <div className="hidden sm:flex items-center gap-2 text-xs">
      {/* Badge Total */}
      <div 
        className="flex items-center gap-1.5 rounded-full px-3 py-1 font-medium border"
        style={{ borderColor: "var(--line)", backgroundColor: "var(--panel)" }}
      >
        <span className="text-[color:var(--muted)]">Total:</span>
        <span className="font-bold text-[color:var(--text)]">{total}</span>
      </div>

      {/* Badge Em Andamento */}
      {emAnaliseOuTeste > 0 && (
        <div 
          className="flex items-center gap-1.5 rounded-full px-3 py-1 font-medium"
          style={{ 
            backgroundColor: `color-mix(in srgb, ${STAGE_COLOR["Teste Técnico"]} 15%, transparent)`,
            color: STAGE_COLOR["Teste Técnico"]
          }}
        >
          <span className="h-2 w-2 rounded-full animate-pulse" style={{ backgroundColor: STAGE_COLOR["Teste Técnico"] }} />
          <span>{emAnaliseOuTeste} em andamento</span>
        </div>
      )}
    </div>
  )
}