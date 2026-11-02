'use client'

import Image from 'next/image'
import { useTheme } from 'next-themes'
import { useSyncExternalStore } from 'react'

const emptySubscribe = () => () => {}

export function Logo() {
  const { resolvedTheme } = useTheme()

  // Evita problemas de hidratação
  const isMounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  )

  // Enquanto não hidrata no navegador, mantém uma imagem padrão para não dar layout shift
  const src = isMounted && resolvedTheme === 'light' ? '/logo-light.png' : '/logo-dark.png'

  return (
    <Image
      src={src}
      alt="ResuMe"
      width={942}
      height={257}
      priority
      className="h-10 w-auto"
    />
  )
}