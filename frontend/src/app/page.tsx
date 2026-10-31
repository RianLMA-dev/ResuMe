import KanbanBoard from "@/components/KanbanBoard";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">ResuMe</h1>
        <p className="text-sm text-slate-600">Suas candidaturas, uma coluna por etapa.</p>
      </header>
      <KanbanBoard />
    </main>
  );
}