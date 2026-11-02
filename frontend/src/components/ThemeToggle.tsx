'use client'

import Image from 'next/image'
import { useTheme } from 'next-themes'
import { useSyncExternalStore } from 'react'

const emptySubscribe = () => () => {}

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  const isMounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  )

  if (!isMounted) return null

  const isDark = theme === 'dark'

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-white transition-all hover:opacity-90 active:scale-95 focus:outline-none"
      style={{ backgroundColor: "var(--accent)" }}
      aria-label={isDark ? "Alternar para modo claro" : "Alternar para modo escuro"}
      title={isDark ? "Alternar para modo claro" : "Alternar para modo escuro"}
    >
      <div className="relative flex h-5 w-5 items-center justify-center">
        <Image
          src={isDark ? "/sun.png" : "/moon.png"}
          alt={isDark ? "Ícone de Sol" : "Ícone de Lua"}
          width={20}
          height={20}
          className="h-full w-full object-contain"
        />
      </div>
    </button>
  )
}