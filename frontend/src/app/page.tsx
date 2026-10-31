import Image from "next/image";

import Dashboard from "@/components/Dashboard";

export default function Home() {
  return (
    <div className="min-h-screen">
      <header className="border-b px-6 py-3" style={{ borderColor: "var(--line)" }}>
        <h1>
          <Image
            src="/logo-dark.png"
            alt="ResuMe"
            width={942}
            height={257}
            priority
            className="h-10 w-auto"
          />
        </h1>
      </header>
      <main className="mx-auto max-w-[1400px] px-6 py-6">
        <Dashboard />
      </main>
    </div>
  );
}