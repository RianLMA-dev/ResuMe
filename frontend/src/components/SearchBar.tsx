'use client'

import { useState } from 'react'

interface SearchBarProps {
  onSearch?: (term: string) => void
}

export function SearchBar({ onSearch }: SearchBarProps) {
  const [term, setTerm] = useState('')

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    setTerm(value)
    if (onSearch) onSearch(value)
  }

  return (
    <div className="relative hidden max-w-sm w-full md:block">
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[color:var(--muted)]">
        
      </div>
      <input
        type="text"
        value={term}
        onChange={handleChange}
        placeholder="Buscar vaga, empresa ou skill..."
        className="w-full rounded-lg border py-1.5 pl-9 pr-3 text-sm transition-colors focus:outline-none focus:ring-1"
        style={{
          backgroundColor: "var(--bg)",
          borderColor: "var(--line)",
          color: "var(--text)",
        }}
      />
    </div>
  )
}