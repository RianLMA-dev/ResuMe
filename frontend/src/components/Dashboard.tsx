"use client";

import { useState } from "react";
import EmailForm from "./EmailForm";
import KanbanBoard from "./KanbanBoard";
import SyncButton from "./SyncButton";
import ResumePanel from "./ResumePanel";

interface DashboardProps {
  searchTerm?: string;
}

export default function Dashboard({ searchTerm = "" }: DashboardProps) {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCreated = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col gap-6">
      <SyncButton onSynced={handleCreated} />
      <EmailForm onSaved={handleCreated} />
      <ResumePanel />
      <KanbanBoard refreshKey={refreshKey} searchTerm={searchTerm} />
    </div>
  );
}