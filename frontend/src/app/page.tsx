import Dashboard from "@/components/Dashboard";
import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function Home() {
  return (
    <div className="min-h-screen">
      <header className="border-b px-6 py-3 flex items-center justify-between" style={{ borderColor: "var(--line)" }}>
        <h1>
          <Logo />
        </h1>
        <ThemeToggle />
      </header>
      <main className="mx-auto max-w-[1400px] px-6 py-6">
        <Dashboard />
      </main>
    </div>
  );
}