'use client'

import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { ReactNode } from 'react'

import { DemoProvider } from '@/components/DemoProvider'

export function Providers({ children }: { children: ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="dark" enableSystem>
      <DemoProvider>{children}</DemoProvider>
    </NextThemesProvider>
  )
}