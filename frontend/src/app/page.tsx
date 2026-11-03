'use client'

import { useEffect, useState } from "react"
import Dashboard from "@/components/Dashboard"
import { HeaderMetrics } from "@/components/HeaderMetrics"
import { Logo } from "@/components/Logo"
import { SearchBar } from "@/components/SearchBar"
import { ThemeToggle } from "@/components/ThemeToggle"
import { UserProfile } from "@/components/UserProfile"
import { listApplications } from "@/lib/api"
import type { Application } from "@/lib/types"

export default function Home() {
  const [applications, setApplications] = useState<Application[]>([])
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    listApplications()
      .then(setApplications)
      .catch(() => {})
  }, [])

  return (
    <div className="min-h-screen">
      <header 
        className="border-b px-6 py-3 flex items-center justify-between gap-4" 
        style={{ borderColor: "var(--line)" }}
      >
        <div className="flex items-center gap-6">
          <h1>
            <Logo />
          </h1>
          <HeaderMetrics applications={applications} />
        </div>

        <SearchBar onSearch={setSearchTerm} />

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <UserProfile />
        </div>
      </header>
      <main className="mx-auto max-w-[1400px] px-6 py-6">
        <Dashboard searchTerm={searchTerm} />
      </main>
    </div>
  )
}