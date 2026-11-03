'use client'

import { useState } from 'react'

interface UserData {
  name: string
  email: string
  autoSyncGmail: boolean
}

export function UserProfile() {
  const [isOpen, setIsOpen] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const [user, setUser] = useState<UserData>({
    name: 'Desenvolvedor',
    email: 'dev@resume.app',
    autoSyncGmail: true,
  })

  const [tempUser, setTempUser] = useState<UserData>(user)
  const initialLetter = user.name.trim().charAt(0).toUpperCase() || 'U'

  function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setUser(tempUser)
    setIsModalOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-8 w-8 items-center justify-center rounded-full font-bold text-white transition-opacity hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        style={{ backgroundColor: '#2f6bff' }}
        aria-label="Menu do usuário"
      >
        {initialLetter}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />

          <div
            className="absolute right-0 z-20 mt-2 w-56 rounded-xl border p-1 shadow-lg"
            style={{
              backgroundColor: 'var(--panel)',
              borderColor: 'var(--line)',
            }}
          >
            <div className="border-b px-3 py-2 text-xs" style={{ borderColor: 'var(--line)' }}>
              <p className="font-semibold text-[color:var(--text)]">{user.name}</p>
              <p className="truncate text-[color:var(--muted)]">{user.email}</p>
            </div>

            <div className="py-1 text-xs flex flex-col gap-1">
              <button
                onClick={() => {
                  setIsOpen(false)
                  setTempUser(user)
                  setIsModalOpen(true)
                }}
                className="w-full rounded-lg px-3 py-1.5 text-left text-[color:var(--text)] transition-colors hover:bg-[color:var(--bg)] flex items-center gap-2"
              >
                ⚙️ Configurações do Perfil
              </button>
            </div>
          </div>
        </>
      )}

      {/* Modal de Configurações do Perfil */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div
            className="w-full max-w-md rounded-2xl border p-6 shadow-2xl"
            style={{
              backgroundColor: 'var(--panel)',
              borderColor: 'var(--line)',
            }}
          >
            <div className="flex items-center justify-between pb-4 border-b" style={{ borderColor: 'var(--line)' }}>
              <h3 className="text-lg font-semibold text-[color:var(--text)]">Perfil e Preferências</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded-lg p-1 text-[color:var(--muted)] hover:text-[color:var(--text)]"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSave} className="mt-4 flex flex-col gap-4 text-sm">
              <div>
                <label className="mb-1 block text-xs font-medium text-[color:var(--muted)]">Nome</label>
                <input
                  type="text"
                  value={tempUser.name}
                  onChange={(e) => setTempUser({ ...tempUser, name: e.target.value })}
                  className="w-full rounded-lg border py-2 px-3 focus:outline-none focus:ring-1"
                  style={{
                    backgroundColor: 'var(--bg)',
                    borderColor: 'var(--line)',
                    color: 'var(--text)',
                  }}
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-[color:var(--muted)]">E-mail</label>
                <input
                  type="email"
                  value={tempUser.email}
                  onChange={(e) => setTempUser({ ...tempUser, email: e.target.value })}
                  className="w-full rounded-lg border py-2 px-3 focus:outline-none focus:ring-1"
                  style={{
                    backgroundColor: 'var(--bg)',
                    borderColor: 'var(--line)',
                    color: 'var(--text)',
                  }}
                  required
                />
              </div>

              <div className="flex items-center justify-between rounded-lg border p-3" style={{ borderColor: 'var(--line)', backgroundColor: 'var(--bg)' }}>
                <div>
                  <p className="font-medium text-[color:var(--text)]">Sincronização Automática</p>
                  <p className="text-xs text-[color:var(--muted)]">Ler e-mails da pasta Vagas</p>
                </div>
                <input
                  type="checkbox"
                  checked={tempUser.autoSyncGmail}
                  onChange={(e) => setTempUser({ ...tempUser, autoSyncGmail: e.target.checked })}
                  className="h-4 w-4 rounded accent-blue-600 cursor-pointer"
                />
              </div>

              <div className="mt-2 flex justify-end gap-2 pt-3 border-t" style={{ borderColor: 'var(--line)' }}>
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-lg border px-4 py-2 text-xs font-medium text-[color:var(--muted)] hover:bg-[color:var(--bg)]"
                  style={{ borderColor: 'var(--line)' }}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="rounded-lg px-4 py-2 text-xs font-medium text-white transition-opacity hover:opacity-90"
                  style={{ backgroundColor: '#2f6bff' }}
                >
                  Salvar Alterações
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}